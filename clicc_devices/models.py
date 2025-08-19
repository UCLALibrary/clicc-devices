from django.db import models


class Set(models.Model):
    alma_set_id = models.CharField(
        max_length=255, unique=True
    )  # Alma set ID character limit is 255
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=100)
    type = models.ForeignKey("ItemType", related_name="sets", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.unit}) - {self.type}"


class ItemType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    set = models.ForeignKey(Set, related_name="items", on_delete=models.CASCADE)
    barcode = models.CharField(max_length=128)  # Alma barcodes character limit is 128
    retrieved_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.barcode} ({self.set.unit})"
