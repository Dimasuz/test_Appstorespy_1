# Generated by Django 5.0 on 2023-12-27 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("regloginout", "0002_alter_user_is_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                verbose_name="active",
            ),
        ),
    ]
