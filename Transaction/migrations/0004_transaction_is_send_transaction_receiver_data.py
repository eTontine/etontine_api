# Generated by Django 4.2.7 on 2023-11-24 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Transaction', '0003_alter_transaction_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='is_send',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='receiver_data',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
    ]