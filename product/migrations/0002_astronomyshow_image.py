# Generated by Django 5.0.3 on 2024-04-13 09:21

import product.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="astronomyshow",
            name="image",
            field=models.ImageField(
                null=True, upload_to=product.models.create_custom_path
            ),
        ),
    ]
