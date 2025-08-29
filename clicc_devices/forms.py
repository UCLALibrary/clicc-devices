from django import forms
from clicc_devices.models import CronJob


class CronForm(forms.ModelForm):
    class Meta:
        model = CronJob
        fields = [
            "minutes",
            "hours",
            "days_of_month",
            "months",
            "days_of_week",
            "command",
            "enabled",
        ]
        # Default sizes are fine except for command field
        widgets = {
            "command": forms.TextInput(attrs={"size": 150}),
        }
