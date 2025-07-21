import random
import string

from django.core.management.base import BaseCommand, CommandError

from tqdm import tqdm

from openzaak_new.components.zaken.models import Zaak


def random_string(length=30):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


class Command(BaseCommand):
    help = "Bulk update Zaak instances by setting a random string on a specified field."

    def add_arguments(self, parser):
        parser.add_argument(
            "--field",
            type=str,
            required=True,
            help="The name of the field to update (e.g. 'name')",
        )

    def handle(self, *args, **options):
        field_name = options["field"]

        if not hasattr(Zaak, field_name):
            raise CommandError(f"Field '{field_name}' does not exist on Zaak model.")

        self.stdout.write(f"Start bulk updating field '{field_name}' with progress...")

        zaken = list(Zaak.objects.all())
        total = len(zaken)
        self.stdout.write(f"Total zaken to update: {total}")

        # Modifica dei dati con barra di avanzamento
        for zaak in tqdm(zaken, desc="Generating random values"):
            setattr(zaak, field_name, random_string())

        # Bulk update in batch
        batch_size = 10000
        self.stdout.write("Starting bulk_update in batches...")

        for i in tqdm(range(0, total, batch_size), desc="Bulk updating"):
            batch = zaken[i : i + batch_size]
            Zaak.objects.bulk_update(batch, [field_name], batch_size=batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"All zaken updated on field '{field_name}' with random values."
            )
        )
