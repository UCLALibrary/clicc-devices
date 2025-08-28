from django.test import TestCase
from django.core.management import call_command
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
