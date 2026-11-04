from django.db import models

from django.conf import settings

from django.core.exceptions import ValidationError

from tools.models import TimeStampedModel

class Device (TimeStampedModel):
    class Meta:
        db_table = 'device'
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    registration_id = models.TextField(verbose_name="FCM Registration Token")
    active = models.BooleanField(default=True , help_text="is this device currently active?")
    device_type = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., Android, iOS, Web", default="Web")

    def save(self, *args, **kwargs):
        self.device_type = self.device_type.lower()
        if(self.device_type not in ['android', 'ios', 'desktop']):
            raise ValidationError('in Device model in the save method: device_type must be in [\'android\', \'ios\', \'desktop\']')
        return super().save(*args , **kwargs)