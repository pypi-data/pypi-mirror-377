from typing import Any, Callable, NoReturn

from fastapi import APIRouter

from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.api.organization import create_organization_endpoints
from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.fastapp import App
from gen_epix.omopdb.api.omop import create_omop_endpoints
from gen_epix.omopdb.api.organization import (
    ApiPermission,
    UpdateUserRequestBody,
    UserInvitationRequestBody,
)
from gen_epix.omopdb.domain import enum, model


def create_routers(
    app: App | None = None,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    assert app
    router_data = [
        # Common routers
        {
            "name": "auth",
            "create_endpoints_fn": create_auth_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.AUTH},
        },
        {
            "name": "rbac",
            "create_endpoints_fn": create_rbac_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.RBAC},
        },
        {
            "name": "organization",
            "create_endpoints_fn": create_organization_endpoints,
            "endpoints_function_kwargs": {
                "service_type": enum.ServiceType.ORGANIZATION,
                "user_class": model.User,
                "user_invitation_class": model.UserInvitation,
                "user_invitation_request_body_class": UserInvitationRequestBody,
                "update_user_request_body_class": UpdateUserRequestBody,
                "api_permission_class": ApiPermission,
            },
        },
        {
            "name": "system",
            "create_endpoints_fn": create_system_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.SYSTEM},
        },
        # Specific routers
        {
            "name": "omop",
            "create_endpoints_fn": create_omop_endpoints,
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        name: str = curr_router_data["name"]  # type: ignore[assignment]
        create_endpoints_fn: Callable = curr_router_data["create_endpoints_fn"]  # type: ignore[assignment]
        router = APIRouter(tags=[name], **router_kwargs)
        endpoints_function_kwargs: dict = curr_router_data.get(  # type: ignore[assignment]
            "endpoints_function_kwargs", {}
        )
        create_endpoints_fn(
            router,
            app,
            registered_user_dependency=registered_user_dependency,
            new_user_dependency=new_user_dependency,
            idp_user_dependency=idp_user_dependency,
            handle_exception=handle_exception,
            **endpoints_function_kwargs,
        )
        routers.append(router)
    return routers
