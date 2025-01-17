import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django_countries import countries
from django_countries.fields import Country

from hexa.core.templatetags.colors import hash_color
from hexa.user_management.models import Organization, User

identity_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

identity_query = QueryType()
identity_mutations = MutationType()


@identity_query.field("me")
def resolve_me(_, info):
    request = info.context["request"]

    return request.user if request.user.is_authenticated else None


@identity_query.field("countries")
def resolve_countries(*_):
    return [Country(c) for c, _ in countries]


@identity_query.field("organizations")
def resolve_organizations(*_):
    return [o for o in Organization.objects.all()]


@identity_mutations.field("login")
def resolve_login(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user_candidate = authenticate(
        request, email=kwargs["input"]["email"], password=kwargs["input"]["password"]
    )

    if user_candidate is not None:
        login(request, user_candidate)

        return {"success": True, "me": user_candidate}
    else:
        return {"success": False}


@identity_mutations.field("logout")
def resolve_logout(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if request.user.is_authenticated:
        logout(request)

    return {"success": True}


user = ObjectType("User")


@user.field("avatar")
def resolve_avatar(obj: User, *_):
    return {"initials": obj.initials, "color": hash_color(obj.email)}


country = ObjectType("Country")


@country.field("alpha3")
def resolve_alpha3(obj: Country, *_):
    return obj.alpha3


@country.field("flag")
def resolve_flag(obj: Country, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(obj.flag)


organization = ObjectType("Organization")


@organization.field("type")
def resolve_type(obj: Organization, *_):
    return obj.get_organization_type_display()


identity_bindables = [
    identity_query,
    user,
    country,
    organization,
    identity_mutations,
]
