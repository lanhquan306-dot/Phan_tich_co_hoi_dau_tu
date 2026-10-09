# StockInsight — Financial Analysis Module

## 1. Mục đích

Module thực hiện phân tích tài chính cơ bản cho cổ phiếu, bao gồm tính toán các chỉ số, tạo nhận định tự động và xử lý một số tình huống dữ liệu thiếu.

## 2. Các chỉ số

* Tăng trưởng doanh thu.
* Tăng trưởng lợi nhuận sau thuế (LNST).
* ROE — tỷ suất sinh lời trên vốn chủ sở hữu.
* ROA — tỷ suất sinh lời trên tổng tài sản.
* D/E — tỷ lệ nợ phải trả trên vốn chủ sở hữu.
* P/E — giá trên lợi nhuận mỗi cổ phiếu.
* P/B — giá trên giá trị sổ sách mỗi cổ phiếu.

## 3. Các file

* `financial_analysis.py`: hàm chuẩn hóa dữ liệu, tính chỉ số và tạo nhận định.
* `test_financial_analysis.py`: kiểm thử bằng dữ liệu mẫu.
* `test_edge_cases.py`: kiểm thử một số tình huống dữ liệu đặc biệt.

## 4. Cài đặt

```bash
python -m pip install pandas numpy
```

## 5. Chạy kiểm thử

```bash
python test_financial_analysis.py
python test_edge_cases.py
```

## 6. Đầu ra

Hàm `analyze_financials()` trả về:

* `indicators`: bảng chỉ số tài chính theo kỳ.
* `latest`: dữ liệu của kỳ gần nhất.
* `assessments`: danh sách nhận định tự động.

## 7. Lưu ý

Kết quả phụ thuộc vào chất lượng, đơn vị và kỳ báo cáo của dữ liệu đầu vào. Các nhận định hiện tại là quy tắc tham khảo, chưa phải khuyến nghị mua hoặc bán cổ phiếu. Module cần được kiểm thử bổ sung với dữ liệu thực tế trước khi tích hợp vào sản phẩm cuối.