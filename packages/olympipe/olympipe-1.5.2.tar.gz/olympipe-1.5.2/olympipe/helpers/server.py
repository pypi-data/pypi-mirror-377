import json
import socket
import time
import urllib.parse
from typing import Any, Dict, Generator, List, Optional, Tuple, Union, cast

import dpkt  # type: ignore

from olympipe.types import OutPacket, RouteHandler


def server_generator(
    route_handlers: List[RouteHandler[OutPacket]],
    host: str = "localhost",
    port: int = 8000,
    debug: bool = False,
    inactivity_timeout: Optional[float] = None,
) -> Generator[Union[Exception, Tuple[socket.socket, OutPacket]], Any, None]:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.settimeout(0.5)
    server_socket.setblocking(False)
    server_socket.bind((host, port))
    server_socket.listen(5)

    last_activity_time = time.time()

    while True:
        try:
            connection, _ = server_socket.accept()
            data = b""
            request_path: str = ""
            body: Any = {}
            while True:
                chunk = connection.recv(1024)
                data += chunk
                try:
                    req: Any = dpkt.http.Request(data)
                    request_path = cast(str, urllib.parse.urlparse(req.uri).path)
                    body = json.loads(req.body)
                    break
                except dpkt.NeedData:
                    pass
                except json.JSONDecodeError:
                    if req.body == b"":
                        body = None
                        break

            found = False
            for method, path, func in route_handlers:
                if method == req.method and path == request_path:
                    if debug:
                        print(f"Handling {req.method} {request_path} with {func}")
                    yield connection, func(body)
                    last_activity_time = time.time()
                    found = True
                    break
            if not found:
                print(f"No route handler for {req.method} {request_path}")
                send_json_response(connection, {"error": "Path not found"}, status=404, reason="Not Found")  # type: ignore
        except StopIteration:
            send_json_response(connection, {"status": "killed"})  # type: ignore
            connection.close()  # type: ignore
            return
        except BlockingIOError:
            if (
                inactivity_timeout is not None
                and time.time() - last_activity_time > inactivity_timeout
            ):
                print("Closing server due to inactivity")
                try:
                    connection.close()
                except Exception as e:
                    print("Error closing connection", e)
                return
        except socket.timeout:
            yield Exception()
        except Exception as e:
            print(e)
            send_json_response(connection, {"error": f"{e}"}, status=500, reason="Internal Server Error")  # type: ignore
            connection.close()  # type: ignore
            return


def send_json_response(
    connection: socket.socket,
    response: Dict[str, Any],
    status: int = 200,
    reason: str = "OK",
) -> None:
    response_json = json.dumps(response)
    encoded_response = dpkt.http.Response(
        status=status,
        reason=reason,
        body=response_json.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Content-Length": f"{len(response_json)}",
        },
    ).pack()
    connection.sendall(encoded_response)
    connection.close()
