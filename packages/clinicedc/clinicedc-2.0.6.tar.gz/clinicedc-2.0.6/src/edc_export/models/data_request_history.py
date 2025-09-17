from django.db import models
from django.db.models import Index
from django.db.models.deletion import PROTECT

from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from .data_request import DataRequest


class DataRequestHistory(SiteModelMixin, BaseUuidModel):
    data_request = models.ForeignKey(DataRequest, on_delete=PROTECT)

    archive_filename = models.CharField(max_length=200, null=True)

    emailed_to = models.EmailField(null=True)

    emailed_datetime = models.DateTimeField(null=True)

    summary = models.TextField(default="")

    exported_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        verbose_name = "Data Request History"
        verbose_name_plural = "Data Request History"
        indexes = (Index(fields=["exported_datetime"]),)
