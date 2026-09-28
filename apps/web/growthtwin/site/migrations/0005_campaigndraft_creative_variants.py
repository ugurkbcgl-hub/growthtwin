from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("site", "0004_campaigndraft_target_audience"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaigndraft",
            name="creative_variants",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="campaigndraft",
            name="creative_source_hash",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
