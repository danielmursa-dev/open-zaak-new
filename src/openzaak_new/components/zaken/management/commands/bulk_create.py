from django.core.management.base import BaseCommand

from openzaak_new.components.zaken.models import Zaak


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Start")

        products = [Zaak() for i in range(1000000)]

        Zaak.objects.bulk_create(products, batch_size=10000)

        self.stdout.write(
            self.style.SUCCESS(f"Total zaken created: {Zaak.objects.all().count()}")
        )
