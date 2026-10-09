
import pandas as pd
import numpy as np

from financial_analysis import analyze_financials


# Bo du lieu co von chu so huu bang 0
df_zero_equity = pd.DataFrame({
    "period": ["2024", "2025"],
    "revenue": [1000, 1200],
    "net_income": [100, 150],
    "total_assets": [2000, 2200],
    "equity": [0, 0],
    "total_liabilities": [2000, 2200],
    "eps": [1000, 1500],
    "book_value_per_share": [0, 0]
})

result = analyze_financials(
    df_zero_equity,
    price=30000
)

latest = result["latest"]

# D/E khong duoc la vo cuc khi equity bang 0
assert pd.isna(latest["de_ratio"])

# P/B khong hop le neu BVPS bang 0
assert pd.isna(latest["pb"])

print("PASS: Xu ly von chu so huu bang 0")


# Bo du lieu thieu loi nhuan
df_missing = pd.DataFrame({
    "period": ["2024", "2025"],
    "revenue": [1000, 1200],
    "net_income": [100, np.nan],
    "total_assets": [2000, 2200],
    "equity": [1000, 1100],
    "total_liabilities": [1000, 1100]
})

result_missing = analyze_financials(df_missing)

# Khong tu dien loi nhuan bi thieu thanh 0
assert pd.isna(result_missing["latest"]["net_income"])

print("PASS: Khong tu dien loi nhuan bi thieu")


# Kiem tra doanh nghiep tai chinh
df_bank = pd.DataFrame({
    "period": ["2024", "2025"],
    "revenue": [1000, 1200],
    "net_income": [100, 130],
    "total_assets": [10000, 12000],
    "equity": [1000, 1200],
    "total_liabilities": [9000, 10800]
})

result_bank = analyze_financials(
    df_bank,
    company_type="financial"
)

assert result_bank["latest"]["de_ratio"] != (
    result_bank["latest"]["de_ratio"]
)

print("PASS: Khong ap dung D/E thong thuong cho doanh nghiep tai chinh")
print("\nTat ca kiem thu bo sung da hoan thanh.")