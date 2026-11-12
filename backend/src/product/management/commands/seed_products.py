from django.core.management.base import BaseCommand
from decimal import Decimal
import random
from faker import Faker

from ...models import Product

from ...services import create_product

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


        for _ in range(count):
            product_data  = {
                "title" : fake.word()[:20].title(),
                "manufacturer": fake.company()[:20],
                "price": Decimal(random.randint(100 , 500000)) / 100,
                "description": fake.sentence(nb_words=10)[:100],
                "stock": random.randint(0,500)
            }
            # product = Product(
            #     title=fake.word()[:20].title(),
            #     manufacturer=fake.company()[:20],
            #     price=Decimal(random.randint(100, 500000)) / 100,
            #     description=fake.sentence(nb_words=10)[:100],
            #     stock=random.randint(0, 500),
            # )
            # products.append(product)
            create_product(4,product_data)

            try:
                create_product(4, product_data)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create product: {str(e)}"))


        # Product.objects.bulk_create(products)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} products")
        )