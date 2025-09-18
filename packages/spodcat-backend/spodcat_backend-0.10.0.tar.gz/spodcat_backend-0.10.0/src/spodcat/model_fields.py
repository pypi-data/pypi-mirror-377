from django.db import models

from spodcat import form_fields


class TimestampField(models.IntegerField):
    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": form_fields.TimestampField, **kwargs})
