from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.test import APITestCase

from order.models import Order, OrderItem
from order.views import IsOwnerOrStaff, OrderViewSet

from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.cache import cache

User = get_user_model()


class OrderOwnershipTests(APITestCase):
    def setUp(self):
        # Reset the class attribute because the view mutates it (due to the bug in get_permissions)
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
        cache.clear()

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


# ════════════════════════════════════════════════════════════════════════
#  NEW: comprehensive endpoint coverage
# ════════════════════════════════════════════════════════════════════════


class OrderCreateEndpointTests(APITestCase):
    """POST /api/v1/orders/ — create endpoint."""

    def setUp(self):
        # Reset the class attr that OrderViewSet.get_permissions mutates
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
        cache.clear()

        self.user = User.objects.create_user(
            username="creator", email="creator@test.com", password="pw12345678"
        )
        self.url = reverse("order:order-list")
        self.client.force_authenticate(self.user)

    # ── happy path ────────────────────────────────────────────
    def test_create_success(self):
        # The service layer is patched so the view logic is tested in isolation.
        with patch("order.views.create_order") as mock_create:
            order = Order.objects.create(user_id=self.user.id, total=Decimal("20.00"))
            OrderItem.objects.create(
                order=order, product_id=1, quantity=2, unit_price=Decimal("10.00")
            )
            mock_create.return_value = order

            payload = {"items": [{"product_id": 1, "quantity": 2}]}
            r = self.client.post(self.url, payload, format="json")

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(r.data["id"]), str(order.id))
        self.assertEqual(r.data["total"], "20.00")
        mock_create.assert_called_once()

    def test_create_calls_service_with_correct_args(self):
        with patch("order.views.create_order") as mock_create:
            order = Order.objects.create(user_id=self.user.id, total=Decimal("10.00"))
            mock_create.return_value = order
            self.client.post(
                self.url, {"items": [{"product_id": 5, "quantity": 3}]}, format="json"
            )

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["user"], self.user)
        self.assertEqual(kwargs["items_data"], [{"product_id": 5, "quantity": 3}])

    # ── validation errors ─────────────────────────────────────
    def test_create_empty_items_returns_400(self):
        r = self.client.post(self.url, {"items": []}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_items_returns_400(self):
        r = self.client.post(self.url, {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_products_returns_400(self):
        payload = {"items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 1, "quantity": 2},
        ]}
        r = self.client.post(self.url, payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", r.data)

    def test_create_zero_quantity_returns_400(self):
        r = self.client.post(
            self.url, {"items": [{"product_id": 1, "quantity": 0}]}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_negative_product_id_returns_400(self):
        r = self.client.post(
            self.url, {"items": [{"product_id": -1, "quantity": 1}]}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    # ── auth ──────────────────────────────────────────────────
    def test_create_anonymous_denied(self):
        self.client.force_authenticate(None)
        r = self.client.post(
            self.url, {"items": [{"product_id": 1, "quantity": 1}]}, format="json"
        )
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class OrderListRetrieveEndpointTests(APITestCase):
    """GET /api/v1/orders/  and  GET /api/v1/orders/{id}/"""

    def setUp(self):
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
        cache.clear()

        self.owner = User.objects.create_user(
            username="l_owner", email="lo@test.com", password="pw12345678"
        )
        self.other = User.objects.create_user(
            username="l_other", email="lot@test.com", password="pw12345678"
        )
        self.staff = User.objects.create_user(
            username="l_staff", email="lst@test.com",
            password="pw12345678", is_staff=True,
        )

        self.order = Order.objects.create(
            user_id=self.owner.id, status=Order.Status.PENDING,
            total=Decimal("100.00"),
        )
        OrderItem.objects.create(
            order=self.order, product_id=1, quantity=2, unit_price=Decimal("50.00")
        )

        self.list_url = reverse("order:order-list")
        self.detail_url = reverse("order:order-detail", args=[self.order.id])

    # ── list ──────────────────────────────────────────────────
    def test_list_requires_authentication(self):
        r = self.client.get(self.list_url)
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_list_pagination_structure(self):
        self.client.force_authenticate(self.owner)
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, r.data)

    def test_list_returns_lightweight_payload(self):
        """OrderListSerializer must NOT include nested items."""
        self.client.force_authenticate(self.owner)
        r = self.client.get(self.list_url)
        self.assertEqual(len(r.data["results"]), 1)
        row = r.data["results"][0]
        for field in (
            "id", "status", "status_display", "total",
            "item_count", "created_at", "updated_at",
        ):
            self.assertIn(field, row)
        self.assertNotIn("items", row)

    def test_list_staff_sees_all_orders(self):
        other_order = Order.objects.create(
            user_id=self.other.id, total=Decimal("50.00")
        )
        self.client.force_authenticate(self.staff)
        r = self.client.get(self.list_url)
        ids = {str(row["id"]) for row in r.data["results"]}
        self.assertIn(str(self.order.id), ids)
        self.assertIn(str(other_order.id), ids)

    # ── retrieve ──────────────────────────────────────────────
    def test_retrieve_nonexistent_returns_404(self):
        self.client.force_authenticate(self.owner)
        r = self.client.get(reverse("order:order-detail", args=[99999]))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_returns_full_order_with_nested_items(self):
        self.client.force_authenticate(self.owner)
        # Patch cross-service facades so the test is deterministic
        with patch("order.views.get_users_map") as mock_users, \
             patch("order.views.get_products_map") as mock_products:
            user_mock = MagicMock()
            user_mock.email = self.owner.email
            mock_users.return_value = {self.owner.id: user_mock}
            mock_products.return_value = {
                1: {
                    "title": "Test Product", "manufacturer": "Acme",
                    "image": "", "description": "", "price": "50.00",
                }
            }
            r = self.client.get(self.detail_url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for field in (
            "id", "user_id", "user_email", "status", "status_display",
            "total", "items", "created_at", "updated_at",
        ):
            self.assertIn(field, r.data)
        self.assertEqual(len(r.data["items"]), 1)
        self.assertEqual(r.data["items"][0]["product_title"], "Test Product")
        self.assertEqual(r.data["items"][0]["subtotal"], Decimal("100.00"))

    def test_retrieve_second_call_hits_cache(self):
        """Second GET for the same user/order must not re-fetch facades."""
        self.client.force_authenticate(self.owner)
        with patch("order.views.get_users_map") as mock_users, \
             patch("order.views.get_products_map") as mock_products:
            user_mock = MagicMock()
            user_mock.email = self.owner.email
            mock_users.return_value = {self.owner.id: user_mock}
            mock_products.return_value = {}

            self.client.get(self.detail_url)
            first_users = mock_users.call_count
            first_products = mock_products.call_count

            r = self.client.get(self.detail_url)
            self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.assertEqual(mock_users.call_count, first_users)
        self.assertEqual(mock_products.call_count, first_products)

    def test_list_cache_is_per_user(self):
        """Two different users must NOT share list cache."""
        self.client.force_authenticate(self.owner)
        r1 = self.client.get(self.list_url)
        owner_ids = {str(row["id"]) for row in r1.data["results"]}
        self.assertIn(str(self.order.id), owner_ids)

        other_order = Order.objects.create(
            user_id=self.other.id, total=Decimal("10.00")
        )
        self.client.force_authenticate(self.other)
        r2 = self.client.get(self.list_url)
        other_ids = {str(row["id"]) for row in r2.data["results"]}
        self.assertIn(str(other_order.id), other_ids)
        self.assertNotIn(str(self.order.id), other_ids)


class OrderStatusEndpointTests(APITestCase):
    """PATCH /api/v1/orders/{id}/status/"""

    def setUp(self):
        OrderViewSet.permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
        cache.clear()

        self.owner = User.objects.create_user(
            username="s_owner", email="so@test.com", password="pw12345678"
        )
        self.other = User.objects.create_user(
            username="s_other", email="sot@test.com", password="pw12345678"
        )
        self.staff = User.objects.create_user(
            username="s_staff", email="sst@test.com",
            password="pw12345678", is_staff=True,
        )
        self.order = Order.objects.create(
            user_id=self.owner.id, status=Order.Status.PENDING,
            total=Decimal("50.00"),
        )
        self.status_url = reverse(
            "order:order-update-status", args=[self.order.id]
        )

    # ── auth matrix ───────────────────────────────────────────
    def test_status_update_anonymous_denied(self):
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_status_update_owner_forbidden(self):
        self.client.force_authenticate(self.owner)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_update_other_user_forbidden(self):
        self.client.force_authenticate(self.other)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    # ── happy path ────────────────────────────────────────────
    def test_status_update_staff_succeeds_and_persists(self):
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.COMPLETE}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["status"], Order.Status.COMPLETE)
        self.assertEqual(r.data["status_display"], "Complete")

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.COMPLETE)

    # ── validation / state-machine errors ─────────────────────
    def test_status_update_same_status_returns_400(self):
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.PENDING}, format="json"
        )
        # print(f"\n\nresponse:\n{r.json()}\n\n")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_update_terminal_to_pending_returns_400(self):
        self.order.status = Order.Status.COMPLETE
        self.order.save()
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            self.status_url, {"status": Order.Status.PENDING}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_update_invalid_choice_returns_400(self):
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            self.status_url, {"status": "not_a_real_status"}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_update_nonexistent_order_returns_404(self):
        self.client.force_authenticate(self.staff)
        url = reverse("order:order-update-status", args=[99999])
        r = self.client.patch(url, {"status": Order.Status.COMPLETE}, format="json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)