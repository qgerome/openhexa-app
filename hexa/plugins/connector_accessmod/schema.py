import pathlib
import uuid
from mimetypes import guess_extension

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest
from django_countries.fields import Country

from config import settings
from hexa.core.graphql import result_page
from hexa.plugins.connector_accessmod.models import File, Fileset, FilesetRole, Project
from hexa.plugins.connector_s3.api import generate_upload_url
from hexa.plugins.connector_s3.models import Bucket

accessmod_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
accessmod_query = QueryType()
accessmod_mutations = MutationType()


@accessmod_query.field("accessmodProject")
def resolve_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Project.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Project.DoesNotExist:
        return None


@accessmod_query.field("accessmodProjects")
def resolve_accessmod_projects(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = Project.objects.filter_for_user(request.user)

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@accessmod_mutations.field("createAccessmodProject")
def resolve_create_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    project = Project.objects.create(
        owner=request.user,
        name=create_input["name"],
        country=Country(create_input["country"]["code"]),
        spatial_resolution=create_input["spatialResolution"],
    )

    return {"success": True, "project": project}


@accessmod_mutations.field("updateAccessmodProject")
def resolve_update_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        # TODO: rationalize
        changed = False
        if "name" in update_input:
            project.name = update_input["name"]
            changed = True
        if "spatialResolution" in update_input:
            project.spatial_resolution = update_input["spatialResolution"]
            changed = True
        if "country" in update_input:
            project.country = Country(update_input["country"]["code"])
            changed = True
        if changed:
            project.save()

        return {"success": True, "project": project}
    except Project.DoesNotExist:
        return {"success": False}


@accessmod_mutations.field("deleteAccessmodProject")
def resolve_delete_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        project.delete()  # TODO: soft-delete?

        return {"success": True}
    except Project.DoesNotExist:
        return {"success": False}


fileset_object = ObjectType("AccessmodFileset")


@fileset_object.field("files")
def resolve_accessmod_fileset_files(fileset: Fileset, info, **kwargs):
    return [f for f in fileset.file_set.all()]


@accessmod_query.field("accessmodFileset")
def resolve_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Fileset.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Fileset.DoesNotExist:
        return None


@accessmod_query.field("accessmodFilesets")
def resolve_accessmod_filesets(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = (
        Fileset.objects.filter_for_user(request.user)
        .filter(project_id=kwargs["projectId"])
        .order_by("-created_at")
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@accessmod_mutations.field("createAccessmodFileset")
def resolve_create_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    fileset = Fileset.objects.create(
        owner=request.user,
        name=create_input["name"],
        project=Project.objects.filter_for_user(request.user).get(
            id=create_input["projectId"]
        ),
        role=FilesetRole.objects.get(id=create_input["roleId"]),
    )

    return {"success": True, "fileset": fileset}


@accessmod_mutations.field("deleteAccessmodFileset")
def resolve_delete_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    delete_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(request.user).get(id=delete_input["id"])
    fileset.delete()

    return {"success": True}


@accessmod_mutations.field("prepareAccessmodFileUpload")
def resolve_prepare_accessmod_file_upload(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    prepare_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(request.user).get(
        id=prepare_input["filesetId"]
    )

    # This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_S3_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_S3_BUCKET_NAME is not set")
    try:
        bucket = Bucket.objects.get(name=settings.ACCESSMOD_S3_BUCKET_NAME)
    except Bucket.DoesNotExist:
        raise ValueError(
            f"The {settings.ACCESSMOD_S3_BUCKET_NAME} bucket does not exist"
        )

    target_key = f"{fileset.project.id}/{uuid.uuid4()}{guess_extension(prepare_input['mimeType'])}"
    upload_url = generate_upload_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_key=target_key,
    )

    return {
        "success": True,
        "upload_url": upload_url,
        "file_uri": f"s3://{bucket.name}/{target_key}",
    }


@accessmod_mutations.field("createAccessmodFile")
def resolve_create_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(request.user).get(
        id=create_input["filesetId"]
    )
    file = File.objects.create(
        uri=create_input["uri"],
        mime_type=create_input["mimeType"],
        fileset=fileset,
    )
    fileset.save()  # Will update updated_at

    return {"success": True, "file": file}


@accessmod_mutations.field("deleteAccessmodFile")
def resolve_delete_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    delete_input = kwargs["input"]
    file = File.objects.filter_for_user(request.user).get(id=delete_input["id"])
    fileset = file.fileset
    file.delete()
    fileset.save()  # Will update updated_at

    return {"success": True}


@accessmod_query.field("accessmodFilesetRole")
def resolve_accessmod_fileset_role(_, info, **kwargs):
    try:
        return FilesetRole.objects.get(id=kwargs["id"])
    except FilesetRole.DoesNotExist:
        return None


@accessmod_query.field("accessmodFilesetRoles")
def resolve_accessmod_fileset_roles(_, info, **kwargs):
    queryset = FilesetRole.objects.all()

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


accessmod_bindables = [accessmod_query, accessmod_mutations, fileset_object]
