
import pandas as pd
from financial_analysis import analyze_financials


df = pd.DataFrame({
    "period": ["2023", "2024", "2025"],
    "revenue": [1000, 1200, 1500],
    "net_income": [100, 120, 180],
    "total_assets": [2000, 2200, 2500],
    "equity": [1000, 1100, 1300],
    "total_liabilities": [1000, 1100, 1200],
    "eps": [1000, 1200, 1800],
    "book_value_per_share": [10000, 11000, 13000]
})

result = analyze_financials(
    df,
    price=30000,
    company_type="non_financial"
)

print("\n=== BANG CHI SO TAI CHINH ===")
print(
    result["indicators"][
        [
            "period",
            "revenue_growth",
            "profit_growth",
            "roe",
            "roa",
            "de_ratio",
            "pe",
            "pb"
        ]
    ].round(4).to_string(index=False)
)

print("\n=== NHAN DINH ===")

for comment in result["assessments"]:
    print("-", comment)