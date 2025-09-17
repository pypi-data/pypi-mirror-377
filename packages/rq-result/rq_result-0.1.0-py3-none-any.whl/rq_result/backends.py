import logging

from django.db import transaction

from rq_result import get_job_model

logger = logging.getLogger(__name__)


class DatabaseBackend:
    def __init__(self):
        self.job_model = get_job_model()

    def store_result(self, job_id: str, status: str | None = None, **kwargs):
        try:
            with transaction.atomic():
                obj, created = self.job_model.objects.get_or_create(
                    job_id=job_id,
                    defaults=kwargs,
                )
                if not created:
                    for k, v in kwargs.items():
                        setattr(obj, k, v)
                    obj.save()
                logger.info(
                    'Stored result for job (%s: %s) in database',
                    job_id, status
                )
        except Exception as e:
            logger.error(
                'Failed to store result for job (%s: %s): %s',
                job_id, status, e
            )
