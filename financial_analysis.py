
import pandas as pd
import numpy as np


def prepare_financial_data(df):
    """Kiem tra va chuan hoa bang du lieu tai chinh."""

    required_columns = [
        "period",
        "revenue",
        "net_income",
        "total_assets",
        "equity",
        "total_liabilities"
    ]

    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Khong co du lieu tai chinh.")

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Thieu cot du lieu: {missing}")

    df = df.copy()

    numeric_columns = [
        "revenue",
        "net_income",
        "total_assets",
        "equity",
        "total_liabilities",
        "eps",
        "book_value_per_share"
    ]

    for col in numeric_columns:
        if col not in df.columns:
            df[col] = np.nan
        else:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    df = df.drop_duplicates(
        subset=["period"], keep="last"
    )

df = df.sort_values("period")
return df.reset_index(drop=True)


def calculate_financial_indicators(
    df, price=None, company_type="non_financial"
):
    """Tinh cac chi so tai chinh co ban."""

    df = prepare_financial_data(df)

    # Du lieu phai duoc sap xep tu ky cu den ky moi
    df["revenue_growth"] = df["revenue"].pct_change(fill_method=None)
    df["profit_growth"] = df["net_income"].pct_change(fill_method=None)

    # Khong tinh tang truong thong thuong neu ky truoc <= 0
    df.loc[
        df["revenue"].shift(1) <= 0,
        "revenue_growth"
    ] = np.nan

    df.loc[
        df["net_income"].shift(1) <= 0,
        "profit_growth"
    ] = np.nan

    # Von chu so huu va tai san binh quan
    avg_equity = (
        df["equity"] + df["equity"].shift(1)
    ) / 2

    avg_assets = (
        df["total_assets"] + df["total_assets"].shift(1)
    ) / 2

    # Ky dau tien dung so cuoi ky lam gia tri xap xi
    avg_equity = avg_equity.fillna(df["equity"])
    avg_assets = avg_assets.fillna(df["total_assets"])

    df["roe"] = (
        df["net_income"]
        / avg_equity.where(avg_equity > 0)
    )

    df["roa"] = (
        df["net_income"]
        / avg_assets.where(avg_assets > 0)
    )

    # D/E khong ap dung cung cach cho ngan hang
    if company_type == "non_financial":
        df["de_ratio"] = (
            df["total_liabilities"]
            / df["equity"].where(df["equity"] > 0)
        )
    else:
        df["de_ratio"] = np.nan

    # Khoi tao P/E va P/B
    if "pe" not in df.columns:
        df["pe"] = np.nan

    if "pb" not in df.columns:
        df["pb"] = np.nan

    if price is not None:
        last_index = df.index[-1]

        eps = df.loc[last_index, "eps"]
        bvps = df.loc[
            last_index, "book_value_per_share"
        ]

        if pd.notna(eps) and eps > 0:
            if pd.isna(df.loc[last_index, "pe"]):
                df.loc[last_index, "pe"] = price / eps

        if pd.notna(bvps) and bvps > 0:
            if pd.isna(df.loc[last_index, "pb"]):
                df.loc[last_index, "pb"] = price / bvps

    return df


def assess_financial_performance(
    row, company_type="non_financial"
):
    """Tao nhan dinh tu cac chi so tai chinh."""

    comments = []

    growth = row.get("revenue_growth", np.nan)

    if pd.isna(growth):
        comments.append(
            "Chua du du lieu danh gia tang truong doanh thu."
        )
    elif growth >= 0.10:
        comments.append(
            f"Doanh thu tang {growth:.1%}, "
            "dat nguong tang truong tham khao."
        )
    elif growth >= 0:
        comments.append(
            f"Doanh thu tang nhe {growth:.1%}."
        )
    else:
        comments.append(
            f"Doanh thu giam {abs(growth):.1%}."
        )

    growth = row.get("profit_growth", np.nan)

    if pd.isna(growth):
        comments.append(
            "Chua du du lieu danh gia tang truong LNST."
        )
    elif growth >= 0.10:
        comments.append(
            f"LNST tang {growth:.1%}, "
            "dat nguong tang truong tham khao."
        )
    elif growth >= 0:
        comments.append(
            f"LNST tang nhe {growth:.1%}."
        )
    else:
        comments.append(
            f"LNST giam {abs(growth):.1%}."
        )

    roe = row.get("roe", np.nan)

    if pd.isna(roe):
        comments.append("Chua du du lieu tinh ROE.")
    elif roe < 0:
        comments.append("ROE am, can xem xet ket qua kinh doanh.")
    else:
        comments.append(
            f"ROE dat {roe:.1%}; can so sanh voi cung nganh."
        )

    roa = row.get("roa", np.nan)

    if pd.isna(roa):
        comments.append("Chua du du lieu tinh ROA.")
    elif roa < 0:
        comments.append("ROA am, can xem xet hieu qua su dung tai san.")
    else:
        comments.append(
            f"ROA dat {roa:.1%}; can so sanh voi cung nganh."
        )

    if company_type == "financial":
        comments.append(
            "Can dung bo chi tieu chuyen nganh tai chinh; "
            "khong dien giai D/E theo quy tac doanh nghiep thong thuong."
        )
    else:
        de = row.get("de_ratio", np.nan)

        if pd.isna(de):
            comments.append("Chua du du lieu tinh D/E.")
        else:
            comments.append(
                f"D/E = {de:.2f} lan; can doi chieu voi cung nganh."
            )

    for label, column in [("P/E", "pe"), ("P/B", "pb")]:
        value = row.get(column, np.nan)

        if pd.isna(value) or value <= 0:
            comments.append(
                f"Chua co {label} hop le de danh gia."
            )
        else:
            comments.append(
                f"{label} = {value:.2f} lan; "
                "can so sanh voi doanh nghiep cung nganh."
            )

    return comments


def analyze_financials(
    df, price=None, company_type="non_financial"
):
    """Ham tong hop de Dashboard goi."""

    indicators = calculate_financial_indicators(
        df,
        price=price,
        company_type=company_type
    )

    latest = indicators.iloc[-1]

    return {
        "indicators": indicators,
        "latest": latest,
        "assessments": assess_financial_performance(
            latest,
            company_type=company_type
        )
    }