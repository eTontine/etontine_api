# Generated by Django 4.2.7 on 2023-11-23 00:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('ALERT_CONTRIBUTION', 'ALERT_CONTRIBUTION'), ('ALERT_PAYMENT', 'ALERT_PAYMENT'), ('ALERT_INVITATION', 'ALERT_INVITATION'), ('ALERT_INTEGRATION', 'ALERT_INTEGRATION'), ('ALERT_CLOTURE', 'ALERT_CLOTURE')], max_length=20)),
                ('is_see', models.BooleanField(default=False)),
                ('is_send', models.BooleanField(default=False)),
                ('content', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]