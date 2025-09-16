from typing import Any
from uuid import UUID

from litestar.enums import RequestEncodingType
from litestar.security.jwt import OAuth2Login, Token


def get_default_signature_namespaces() -> dict[str, Any]:
    return {
        'Token': Token,
        'OAuth2Login': OAuth2Login,
        'RequestEncodingType': RequestEncodingType,
        'UUID': UUID,
        # 'Body': Body,
        # 'm': m,
        # 'UserService': UserService,
        # 'RoleService': RoleService,
        # 'TeamService': TeamService,
        # 'TeamMemberService': TeamMemberService,
        # 'UserRoleService': UserRoleService,
    }
