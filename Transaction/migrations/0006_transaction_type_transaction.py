# Generated by Django 4.2.7 on 2023-11-29 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Transaction', '0005_remove_transaction_is_send_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='type_transaction',
            field=models.CharField(choices=[('CONTRIBUTION', 'CONTRIBUTION'), ('COLLECTED', 'COLLECTED')], default='CONTRIBUTION', max_length=255),
        ),
    ]
