from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.test import APITestCase

from order.models import Order, OrderItem
from order.views import IsOwnerOrStaff, OrderViewSet

User = get_user_model()


class OrderOwnershipTests(APITestCase):
    def setUp(self):
        # Reset the class attribute because the view mutates it (due to the bug in get_permissions)
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

        self.owner = User.objects.create_user(username="owner", email="y@y.com", password="pw12345678")
        self.other = User.objects.create_user(username="other", email="y@yy.com", password="pw12345678")
        self.staff = User.objects.create_user(
            username="staff", email="y@yyy.com", password="pw12345678", is_staff=True
        )

        self.order = Order.objects.create(
            user_id=self.owner.id, status=Order.Status.PENDING, total=100
        )
        OrderItem.objects.create(
            order=self.order, product_id=2, quantity=1, unit_price=100
        )

        # Removed retrieve_one_url since the action is commented out in the view
        self.detail_url = reverse("order:order-detail", args=[self.order.id])
        self.status_url = reverse("order:order-update-status", args=[self.order.id])

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

    # ── 2. Status update ────────────────────────────────────────────────────
    def test_other_user_cannot_change_status(self):
        self.client.force_authenticate(self.other)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        # print(r.context)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_set_status(self):
        """Even the owner is forbidden from changing status (requires admin)."""
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
        
        # Verify the database was actually updated by the service layer
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.COMPLETE)

    # ── 3. List vs Filtering ────────────────────────────────────────────────
    def test_list_only_returns_own_orders(self):
        other_order = Order.objects.create(
            user_id=self.other.id, status=Order.Status.PENDING, total=50
        )
        self.client.force_authenticate(self.other)
        r = self.client.get(reverse("order:order-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        rows = r.data["results"] if isinstance(r.data, dict) else r.data
        ids = {str(row["id"]) for row in rows}
        self.assertIn(str(other_order.id), ids)
        self.assertNotIn(str(self.order.id), ids)

    # ── 4. Destructive methods disabled ─────────────────────────────────────
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

    # ── 5. Unauthenticated access ───────────────────────────────────────────
    def test_anonymous_cannot_retrieve(self):
        r = self.client.get(self.detail_url)
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )