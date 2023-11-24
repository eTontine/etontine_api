from django.db import transaction
from django.core.management.base import BaseCommand
from Account.models import Countries
from Abonnement.models import Abonnement
from BaseApi.AppEnum import *

class Seeder:
    @classmethod
    def countrySeed(cls):
        with transaction.atomic():
            pays_data = [{'name': country.value['name'], 'code': country.value['code'], 'phone_code': country.value['phone_code']} for country in CountryEnum]
            for data in pays_data:
                Countries.objects.get_or_create(code=data['code'], defaults=data)

    @classmethod
    def abonnementSeed(cls):
        with transaction.atomic():
            for abonnement in AbonnementEnum:
                Abonnement.objects.get_or_create(
                    name=abonnement.value['name'],
                    sale_price=abonnement.value['sale_price'],
                    interval_user_min=abonnement.value['interval_user_min'],
                    interval_user_max=abonnement.value['interval_user_max'],
                    interval_groupe_min=abonnement.value['interval_groupe_min'],
                    interval_groupe_max=abonnement.value['interval_groupe_max'],
                    duration_days=abonnement.value['duration_days']
                )

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding de pays...')
        Seeder.countrySeed()

        self.stdout.write('Seeding des abonnements...')
        Seeder.abonnementSeed()

        self.stdout.write(self.style.SUCCESS('Successfully seeded pays, abonnements'))