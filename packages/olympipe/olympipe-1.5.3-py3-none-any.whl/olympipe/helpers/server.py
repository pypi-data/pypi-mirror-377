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
    server_socket.listen(100)

    last_activity_time = time.time()

    while True:
        connection: Optional[socket.socket] = None
        try:
            connection, _ = server_socket.accept()
            data = b""
            request_path: str = ""
            body: Any = {}

            # Lecture sécurisée des données HTTP
            while True:
                try:
                    chunk = connection.recv(1024)
                    if not chunk:  # Connexion fermée par le client
                        break
                    data += chunk

                    try:
                        req: Any = dpkt.http.Request(data)
                        request_path = cast(str, urllib.parse.urlparse(req.uri).path)
                        try:
                            body = json.loads(req.body) if req.body else None
                        except json.JSONDecodeError:
                            body = None
                        break
                    except dpkt.NeedData:
                        continue  # Besoin de plus de données

                except socket.timeout:
                    # Timeout sur la lecture, on abandonne cette connexion
                    break
                except Exception:
                    # Erreur de lecture, on abandonne cette connexion
                    break

            # Si pas de données valides reçues, fermer la connexion
            if not data:
                if connection:
                    connection.close()
                continue

            # Recherche du handler approprié
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
                send_json_response(
                    connection,
                    {"error": "Path not found"},
                    status=404,
                    reason="Not Found",
                )

        except StopIteration:
            # Arrêt propre demandé
            if connection:
                send_json_response(connection, {"status": "killed"})
                connection.close()
            return

        except BlockingIOError:
            # Aucune connexion en attente - vérifier le timeout d'inactivité
            if (
                inactivity_timeout is not None
                and time.time() - last_activity_time > inactivity_timeout
            ):
                print("Closing server due to inactivity")
                return
            # Continuer la boucle pour les autres connexions

        except socket.timeout:
            # Timeout sur accept() - continuer normalement
            yield Exception()

        except Exception as e:
            # Erreur générale - logguer et continuer si possible
            print(f"Server error: {e}")
            if connection:
                try:
                    send_json_response(
                        connection,
                        {"error": f"{e}"},
                        status=500,
                        reason="Internal Server Error",
                    )
                except Exception:
                    # Si on ne peut pas envoyer la réponse, tant pis
                    pass
                try:
                    connection.close()
                except Exception:
                    pass
            # Continuer le serveur au lieu de s'arrêter


def send_json_response(
    connection: socket.socket,
    response: Dict[str, Any],
    status: int = 200,
    reason: str = "OK",
) -> None:
    try:
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
    except Exception as e:
        print("Error sending response", e)
        connection.close()
