from __future__ import annotations

import asyncio
import dataclasses
import datetime
import json
import logging
import pickle
from asyncio import Event
from typing import Any
from typing import Callable

import zmq.asyncio
from rich.traceback import Traceback

from egse.exceptions import InitialisationError
from egse.process import ProcessStatus
from egse.registry.client import AsyncRegistryClient
from egse.system import Periodic
from egse.system import get_average_execution_time
from egse.system import get_average_execution_times
from egse.system import get_current_location
from egse.system import get_host_ip
from egse.system import log_rich_output
from egse.system import type_name
from egse.zmq_ser import get_port_number
from egse.zmq_ser import set_address_port
from egse.zmq_ser import zmq_error_response
from egse.zmq_ser import zmq_json_request
from egse.zmq_ser import zmq_json_response
from egse.zmq_ser import zmq_string_request
from egse.zmq_ser import zmq_string_response

logger = logging.getLogger("egse.async_control")

# When zero (0) ports will be dynamically allocated by the system
CONTROL_SERVER_DEVICE_COMMANDING_PORT = 0
CONTROL_SERVER_SERVICE_COMMANDING_PORT = 0


@dataclasses.dataclass
class MessageFormat:
    STRING = 0
    JSON = 1
    PICKLE = 2


async def is_control_server_active(service_type: str, timeout: float = 0.5) -> bool:
    """
    Checks if the Control Server is running.

    This function sends a *Ping* message to the Control Server and expects a *Pong* answer back within the timeout
    period.

    Args:
        service_type (str): the service type of the control server to check
        timeout (float): Timeout when waiting for a reply [s, default=0.5]

    Returns:
        True if the Control Server is running and replied with the expected answer; False otherwise.
    """

    # I have a choice here to check if the control server is active/healthy.
    #
    # 1. I can connect to the ServiceRegistry, and analyse the 'health' field if it is 'passing', or

    with AsyncRegistryClient() as registry:
        service = await registry.discover_service(service_type)
    if service:
        return True if service["health"] == "passing" else False
    else:
        return False

    # 2. I can connect to the control server (by first contacting the service registry) and send a ping.

    # async with AsyncControlClient(service_type=service_type) as client:
    #     response = await client.ping()
    # return response == 'pong'


class AsyncControlServer:
    def __init__(self):
        self.interrupted: Event = asyncio.Event()
        self.logger = logging.getLogger("egse.async_control")

        self.mon_delay = 1000
        """Delay between publish status information [ms]."""
        self.hk_delay = 1000
        """Delay between saving housekeeping information [ms]."""

        self._process_status = ProcessStatus()

        self._service_id = None

        self._sequential_queue = asyncio.Queue()
        """Queue for sequential operations that must preserve order of execution."""

        self.device_command_port = CONTROL_SERVER_DEVICE_COMMANDING_PORT
        """The device commanding port for the control server. This will be 0 at start and dynamically assigned by the
        system."""

        self.service_command_port = CONTROL_SERVER_SERVICE_COMMANDING_PORT
        """The service commanding port for the control server. This will be 0 at start and dynamically assigned by the
        system."""

        self._tasks: list | None = None
        """The background top-level tasks that are performed by the control server."""

        self._ctx = zmq.asyncio.Context.instance()

        # Socket to handle REQ-REP device commanding pattern
        self.device_command_socket = self._ctx.socket(zmq.REP)
        self.device_command_socket.bind(f"tcp://*:{self.device_command_port}")
        self.device_command_port = get_port_number(self.device_command_socket)

        # Socket to handle REQ-REP service commanding pattern
        self.service_command_socket = self._ctx.socket(zmq.REP)
        self.service_command_socket.bind(f"tcp://*:{self.service_command_port}")
        self.service_command_port = get_port_number(self.service_command_socket)

    # FIXME: I don't think we need these methods anymore, since that information should be in the service registry.

    def get_communication_protocol(self) -> str:
        pass

    def get_commanding_port(self) -> int:
        pass

    def get_service_port(self) -> int:
        pass

    def get_monitoring_port(self) -> int:
        pass

    @staticmethod
    def get_ip_address() -> str:
        """Returns the IP address of the current host."""
        return get_host_ip()

    def get_storage_mnemonic(self) -> str:
        """Returns the storage mnemonics used by the Control Server.

        This is a string that will appear in the filename with the housekeeping information of the device, as a way of
        identifying the device.  If this is not implemented in the subclass, then the class name will be used.

        Returns:
            Storage mnemonics used by the Control Server.
        """

        return self.__class__.__name__

    def get_process_status(self) -> dict:
        """Returns the process status of the Control Server.

        Returns:
            Dictionary with the process status of the Control Server.
        """

        return self._process_status.as_dict()

    @staticmethod
    def get_average_execution_times() -> dict:
        """Returns the average execution times of all functions that have been monitored by this process.

        Returns:
            Dictionary with the average execution times of all functions that have been monitored by this process.
                The dictionary keys are the function names, and the values are the average execution times in ms.
        """

        return get_average_execution_times()

    def set_mon_delay(self, seconds: float) -> float:
        """Sets the delay time for monitoring.

        The delay time is the time between two successive executions of the `get_status()` function of the device
        protocol.

        It might happen that the delay time that is set is longer than what you requested. That is the case when the
        execution of the `get_status()` function takes longer than the requested delay time. That should prevent the
        server from blocking when a too short delay time is requested.

        Args:
            seconds (float): Number of seconds between the monitoring calls

        Returns:
            Delay that was set [ms].
        """

        execution_time = get_average_execution_time(self.device_protocol.get_status)
        self.mon_delay = max(seconds * 1000, (execution_time + 0.2) * 1000)

        return self.mon_delay

    def set_hk_delay(self, seconds: float) -> float:
        """Sets the delay time for housekeeping.

        The delay time is the time between two successive executions of the `get_housekeeping()` function of the device
        protocol.

        It might happen that the delay time that is set is longer than what you requested. That is the case when the
        execution of the `get_housekeeping()` function takes longer than the requested delay time. That should prevent
        the server from blocking when a too short delay time is requested.

        Args:
            seconds (float): Number of seconds between the housekeeping calls

        Returns:
            Delay that was set [ms].
        """

        execution_time = get_average_execution_time(self.device_protocol.get_housekeeping)
        self.hk_delay = max(seconds * 1000, (execution_time + 0.2) * 1000)

        return self.hk_delay

    def stop(self):
        self.logger.warning("Stopping the async control server.")
        self.interrupted.set()

    async def start(self):
        await self.register_service()

        self._tasks: list[asyncio.Task] = [
            asyncio.create_task(self.process_device_command(), name="process-device-commands"),
            asyncio.create_task(self.process_service_command(), name="process-service-commands"),
            asyncio.create_task(self.send_status_updates(), name="send-status-updates"),
            asyncio.create_task(self.process_sequential_queue(), name="process-sequential-queue"),
        ]

        try:
            while not self.interrupted.is_set():
                await self._check_tasks_health()
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            self.logger.debug(f"Caught CancelledError on server keep-alive loop, terminating {type(self).__name__}.")
        finally:
            await self._cleanup_running_tasks()

        await self.deregister_service()

    async def register_service(self):
        with AsyncRegistryClient() as registry:
            self.logger.info("Registering service AsyncControlServer as type async-control-server")
            self._service_id = await registry.register(
                name=type_name(self),
                host=get_host_ip() or "127.0.0.1",
                port=get_port_number(self.device_command_socket),
                service_type="async-control-server",
                metadata={"service_port": get_port_number(self.service_command_socket)},
            )

    async def deregister_service(self):
        with AsyncRegistryClient() as registry:
            await registry.deregister(self._service_id)

    async def _check_tasks_health(self):
        """Check if any tasks unexpectedly terminated."""
        for task in self._tasks:
            if task.done() and not task.cancelled():
                try:
                    # This will raise any exception that occurred in the task
                    task.result()
                except Exception as exc:
                    self.logger.error(f"Task {task.get_name()} failed: {exc}")
                    # Potentially restart the task or shut down service

    async def _cleanup_running_tasks(self):
        # Cancel all running tasks
        for task in self._tasks:
            if not task.done():
                self.logger.debug(f"Cancelling task {task.get_name()}.")
                task.cancel()

        # Wait for tasks to complete their cancellation
        if self._tasks:
            try:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            except asyncio.CancelledError as exc:
                self.logger.debug(f"Caught {type(exc).__name__}: {exc}.")
                pass

    def _cleanup_device_command_socket(self):
        self.logger.debug("Cleaning up device command sockets.")
        if self.device_command_socket:
            self.device_command_socket.close(linger=100)
        self.device_command_socket = None

    def _cleanup_service_command_socket(self):
        self.logger.debug("Cleaning up service command sockets.")
        if self.service_command_socket:
            self.service_command_socket.close(linger=100)
        self.service_command_socket = None

    async def process_device_command(self):
        while not self.interrupted.is_set():
            try:
                # Wait for a request with timeout to allow checking if still running
                try:
                    parts = await asyncio.wait_for(self.device_command_socket.recv_multipart(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # For commanding, we only accept simple commands as a string or a complex command with arguments as
                # JSON data. In both cases, there are only two parts in this multipart message.
                message_type, data = parts
                if message_type == b"MESSAGE_TYPE:STRING":
                    device_command = {"command": data.decode("utf-8")}
                elif message_type == b"MESSAGE_TYPE:JSON":
                    device_command = json.loads(data.decode())
                else:
                    filename, lineno, function_name = get_current_location()
                    # We have an unknown message format, send an error message back
                    message = zmq_error_response(
                        {
                            "success": False,
                            "message": f"Incorrect message type: {message_type}",
                            "metadata": {
                                "data": data.decode(),
                                "file": filename,
                                "lineno": lineno,
                                "function": function_name,
                            },
                        }
                    )
                    await self.device_command_socket.send_multipart(message)
                    continue

                self.logger.debug(f"Received request: {device_command}")

                self.logger.debug("Process the command...")
                response = await self._process_device_command(device_command)

                self.logger.debug("Send the response...")
                await self.device_command_socket.send_multipart(response)

            except asyncio.CancelledError:
                self.logger.debug("Device command handling task cancelled.")
                break

        self._cleanup_device_command_socket()

    async def _process_device_command(self, cmd: dict[str, Any]) -> list:
        command = cmd.get("command")
        if not command:
            return zmq_error_response(
                {
                    "success": False,
                    "message": "no command field provide, don't know what to do.",
                }
            )

        handlers: dict[str, Callable] = {
            "block": self._block,
            "say": self._hello,
        }

        handler = handlers.get(command)
        if not handler:
            filename, lineno, function_name = get_current_location()
            return zmq_error_response(
                {
                    "success": False,
                    "message": f"Unknown command: {command}",
                    "metadata": {"file": filename, "lineno": lineno, "function": function_name},
                }
            )

        return await handler(cmd)

    async def _hello(self, cmd: dict[str, Any]):
        self.logger.debug("Saying Hello...")
        return zmq_string_response("Hello!")

    async def _block(self, cmd: dict[str, Any]):
        self.logger.debug(f"Blocking the commanding for {cmd['sleep']}s...")
        await asyncio.sleep(cmd["sleep"])
        self.logger.debug(f"Blocking finished after {cmd['sleep']}s.")
        return zmq_string_response("ACK")

    async def _handle_ping(self, cmd: dict[str, Any]) -> list:
        self.logger.debug(f"Handling '{cmd['command']}' request.")

        return zmq_string_response("pong")

    async def _handle_info(self, cmd: dict[str, Any]) -> list:
        self.logger.debug(f"Handling '{cmd['command']}' request.")

        return zmq_json_response(
            {
                "success": True,
                "message": {
                    "name": type(self).__name__,
                    "hostname": self.get_ip_address() or "localhost",
                    "device commanding port": self.device_command_port,
                    "service commanding port": self.service_command_port,
                },
            }
        )

    async def _handle_terminate(self, cmd: dict[str, Any]) -> list:
        self.logger.debug(f"Handling '{cmd['command']}' request.")

        self.stop()

        return zmq_json_response(
            {
                "success": True,
                "message": {"status": "terminating"},
            }
        )

    async def process_service_command(self):
        while not self.interrupted.is_set():
            try:
                # Wait for a request with timeout to allow checking if still running
                try:
                    parts = await asyncio.wait_for(self.service_command_socket.recv_multipart(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # For commanding, we only accept simple commands as a string or a complex command with arguments as
                # JSON data. In both cases, there are only two parts in this multipart message.
                message_type, data = parts
                if message_type == b"MESSAGE_TYPE:STRING":
                    service_command = {"command": data.decode("utf-8")}
                elif message_type == b"MESSAGE_TYPE:JSON":
                    service_command = json.loads(data.decode())
                else:
                    filename, lineno, function_name = get_current_location()
                    # We have an unknown message format, send an error message back
                    message = zmq_error_response(
                        {
                            "success": False,
                            "message": f"Incorrect message type: {message_type}",
                            "metadata": {
                                "data": data.decode(),
                                "file": filename,
                                "lineno": lineno,
                                "function": function_name,
                            },
                        }
                    )
                    await self.service_command_socket.send_multipart(message)
                    continue

                self.logger.debug(f"Received request: {service_command}")

                self.logger.debug("Process the command...")
                response = await self._process_service_command(service_command)

                self.logger.debug("Send the response...")
                await self.service_command_socket.send_multipart(response)

            except asyncio.CancelledError:
                self.logger.debug("Service command handling task cancelled.")
                break

        self._cleanup_service_command_socket()

    async def _process_service_command(self, cmd: dict[str, Any]) -> list:
        command = cmd.get("command")
        if not command:
            return zmq_error_response(
                {
                    "success": False,
                    "message": "no command field provide, don't know what to do.",
                }
            )

        handlers: dict[str, Callable] = {
            "terminate": self._handle_terminate,
            "info": self._handle_info,
            "ping": self._handle_ping,
        }

        handler = handlers.get(command)
        if not handler:
            filename, lineno, function_name = get_current_location()
            return zmq_error_response(
                {
                    "success": False,
                    "message": f"Unknown command: {command}",
                    "metadata": {"file": filename, "lineno": lineno, "function": function_name},
                }
            )

        return await handler(cmd)

    async def process_sequential_queue(self):
        """
        Process operations that need to be executed sequentially.

        When the operation return "Quit" the processing is interrupted.
        """

        while not self.interrupted.is_set():
            try:
                operation = await asyncio.wait_for(self._sequential_queue.get(), 0.1)
                await operation
                self._sequential_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error processing sequential operation: {exc}")

    async def send_status_updates(self):
        """
        Send status information about the control server and the device connection to the monitoring channel.
        """

        async def status():
            self.logger.info(f"{datetime.datetime.now()} Sending status updates.")
            await asyncio.sleep(0.5)  # ideally, should not be larger than periodic interval

        try:
            periodic = Periodic(interval=1.0, callback=status)
            periodic.start()

            await self.interrupted.wait()

            periodic.stop()

        except asyncio.CancelledError:
            self.logger.debug("Caught CancelledError on status updates keep-alive loop.")

    async def enqueue_sequential_operation(self, coroutine_func):
        """
        Add an operation to the sequential queue.

        Args:
            coroutine_func: A coroutine function (async function) to be executed sequentially
        """

        if self._sequential_queue is not None:  # sanity check
            self._sequential_queue.put_nowait(coroutine_func)


DEFAULT_CLIENT_REQUEST_TIMEOUT = 5.0  # seconds
"""Default timeout for sending requests to the control server."""
DEFAULT_LINGER = 100  # milliseconds
"""Default linger for ZeroMQ sockets."""


class AsyncControlClient:
    def __init__(
        self,
        endpoint: str = None,
        service_type: str = None,
        timeout: float = DEFAULT_CLIENT_REQUEST_TIMEOUT,
        linger: int = DEFAULT_LINGER,
    ):
        self.logger = logging.getLogger("egse.async_control")

        self.endpoint = endpoint
        self.service_type = service_type
        self.timeout = timeout  # seconds
        self.linger = linger  # milliseconds

        self.context: zmq.asyncio.Context = zmq.asyncio.Context.instance()
        self.device_command_socket: zmq.asyncio.Socket | None = None
        self.service_command_socket: zmq.asyncio.Socket | None = None

        self.device_command_port: int = 0
        self.service_command_port: int = 0

        self._post_init_is_done = False

    async def _post_init(self) -> bool:
        """
        A post initialisation method that sets the device and service commanding
        ports and the endpoint for this client. The information is retrieved from
        the service registry.

        Returns:
            The method returns True if the device and service commanding port and
            the endpoint could be determined from the service registry.

            If the post initialisation step has already been called, a warning is
            issued, and the method returns True.

            If no service_type is known or the service_type is not registered,
            False is returned.

        """
        if self._post_init_is_done:
            logger.warning("The post_init function is already called, returning.")
            return True

        self._post_init_is_done = True
        if self.service_type:
            with AsyncRegistryClient() as registry:
                service = await registry.discover_service(self.service_type)
            if service:
                hostname = service["host"]
                self.device_command_port = port = service["port"]
                self.service_command_port = service["metadata"]["service_port"]
                self.endpoint = f"tcp://{hostname}:{port}"
                return True
            else:
                return False

        return False

    # Why do we need this create method here?
    # The constructor (`__init__`) can not be an async method and to properly initialise the client,
    # we need to contact the ServiceRegistry for the hostname and port numbers. The service discovery
    # is an async operation.
    # Additionally, it's not a good idea to perform such initialisation inside the constructor of the
    # class anyway. The class can also be called as an async context manager, in which case the create()
    # is not needed and the post initialisation will be done in the `__aenter__` method.

    @classmethod
    async def create(cls, service_type: str) -> AsyncControlClient:
        """Factory method that creates an AsyncControlClient and collects information about the service it needs to
        connect to."""
        client = cls(service_type=service_type)
        if not await client._post_init():
            raise InitialisationError(
                f"Could not initialise AsyncControlClient, no service_type ({service_type}) found. Will not be "
                f"able to connect to the control server."
            )
        return client

    def connect(self):
        self.device_command_socket = self.context.socket(zmq.REQ)
        self.device_command_socket.setsockopt(zmq.LINGER, self.linger)
        self.device_command_socket.connect(self.endpoint)

        self.service_command_socket = self.context.socket(zmq.REQ)
        self.service_command_socket.setsockopt(zmq.LINGER, self.linger)
        self.service_command_socket.connect(set_address_port(self.endpoint, self.service_command_port))

    def disconnect(self):
        if self.device_command_socket:
            self.device_command_socket.close(linger=100)
        self.device_command_socket = None

        if self.service_command_socket:
            self.service_command_socket.close(linger=100)
        self.service_command_socket = None

    async def __aenter__(self):
        if not self._post_init_is_done:
            if not await self._post_init():
                raise InitialisationError(
                    f"Could not initialise AsyncControlClient, no service_type ({self.service_type}) found. Will not "
                    f"be able to connect to the control server."
                )

        self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    async def do(self, cmd: dict[str, Any], timeout: float = 5.0) -> dict[str, Any]:
        """
        Sends a device command to the control server and waits for a response.

        Args:
            cmd (dict): The command to send. Should contain at least a 'command' key.
            timeout (float, optional): Maximum time to wait for a response in seconds. Defaults to 5.0.

        Returns:
            dict: The response from the control server. Contains at least:
                - 'success' (bool): True if the command was processed successfully, False otherwise.
                - 'message' (str or dict): The server's response or an error message.

        Notes:
            If the request times out or a socket error occurs, the method attempts
            to reset the sockets and returns a response with 'success' set to False
            and an appropriate error message.
        """
        response = await self._send_request(self.device_command_socket, cmd, timeout)
        return response

    async def ping(self, timeout: int | None = None) -> str | None:
        response = await self._send_request(self.service_command_socket, "ping", timeout=timeout)
        if response["success"]:
            return response["message"]
        else:
            self.logger.error(f"Server returned an error: {response['message']}")
            return None

    async def info(self) -> str | None:
        response = await self._send_request(self.service_command_socket, "info")
        if response["success"]:
            return response["message"]
        else:
            self.logger.error(f"Server returned an error: {response['message']}")
            return None

    async def stop_server(self) -> str | None:
        response = await self._send_request(self.service_command_socket, "terminate")
        if response["success"]:
            return response["message"]
        else:
            self.logger.error(f"Server returned an error: {response['message']}")
            return None

    def _reset_socket(self) -> bool:
        """
        Closes and re-creates both the device and service command sockets for the client,
        reconnecting them to their respective endpoints.

        If the endpoint or port numbers are missing, the socket will not be connected
        and a warning will be issued.

        This method is typically used to recover from socket errors or timeouts.

        Raises:
            Exceptions are logged as error messages and the method returns False.

        Returns:
            True if both sockets were properly reconnected, False if any socket
            is not connected or an Exception occurred..
        """

        def reset(socket_attr, port):
            sock = getattr(self, socket_attr)
            if sock:
                sock.close()
            new_sock = self.context.socket(zmq.REQ)
            new_sock.setsockopt(zmq.LINGER, self.linger)
            if self.endpoint and port:
                new_sock.connect(set_address_port(self.endpoint, port))
                connected = True
            else:
                self.logger.warning(f"Socket '{socket_attr}' not connected: endpoint='{self.endpoint}', port='{port}'")
                connected = False
            setattr(self, socket_attr, new_sock)
            return connected

        try:
            dev_sock_connected = reset("device_command_socket", self.device_command_port)
            srv_sock_connected = reset("service_command_socket", self.service_command_port)
            return dev_sock_connected and srv_sock_connected
        except Exception as exc:
            self.logger.error(f"Failed to reset sockets: Caught {type_name(exc)}: {exc}")
            return False

    async def _send_request(
        self, socket: zmq.asyncio.Socket, request: dict[str, Any] | str, timeout: float | None = None
    ) -> dict[str, Any]:
        """
        Send a request to the control server and get the response.

        A request can be a string with a simple command, e.g. 'ping', or it can be a dictionary
        in which case it will be sent as a JSON request. The dictionary shall have the following format:

            request = {
                'command': <the command string without arguments>,
                'args': [*args],
                'kwargs': {**kwargs},
            }

        The response from the server will always be a dictionary with at least the following structure:

            response = {
                'success': <True or False>,
                'message': <The content of the data returned by the server>,
            }

        Args:
            request: The request to send to the control server.
            timeout: how many seconds before the request times out.

        Returns:
            The response from the control server as a dictionary.
        """

        timeout = timeout or self.timeout

        try:
            if not socket:
                raise RuntimeError("Socket of the AsyncControlClient is not initialized.")

            if isinstance(request, str):
                message = zmq_string_request(request)
            elif isinstance(request, dict):
                message = zmq_json_request(request)
            else:
                raise ValueError(f"request argument shall be a string or a dictionary, not {type(request)}.")

            await socket.send_multipart(message)

            msg_type, data = await asyncio.wait_for(socket.recv_multipart(), timeout=timeout)
            if msg_type == b"MESSAGE_TYPE:STRING":
                return {"success": True, "message": data.decode("utf-8")}
            elif msg_type == b"MESSAGE_TYPE:JSON":
                return json.loads(data)
            elif msg_type == b"MESSAGE_TYPE:ERROR":
                return pickle.loads(data)
            else:
                msg = f"Unknown server response message type: {msg_type}"
                self.logger.error(msg)
                return {"success": False, "message": msg}
        except asyncio.TimeoutError:
            self.logger.error(f"Request timed out after {timeout:.3f}s")
            reconnected = self._reset_socket()
            return {
                "success": False,
                "message": f"Request timed out, sockets are{' ' if reconnected else ' not '}reconnected",
            }

        except zmq.ZMQError as exc:
            self.logger.error(f"ZMQ error: {exc}")
            reconnected = self._reset_socket()
            return {
                "success": False,
                "message": f"ZMQError: {exc}, sockets are{' ' if reconnected else ' not '}reconnected.",
            }

        except Exception as exc:
            self.logger.error(f"Error sending request: {type(exc).__name__} – {exc}")
            traceback = Traceback.from_exception(
                type(exc),
                exc,
                exc.__traceback__,
                show_locals=True,  # Optional: show local variables
                width=None,  # Optional: use full width
                extra_lines=3,  # Optional: context lines
            )
            log_rich_output(self.logger, logging.ERROR, traceback)
            return {"success": False, "message": str(exc)}


async def control_server_test():
    # First start the control server as a background task.
    server = AsyncControlServer()
    server_task = asyncio.create_task(server.start())

    # Give the control server the time to start up
    await asyncio.sleep(0.5)

    # As of now, the server_task is running 'in the background' in the event loop.

    # Now create a control client that will connect to the above server.
    async with AsyncControlClient(service_type="async-control-server") as client:
        # Sleep some time, so we can see the control server in action, e.g. status reports, housekeeping, etc
        logger.info("Sleep for 5s...")
        await asyncio.sleep(5.0)

        response = await client.ping()
        logger.info(f"ping: {response = }")

        response = await client.info()
        logger.info(f"info: {response = }")

        # info() is a service command and not a device command, so this will fail.
        response = await client.do({"command": "info"})
        logger.info(f"command info: {response=}")

        # this will block commanding since commands are executed in the same task
        # the do() will timeout after 3s, but the block command will run for 10s on the server
        response = await client.do({"command": "block", "sleep": 9}, timeout=3.0)
        logger.info(f"Blocking response: {response=}")

        # ping() is a service command is so this is not blocked by the above block() command
        response = await client.ping()
        logger.info(f"ping: {response=}")

        # say() is a device command and will time out after 2s because the above blocking
        # block() command is still running on the server
        response = await client.do({"command": "say"}, timeout=2.0)
        logger.info(f"say: {response=}")

        # Sleep some time, so we can see the control server in action, e.g. status reports, housekeeping, etc
        logger.info("Sleep for 8s...")
        await asyncio.sleep(8.0)

        is_active = await is_control_server_active(service_type="async-control-server")
        logger.info(f"Server status: {'active' if is_active else 'unreachable'}")

        logger.info("Terminating the server.")
        response = await client.stop_server()
        logger.info(f"stop_server: {response = }")

    is_active = await is_control_server_active(service_type="async-control-server")
    logger.info(f"Server status: {'active' if is_active else 'unreachable'}")

    await server_task

    is_active = await is_control_server_active(service_type="async-control-server")
    logger.info(f"Server status: {'active' if is_active else 'unreachable'}")


if __name__ == "__main__":
    logging.captureWarnings(True)

    try:
        asyncio.run(control_server_test())
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating.")
