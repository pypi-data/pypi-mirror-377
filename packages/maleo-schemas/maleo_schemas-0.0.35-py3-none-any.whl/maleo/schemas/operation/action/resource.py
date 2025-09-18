import re
from fastapi import status, HTTPException, Request
from pydantic import Field
from typing import Callable, Literal, Mapping, Optional, Type, TypeVar, Union, overload
from ..enums import (
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)
from .base import BaseOperationAction


class ResourceOperationAction(BaseOperationAction[ResourceOperationType]):
    create_type: Optional[ResourceOperationCreateType] = Field(
        None, description="Resource operation's create type (optional)"
    )
    update_type: Optional[ResourceOperationUpdateType] = Field(
        None, description="Resource operation's update type (optional)"
    )
    data_update_type: Optional[ResourceOperationDataUpdateType] = Field(
        None, description="Resource operation's data update type (optional)"
    )
    status_update_type: Optional[ResourceOperationStatusUpdateType] = Field(
        None, description="Resource operation's status update type (optional)"
    )


ResourceOperationActionT = TypeVar(
    "ResourceOperationActionT", bound=ResourceOperationAction
)


class CreateResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.CREATE
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class ReadResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.READ
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class UpdateResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.UPDATE
    create_type: Optional[ResourceOperationCreateType] = None


class DeleteResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.DELETE
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


AllResourceOperationAction = Union[
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
]


TYPE_ACTION_MODEL_MAP: Mapping[ResourceOperationType, Type] = {
    ResourceOperationType.CREATE: CreateResourceOperationAction,
    ResourceOperationType.READ: ReadResourceOperationAction,
    ResourceOperationType.UPDATE: UpdateResourceOperationAction,
    ResourceOperationType.DELETE: DeleteResourceOperationAction,
}


class Factory:
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.CREATE],
        *,
        create_type: Optional[ResourceOperationCreateType] = ...,
    ) -> CreateResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.READ],
        /,
    ) -> ReadResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.UPDATE],
        *,
        update_type: Optional[ResourceOperationUpdateType] = ...,
        data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
    ) -> UpdateResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.DELETE],
        /,
    ) -> DeleteResourceOperationAction: ...
    @staticmethod
    def generate(
        type_: ResourceOperationType,
        *,
        create_type: Optional[ResourceOperationCreateType] = None,
        update_type: Optional[ResourceOperationUpdateType] = None,
        data_update_type: Optional[ResourceOperationDataUpdateType] = None,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
    ) -> AllResourceOperationAction:
        if type_ is ResourceOperationType.CREATE:
            return CreateResourceOperationAction(create_type=create_type)

        elif type_ is ResourceOperationType.READ:
            return ReadResourceOperationAction()

        elif type_ is ResourceOperationType.UPDATE:
            return UpdateResourceOperationAction(
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )

        elif type_ is ResourceOperationType.DELETE:
            return DeleteResourceOperationAction()

    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.CREATE],
        *,
        request: Request,
        from_state: bool = True,
    ) -> CreateResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.READ],
        *,
        request: Request,
        from_state: bool = True,
    ) -> ReadResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.UPDATE],
        *,
        request: Request,
        from_state: bool = True,
    ) -> UpdateResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.DELETE],
        *,
        request: Request,
        from_state: bool = True,
    ) -> DeleteResourceOperationAction: ...
    @staticmethod
    def extract(
        type_: ResourceOperationType, *, request: Request, from_state: bool = True
    ) -> AllResourceOperationAction:
        model = TYPE_ACTION_MODEL_MAP[type_]
        if from_state:
            action = request.state.operation_action

            if not isinstance(action, model):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mismatched 'resource_operation_action' type, expected '{model.__name__}' but received '{type(action).__name__}'.",
                )

            return action

        else:
            create_type = None
            update_type = None
            data_update_type = None
            status_update_type = None

            if request.method == "POST":
                if request.url.path.endswith("/restore"):
                    create_type = ResourceOperationCreateType.RESTORE
                else:
                    create_type = ResourceOperationCreateType.NEW
                return CreateResourceOperationAction(create_type=create_type)
            elif request.method == "GET":
                return ReadResourceOperationAction()
            elif request.method in ["PATCH", "PUT"]:
                if request.method == "PUT":
                    update_type = ResourceOperationUpdateType.DATA
                    data_update_type = ResourceOperationDataUpdateType.FULL
                elif request.method == "PATCH":
                    status_pattern = re.search(
                        r"/status/(delete|restore|deactivate|activate)(?:/.*)?$",
                        request.url.path,
                    )
                    if status_pattern:
                        update_type = ResourceOperationUpdateType.STATUS
                        action = status_pattern.group(1)
                        try:
                            status_update_type = ResourceOperationStatusUpdateType(
                                action
                            )
                        except ValueError:
                            # This shouldn't happen since regex already validates, but keep for safety
                            pass
                    else:
                        update_type = ResourceOperationUpdateType.DATA
                        data_update_type = ResourceOperationDataUpdateType.PARTIAL
                return UpdateResourceOperationAction(
                    update_type=update_type,
                    data_update_type=data_update_type,
                    status_update_type=status_update_type,
                )
            elif request.method == "DELETE":
                return DeleteResourceOperationAction()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to determine resource operation action",
                )

    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.CREATE], *, from_state: bool = True
    ) -> Callable[..., CreateResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.READ], *, from_state: bool = True
    ) -> Callable[..., ReadResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.UPDATE], *, from_state: bool = True
    ) -> Callable[..., UpdateResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.DELETE], *, from_state: bool = True
    ) -> Callable[..., DeleteResourceOperationAction]: ...
    @staticmethod
    def as_dependency(
        type_: ResourceOperationType, *, from_state: bool = True
    ) -> Callable[..., AllResourceOperationAction]:

        def dependency(request: Request) -> AllResourceOperationAction:
            return Factory.extract(type_, request=request, from_state=from_state)

        return dependency
