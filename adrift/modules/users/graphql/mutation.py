import graphene
from graphql_auth import relay
from core.types import RelayMutation, eval_permission
from .types import RoleNode
from users.models import Role
from users.enums import Role as RoleEnum
from graphql_jwt.decorators import login_required, user_passes_test

class CreateRoleMutation(RelayMutation):
    class Input:
        name = graphene.String(required=True)

    role = graphene.Field(RoleNode)

    @classmethod
    @user_passes_test(lambda user: eval_permission(user, login_required=True))
    def resolve_mutation(cls, root, info, name):
        if Role.objects.contains_duplicates(name):
            return cls(success=False)
        
        role = Role.objects.create(name)
        return cls(success=True, role=role)

class AuthMutation(graphene.ObjectType):
    register = relay.Register.Field()
    verify_account = relay.VerifyAccount.Field()
    resend_activation_email = relay.ResendActivationEmail.Field()
    send_password_reset_email = relay.SendPasswordResetEmail.Field()
    password_reset = relay.PasswordReset.Field()
    password_change = relay.PasswordChange.Field()
    archive_account = relay.ArchiveAccount.Field()
    delete_account = relay.DeleteAccount.Field()
    update_account = relay.UpdateAccount.Field()

    # django-graphql-jwt inheritances
    token_auth = relay.ObtainJSONWebToken.Field()
    verify_token = relay.VerifyToken.Field()
    refresh_token = relay.RefreshToken.Field()
    revoke_token = relay.RevokeToken.Field()

class Mutation(AuthMutation, graphene.ObjectType):
    create_role = CreateRoleMutation.Field()