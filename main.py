from services.investment_service import analyze_stock


def main():
    ticker = input("Nhập mã cổ phiếu (FPT/MWG/VIC): ").strip().upper()

    print("\nChọn khẩu vị rủi ro:")
    print("1. Thận trọng")
    print("2. Cân bằng")
    print("3. Tăng trưởng")

    choices = {
        "1": "thận trọng",
        "2": "cân bằng",
        "3": "tăng trưởng",
    }

    choice = input("Lựa chọn (1/2/3): ").strip()
    profile = choices.get(choice)

    if profile is None:
        print("Lựa chọn không hợp lệ.")
        return

    # Điểm giả để kiểm tra luồng tích hợp.
    # Khi ghép nhóm, thay bằng điểm từ phần phân tích cơ bản.
    mock_fundamental_scores = {
        "financial": 80,
        "growth": 75,
        "valuation": 70,
        "risk": 65,
    }

    result = analyze_stock(
        ticker=ticker,
        risk_profile=profile,
        fundamental_scores=mock_fundamental_scores,
        source="mock",
    )

    if not result["success"]:
        print("\nLỗi:", result["error"])
        return

    report = result["report"]
    tech = report["technical"]
    investment = report["investment"]

    print("\n========== KẾT QUẢ PHÂN TÍCH ==========")
    print("Mã cổ phiếu:", result["ticker"])
    print("Nguồn dữ liệu:", result["data_source"])
    print("Giá đóng cửa:", round(tech["close"], 2))
    print("MA20:", round(tech["ma20"], 2))
    print("MA50:", round(tech["ma50"], 2))
    print("RSI14:", round(tech["rsi14"], 2))
    print("Xu hướng:", tech["trend"])
    print("Tín hiệu RSI:", tech["rsi_signal"])
    print("Điểm kỹ thuật:", tech["technical_score"])
    print("Khẩu vị:", investment["risk_profile"])
    print("Điểm đầu tư:", investment["total_score"])
    print("Đánh giá:", investment["rating"])

    print("\nĐiểm mạnh:")
    for item in report["strengths"]:
        print("-", item)

    print("\nĐiểm yếu:")
    for item in report["weaknesses"]:
        print("-", item)

    print("\nRủi ro:")
    for item in report["risks"]:
        print("-", item)

    print("\nLưu ý:", report["disclaimer"])


if __name__ == "__main__":
    main()