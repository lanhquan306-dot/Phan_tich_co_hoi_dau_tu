"""
data_module.py (v3 - dùng vnstock 4.x) - Module thu thập dữ liệu đa mã (Ân - TV2)

Cài đặt (Python 3.12):
    py -3.12 -m pip install -U --extra-index-url https://vnstocks.com/api/simple vnstock vnai pandas

Cách dùng:
    from data_module import lay_toan_bo
    kq = lay_toan_bo("VCB")

kq là dict gồm:
    hop_le, ma, nganh, la_ngan_hang
    gia        bảng giá lịch sử: symbol, date, open, high, low, close, volume
               ĐƠN VỊ: giá = VND/cổ phiếu, volume = cổ phiếu
    realtime   giá trong phiên (độ trễ theo nguồn), khop_lenh: khớp lệnh trong phiên
    thong_tin  hồ sơ doanh nghiệp, tin_tuc: tin doanh nghiệp
    kqkd, cdkt, luu_chuyen, chiso   báo cáo tài chính (giữ nguyên cột gốc)
    meta_bctc  số kỳ, tên cột kỳ của từng bảng
    canh_bao   danh sách cảnh báo (TV5 hiển thị lên Dashboard)
"""
from datetime import date, timedelta
from functools import lru_cache

import pandas as pd

# Đơn vị giá của nguồn: "auto" (tự nhận biết, có cảnh báo), "nghin" (nghìn đồng), "vnd"
# SAU KHI CHẠY: đối chiếu giá đóng cửa VCB với giá thật rồi đặt cố định "nghin" hoặc "vnd".
DON_VI_GIA = "nghin"   # đã đối chiếu: nguồn trả giá theo NGHÌN ĐỒNG (VCB 56.5 = 56.500 VND)
CAC_COT_GIA = ["open", "high", "low", "close", "volume"]
NGAN_HANG = {"VCB", "BID", "CTG", "TCB", "VPB", "MBB", "ACB", "STB", "HDB",
             "SHB", "TPB", "VIB", "LPB", "MSB", "OCB", "SSB", "EIB", "ABB"}


# ---------------------------------------------------------------- tiện ích
@lru_cache(maxsize=1)
def _api():
    from vnstock import Market, Reference, Fundamental
    return Market(), Reference(), Fundamental()


def _goi_api(nhom, ten, symbol, methods, **kw):
    """Gọi API theo 2 kiểu (tài liệu vnstock 4 có 2 cách viết):
       kiểu 1: nhom.ten.method(symbol=..., **kw)
       kiểu 2: nhom.ten(symbol).method(**kw)
       methods: tên hàm, có thể kèm tên thay thế (vd ("ratios", "ratio"))."""
    if isinstance(methods, str):
        methods = (methods,)
    doi_tuong = getattr(nhom, ten)
    loi = []
    for m in methods:
        try:
            return getattr(doi_tuong, m)(symbol=symbol, **kw)
        except (TypeError, AttributeError) as e:
            loi.append(f"kiểu1/{m}: {e}")
        try:
            return getattr(doi_tuong(symbol), m)(**kw)
        except (TypeError, AttributeError) as e:
            loi.append(f"kiểu2/{m}: {e}")
    raise RuntimeError(" | ".join(loi))


def _goi(ham, *cach):
    """Thử lần lượt các cách truyền tham số (phòng khi tên tham số khác nhau)."""
    loi = None
    for args, kwargs in cach:
        try:
            return ham(*args, **kwargs)
        except TypeError as e:
            loi = e
    raise loi


def _lam_phang_cot(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(str(x) for x in c if str(x)) for c in df.columns]
    return df


def _df_hop_le(df):
    return isinstance(df, pd.DataFrame) and not df.empty


# ------------------------------------------------------------ danh sách mã
@lru_cache(maxsize=1)
def _danh_sach_ma_cache():
    return _api()[1].equity.list()


def lay_danh_sach_ma():
    """Trả về (DataFrame, cảnh báo)."""
    try:
        df = _danh_sach_ma_cache()
        if not _df_hop_le(df):
            return pd.DataFrame(), ["Danh sách mã trống"]
        return df.copy(), []
    except Exception as e:
        return pd.DataFrame(), [f"Lỗi lấy danh sách mã: {e}"]


def kiem_tra_ma(symbol):
    """Trả về (mã sạch, cảnh báo, hợp_lệ). Không ném lỗi để Dashboard không sập."""
    if not isinstance(symbol, str) or not symbol.strip():
        return "", ["Mã cổ phiếu không được để trống"], False
    ma = symbol.upper().strip()
    ds, _ = lay_danh_sach_ma()
    if ds.empty:
        return ma, ["Không kiểm tra được mã trong danh sách (lỗi nguồn)"], True
    cot = "symbol" if "symbol" in ds.columns else ds.columns[0]
    if ma not in set(ds[cot].astype(str).str.upper()):
        return ma, [f"Mã {ma} không có trong danh sách chứng khoán"], False
    return ma, [], True


# ------------------------------------------------------- thông tin / tin tức
def lay_thong_tin_dn(symbol):
    try:
        df = _goi_api(_api()[1], "company", symbol, "info")
        if not _df_hop_le(df):
            return pd.DataFrame(), ["Thông tin doanh nghiệp trống"]
        return _lam_phang_cot(df), []
    except Exception as e:
        return pd.DataFrame(), [f"Lỗi thông tin doanh nghiệp: {e}"]


def lay_tin_tuc(symbol):
    try:
        df = _goi_api(_api()[1], "company", symbol, "news")
        if not _df_hop_le(df):
            return pd.DataFrame(), ["Không có tin tức doanh nghiệp"]
        return _lam_phang_cot(df), []
    except Exception as e:
        return pd.DataFrame(), [f"Lỗi lấy tin tức: {e}"]


def tim_nganh(symbol, df_tt):
    nganh = None
    if _df_hop_le(df_tt):
        for c in df_tt.columns:
            if any(k in str(c).lower() for k in ("icb_name3", "industry", "icb_name2", "sector")):
                v = df_tt[c].iloc[0]
                if pd.notna(v):
                    nganh = str(v)
                    break
    la_nh = symbol in NGAN_HANG or (nganh is not None and "ngân hàng" in nganh.lower())
    return nganh, la_nh


# ---------------------------------------------------------------- giá lịch sử
def chuan_hoa_gia(df, symbol):
    """Chuẩn hóa về VND (tự phát hiện nếu nguồn trả giá theo nghìn đồng)."""
    cb = []
    if not _df_hop_le(df):
        return pd.DataFrame(), ["Không có dữ liệu giá"]
    df = df.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]
    if "time" in df.columns:
        df = df.rename(columns={"time": "date"})
    thieu = [c for c in ["date"] + CAC_COT_GIA if c not in df.columns]
    if thieu:
        return pd.DataFrame(), [f"Dữ liệu giá thiếu cột {thieu}; cột hiện có: {list(df.columns)}"]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in CAC_COT_GIA:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    n = int(df.duplicated(subset="date").sum())
    if n:
        cb.append(f"Đã xóa {n} ngày trùng")
        df = df.drop_duplicates(subset="date", keep="last")
    n = int(df[["date"] + CAC_COT_GIA].isna().any(axis=1).sum())
    if n:
        cb.append(f"Đã loại {n} dòng thiếu dữ liệu")
        df = df.dropna(subset=["date"] + CAC_COT_GIA)
    xau = (df[["open", "high", "low", "close"]] <= 0).any(axis=1) | (df["volume"] < 0)
    if int(xau.sum()):
        cb.append(f"Đã loại {int(xau.sum())} dòng giá <= 0 hoặc khối lượng âm")
        df = df[~xau]
    sai = df["high"] < df["low"]
    if int(sai.sum()):
        cb.append(f"Đã loại {int(sai.sum())} dòng giá cao nhất < thấp nhất")
        df = df[~sai]
    if df.empty:
        return pd.DataFrame(), cb + ["Sau khi làm sạch không còn dữ liệu giá"]

    df = df.sort_values("date").reset_index(drop=True)
    trung_vi = float(df["close"].median())
    if DON_VI_GIA == "nghin":
        nhan = True
    elif DON_VI_GIA == "vnd":
        nhan = False
    else:  # auto: giá cổ phiếu VN hầu như luôn >= 1.000 VND nên < 1000 nghĩa là đang tính nghìn đồng
        nhan = trung_vi < 1000
        cb.append(f"Đơn vị giá tự nhận biết (trung vị giá đóng cửa gốc = {trung_vi:g}); "
                  f"cần đối chiếu với giá thật")
    if nhan:
        for c in ["open", "high", "low", "close"]:
            df[c] = df[c] * 1000
        cb.append("Giá nguồn tính theo nghìn đồng, đã quy đổi sang VND")
    cb.append("Chưa xác nhận giá đã điều chỉnh cổ tức/chia tách hay chưa (tùy nguồn)")
    df.insert(0, "symbol", symbol)
    df = df[["symbol", "date"] + CAC_COT_GIA]

    if len(df) < 50:
        cb.append(f"Chỉ có {len(df)} phiên - không đủ để tính MA50")
    return df, cb


def lay_du_lieu_gia(symbol, so_ngay=730):
    try:
        end = date.today()
        start = end - timedelta(days=so_ngay)
        df = _goi_api(_api()[0], "equity", symbol, "ohlcv",
                      start=start.strftime("%Y-%m-%d"),
                      end=end.strftime("%Y-%m-%d"))
        return chuan_hoa_gia(df, symbol)
    except Exception as e:
        return pd.DataFrame(), [f"Lỗi lấy giá lịch sử: {e}"]


# ------------------------------------------------------------------ realtime
def lay_gia_realtime(symbols):
    """Giá hiện tại trong phiên (lấy khi gọi hàm, KHÔNG tự cập nhật liên tục; có độ trễ theo nguồn).
    Nhận 1 mã hoặc list mã."""
    if isinstance(symbols, str):
        symbols = [symbols]
    ds = [x.upper().strip() for x in symbols]
    loi = []
    thu = []
    if len(ds) == 1:
        thu.append(lambda: _goi_api(_api()[0], "equity", ds[0], "quote"))
    thu.append(lambda: _api()[0].quote(ds))
    for f in thu:
        try:
            df = f()
            if _df_hop_le(df):
                return _lam_phang_cot(df), []
            loi.append("trống")
        except Exception as e:
            loi.append(str(e))
    return pd.DataFrame(), ["Giá realtime không lấy được (có thể ngoài giờ giao dịch): " + " | ".join(loi)]


def lay_khop_lenh(symbol, so_dong=200):
    try:
        try:
            df = _goi_api(_api()[0], "equity", symbol, "trades", page_size=so_dong)
        except Exception:
            df = _goi_api(_api()[0], "equity", symbol, "trades")
        if not _df_hop_le(df):
            return pd.DataFrame(), ["Không có khớp lệnh trong phiên"]
        return df, []
    except Exception as e:
        return pd.DataFrame(), [f"Lỗi khớp lệnh: {e}"]


# ---------------------------------------------------------------------- BCTC
def lay_bctc(symbol, ky="year"):
    ham = {"kqkd": "income_statement", "cdkt": "balance_sheet",
           "luu_chuyen": "cash_flow", "chiso": ("ratios", "ratio")}
    kq, meta, cb = {}, {}, []
    for ten, m in ham.items():
        try:
            fa = _api()[2]
            try:
                df = _goi_api(fa, "equity", symbol, m, period=ky)
            except RuntimeError:          # một số hàm (vd ratio) có thể không nhận period
                df = _goi_api(fa, "equity", symbol, m)
            if not _df_hop_le(df):
                kq[ten] = pd.DataFrame()
                cb.append(f"{ten}: không có dữ liệu")
                continue
            df = _lam_phang_cot(df).drop_duplicates()
            kq[ten] = df
            # Lưu ý: BCTC có thể có chỉ tiêu theo HÀNG, kỳ báo cáo theo CỘT -> không suy ra số kỳ từ số dòng
            meta[ten] = {"so_dong": df.shape[0], "so_cot": df.shape[1],
                         "loai_ky": ky, "cac_cot": [str(c) for c in df.columns][:12]}
        except Exception as e:
            kq[ten] = pd.DataFrame()
            cb.append(f"{ten}: lỗi {e}")
    return kq, meta, cb


# ------------------------------------------------------------- lưu / tổng hợp
def luu_csv(kq, thu_muc="du_lieu"):
    """Lưu bản chụp ra du_lieu/<MA>/*.csv (bảng nguồn cho Kiều + dự phòng khi mạng lỗi)."""
    import os
    d = os.path.join(thu_muc, kq["ma"])
    os.makedirs(d, exist_ok=True)
    for ten in ["gia", "thong_tin", "kqkd", "cdkt", "luu_chuyen", "chiso",
                "realtime", "khop_lenh", "tin_tuc"]:
        df = kq.get(ten)
        if _df_hop_le(df):
            df.to_csv(os.path.join(d, ten + ".csv"), index=False, encoding="utf-8-sig")
    return d


def _lay_toan_bo_goc(symbol, ky="year", realtime=True, khop_lenh=False, tin_tuc=True):
    """Hàm chính cho TV1 gọi: nhập mã -> trả về toàn bộ dữ liệu chuẩn."""
    ma, cb0, hop_le = kiem_tra_ma(symbol)
    rong = pd.DataFrame()
    kq = {"hop_le": hop_le, "co_du_lieu_gia": False, "ma": ma, "nganh": None, "la_ngan_hang": False,
          "gia": rong, "thong_tin": rong, "kqkd": rong, "cdkt": rong,
          "luu_chuyen": rong, "chiso": rong, "realtime": rong, "khop_lenh": rong,
          "tin_tuc": rong, "meta_bctc": {}, "canh_bao": list(cb0),
          "ngay_lay": date.today().isoformat(),
          "don_vi": {"gia": "VND/cổ phiếu", "volume": "cổ phiếu"}}
    if not hop_le:
        return kq

    gia, cb1 = lay_du_lieu_gia(ma)
    tt, cb2 = lay_thong_tin_dn(ma)
    bctc, meta, cb3 = lay_bctc(ma, ky)
    kq.update(bctc)
    cb4 = cb5 = cb6 = []
    if realtime:
        kq["realtime"], cb4 = lay_gia_realtime(ma)
    if khop_lenh:                      # mặc định tắt vì chậm + tốn lượt gọi API
        kq["khop_lenh"], cb5 = lay_khop_lenh(ma)
    if tin_tuc:
        kq["tin_tuc"], cb6 = lay_tin_tuc(ma)
    kq["gia"], kq["thong_tin"], kq["meta_bctc"] = gia, tt, meta
    kq["nganh"], kq["la_ngan_hang"] = tim_nganh(ma, tt)
    kq["canh_bao"] += cb1 + cb2 + cb3 + cb4 + cb5 + cb6
    kq["co_du_lieu_gia"] = not gia.empty      # hop_le chỉ nghĩa là MÃ hợp lệ
    if gia.empty:
        kq["canh_bao"].append("Không lấy được giá - kiểm tra kết nối mạng / API key")
    return kq


def lay_toan_bo(symbol, ky="year", realtime=True, khop_lenh=False, tin_tuc=True):
    """Hàm chính cho TV1 gọi (có bắt lỗi hết hạn mức API để Dashboard không bị tắt)."""
    try:
        return _lay_toan_bo_goc(symbol, ky, realtime, khop_lenh, tin_tuc)
    except SystemExit:
        rong = pd.DataFrame()
        return {"hop_le": False, "co_du_lieu_gia": False,
                "ma": str(symbol).upper().strip(), "nganh": None, "la_ngan_hang": False,
                "gia": rong, "thong_tin": rong, "kqkd": rong, "cdkt": rong,
                "luu_chuyen": rong, "chiso": rong, "realtime": rong, "khop_lenh": rong,
                "tin_tuc": rong, "meta_bctc": {}, "ngay_lay": date.today().isoformat(),
                "don_vi": {"gia": "VND/cổ phiếu", "volume": "cổ phiếu"},
                "canh_bao": ["Hết hạn mức lượt gọi API (20/phút với khách). "
                             "Chờ 1 phút rồi thử lại hoặc đăng ký API key miễn phí tại vnstocks.com/login"]}


def luu_danh_sach_ma(thu_muc="du_lieu"):
    """Lưu TOÀN BỘ danh sách mã cổ phiếu ra du_lieu/danh_sach_ma.csv. Trả về (đường dẫn, cảnh báo)."""
    import os
    ds, cb = lay_danh_sach_ma()
    if ds.empty:
        return None, cb
    os.makedirs(thu_muc, exist_ok=True)
    duong_dan = os.path.join(thu_muc, "danh_sach_ma.csv")
    ds.to_csv(duong_dan, index=False, encoding="utf-8-sig")
    return duong_dan, cb


def lay_nhieu_ma(ds_ma, nghi_giay=0, **kw):
    """Lấy dữ liệu NHIỀU mã: trả về dict {mã: kq}. Mỗi mã tốn ~9 lượt gọi API;
    tài khoản Cộng đồng 60 lượt/phút (~6 mã/phút) nên đặt nghi_giay=10 nếu lấy nhiều mã."""
    import time
    ket_qua = {}
    for ma in ds_ma:
        ket_qua[str(ma).upper().strip()] = lay_toan_bo(ma, **kw)
        if nghi_giay:
            time.sleep(nghi_giay)
    return ket_qua


if __name__ == "__main__":
    ds_tat_ca, _ = lay_danh_sach_ma()
    print("Tổng số mã trong danh sách:", len(ds_tat_ca))
    if not ds_tat_ca.empty:
        print("Đã lưu danh sách mã:", luu_danh_sach_ma()[0])
    for ma in ["VCB", "FPT", "ABCXYZ", ""]:
        kq = lay_toan_bo(ma)
        print("=" * 60, repr(ma))
        print("Mã hợp lệ:", kq["hop_le"], "| Có giá:", kq["co_du_lieu_gia"], "| Ngành:", kq["nganh"], "| Ngân hàng:", kq["la_ngan_hang"])
        if not kq["gia"].empty:
            print(kq["gia"].tail(3).to_string())
            print(">>> Đối chiếu: giá đóng cửa trên khớp giá thật của", ma, "chưa? (đơn vị VND)")
            print("Cột KQKD:", list(kq["kqkd"].columns)[:8])
            print("Realtime:", kq["realtime"].shape, "| Tin tức:", kq["tin_tuc"].shape)
            print("Đã lưu CSV vào:", luu_csv(kq))
        print("Meta BCTC:", kq["meta_bctc"])
        print("Cảnh báo:", kq["canh_bao"] or "Không có")