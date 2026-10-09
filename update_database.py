
import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
from vnstock import Quote


# Đường dẫn cơ sở dữ liệu
PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "data" / "market_data.db"

# Các mã cổ phiếu cần cập nhật
TICKERS = ["FPT", "MWG", "VIC"]

# Ngày bắt đầu lấy dữ liệu bổ sung
START_DATE = "2025-01-01"

# Ngày kết thúc là ngày hiện tại
END_DATE = date.today().isoformat()


def update_ticker(conn, ticker):
    print(f"\nĐang lấy dữ liệu {ticker}...")

    # Lấy lịch sử giá từ nguồn KBS
    quote = Quote(symbol=ticker, source="KBS")
    df = quote.history(
        start=START_DATE,
        end=END_DATE
    )

    if df is None or df.empty:
        print(f"Không có dữ liệu trả về cho {ticker}.")
        return

    # Chuẩn hóa tên cột
    df.columns = [str(col).lower() for col in df.columns]

    required = ["time", "open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"{ticker}: thiếu cột {missing}. "
            f"Các cột nhận được: {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(
        df["time"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df["symbol"] = ticker

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=["date", "open", "high", "low", "close", "volume"]
    )

    # Chỉ ghi thêm dữ liệu chưa có, không tạo bản ghi trùng
    rows = df[
        ["symbol", "date", "open", "high", "low", "close", "volume"]
    ].drop_duplicates(subset=["symbol", "date"])

    before = conn.total_changes

    conn.executemany(
        """
        INSERT INTO historical_ohlcv
            (symbol, date, open, high, low, close, volume)
        SELECT ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1
            FROM historical_ohlcv
            WHERE symbol = ? AND date = ?
        )
        """,
        [
            (
                row.symbol, row.date,
                float(row.open), float(row.high),
                float(row.low), float(row.close),
                float(row.volume),
                row.symbol, row.date
            )
            for row in rows.itertuples(index=False)
        ]
    )

    conn.commit()
    added = conn.total_changes - before

    latest = conn.execute(
        """
        SELECT MAX(date)
        FROM historical_ohlcv
        WHERE symbol = ?
        """,
        (ticker,)
    ).fetchone()[0]

    print(f"{ticker}: thêm {added} bản ghi mới.")
    print(f"Ngày dữ liệu mới nhất trong DB: {latest}")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy DB: {DB_PATH}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        for ticker in TICKERS:
            try:
                update_ticker(conn, ticker)
            except Exception as error:
                print(f"Lỗi khi cập nhật {ticker}: {error}")

    print("\nHoàn tất quá trình cập nhật.")


if __name__ == "__main__":
    main()