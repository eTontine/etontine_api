# Generated by Django 4.2.7 on 2023-11-23 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Transaction', '0002_alter_transaction_reseau_id_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=60),
        ),
    ]
