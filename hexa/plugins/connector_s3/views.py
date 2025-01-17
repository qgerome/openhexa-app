import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ...metrics.decorators import do_not_track
from .api import generate_download_url, generate_upload_url
from .datacards import BucketCard, ObjectCard
from .datagrids import ObjectGrid
from .models import Bucket

logger = getLogger(__name__)


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.prefetch_indexes().filter_for_user(request.user),
        pk=datasource_id,
    )
    bucket_card = BucketCard(bucket, request=request)
    if request.method == "POST" and bucket_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.display_name, "connector_s3:datasource_detail", datasource_id),
    ]

    object_grid = ObjectGrid(
        bucket.object_set.prefetch_indexes()
        .filter(parent_key="/")
        .select_related("bucket"),
        parent_model=bucket,
        prefix="",
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    return render(
        request,
        "connector_s3/bucket_detail.html",
        {
            "datasource": bucket,
            "breadcrumbs": breadcrumbs,
            "bucket_card": bucket_card,
            "object_grid": object_grid,
        },
    )


def object_detail(
    request: HttpRequest, bucket_id: uuid.UUID, path: str
) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.prefetch_indexes().filter_for_user(request.user), pk=bucket_id
    )
    s3_object = get_object_or_404(bucket.object_set.prefetch_indexes(), key=path)
    object_card = ObjectCard(model=s3_object, request=request)
    if request.method == "POST" and object_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.name, "connector_s3:datasource_detail", bucket_id),
    ]

    acc = []
    for i, part in enumerate(s3_object.key.split("/")):
        acc.append(part)
        path = "/".join(acc)
        if i != len(s3_object.key.split("/")) - 1:
            path += "/"
        breadcrumbs.append(
            (part, "connector_s3:object_detail", bucket_id, path),
        )

    if s3_object.type == "directory":
        object_grid = ObjectGrid(
            bucket.object_set.prefetch_indexes().filter(parent_key=path),
            parent_model=bucket,
            prefix=s3_object.key,
            per_page=20,
            page=int(request.GET.get("page", "1")),
            request=request,
        )
    else:
        object_grid = None

    return render(
        request,
        "connector_s3/object_detail.html",
        {
            "datasource": bucket,
            "object": s3_object,
            "object_card": object_card,
            "breadcrumbs": breadcrumbs,
            "object_grid": object_grid,
            "default_tab": "content" if s3_object.type == "directory" else "details",
            "download_url": reverse(
                "connector_s3:object_download",
                kwargs={"bucket_id": bucket_id, "path": path},
            )
            if s3_object.type == "file"
            else None,
        },
    )


def object_download(
    request: HttpRequest, bucket_id: uuid.UUID, path: str
) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    target_object = get_object_or_404(bucket.object_set.all(), key=path)

    download_url = generate_download_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_object=target_object,
    )

    return redirect(download_url)


def object_upload(request, bucket_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )

    if not bucket.writable_by(request.user):
        logger.warning("object_upload() called on RO bucket %s", bucket.id)
        raise HttpResponseForbidden(
            "No permission to perform the upload action on this bucket"
        )

    upload_url = generate_upload_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_key=request.GET["object_key"],
    )

    return HttpResponse(upload_url, status=201)


@do_not_track
def bucket_refresh(request, bucket_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )

    object_key = request.GET.get("object_key")
    bucket.refresh(object_key)
    return redirect(
        request.META.get(
            "HTTP_REFERER",
            reverse(
                "connector_s3:object_detail",
                kwargs={"bucket_id": bucket_id, "path": object_key},
            ),
        )
    )
