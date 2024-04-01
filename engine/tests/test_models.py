import pytest
from engine.models import CostItem


class TestCostItem:
    @pytest.mark.django_db
    def test_credits(self):
        cost_item = CostItem(
            title="Test Item",
            model_name="TestModel",
            prompt_token_count=100,
            completion_token_count=200,
            requests=1,
            total_cost_usd=10.0,
        )
        cost_item.save()

        # Assuming CREDIT_MULTIPLIER is set to 2 for this test
        expected_credits = 10.0 * 2 * 100
        assert cost_item.credits == expected_credits, "The credits calculation did not match the expected value."
