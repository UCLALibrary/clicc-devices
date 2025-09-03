from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from .models import CronJob
from io import StringIO


class CronTest(TestCase):
    def test_only_one_cron_record_is_created(self):
        # Fields have defaults, no need to specify values
        # CronJob.save() has been overridden to allow creation of
        # only one instance.
        r1 = CronJob.objects.create()
        r2 = CronJob.objects.create()
        self.assertEqual(r1.pk, r2.pk)
        records = CronJob.objects.all()
        self.assertEqual(len(records), 1)

    def test_save_works_correctly(self):
        # Since CronJob.save() has been overridden, confirm it
        # still works as expected when a record is updated.
        # Use default fields, then change one and check it.
        r1 = CronJob.objects.create()
        r1.command = "new value for testing"
        r1.save()
        r2 = CronJob.objects.get(pk=r1.pk)
        self.assertEqual(r2.command, "new value for testing")

    def test_no_records_generates_no_command_output(self):
        # Make sure no objects exists.
        CronJob.objects.all().delete()
        # Capture output from running management command
        output = StringIO()
        call_command("update_crontab", stdout=output)
        # Should be no output (empty string) when no objects.
        self.assertEqual(output.getvalue(), "")

    def test_records_generate_command_output(self):
        # Use defaults defined on model.
        CronJob.objects.create()
        # Capture output from running management command
        output = StringIO()
        call_command("update_crontab", stdout=output)
        expected = output.getvalue()
        # Expected value printed by command has a trailing line feed.
        self.assertEqual(expected, "#0 0 1 1 * echo 'Hello' >> /tmp/cron.log 2>&1\n")


class DeviceViewTests(TestCase):

    # Create some sample data for testing
    @classmethod
    def setUpTestData(cls):
        from .models import Set, ItemType, Item

        type_a = ItemType.objects.create(name="typeA")
        type_b = ItemType.objects.create(name="typeB")

        unit1 = "unit1"

        set1 = Set.objects.create(
            alma_set_id="set1",
            name="Set 1",
            unit=unit1,
            type=type_a,
            retrieved=timezone.now(),
        )
        set2 = Set.objects.create(
            alma_set_id="set2",
            name="Set 2",
            unit=unit1,
            type=type_b,
            retrieved=timezone.now(),
        )
        # same unit and type as set1, to test aggregation
        set3 = Set.objects.create(
            alma_set_id="set3",
            name="Set 3",
            unit=unit1,
            type=type_a,
            retrieved=timezone.now(),
        )

        # Add items to sets
        for i in range(3):
            Item.objects.create(set=set1, barcode=f"barcode_a_{i+1}")
        for i in range(4):
            Item.objects.create(set=set2, barcode=f"barcode_b_{i+1}")
        for i in range(5):
            Item.objects.create(set=set3, barcode=f"barcode_a2_{i+1}")

    def test_devices_view_structure(self):
        response = self.client.get("/devices/")
        data = response.json()
        # Check top-level keys
        self.assertIn("unit1", data)
        unit1_data = data["unit1"]
        # Check item types and counts
        self.assertIn("typeA", unit1_data)
        self.assertIn("typeB", unit1_data)
        self.assertEqual(unit1_data["typeA"], 8)  # 3 from set1 + 5 from set3
        self.assertEqual(unit1_data["typeB"], 4)
