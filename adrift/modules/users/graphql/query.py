import graphene
from graphene import relay
from core.types import RelayFilterConnectionField, RelayNode
from core.utils import handle_graphql_error
from users.enums import Role as RoleEnum
from .types import *

class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)
    user = RelayNode.Field(UserNode)
    all_users = RelayFilterConnectionField(UserNode)

    @handle_graphql_error()
    def resolve_me(self, info):
        user = info.context.user

        if user.is_authenticated:
            return user
        return None