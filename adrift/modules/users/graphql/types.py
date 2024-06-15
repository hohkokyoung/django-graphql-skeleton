import graphene
from django.contrib.auth import get_user_model
from core.types import RelayObjectType
from core.utils import safe_get
from users.models import Role

User = get_user_model()

class RoleNode(RelayObjectType):
    class Meta:
        model = Role
        filter_fields = ["name"]
        fields = "__all__"

class UserNode(RelayObjectType):
    class Meta:
        model = User
        filter_fields = ["username", "roles__name"]
        skip_registry = True
        fields = "__all__"

    pk = graphene.Int()
    full_name = graphene.String()
    archived = graphene.Boolean(default_value=False)
    verified = graphene.Boolean(default_value=False)
    secondary_email = graphene.String(default_value=None)

    def resolve_pk(self, info):
        return self.pk
    
    def resolve_full_name(self, info):
        return f"{self.first_name} {self.last_name}"

    def resolve_archived(self, info):
        return self.status.archived

    def resolve_verified(self, info):
        return self.status.verified

    def resolve_secondary_email(self, info):
        return self.status.secondary_email

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related("roles").select_related("status")

