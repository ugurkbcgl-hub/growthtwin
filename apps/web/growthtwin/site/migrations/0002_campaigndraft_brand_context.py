from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("site", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaigndraft",
            name="brand_context",
            field=models.CharField(blank=True, default="", max_length=320),
        ),
    ]
