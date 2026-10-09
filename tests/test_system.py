import unittest

from data_sources.price_provider import get_price_data
from analysis.technical_analysis import analyze_technical
from services.investment_service import analyze_stock


class TestInvestmentSystem(unittest.TestCase):

    def test_get_prices_by_ticker(self):
        df = get_price_data("FPT", source="mock")
        self.assertTrue((df["ticker"] == "FPT").all())
        self.assertGreaterEqual(len(df), 50)

    def test_invalid_ticker(self):
        result = analyze_stock("UNKNOWN", "cân bằng")
        self.assertFalse(result["success"])

    def test_technical_indicators(self):
        df = get_price_data("MWG", source="mock")
        result = analyze_technical(df)

        self.assertGreater(result["close"], 0)
        self.assertGreater(result["ma20"], 0)
        self.assertGreater(result["ma50"], 0)
        self.assertGreaterEqual(result["rsi14"], 0)
        self.assertLessEqual(result["rsi14"], 100)
        self.assertIn(
            result["trend"],
            ["Tích cực", "Trung tính", "Tiêu cực"],
        )

    def test_full_analysis(self):
        fundamental = {
            "financial": 80,
            "growth": 75,
            "valuation": 70,
            "risk": 65,
        }

        result = analyze_stock(
            "FPT",
            "cân bằng",
            fundamental_scores=fundamental,
            source="mock",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["ticker"], "FPT")
        self.assertIn("report", result)
        self.assertIn("total_score", result["report"]["investment"])

    def test_invalid_risk_profile(self):
        result = analyze_stock(
            "FPT",
            "không hợp lệ",
            fundamental_scores={
                "financial": 80,
                "growth": 75,
                "valuation": 70,
                "risk": 65,
            },
        )
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()