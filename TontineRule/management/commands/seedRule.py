from django.db import transaction
from django.core.management.base import BaseCommand
from TontineRule.models import Rules
from BaseApi.AppEnum import *

class Seeder:
    @classmethod
    def seedRule(cls):
        with transaction.atomic():
            for rule_data in rules_data:
                Rules.objects.update_or_create(**rule_data)

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding de rules...')
        Seeder.seedRule()

        self.stdout.write(self.style.SUCCESS('Successfully seeded rules'))


rules_data = [
    {'key':'GAIN_TONTINIER', 'title': 'Gain du tontinier - Montant fixe', 'description': 'Montant fixe gagné par le tontinier à chaque contribution', 'type': TypeRuleEnum.COMMUN.value, 'online': True, 'field_type': 'currency', 'default_value': None},
    {'key':'PENALITY_PAYMENT', 'title': 'Pénalité pour retard de paiement - Montant fixe', 'description': 'Montant fixe de pénalité pour chaque retard de paiement', 'type': TypeRuleEnum.GROUPES.value, 'online': True, 'field_type': 'currency', 'default_value': None}
]
