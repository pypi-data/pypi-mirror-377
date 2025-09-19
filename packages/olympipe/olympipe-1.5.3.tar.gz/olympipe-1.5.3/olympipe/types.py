from typing import Any, Callable, Dict, Literal, Tuple, TypeVar


InPacket = TypeVar("InPacket")
OutPacket = TypeVar("OutPacket")
ClassType = TypeVar("ClassType")
OptionalInPacket = TypeVar("OptionalInPacket")

RouteMethod = Literal["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
RouteHandler = Tuple[RouteMethod, str, Callable[[Dict[str, Any]], OutPacket]]
