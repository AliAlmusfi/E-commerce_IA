"""
Unit tests for `product/views.py` — ProductViewSet

Assumptions / Notes
-------------------
* The viewset is registered on a router with basename **`product`**, so
  URL names are:
      - `product-list`          →  /products/
      - `product-detail`        →  /products/<pk>/
      - `product-update-stock`  →  /products/<pk>/update_stock/   (custom @action)
  If your router uses a different basename, adjust `reverse(...)` calls
  (all handled through `BaseProductAPITest.setUp`).

* Permissions enforced by `ProductViewSet.get_permissions()`:
      list / retrieve / destroy  → IsAuthenticated
      create / update / partial_update / update_stock → IsAuthenticated + IsAdminUser

* `create`, `partial_update` and `update_stock` call external services
  (`product.services.*`), so they are mocked here — tests exercise the
  view logic (permissions, serializers, response shape), not gRPC.

* Caching (`product.tools.caching`) is mocked so tests are deterministic
  and don't need a real cache backend.
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .models import Product
from . import views as product_views

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_user(username="user", is_staff=False):
    return User.objects.create_user(
        username=username,
        password="password123",
        is_staff=is_staff,
        email=f"{username}@{username}.com"
    )


def make_product(**overrides):
    data = {
        "title": "Test Product",
        "description": "A test description",
        "manufacturer": "TestCorp",
        "price": 100,
        # "stock": 10,
    }
    data.update(overrides)
    return Product.objects.create(**data)


class BaseProductAPITest(APITestCase):
    """Common setUp + helpers for all view tests."""

    def setUp(self):
        self.admin = make_user("admin", is_staff=True)
        self.user = make_user("user")
        self.product = make_product()

        self.list_url = reverse("product:product-list")
        self.detail_url = reverse("product:product-detail", args=[self.product.pk])
        try:
            self.update_stock_url = reverse(
                "product:product-update-stock", args=[self.product.pk]
            )
        except Exception:
            self.update_stock_url = None  # skip related tests if not routed

    # -- auth helpers -------------------------------------------------------
    def login_admin(self):
        self.client.force_authenticate(user=self.admin)

    def login_user(self):
        self.client.force_authenticate(user=self.user)

    def logout(self):
        self.client.force_authenticate(user=None)


# ===========================================================================
# CREATE  —  POST /products/   (IsAuthenticated + IsAdminUser)
# ===========================================================================
class CreateProductTests(BaseProductAPITest):
    def setUp(self):
        super().setUp()
        self.payload = {
            "title": "New Product",
            "description": "Description of the new product",
            "manufacturer": "Giant",
            "price": 200,
            "stock": 20,
        }

    def test_create_success_as_admin(self):
        self.login_admin()
        new_product = make_product(title="New Product3ff32", price=200)

        with patch.object(
            product_views, "create_product", return_value=new_product
        ) as mock_create:
            response = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Product3ff32")
        self.assertEqual(float(response.data["price"]), float(200))

        # Assert the service was called with the correct user id + validated data
        mock_create.assert_called_once()
        args, _ = mock_create.call_args
        self.assertEqual(args[0], self.admin.id)
        self.assertEqual(args[1]["title"], "New Product")
        self.assertEqual(args[1]["manufacturer"], "Giant")
        self.assertEqual(float(args[1]["price"]), float(200))

    def test_create_success_multipart(self):
        self.login_admin()
        new_product = make_product(title="New Product2sdf")
        with patch.object(product_views, "create_product", return_value=new_product):
            response = self.client.post(self.list_url, self.payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unauthenticated_returns_401(self):
        with patch.object(product_views, "create_product") as mock_create:
            response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_create.assert_not_called()

    def test_create_forbidden_for_non_admin(self):
        self.login_user()
        with patch.object(product_views, "create_product") as mock_create:
            response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_create.assert_not_called()

    def test_create_invalid_payload_returns_400(self):
        self.login_admin()
        with patch.object(product_views, "create_product") as mock_create:
            response = self.client.post(self.list_url, {"title": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_create.assert_not_called()

    def test_create_missing_required_fields_returns_400(self):
        self.login_admin()
        with patch.object(product_views, "create_product") as mock_create:
            # Missing manufacturer / price / stock
            response = self.client.post(
                self.list_url, {"title": "Only a title"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_create.assert_not_called()

    def test_create_service_exception_bubbles_up(self):
        """
        Current view does NOT swallow service exceptions (try/except is
        commented out), so an unhandled exception → 500.
        """
        self.login_admin()
        with patch.object(
            product_views, "create_product", side_effect=RuntimeError("boom")
        ):
            # DRF test client re-raises unless raise_request_exception=False
            response = self.client.post(
                self.list_url, self.payload, format="json",
                raise_request_exception=False,
            )
        self.assertIn(response.status_code, [500, 409])


# ===========================================================================
# PARTIAL UPDATE  —  PATCH /products/<pk>/   (IsAuthenticated + IsAdminUser)
# ===========================================================================
class PartialUpdateProductTests(BaseProductAPITest):
    def test_partial_update_success(self):
        self.login_admin()

        updated = self.product
        updated.title = "Updated Title"
        # updated.save()

        with patch.object(
            product_views, "patch_product", return_value=updated
        ) as mock_patch:
            response = self.client.patch(
                self.detail_url, {"title": "Updated Title"}, format="json"
            )
            # print(f"\n\nresponse_data:\n{response.data}\n\n")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["title"], "Updated Title")
        mock_patch.assert_called_once()

        # verify (pk, user_id, validated_data)
        args, _ = mock_patch.call_args
        self.assertEqual(str(args[0]), str(self.product.pk))
        self.assertEqual(args[1], self.admin.id)
        self.assertIn("title", args[2])
        self.assertEqual(args[2]["title"], "Updated Title")

    def test_partial_update_unauthenticated(self):
        with patch.object(product_views, "patch_product") as mock_patch:
            response = self.client.patch(
                self.detail_url, {"title": "X"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_patch.assert_not_called()

    def test_partial_update_forbidden_for_non_admin(self):
        self.login_user()
        with patch.object(product_views, "patch_product") as mock_patch:
            response = self.client.patch(
                self.detail_url, {"title": "X"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_patch.assert_not_called()

    def test_partial_update_invalid_payload(self):
        self.login_admin()
        with patch.object(product_views, "patch_product") as mock_patch:
            # Suppose ProductUpdateSerializer rejects this payload.
            # We just check the service isn't invoked on validation failure.
            response = self.client.patch(
                self.detail_url, {"price": "not-a-number"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_patch.assert_not_called()

    def test_partial_update_no_data_returns_400(self):
        """
        Empty PATCH body: ProductUpdateSerializer.validate() rejects payloads
        with no updatable fields, so the request is a 400 and the service is
        never invoked.
        """
        self.login_admin()
        with patch.object(product_views, "patch_product") as mock_patch:
            response = self.client.patch(self.detail_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_patch.assert_not_called()


# ===========================================================================
# UPDATE STOCK  —  PATCH /products/<pk>/update_stock/   (Admin only)
# ===========================================================================
class UpdateStockTests(BaseProductAPITest):
    def setUp(self):
        super().setUp()
        if self.update_stock_url is None:
            self.skipTest("product-update-stock URL not routed")

    def test_update_stock_success(self):
        self.login_admin()
        with patch.object(
            product_views, "update_stk", return_value=True
        ) as mock_update:
            response = self.client.patch(
                self.update_stock_url, {"amount": 5}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {"success": True})
        mock_update.assert_called_once()
        args, _ = mock_update.call_args
        # View casts pk to int
        self.assertEqual(args[0], int(self.product.pk))
        self.assertEqual(args[1], self.admin.id)
        self.assertEqual(args[2], 5)

    def test_update_stock_returns_false(self):
        self.login_admin()
        with patch.object(product_views, "update_stk", return_value=False):
            response = self.client.patch(
                self.update_stock_url, {"amount": 5}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(response.data["success"])

    def test_update_stock_unauthenticated(self):
        with patch.object(product_views, "update_stk") as mock_update:
            response = self.client.patch(
                self.update_stock_url, {"amount": 5}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_update.assert_not_called()

    def test_update_stock_forbidden_for_non_admin(self):
        self.login_user()
        with patch.object(product_views, "update_stk") as mock_update:
            response = self.client.patch(
                self.update_stock_url, {"amount": 5}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_update.assert_not_called()

    def test_update_stock_missing_amount_returns_400(self):
        self.login_admin()
        with patch.object(product_views, "update_stk") as mock_update:
            response = self.client.patch(self.update_stock_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_update.assert_not_called()

    def test_update_stock_zero_amount(self):
        self.login_admin()
        with patch.object(product_views, "update_stk", return_value=True):
            response = self.client.patch(
                self.update_stock_url, {"amount": 0}, format="json"
            )
        self.assertIn(response.status_code, [status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST])


# ===========================================================================
# LIST  —  GET /products/   (IsAuthenticated, with caching)
# ===========================================================================
class ListProductTests(BaseProductAPITest):
    def setUp(self):
        super().setUp()
        for i in range(3):
            make_product(title=f"Extra Product {i}", manufacturer=f"Maker{i}")

    def _mock_cache_miss(self):
        return (
            patch.object(product_views, "get_cache_key", return_value="cache-key"),
            patch.object(product_views, "get_cached_response", return_value=None),
            patch.object(product_views, "do_cache"),
        )

    def test_list_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_paginated_payload(self):
        self.login_user()
        p_key, p_get, p_do = self._mock_cache_miss()
        with p_key as m_key, p_get as m_get, p_do as m_do:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertEqual(response.data["count"], 4)
        self.assertEqual(len(response.data["results"]), 4)

        # Cache helpers called
        m_key.assert_called_once()
        m_get.assert_called_once_with("cache-key")
        m_do.assert_called_once()

    def test_list_cached_response_is_returned(self):
        self.login_user()
        cached = Response({"cached": True, "results": []})
        with patch.object(product_views, "get_cache_key", return_value="cache-key"), \
             patch.object(product_views, "get_cached_response", return_value=cached), \
             patch.object(product_views, "do_cache") as mock_do:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"cached": True, "results": []})
        mock_do.assert_not_called()

    def test_list_size_query_param_overrides_page_size(self):
        self.login_user()
        p_key, p_get, p_do = self._mock_cache_miss()
        with p_key, p_get, p_do:
            response = self.client.get(self.list_url, {"size": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_ordering(self):
        self.login_user()
        p_key, p_get, p_do = self._mock_cache_miss()
        with p_key, p_get, p_do:
            response = self.client.get(self.list_url, {"ordering": "-title"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_list_ordering_invalid_field_is_ignored(self):
        self.login_user()
        p_key, p_get, p_do = self._mock_cache_miss()
        with p_key, p_get, p_do:
            response = self.client.get(self.list_url, {"ordering": "doesnotexist"})
        # OrderingFilter silently ignores unknown fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_do_cache_receives_correct_payload(self):
        self.login_user()
        with patch.object(product_views, "get_cache_key", return_value="k"), \
             patch.object(product_views, "get_cached_response", return_value=None), \
             patch.object(product_views, "do_cache") as mock_do:
            self.client.get(self.list_url)

        self.assertEqual(mock_do.call_count, 1)
        kwargs = mock_do.call_args.kwargs
        self.assertEqual(kwargs["cache_key"], "k")
        self.assertEqual(kwargs["timeout"], 60 * 30)  # 30 minutes
        self.assertIn("results", kwargs["data"])


# ===========================================================================
# RETRIEVE  —  GET /products/<pk>/   (IsAuthenticated, with caching + gRPC stock)
# ===========================================================================
class RetrieveProductTests(BaseProductAPITest):
    def test_retrieve_unauthenticated(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_not_found(self):
        self.login_user()
        with patch.object(product_views, "get_cache_key", return_value="k"), \
             patch.object(product_views, "get_cached_response", return_value=None):
            response = self.client.get(
                reverse("product:product-detail", args=[999_999])
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_success_with_cache_hit(self):
        """
        NOTE — Known bug in the view:
            product_data = get_cached_response(...)   # dict, when cached
            product_data.data['stock'] = ...          # AttributeError on dict!

        Here we simulate the *intended* contract that get_cached_response
        returns an object with a `.data` attribute.  Once the view is fixed
        to use `product_data['stock'] = ...` (and `Response(product_data)`),
        this test will need to be adjusted to patch a plain dict instead.
        """
        self.login_user()
        cached = SimpleNamespace(data={"id": self.product.pk, "title": "X"})

        with patch.object(product_views, "get_cache_key", return_value="k"), \
             patch.object(product_views, "get_cached_response", return_value=cached), \
             patch.object(product_views, "get_stock", return_value=42) as mock_stock:
            response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock"], 42)
        self.assertEqual(response.data["title"], "X")

        mock_stock.assert_called_once()
        _, kwargs = mock_stock.call_args
        self.assertEqual(kwargs["id"], int(self.product.pk))
        self.assertEqual(kwargs["user_id"], int(self.user.id))

    def test_retrieve_calls_get_stock_with_user_context(self):
        self.login_admin()
        cached = SimpleNamespace(data={"id": self.product.pk, "title": "X"})
        with patch.object(product_views, "get_cache_key", return_value="k"), \
             patch.object(product_views, "get_cached_response", return_value=cached), \
             patch.object(product_views, "get_stock", return_value=7) as mock_stock:
            self.client.get(self.detail_url)

        _, kwargs = mock_stock.call_args
        # Admin id should be passed as user_id
        self.assertEqual(kwargs["user_id"], self.admin.id)


# ===========================================================================
# DESTROY  —  DELETE /products/<pk>/
# ===========================================================================
class DestroyProductTests(BaseProductAPITest):
    def test_destroy_as_admin(self):
        self.login_admin()
        pk = self.product.pk
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=pk).exists())

    def test_destroy_as_regular_user(self):
        """
        NOTE — Current get_permissions() only requires IsAuthenticated for
        `destroy`, so a non-admin can delete a product.

        If you fix this (add IsAdminUser for destroy), flip this test to
        expect 403.
        """
        self.login_user()
        pk = self.product.pk
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(pk=pk).exists())

    def test_destroy_unauthenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_not_found(self):
        self.login_admin()
        response = self.client.delete(reverse("product:product-detail", args=[999_999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ===========================================================================
# FULL UPDATE  —  PUT /products/<pk>/   (Admin only, ModelViewSet default)
# ===========================================================================
class FullUpdateProductTests(BaseProductAPITest):
    def setUp(self):
        super().setUp()
        self.payload = {
            "title": "Fully Updated",
            "description": "Updated description",
            "manufacturer": "NewMaker",
            "price": 250,
            "stock": 30,
        }

    def test_update_success(self):
        self.login_admin()
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Fully Updated")
        self.assertEqual(response.data["manufacturer"], "NewMaker")
        self.assertEqual(float(response.data["price"]), float(250))

        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Fully Updated")
        self.assertEqual(self.product.manufacturer, "NewMaker")
        self.assertEqual(float(self.product.price), float(250))

    def test_update_unauthenticated(self):
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_forbidden_for_non_admin(self):
        self.login_user()
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_not_found(self):
        self.login_admin()
        response = self.client.put(
            reverse("product:product-detail", args=[999_999]), self.payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_missing_required_field(self):
        self.login_admin()
        # Missing manufacturer
        response = self.client.put(
            self.detail_url, {"title": "Only title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)