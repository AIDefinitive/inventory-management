"""
Tests for restocking API endpoints (recommendations and submitted orders).
"""
from datetime import datetime, timedelta

import pytest

import main


@pytest.fixture(autouse=True)
def reset_restock_orders():
    """Submitted orders are stored in a module-level list, so clear it
    around each test to keep tests independent."""
    main.restock_orders.clear()
    yield
    main.restock_orders.clear()


class TestRestockRecommendationEndpoints:
    """Test suite for budget-based restock recommendations."""

    def test_get_recommendations(self, client):
        """Test getting recommendations returns the expected structure."""
        response = client.get("/api/restocking/recommendations?budget=2000")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        for field in ["budget", "total_cost", "remaining_budget", "full_restock_cost", "items"]:
            assert field in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

        for item in data["items"]:
            for field in ["item_sku", "item_name", "trend", "demand_gap",
                          "recommended_quantity", "unit_cost", "line_total", "lead_time_days"]:
                assert field in item
            assert isinstance(item["recommended_quantity"], int)
            assert isinstance(item["lead_time_days"], int)

    def test_recommendations_stay_within_budget(self, client):
        """Test that recommended totals never exceed the budget."""
        for budget in [0, 50, 500, 1234.56, 2000, 10000]:
            data = client.get(f"/api/restocking/recommendations?budget={budget}").json()
            assert data["total_cost"] <= budget + 0.001
            assert abs(data["total_cost"] + data["remaining_budget"] - budget) < 0.01

    def test_recommendations_total_cost_calculation(self, client):
        """Test that line totals and the overall total are accurate."""
        data = client.get("/api/restocking/recommendations?budget=2000").json()

        for item in data["items"]:
            assert abs(item["line_total"] - item["recommended_quantity"] * item["unit_cost"]) < 0.01

        assert abs(data["total_cost"] - sum(i["line_total"] for i in data["items"])) < 0.01

    def test_recommended_quantity_never_exceeds_demand_gap(self, client):
        """Test that quantities are capped at the forecast demand gap."""
        data = client.get("/api/restocking/recommendations?budget=1000000").json()

        for item in data["items"]:
            assert 0 < item["recommended_quantity"] <= item["demand_gap"]

    def test_large_budget_covers_full_restock(self, client):
        """Test that a budget above the full cost recommends every gap in full."""
        data = client.get("/api/restocking/recommendations?budget=1000000").json()

        assert abs(data["total_cost"] - data["full_restock_cost"]) < 0.01
        for item in data["items"]:
            assert item["recommended_quantity"] == item["demand_gap"]

    def test_recommendations_match_demand_forecasts(self, client):
        """Test that gaps, prices, and lead times come from the forecast data."""
        forecasts = {f["item_sku"]: f for f in client.get("/api/demand").json()}
        data = client.get("/api/restocking/recommendations?budget=1000000").json()

        expected_skus = {
            sku for sku, f in forecasts.items()
            if f["forecasted_demand"] > f["current_demand"]
        }
        assert {i["item_sku"] for i in data["items"]} == expected_skus

        for item in data["items"]:
            forecast = forecasts[item["item_sku"]]
            assert item["demand_gap"] == forecast["forecasted_demand"] - forecast["current_demand"]
            assert item["unit_cost"] == forecast["unit_cost"]
            assert item["lead_time_days"] == forecast["lead_time_days"]

    def test_increasing_trend_items_prioritized(self, client):
        """Test that increasing-demand items are ranked before stable ones."""
        data = client.get("/api/restocking/recommendations?budget=1000000").json()

        priority = {"increasing": 0, "stable": 1, "decreasing": 2}
        ranks = [priority[i["trend"]] for i in data["items"]]
        assert ranks == sorted(ranks)

    def test_limited_budget_funds_highest_priority_first(self, client):
        """Test that a small budget goes to the top-ranked item first."""
        full = client.get("/api/restocking/recommendations?budget=1000000").json()
        top = full["items"][0]

        # Enough for exactly 3 units of the top item.
        budget = top["unit_cost"] * 3
        data = client.get(f"/api/restocking/recommendations?budget={budget}").json()

        assert data["items"][0]["item_sku"] == top["item_sku"]
        assert data["items"][0]["recommended_quantity"] == 3

    def test_zero_budget_returns_no_items(self, client):
        """Test that a zero budget recommends nothing."""
        data = client.get("/api/restocking/recommendations?budget=0").json()

        assert data["items"] == []
        assert data["total_cost"] == 0
        assert data["full_restock_cost"] > 0

    def test_recommendations_missing_budget(self, client):
        """Test that the budget parameter is required."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 422

    def test_recommendations_negative_budget(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/restocking/recommendations?budget=-10")
        assert response.status_code == 422


class TestRestockOrderEndpoints:
    """Test suite for submitting and listing restocking orders."""

    def test_get_restock_orders_initially_empty(self, client):
        """Test that no orders exist before any are submitted."""
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restock_order(self, client):
        """Test submitting a restocking order."""
        payload = {"items": [{"item_sku": "WDG-001", "quantity": 10}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        for field in ["id", "order_number", "items", "total_value", "status",
                      "submitted_date", "lead_time_days", "expected_delivery"]:
            assert field in order
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-")
        assert len(order["items"]) == 1
        assert order["items"][0]["item_name"] == "Industrial Widget Type A"

    def test_restock_order_total_value_calculation(self, client):
        """Test that totals are computed from server-side unit costs."""
        forecasts = {f["item_sku"]: f for f in client.get("/api/demand").json()}
        payload = {"items": [
            {"item_sku": "WDG-001", "quantity": 10},
            {"item_sku": "GSK-203", "quantity": 25},
        ]}
        order = client.post("/api/restocking/orders", json=payload).json()

        expected = sum(forecasts[l["item_sku"]]["unit_cost"] * l["quantity"] for l in payload["items"])
        assert abs(order["total_value"] - expected) < 0.01
        for item in order["items"]:
            assert abs(item["line_total"] - item["unit_cost"] * item["quantity"]) < 0.01

    def test_restock_order_lead_time_is_longest_item(self, client):
        """Test that order lead time equals the slowest item's lead time."""
        forecasts = {f["item_sku"]: f for f in client.get("/api/demand").json()}
        skus = ["FLT-405", "CTL-330", "GSK-203"]
        payload = {"items": [{"item_sku": s, "quantity": 1} for s in skus]}
        order = client.post("/api/restocking/orders", json=payload).json()

        assert order["lead_time_days"] == max(forecasts[s]["lead_time_days"] for s in skus)

    def test_restock_order_dates_format(self, client):
        """Test that dates are ISO 8601 and delivery = submitted + lead time."""
        payload = {"items": [{"item_sku": "MTR-304", "quantity": 1}]}
        order = client.post("/api/restocking/orders", json=payload).json()

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert expected - submitted == timedelta(days=order["lead_time_days"])

    def test_submitted_orders_listed_newest_first(self, client):
        """Test that submitted orders appear in the list, newest first."""
        first = client.post("/api/restocking/orders",
                            json={"items": [{"item_sku": "WDG-001", "quantity": 1}]}).json()
        second = client.post("/api/restocking/orders",
                             json={"items": [{"item_sku": "BRG-102", "quantity": 2}]}).json()

        data = client.get("/api/restocking/orders").json()
        assert [o["id"] for o in data] == [second["id"], first["id"]]
        assert first["order_number"] != second["order_number"]

    def test_restock_order_ignores_client_prices(self, client):
        """Test that extra client-supplied price fields don't affect the total."""
        payload = {"items": [{"item_sku": "WDG-001", "quantity": 10, "unit_cost": 0.01}]}
        order = client.post("/api/restocking/orders", json=payload).json()

        assert order["items"][0]["unit_cost"] == 12.5
        assert abs(order["total_value"] - 125.0) < 0.01

    def test_restock_order_within_budget(self, client):
        """Test that an order at or under the budget is accepted."""
        payload = {"items": [{"item_sku": "WDG-001", "quantity": 10}], "budget": 125.0}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201

    def test_restock_order_exceeds_budget(self, client):
        """Test that an order over the budget is rejected and not stored."""
        payload = {"items": [{"item_sku": "WDG-001", "quantity": 10}], "budget": 100}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400
        assert "budget" in response.json()["detail"].lower()
        assert client.get("/api/restocking/orders").json() == []

    def test_restock_order_unknown_sku(self, client):
        """Test that an unknown SKU is rejected."""
        payload = {"items": [{"item_sku": "NOPE-999", "quantity": 1}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400
        assert "NOPE-999" in response.json()["detail"]

    def test_restock_order_empty_items(self, client):
        """Test that an order with no items is rejected."""
        response = client.post("/api/restocking/orders", json={"items": []})
        assert response.status_code == 422

    @pytest.mark.parametrize("quantity", [0, -5])
    def test_restock_order_invalid_quantity(self, client, quantity):
        """Test that non-positive quantities are rejected."""
        payload = {"items": [{"item_sku": "WDG-001", "quantity": quantity}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 422
