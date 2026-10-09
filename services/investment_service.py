from typing import Optional
from data_sources.price_provider import get_price_data
from analysis.technical_analysis import analyze_technical
from analysis.technical_scoring import calculate_technical_score
from analysis.investment_scoring import calculate_investment_score
from analysis.report_builder import build_report


def analyze_stock(
    ticker: str,
    risk_profile: str = "cân bằng",
    fundamental_scores: Optional[dict] = None,
    source: str = "mock",
) -> dict:
    """
    Hàm giao diện gọi:
    - ticker: mã cổ phiếu
    - risk_profile: thận trọng / cân bằng / tăng trưởng
    - fundamental_scores: điểm từ phần phân tích cơ bản
    - source: nguồn dữ liệu, hiện tại là mock
    """

    try:
        ticker = ticker.strip().upper()

        if not ticker:
            raise ValueError("Vui lòng nhập mã cổ phiếu.")

        # 1. Lấy dữ liệu giá theo đúng mã.
        price_df = get_price_data(ticker, source=source)

        # 2. Tính chỉ báo và xác định xu hướng.
        technical = analyze_technical(price_df)

        # 3. Chấm điểm kỹ thuật.
        technical_score = calculate_technical_score(technical)

        # 4. Chưa nhận điểm cơ bản thì không giả vờ đưa ra điểm tổng.
        if fundamental_scores is None:
            return {
                "success": True,
                "ticker": ticker,
                "data_source": source,
                "status": "technical_only",
                "technical": {
                    "close": technical["close"],
                    "ma20": technical["ma20"],
                    "ma50": technical["ma50"],
                    "rsi14": technical["rsi14"],
                    "trend": technical["trend"],
                    "rsi_signal": technical["rsi_signal"],
                    **technical_score,
                },
                "message": (
                    "Đã phân tích kỹ thuật. Cần điểm phân tích cơ bản "
                    "để tính điểm đầu tư tổng hợp."
                ),
            }

        required = {"financial", "growth", "valuation", "risk"}
        if not required.issubset(fundamental_scores):
            raise ValueError(
                "Điểm cơ bản phải có financial, growth, valuation và risk."
            )

        # 5. Tổng hợp điểm đầu tư.
        investment = calculate_investment_score(
            financial_score=fundamental_scores["financial"],
            growth_score=fundamental_scores["growth"],
            valuation_score=fundamental_scores["valuation"],
            technical_score=technical_score["technical_score"],
            risk_score=fundamental_scores["risk"],
            risk_profile=risk_profile,
        )

        # 6. Tạo báo cáo bàn giao.
        report = build_report(technical, technical_score, investment)

        return {
            "success": True,
            "ticker": ticker,
            "data_source": source,
            "status": "complete",
            "report": report,
        }

    except (ValueError, TypeError, KeyError) as exc:
        return {
            "success": False,
            "ticker": ticker.strip().upper() if isinstance(ticker, str) else "",
            "error": str(exc),
        }