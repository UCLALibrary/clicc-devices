from django.db import models


class Set(models.Model):
    alma_set_id = models.CharField(
        max_length=255, unique=True
    )  # Alma set ID character limit is 255
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=100)
    type = models.ForeignKey("ItemType", related_name="sets", on_delete=models.PROTECT)
    retrieved = models.DateTimeField()

    def __str__(self):
        return f"{self.name} ({self.unit}) - {self.type}"


class ItemType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    set = models.ForeignKey(Set, related_name="items", on_delete=models.CASCADE)
    barcode = models.CharField(max_length=128)  # Alma barcodes character limit is 128

    def __str__(self):
        return f"{self.barcode} ({self.set.unit})"


class CronJob(models.Model):
    # Use charfield to support wildcards and intervals.
    # No attempt at validation.
    # Set reasonable defaults for midnight Jan 1 (any day of week),
    # basic echo command, with job disabled.
    # 0 0 1 1 * echo 'Hello' >> /tmp/cron.log 2>&1
    minutes = models.CharField(max_length=20, null=False, blank=False, default="0")
    hours = models.CharField(max_length=20, null=False, blank=False, default="0")
    days_of_month = models.CharField(
        max_length=20, null=False, blank=False, default="1"
    )
    months = models.CharField(max_length=20, null=False, blank=False, default="1")
    days_of_week = models.CharField(max_length=20, null=False, blank=False, default="*")
    command = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        default="echo 'Hello' >> /tmp/cron.log 2>&1",
    )
    enabled = models.BooleanField(null=False, default=False)
    # With custom save(), ensure there's only one record, with pk = 1:
    # each new record replaces the previous (and only) one.
    permanent_id = models.SmallIntegerField(default=1)

    def save(self, *args, **kwargs):
        # If there's already an object, and we're trying to create a new one,
        # disable creation (remove the insert request) and use the existing id
        # to trigger an update instead.
        object_count = CronJob.objects.count()
        if object_count > 0:
            # Remove the insert request, so the record just gets replaced.
            kwargs.pop("force_insert", None)
        self.id = self.permanent_id
        super().save(*args, **kwargs)
