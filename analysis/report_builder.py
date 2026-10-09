def build_report(technical: dict, technical_score: dict,
                 investment: dict) -> dict:
    """Tạo phần nhận định từ kết quả phân tích."""

    scores = investment["component_scores"]
    strengths = []
    weaknesses = []
    risks = []

    labels = {
        "financial": "Sức khỏe tài chính",
        "growth": "Triển vọng tăng trưởng",
        "valuation": "Mức độ hấp dẫn về định giá",
        "technical": "Tín hiệu kỹ thuật",
        "risk": "Mức độ an toàn",
    }

    for name, score in scores.items():
        if score >= 75:
            strengths.append(labels[name])
        elif score < 50:
            weaknesses.append(labels[name])

    if technical["trend"] == "Tiêu cực":
        risks.append("Xu hướng giá hiện tại đang tiêu cực.")

    if technical["rsi_signal"] == "Vùng quá mua":
        risks.append("RSI ở vùng quá mua; cần chú ý khả năng điều chỉnh.")

    if technical["rsi_signal"] == "Vùng quá bán":
        risks.append("RSI ở vùng quá bán; cần đánh giá nguyên nhân giá giảm.")

    if scores["risk"] < 50:
        risks.append("Điểm an toàn thấp theo bộ tiêu chí hiện tại.")

    if scores["technical"] < 50:
        risks.append("Điểm kỹ thuật thấp, cần theo dõi diễn biến giá.")

    if not strengths:
        strengths.append("Chưa có tiêu chí nào đạt ngưỡng điểm mạnh.")

    if not weaknesses:
        weaknesses.append("Chưa có tiêu chí nào dưới ngưỡng điểm yếu.")

    if not risks:
        risks.append("Tiếp tục theo dõi rủi ro doanh nghiệp và thị trường.")

    return {
        "ticker": technical["ticker"],
        "technical": {
            "close": technical["close"],
            "ma20": technical["ma20"],
            "ma50": technical["ma50"],
            "rsi14": technical["rsi14"],
            "trend": technical["trend"],
            "rsi_signal": technical["rsi_signal"],
            "technical_score": technical_score["technical_score"],
            "interpretation": technical_score["technical_interpretation"],
        },
        "investment": investment,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "risks": risks,
        "disclaimer": (
            "Kết quả hỗ trợ phân tích, không phải cam kết lợi nhuận "
            "hoặc khuyến nghị mua bán tự động."
        ),
    }