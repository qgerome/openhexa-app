import os

from notebook.services.contents.largefilemanager import LargeFileManager
from habari.contents import MultiContentsManager, GCSContentsManager, S3ContentsManager


c = get_config()

c.NotebookApp.contents_manager_class = MultiContentsManager
c.MultiContentsManager.manager_classes = {
    "": LargeFileManager,
    "(GCS) habari-test": GCSContentsManager,
    "(S3) blsq-habari-test": S3ContentsManager,
}
c.HybridContentsManager.manager_kwargs = {
    "": {},
    "(GCS) habari-test": {
        "project": os.environ["GCS_PROJECT"],
        "token": "/etc/secrets/service-account.json",
        "bucket": os.environ["GCS_BUCKET_NAME"],
    },
    "(S3) blsq-habari-test": {
        "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "bucket": os.environ["S3_BUCKET_NAME"],
    },
}

c.GCSManager.bucket = os.environ["GCS_BUCKET_NAME"]

c.NotebookApp.tornado_settings = {"autoreload": os.environ.get("DEBUG", False)}
