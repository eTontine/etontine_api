from django.db import transaction
from django.core.management.base import BaseCommand
from BaseApi.AppEnum import *
from Account.models import Users, Countries

class Seeder:
    @classmethod
    def seedSuperAdmin(cls):

        available_country_codes = [country.value['code'] for country in CountryEnum]
        print("Available country codes:", ", ".join(available_country_codes))

        country_code = input("Enter country code: ")
        choice_country = None

        for country in CountryEnum:
            if country.value['code'] == country_code:
                choice_country = country
                break
        
        if choice_country is None:
            print(f"Country with code {country_code} not found in CountryEnum.")
            return

        super_phone = input("Enter super user phone:")
        super_password = input("Enter super user code(NUMERIC) _ MINIMUM 6 DIGITS:")

        country, _ = Countries.objects.get_or_create(code=choice_country.value['code'], defaults=choice_country.value)

        with transaction.atomic():
            super_user, created = Users.objects.get_or_create(
                phone=super_phone,
                account_type=AccountTypeEnum.ADMIN.value,
                defaults={
                    'name': 'Super Admin',
                    'phone': super_phone,
                    'country': country,
                    'account_type': AccountTypeEnum.ADMIN.value,
                }
            )

            if created:
                super_user.set_password(super_password)
                super_user.save()
                    
            print (f"Message: Success, [Phone: {super_phone}, Code: **********]");

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Super Admin...')
        Seeder.seedSuperAdmin()
        self.stdout.write(self.style.SUCCESS('Successfully seeded the Super Admin'))
