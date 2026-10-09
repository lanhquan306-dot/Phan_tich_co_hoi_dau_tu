
from data_sources.price_provider import get_price_data

df = get_price_data(
    ticker="FPT",
    source="real",
    start="2025-01-01",
    end="2026-10-09",
)

print(df.tail())
print("Số dòng dữ liệu:", len(df))
print("Ngày cuối:", df["date"].max())
print("Giá đóng cửa gần nhất:", df["close"].iloc[-1])