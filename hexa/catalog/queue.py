from logging import getLogger

from django.contrib.contenttypes.models import ContentType
from dpq.queue import AtLeastOnceQueue

logger = getLogger(__name__)


def datasource_sync(queue, job):
    try:
        # permission and db existing are checked by views -> but may change since, so assume failure is possible
        logger.info(
            "start datasource sync, type: %s, id: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
        )
        datasource_type = ContentType.objects.get_for_id(id=job.args["contenttype_id"])
        datasource = datasource_type.get_object_for_this_type(id=job.args["object_id"])
        sync_result = datasource.sync()
        logger.info(
            "end datasource sync type: %s, id: %s, result: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
            sync_result,
        )
    except Exception:
        logger.exception("datasource sync failed")


# task queue for the postgresql connector
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
datasource_sync_queue = AtLeastOnceQueue(
    tasks={
        "datasource_sync": datasource_sync,
    },
    notify_channel="datasource_sync_queue",
)