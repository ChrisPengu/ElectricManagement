# Nhật ký bug và hướng xử lý

## Mục đích

File này dùng để ghi lại:

- lỗi hoặc hành vi bất thường đã quan sát được
- cách kiểm tra hoặc cách sửa đã thử
- kết quả sau mỗi lần thử
- bước tiếp theo cần làm

Nên cập nhật theo thời gian để dễ theo dõi tiến độ sửa lỗi của dự án.

## Mẫu ghi log đề xuất

```text
## YYYY-MM-DD HH:MM
- Module:
- Mô tả lỗi:
- Mức độ ảnh hưởng:
- Cách đã thử:
- Kết quả:
- Nguyên nhân nghi ngờ:
- Hướng xử lý tiếp theo:
```

## Lịch sử hiện tại

## 2026-04-21 01:55
- Module: Toàn dự án
- Mô tả lỗi: Khi đọc mã nguồn trực tiếp bằng thiết lập mặc định của PowerShell, tiếng Việt hiển thị bị lỗi ký tự.
- Mức độ ảnh hưởng: Ảnh hưởng quá trình debug và review mã nguồn, dễ hiểu nhầm là file bị hỏng.
- Cách đã thử:
  - Đọc file bằng `Get-Content` mặc định.
  - Đọc lại bằng `Get-Content -Encoding utf8`.
- Kết quả:
  - Chế độ mặc định cho ra chuỗi bị lỗi hiển thị.
  - Đọc với `UTF-8` cho ra nội dung tiếng Việt chính xác.
- Nguyên nhân nghi ngờ: Khác biệt giữa encoding file nguồn và code page của console Windows.
- Hướng xử lý tiếp theo:
  - Khi debug nên ưu tiên dùng `Get-Content -Encoding utf8`.
  - Có thể thiết lập thêm `chcp 65001` hoặc `PYTHONIOENCODING=utf-8` khi cần in chuỗi tiếng Việt ra console.

## 2026-04-21 02:03
- Module: Toàn dự án
- Mô tả lỗi: Cần xác minh xem mã nguồn có lỗi cú pháp hay không.
- Mức độ ảnh hưởng: Cao nếu có lỗi, vì sẽ chặn việc chạy ứng dụng.
- Cách đã thử:
  - Chạy kiểm tra cú pháp với `python -m py_compile` cho `main.py` và toàn bộ các file trong thư mục `ui/`.
- Kết quả:
  - Không phát hiện lỗi cú pháp ở các file đã kiểm tra.
- Nguyên nhân nghi ngờ: Không có lỗi cú pháp hiện tại; các biểu hiện lạ trước đó chủ yếu do lỗi hiển thị encoding.
- Hướng xử lý tiếp theo:
  - Chuyển sang kiểm tra hành vi chạy thực tế và các lỗi nghiệp vụ/UX.

## 2026-04-21 02:05
- Module: Khởi động ứng dụng
- Mô tả lỗi: Cần xác minh ứng dụng có khởi tạo được hay không trong môi trường kiểm tra không hiển thị cửa sổ.
- Mức độ ảnh hưởng: Cao, liên quan đến khả năng chạy ứng dụng.
- Cách đã thử:
  - Khởi tạo `QApplication` và `App()` với `QT_QPA_PLATFORM=offscreen`.
- Kết quả:
  - Ứng dụng khởi tạo thành công.
  - Khi in `windowTitle()` ra console, phát sinh `UnicodeEncodeError`.
- Nguyên nhân nghi ngờ:
  - Không phải lỗi khởi tạo GUI.
  - Lỗi nằm ở console Windows không encode được chuỗi tiếng Việt khi xuất ra màn hình.
- Hướng xử lý tiếp theo:
  - Không dùng kết quả in ra console để kết luận ứng dụng lỗi.
  - Nếu cần log tiếng Việt, cấu hình console sang UTF-8 trước khi chạy.

## 2026-04-21 02:10
- Module: Nghiệp vụ tổng thể
- Mô tả lỗi: Các phân hệ hiện mới dừng ở mức giao diện và dữ liệu mẫu, chưa có xử lý nghiệp vụ thực.
- Mức độ ảnh hưởng: Rất cao đối với khả năng sử dụng thật của phần mềm.
- Cách đã thử:
  - Rà soát mã nguồn các file trong `ui/`.
  - Tìm các điểm có `clicked.connect`, dữ liệu mẫu, bảng dữ liệu và combobox.
- Kết quả:
  - Luồng sự kiện thực tế hiện chủ yếu có ở đăng nhập, đăng xuất và chuyển trang.
  - Các module hộ dân, công tơ, hóa đơn, thanh toán, sự cố, báo cáo chưa có CRUD hoặc đồng bộ dữ liệu thật.
- Nguyên nhân nghi ngờ:
  - Dự án đang ở giai đoạn prototype GUI, chưa có tầng dữ liệu và service nghiệp vụ.
- Hướng xử lý tiếp theo:
  - Xây lớp dữ liệu dùng `SQLite`.
  - Kết nối nút thao tác với xử lý thật.
  - Đồng bộ dữ liệu giữa các module.

## 2026-04-21 02:15
- Module: Xác thực
- Mô tả lỗi: Tài khoản đăng nhập đang được hard-code trực tiếp trong `main.py`.
- Mức độ ảnh hưởng: Trung bình trong giai đoạn demo, cao nếu triển khai thực tế.
- Cách đã thử:
  - Đọc luồng `handle_login()` trong `main.py`.
- Kết quả:
  - Có duy nhất một tài khoản mẫu `admin/admin123`.
- Nguyên nhân nghi ngờ:
  - Chưa có bảng người dùng hoặc cơ chế quản lý tài khoản riêng.
- Hướng xử lý tiếp theo:
  - Chuyển thông tin tài khoản sang cơ sở dữ liệu.
  - Băm mật khẩu trước khi lưu.
  - Bổ sung phân quyền theo vai trò.

## 2026-04-21 02:45
- Module: Tầng database
- Mô tả lỗi: Ban đầu kiến trúc dữ liệu được dựng trên `SQLite`, nhưng yêu cầu thực tế của dự án là dùng `SQL Server`.
- Mức độ ảnh hưởng: Cao, vì ảnh hưởng trực tiếp đến schema, cách seed dữ liệu và chiến lược kết nối.
- Cách đã thử:
  - Rà soát lại `DatabaseManager` và các repository đang phụ thuộc `sqlite3.Row`.
  - Refactor tầng DB theo hướng đa backend, trong đó `SQL Server` là backend mục tiêu.
  - Thêm cấu hình qua biến môi trường cho SQL Server.
- Kết quả:
  - Đã thêm cấu hình `DB_BACKEND`, `DB_SQLSERVER_HOST`, `DB_SQLSERVER_DATABASE`, `DB_SQLSERVER_USERNAME`, `DB_SQLSERVER_PASSWORD`, `DB_SQLSERVER_DRIVER`.
  - Đã bổ sung schema/seed riêng cho SQL Server.
  - Đã chuyển repository sang dùng helper `fetch_one`, `fetch_all`, `execute` thay vì phụ thuộc trực tiếp `sqlite3`.
- Nguyên nhân nghi ngờ:
  - Ở giai đoạn trước chưa có thông tin rõ ràng rằng backend chính thức là SQL Server.
- Hướng xử lý tiếp theo:
  - Cài `pyodbc` và ODBC Driver for SQL Server trên máy dev.
  - Thử kết nối thật đến SQL Server và validate toàn bộ repository/service bằng dữ liệu thật.

## Việc nên ghi tiếp trong tương lai

- Lỗi CRUD từng module sau khi gắn cơ sở dữ liệu.
- Lỗi validate dữ liệu đầu vào.
- Lỗi đồng bộ dữ liệu giữa công tơ, hóa đơn và thanh toán.
- Lỗi hiệu năng khi dữ liệu bảng tăng lớn.
- Lỗi giao diện trên các độ phân giải khác nhau.
