# order/management/commands/seed_orders.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import random
from ...models import Order, OrderItem
from product.models import Product # Import Product to get valid IDs

User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with fake Orders and OrderItems"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of orders to create (default: 10)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing orders before seeding",
        )

    def handle(self, *args, **options):
        count = options["count"]

        if options["flush"]:
            # This will also delete OrderItems because of on_delete=models.CASCADE
            deleted, _ = Order.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing orders"))

        # 1. Fetch existing IDs
        # Note: If you are using multiple databases, you may need .using('user_db') and .using('product_db') here
        user_ids = list(User.objects.values_list('id', flat=True))
        product_ids = list(Product.objects.values_list('id', flat=True))

        if not user_ids:
            self.stdout.write(self.style.ERROR("No users found. Please create a user first."))
            return
            
        if not product_ids:
            self.stdout.write(self.style.ERROR("No products found. Please run seed_products first."))
            return

        # 2. Create Orders
        orders_created = 0
        for _ in range(count):
            # Pick a random user
            random_user_id = random.choice(user_ids)
            
            # Create the order (status defaults to PENDING)
            order = Order.objects.create(user_id=random_user_id)
            
            # 3. Create OrderItems for this order
            # Pick 1 to 5 random products per order
            num_items = random.randint(1, 5)
            selected_product_ids = random.sample(product_ids, min(num_items, len(product_ids)))
            
            total = Decimal("0.00")
            
            for pid in selected_product_ids:
                # Fetch the product to get the price
                product = Product.objects.get(id=pid)
                qty = random.randint(1, 3)
                unit_price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product_id=pid,
                    quantity=qty,
                    unit_price=unit_price
                )
                
                total += unit_price * qty
                
            # 4. Update the order total
            order.total = total
            order.save(update_fields=["total"])
            orders_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {orders_created} orders with items")
        )