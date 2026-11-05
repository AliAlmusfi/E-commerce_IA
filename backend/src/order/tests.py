from django.test import TestCase

# Create your tests here.
# orders/tests/test_order_permissions.py
"""
Ensures a user cannot view, cancel, or modify another user's order,
and that admin-only endpoints reject non-staff users.

Assumes:
  - Router basename is "order"  ->  order-list, order-detail,
    order-update-status, order-list-all, order-retrieve-one
  - Order.Status has PENDING / COMPLETE / CANCELLED
  - OrderItem has product_title, quantity, price
Adjust field names / reverse() names if yours differ.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.test import APITestCase

from order.models import Order, OrderItem
from order.views import IsOwnerOrStaff, OrderViewSet

User = get_user_model()


class OrderOwnershipTests(APITestCase):
    def setUp(self):
        # Undo the class-attribute mutation caused by get_permissions()
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

        self.owner = User.objects.create_user(username="owner", email="y@y.com", password="pw12345678")
        self.other = User.objects.create_user(username="other", email="y@yy.com", password="pw12345678")
        self.staff = User.objects.create_user(
            username="staff", email="y@yyy.com", password="pw12345678", is_staff=True
        )

        self.order = Order.objects.create(
            user=self.owner, status=Order.Status.PENDING, total=100
        )
        OrderItem.objects.create(
            order=self.order, product_id=1, quantity=1, unit_price=100
        )

        self.detail_url       = reverse("order-detail",         args=[self.order.id])
        self.retrieve_one_url = reverse("order-retrieve-one",   args=[self.order.id])
        self.status_url       = reverse("order-update-status",  args=[self.order.id])

    # ── 1. Standard retrieve ────────────────────────────────────────────────
    def test_owner_can_retrieve_own_order(self):
        self.client.force_authenticate(self.owner)
        r = self.client.get(self.detail_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_retrieve_order(self):
        """get_queryset() filters by user -> 404 for foreign order."""
        self.client.force_authenticate(self.other)
        r = self.client.get(self.detail_url)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_retrieve_any_order(self):
        self.client.force_authenticate(self.staff)
        r = self.client.get(self.detail_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    # ── 2. Custom admin action: retrieve_one ────────────────────────────────
    def test_other_user_cannot_use_retrieve_one(self):
        self.client.force_authenticate(self.other)
        r = self.client.get(self.retrieve_one_url)
        # IsAdminUser -> 403 (or 404 if permission gate were removed)
        self.assertIn(
            r.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_staff_can_use_retrieve_one(self):
        self.client.force_authenticate(self.staff)
        r = self.client.get(self.retrieve_one_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    # ── 3. Status update ────────────────────────────────────────────────────
    def test_other_user_cannot_change_status(self):
        self.client.force_authenticate(self.other)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    # def test_owner_can_cancel_own_order(self):
    #     self.client.force_authenticate(self.owner)
    #     r = self.client.patch(
    #         self.status_url, {"status": Order.Status.CANCELLED}, format="json"
    #     )
    #     self.assertEqual(r.status_code, status.HTTP_200_OK)
    #     self.order.refresh_from_db()
    #     self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_owner_cannot_set_non_cancel_status(self):
            self.client.force_authenticate(self.owner)
            r = self.client.patch(
                self.status_url, {"status": Order.Status.COMPLETE}, format="json"
            )
            self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_set_any_status(self):
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    # ── 4. list vs list_all ─────────────────────────────────────────────────
    def test_list_only_returns_own_orders(self):
        other_order = Order.objects.create(
            user=self.other, status=Order.Status.PENDING, total=50
        )
        self.client.force_authenticate(self.other)
        r = self.client.get(reverse("order-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        rows = r.data["results"] if isinstance(r.data, dict) else r.data
        ids = {str(row["id"]) for row in rows}
        self.assertIn(str(other_order.id), ids)
        self.assertNotIn(str(self.order.id), ids)

    def test_non_staff_cannot_use_list_all(self):
        self.client.force_authenticate(self.other)
        r = self.client.get(reverse("order-list-all"))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_use_list_all(self):
        self.client.force_authenticate(self.staff)
        r = self.client.get(reverse("order-list-all"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    # ── 5. Destructive methods disabled ─────────────────────────────────────
    def test_put_and_patch_on_order_are_disabled(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(
            self.client.put(self.detail_url, {}, format="json").status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.patch(self.detail_url, {}, format="json").status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_delete_is_disabled(self):
        self.client.force_authenticate(self.owner)
        r = self.client.delete(self.detail_url)
        self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ── 6. Unauthenticated access ───────────────────────────────────────────
    def test_anonymous_cannot_retrieve(self):
        r = self.client.get(self.detail_url)
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
