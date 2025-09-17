from uuid import uuid4

from django.conf import settings
from django.db import models


class AbstractJob(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('queued', 'Queued'),
        ('started', 'Started'),
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
        ('stopped', 'Stopped'),
        ('deferred', 'Deferred'),
        ('scheduled', 'Scheduled'),
    )

    job_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=128)
    meta = models.JSONField(blank=True, default=dict)
    kwargs = models.JSONField(blank=True, default=dict)
    queue = models.CharField(max_length=128)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    group_id = models.CharField(max_length=128, blank=True, null=True)
    worker_name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    inventory = models.CharField(max_length=255, blank=True, null=True)
    timeout = models.SmallIntegerField(blank=True, default=3600)
    ttl = models.SmallIntegerField(blank=True, null=True)
    result_ttl = models.SmallIntegerField(blank=True, default=500)
    failure_ttl = models.SmallIntegerField(blank=True, default=604800)
    success_callback_name = models.CharField(max_length=128, blank=True, null=True)
    failure_callback_name = models.CharField(max_length=128, blank=True, null=True)
    stopped_callback_name = models.CharField(max_length=128, blank=True, null=True)
    rc = models.SmallIntegerField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    exc_info = models.TextField(blank=True, null=True)
    last_heartbeat = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enqueued_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True
        db_table = getattr(settings, 'JOB_TABLE', 'job')
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def __str__(self):
        return f'{self.job_id} ({self.status})'


class Job(AbstractJob):
    class Meta(AbstractJob.Meta):
        swappable = 'JOB_MODEL'
