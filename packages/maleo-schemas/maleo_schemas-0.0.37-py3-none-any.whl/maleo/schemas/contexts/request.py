from datetime import datetime, timezone
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Callable, Generic, List, Optional, Tuple, TypeVar
from uuid import UUID, uuid4
from maleo.mixins.identity import RequestId
from maleo.mixins.timestamp import RequestTimestamp
from maleo.types.boolean import OptionalBoolean
from maleo.types.dict import OptionalStringToStringDict
from maleo.types.string import OptionalString
from ..user_agent import UserAgent


class RequestContext(
    RequestTimestamp,
    RequestId,
):
    method: str = Field(..., description="Request's method")
    url: str = Field(..., description="Request's URL")
    ip_address: str = Field("unknown", description="Client's IP address")
    is_internal: OptionalBoolean = Field(None, description="True if IP is internal")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Request's headers"
    )
    path_params: OptionalStringToStringDict = Field(
        None, description="Request's path parameters"
    )
    query_params: OptionalString = Field(None, description="Request's query parameters")
    user_agent: UserAgent = Field(..., description="User agent")
    referer: OptionalString = Field(None, description="Referrer URL")
    origin: OptionalString = Field(None, description="Origin of the request")
    host: OptionalString = Field(None, description="Host header from request")
    forwarded_proto: OptionalString = Field(
        None, description="Forwarded protocol (http/https)"
    )
    language: OptionalString = Field(None, description="Accepted languages from client")

    @classmethod
    def extract_client_ip(cls, request: Request) -> str:
        """Extract client IP with more robust handling of proxies"""
        # * Check for x-forwarded-for header (common when behind proxy/load balancer)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # * The client's IP is the first one in the list
            ips = [ip.strip() for ip in x_forwarded_for.split(",")]
            return ips[0]

        # * Check for x-real-ip header (used by some proxies)
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip

        # * Fall back to direct client requestection
        return request.client.host if request.client else "unknown"

    @classmethod
    def from_request(cls, request: Request) -> "RequestContext":
        id = request.state.request_id
        if not id or not isinstance(id, UUID):
            id = uuid4()
            request.state.request_id = id

        requested_at = request.state.requested_at
        if not requested_at or not isinstance(requested_at, datetime):
            requested_at = datetime.now(tz=timezone.utc)
            request.state.requested_at = requested_at

        ip_address = cls.extract_client_ip(request)

        user_agent_string = request.headers.get("user-agent", "")
        user_agent = UserAgent.from_string(user_agent_string=user_agent_string)

        return cls(
            id=id,
            requested_at=requested_at,
            method=request.method,
            url=request.url.path,
            ip_address=ip_address,
            is_internal=(
                None
                if ip_address == "unknown"
                else (
                    ip_address.startswith("10.")
                    or ip_address.startswith("192.168.")
                    or ip_address.startswith("172.")
                )
            ),
            headers=request.headers.items(),
            path_params=None if not request.path_params else request.path_params,
            query_params=(
                None if not request.query_params else str(request.query_params)
            ),
            user_agent=user_agent,
            referer=request.headers.get("referer"),
            origin=request.headers.get("origin"),
            host=request.headers.get("host"),
            forwarded_proto=request.headers.get("x-forwarded-proto"),
            language=request.headers.get("accept-language"),
        )

    @classmethod
    def as_dependency(cls) -> Callable[..., "RequestContext"]:
        """Create a FastAPI dependency for this request context."""

        def dependency(request: Request) -> "RequestContext":
            return cls.from_request(request)

        return dependency


RequestContextT = TypeVar("RequestContextT", bound=Optional[RequestContext])


class RequestContextMixin(BaseModel, Generic[RequestContextT]):
    request_context: RequestContextT = Field(..., description="Request's context")
