from django.core.management.base import BaseCommand
from decimal import Decimal
import random
from faker import Faker

from ...models import Product

fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with fake Product records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of products to create (default: 20)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing products before seeding",
        )

    def handle(self, *args, **options):
        count = options["count"]

        if options["flush"]:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing products"))

        products = []
        for _ in range(count):
            products.append(
                Product(
                    title=fake.word()[:20].title(),
                    manufacture=fake.company()[:20],
                    price=Decimal(random.randint(100, 500000)) / 100,
                    description=fake.sentence(nb_words=10)[:100],
                    stock=random.randint(0, 500),
                )
            )

        Product.objects.bulk_create(products)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} products")
        )