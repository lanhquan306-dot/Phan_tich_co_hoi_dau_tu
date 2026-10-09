PROFILE_WEIGHTS = {
    "thận trọng": {
        "financial": 0.30,
        "growth": 0.10,
        "valuation": 0.20,
        "technical": 0.10,
        "risk": 0.30,
    },
    "cân bằng": {
        "financial": 0.25,
        "growth": 0.20,
        "valuation": 0.20,
        "technical": 0.15,
        "risk": 0.20,
    },
    "tăng trưởng": {
        "financial": 0.15,
        "growth": 0.30,
        "valuation": 0.15,
        "technical": 0.25,
        "risk": 0.15,
    },
}


def calculate_investment_score(
    financial_score: float,
    growth_score: float,
    valuation_score: float,
    technical_score: float,
    risk_score: float,
    risk_profile: str = "cân bằng",
) -> dict:
    """Tính điểm đầu tư tổng hợp theo khẩu vị rủi ro."""

    profile = risk_profile.strip().lower()

    if profile not in PROFILE_WEIGHTS:
        raise ValueError(
            "Khẩu vị hợp lệ: thận trọng, cân bằng hoặc tăng trưởng."
        )

    scores = {
        "financial": financial_score,
        "growth": growth_score,
        "valuation": valuation_score,
        "technical": technical_score,
        "risk": risk_score,
    }

    for name, score in scores.items():
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(f"Điểm {name} phải là số.")
        if not 0 <= score <= 100:
            raise ValueError(f"Điểm {name} phải nằm trong khoảng 0–100.")

    weights = PROFILE_WEIGHTS[profile]
    total = sum(scores[name] * weights[name] for name in scores)

    if total >= 80:
        rating = "Được đánh giá cao theo bộ tiêu chí"
    elif total >= 65:
        rating = "Cần xem xét thêm"
    else:
        rating = "Chưa hấp dẫn theo bộ tiêu chí"

    return {
        "risk_profile": profile,
        "total_score": round(total, 2),
        "rating": rating,
        "component_scores": scores,
        "weights": weights,
    }