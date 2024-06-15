from django.conf import settings
import graphene
from graphene import relay
from graphql import GraphQLError
from graphene.relay.node import NodeField, Node
from graphene_django import DjangoObjectType as BaseObjectType
from graphene_django.filter import DjangoFilterConnectionField as BaseRelayFilterConnectionField
from core.utils import handle_graphql_error

def eval_permission(user, login_required=False, permission_roles=[]):
    if login_required and not user.is_authenticated:
        raise Exception("Only for logged-in users.")
    
    if (user.is_authenticated):
        user_has_permission = user.roles.exists_by_names(permission_roles)
    
    if login_required and permission_roles and not user_has_permission:
        raise Exception("You do not have the permission to access this.")
    
    return True
    

class RelayNode(Node):
    @classmethod
    def Field(cls, *args, **kwargs):
        cls.login_required = kwargs.pop("login_required", False)
        cls.permission_roles = kwargs.pop("permission_roles", [])
        return NodeField(cls, *args, **kwargs)
    
    @classmethod
    @handle_graphql_error()
    def node_resolver(cls, only_type, root, info, id):
        # check whether the query requires permission
        eval_permission(info.context.user, cls.login_required, cls.permission_roles)
        return super().get_node_from_global_id(info, id, only_type=only_type)
    

class CountableConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return len(root.iterable)


class RelayObjectType(BaseObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model,
        interfaces=(RelayNode,),
        filter_fields=["id"],
        connection_class=CountableConnection,
        **options,
    ):
        return super().__init_subclass_with_meta__(
            model=model,
            interfaces=interfaces,
            filter_fields=filter_fields,
            connection_class=connection_class,
            **options,
        )


class RelayFilterConnectionField(BaseRelayFilterConnectionField):
    def __init__(
        self,
        type_,
        *args,
        **kwargs,
    ):
        self.login_required = kwargs.pop("login_required", False)
        self.permission_roles = kwargs.pop("permission_roles", [])
        super().__init__(type_, *args, **kwargs)

    @classmethod
    def default_resolver(cls, args, info, iterable):
        return iterable

    @handle_graphql_error()
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        # get queryset back from default resolver
        iterable = cls.default_resolver(args=args, info=info, iterable=iterable)

        # check whether the query requires permission
        eval_permission(info.context.user, cls.login_required, cls.permission_roles)

        # return error if no queryset is found
        # otherwise proceed to return the result from the queryset
        if iterable is None:
            raise Exception(f"{connection.__name__} matching query does not exist.")
        
        return super(RelayFilterConnectionField, cls).resolve_queryset(
            **{
                "connection": connection,
                "iterable": iterable,
                "info": info,
                "args": args,
                "filtering_args": filtering_args,
                "filterset_class": filterset_class,
            }
        )

class RelayMutation(relay.ClientIDMutation):
    """Base class for all mutations with default success and errors fields."""
    # Define the output fields
    success = graphene.Boolean(description="Indicates whether the mutation was successful.")
    errors = graphene.List(graphene.String, description="List of errors, if any.")

    class Meta:
        abstract = True

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        """
        Placeholder for the main logic to be executed.
        Should be overridden by the inheriting class.
        """
        raise NotImplementedError("The resolve_mutation method must be overridden.")

    @classmethod
    @handle_graphql_error()
    def mutate_and_get_payload(cls, root, info, **input):
        """
        Wrap the main mutation logic and handle success/error response.
        """

        return cls.resolve_mutation(root, info, **input)
