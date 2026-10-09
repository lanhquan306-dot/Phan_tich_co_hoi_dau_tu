import pandas as pd


def analyze_technical(price_df: pd.DataFrame) -> dict:
    """Tính chỉ báo kỹ thuật và xác định xu hướng giá."""

    required = {"ticker", "date", "close"}

    if not required.issubset(price_df.columns):
        raise ValueError(f"Dữ liệu phải có các cột: {required}")

    df = price_df[["ticker", "date", "close"]].copy()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = (
        df.dropna(subset=["ticker", "date", "close"])
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
        .reset_index(drop=True)
    )

    if df.empty:
        raise ValueError("Không có dữ liệu giá hợp lệ.")

    if df["ticker"].nunique() != 1:
        raise ValueError("Dữ liệu chứa nhiều mã cổ phiếu khác nhau.")

    if (df["close"] <= 0).any():
        raise ValueError("Giá đóng cửa phải lớn hơn 0.")

    if len(df) < 50:
        raise ValueError("Cần tối thiểu 50 phiên để tính MA50.")

    # Trung bình giá đóng cửa 20 và 50 phiên.
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()

    # RSI14 theo cách làm mượt Wilder.
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14, min_periods=14, adjust=False
    ).mean()
    avg_loss = loss.ewm(
        alpha=1 / 14, min_periods=14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss
    df["RSI14"] = 100 - (100 / (1 + rs))

    df.loc[(avg_loss == 0) & (avg_gain > 0), "RSI14"] = 100
    df.loc[(avg_loss == 0) & (avg_gain == 0), "RSI14"] = 50

    latest = df.iloc[-1]

    if latest["close"] > latest["MA20"] > latest["MA50"]:
        trend = "Tích cực"
    elif latest["close"] < latest["MA20"] < latest["MA50"]:
        trend = "Tiêu cực"
    else:
        trend = "Trung tính"

    rsi = float(latest["RSI14"])

    if rsi >= 70:
        rsi_signal = "Vùng quá mua"
    elif rsi <= 30:
        rsi_signal = "Vùng quá bán"
    else:
        rsi_signal = "Vùng trung tính"

    return {
        "ticker": str(latest["ticker"]),
        "close": float(latest["close"]),
        "ma20": float(latest["MA20"]),
        "ma50": float(latest["MA50"]),
        "rsi14": rsi,
        "trend": trend,
        "rsi_signal": rsi_signal,
        "history": df,
    }