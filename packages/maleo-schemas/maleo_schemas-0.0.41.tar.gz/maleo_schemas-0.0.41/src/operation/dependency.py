from fastapi import Request, Header
from uuid import UUID, uuid4
from maleo.enums.request import Header as HeaderEnum
from maleo.types.uuid import OptionalUUID


def get_operation_id(
    request: Request,
    oid: OptionalUUID = Header(
        None, alias=HeaderEnum.X_OPERATION_ID.value, description="Operation ID Header"
    ),
) -> UUID:
    # Try request's state first
    operation_id = request.state.operation_id
    if isinstance(operation_id, UUID):
        return operation_id

    # Try header next
    if oid is not None:
        return oid

    # Generate and assign if not found
    operation_id = uuid4()
    request.state.operation_id = operation_id

    return operation_id
