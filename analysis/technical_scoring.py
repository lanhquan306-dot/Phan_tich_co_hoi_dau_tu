def calculate_technical_score(technical: dict) -> dict:
    """
    Trả về điểm kỹ thuật từ 0 đến 100.
    Điểm số là quy tắc thử nghiệm của dự án, cần hiệu chỉnh sau.
    """

    required = {"close", "ma20", "ma50", "rsi14", "trend"}

    if not required.issubset(technical):
        raise ValueError("Thiếu thông tin để chấm điểm kỹ thuật.")

    close = technical["close"]
    ma20 = technical["ma20"]
    ma50 = technical["ma50"]
    rsi = technical["rsi14"]
    trend = technical["trend"]

    score = 50

    if close > ma20:
        score += 15
    elif close < ma20:
        score -= 15

    if ma20 > ma50:
        score += 20
    elif ma20 < ma50:
        score -= 20

    if 40 <= rsi <= 60:
        score += 10
    elif 30 <= rsi < 40 or 60 < rsi < 70:
        score += 5
    elif rsi <= 30 or rsi >= 70:
        score -= 5

    score = max(0, min(100, score))

    return {
        "technical_score": score,
        "technical_interpretation": (
            "Tín hiệu kỹ thuật tương đối tích cực."
            if score >= 70
            else "Tín hiệu kỹ thuật ở mức trung bình."
            if score >= 50
            else "Tín hiệu kỹ thuật tương đối yếu."
        ),
    }