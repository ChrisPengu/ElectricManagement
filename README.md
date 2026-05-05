# Xây dựng phần mềm quản lý dịch vụ cung cấp điện tại khu dân cư

## 1. Tổng quan

Đây là đồ án xây dựng ứng dụng desktop bằng `Python + PyQt5` để hỗ trợ quản lý các nghiệp vụ cung cấp điện trong khu dân cư. Ứng dụng hiện đang ở mức `prototype giao diện`, đã có bố cục màn hình tương đối rõ ràng, chia module hợp lý và mô phỏng được luồng sử dụng cơ bản.

Mục tiêu nghiệp vụ mà dự án đang hướng tới:

- Đối tượng sử dụng phần mềm chỉ là `Admin`.
- Quản lý hộ dân sử dụng điện.
- Theo dõi chỉ số công tơ điện.
- Quản lý hóa đơn điện theo kỳ.
- Theo dõi thanh toán hóa đơn.
- Ghi nhận và xử lý sự cố điện.
- Hiển thị báo cáo và thống kê tổng quan.

## 2. Công nghệ sử dụng

- Ngôn ngữ: `Python`
- Thư viện giao diện: `PyQt5`
- Kiến trúc hiện tại: giao diện nhiều màn hình bằng `QStackedWidget`
- Cơ sở dữ liệu mục tiêu: `SQL Server`

## 3. Cấu trúc dự án hiện tại

```text
ElectricManagement/
├─ main.py
├─ ui/
│  ├─ login.py
│  ├─ main_window.py
│  ├─ hodan.py
│  ├─ congto.py
│  ├─ hoadon.py
│  ├─ thanhtoan.py
│  ├─ suco.py
│  └─ report.py
└─ BUG_LOG.md
```

## 4. Những việc dự án đã làm được

### 4.1. Luồng đăng nhập và điều hướng

- Đã có màn hình đăng nhập riêng với giao diện tương đối hiện đại.
- Đã có kiểm tra tài khoản mẫu:
  - Tài khoản: `admin`
  - Mật khẩu: `admin123`
- Chỉ tài khoản có vai trò `Admin` được phép truy cập hệ thống.
- Sau khi đăng nhập thành công, hệ thống chuyển sang màn hình quản trị chính.
- Đã có chức năng đăng xuất và quay về màn hình đăng nhập.

### 4.2. Khung giao diện chính

- Đã xây dựng `sidebar menu` để chuyển qua lại giữa các phân hệ.
- Đã có `header`, `user info`, vùng nội dung và thẻ nội dung chính.
- Đã tách các màn hình thành các module riêng trong thư mục `ui/`, thuận lợi cho mở rộng.

### 4.3. Các phân hệ giao diện đã có

#### Quản lý hộ dân

- Có form nhập thông tin hộ dân gồm:
  - Mã hộ
  - Tên chủ hộ
  - Địa chỉ
  - Số điện thoại
- Có bảng hiển thị danh sách hộ dân mẫu.
- Có các nút thao tác giao diện: `Thêm`, `Sửa`, `Xóa`, `Làm mới`.

#### Quản lý công tơ

- Có màn hình cập nhật chỉ số công tơ.
- Có combobox chọn hộ dân.
- Có nhập chỉ số cũ và chỉ số mới.
- Có bảng hiển thị lịch sử chỉ số điện mẫu theo tháng.

#### Quản lý hóa đơn

- Có bảng danh sách hóa đơn điện mẫu.
- Có các nút giao diện cho các thao tác chính:
  - `Tạo hóa đơn`
  - `Xem chi tiết`
  - `In hóa đơn`

#### Quản lý thanh toán

- Có giao diện chọn hóa đơn chưa thanh toán.
- Có hiển thị số tiền và trạng thái thanh toán.
- Có nút xác nhận thanh toán.

#### Quản lý sự cố

- Có giao diện tiếp nhận sự cố điện theo hộ dân.
- Có lựa chọn loại sự cố và mô tả ngắn.
- Có bảng danh sách sự cố mẫu với các trạng thái xử lý.

#### Báo cáo - thống kê

- Có bộ lọc theo khoảng ngày.
- Có khối thống kê tổng quan:
  - Tổng số hộ dân quản lý
  - Doanh thu tháng
  - Số hóa đơn chưa thanh toán

## 5. Hiện trạng kỹ thuật

Những điểm đã ổn:

- Mã nguồn tách file theo module rõ ràng.
- Giao diện thống nhất về màu sắc và phong cách cơ bản.
- Các file nguồn đang đọc tốt theo `UTF-8`.
- Kiểm tra cú pháp bằng `py_compile` hiện không phát hiện lỗi cú pháp.
- Khởi tạo ứng dụng thành công trong chế độ kiểm tra `offscreen`.

## 6. Thiết kế class

Phần mềm hiện được tổ chức theo hướng phân tầng để tránh đưa toàn bộ logic vào giao diện.

Luồng tổng quát:

```text
UI -> DTO -> Service -> Repository -> DatabaseManager -> SQL Server
```

### 6.1. Nhóm class giao diện

Các class trong thư mục `ui/` như:

- `LoginForm`
- `MainWindow`
- `HoDanForm`
- `CongToForm`
- `HoaDonForm`
- `ThanhToanForm`
- `SuCoForm`
- `ReportForm`
- `TariffForm`

Vai trò:

- hiển thị giao diện
- nhận thao tác từ người dùng
- gửi dữ liệu xuống tầng service
- không nên chứa xử lý nghiệp vụ hoặc câu lệnh SQL

### 6.2. Nhóm class model

Các class trong `app/models/` là các domain model chính của hệ thống:

- `UserAccount`
- `Customer`
- `TariffConfig`
- `MeterReading`
- `Invoice`
- `Payment`
- `Incident`

Ngoài ra còn có các enum:

- `ContractType`
- `InvoiceStatus`
- `IncidentStatus`

Vai trò:

- biểu diễn dữ liệu nghiệp vụ
- làm nền cho repository và service
- giúp hệ thống có cấu trúc rõ ràng thay vì truyền dữ liệu tự do bằng dict

### 6.3. Nhóm class DTO

Các class trong `app/dto/` dùng để trung chuyển dữ liệu giữa UI và service.

Gồm 2 nhóm:

- request DTO:
  - `LoginRequestDTO`
  - `TariffUpsertDTO`
  - `CustomerCreateDTO`
  - `CustomerUpdateDTO`
  - `MeterReadingCreateDTO`
  - `InvoiceCreateDTO`
  - `PaymentCreateDTO`
  - `IncidentCreateDTO`
- response DTO:
  - `UserDTO`
  - `CustomerDTO`
  - `TariffConfigDTO`
  - `MeterReadingDTO`
  - `InvoiceDTO`
  - `PaymentDTO`
  - `IncidentDTO`

Vai trò:

- tách dữ liệu giao tiếp với UI khỏi entity nội bộ
- giúp dễ thay đổi cấu trúc service hoặc database mà ít ảnh hưởng giao diện
- làm rõ dữ liệu đầu vào và đầu ra của từng use case

### 6.4. Nhóm class repository

Các class repository trong `app/repositories/` chịu trách nhiệm truy cập database.

Hiện tại có:

- `AuthRepository`
- `CustomerRepository`
- `TariffRepository`

Vai trò:

- đọc/ghi dữ liệu từ database
- trả dữ liệu dạng model
- không xử lý nghiệp vụ phức tạp

### 6.5. Nhóm class service

Các class service trong `app/services/` là nơi xử lý nghiệp vụ chính.

Hiện tại có:

- `AuthService`
- `CustomerService`
- `TariffService`
- `BillingService`
- `AppContext`

Vai trò:

- kiểm tra điều kiện nghiệp vụ
- điều phối repository
- chuyển đổi giữa model và DTO
- cung cấp logic dùng lại cho nhiều màn hình

Ví dụ:

- `AuthService` xử lý đăng nhập
- `TariffService` xử lý cấu hình biểu giá
- `BillingService` tính tiền điện
- `AppContext` khởi tạo và gom toàn bộ dependency của ứng dụng

### 6.6. Nhóm class core

Trong `app/core/` hiện có:

- `DatabaseSettings`
- `DatabaseManager`

Vai trò:

- đọc cấu hình database từ môi trường
- khởi tạo kết nối dữ liệu
- hỗ trợ `SQL Server` là backend mục tiêu
- giữ fallback `SQLite` cho môi trường local khi chưa cài driver SQL Server

### 6.7. Lý do thiết kế như vậy

Thiết kế này giúp dự án:

- dễ mở rộng khi số lượng chức năng tăng lên
- giảm việc phụ thuộc trực tiếp giữa giao diện và database
- dễ bảo trì hơn khi cần đổi công thức tính tiền điện hoặc đổi backend database
- dễ thêm kiểm thử cho từng tầng riêng biệt

Nếu cần chi tiết kỹ thuật đầy đủ hơn về từng class và từng bảng database, xem thêm file `DESIGN_README.md`.

## 7. Hiện trạng kỹ thuật

Những điểm còn hạn chế:

- Dữ liệu hiện tại chủ yếu là `dữ liệu mẫu`, chưa gắn với cơ sở dữ liệu thật.
- Các nút như `Thêm`, `Sửa`, `Xóa`, `Tạo hóa đơn`, `Xác nhận thanh toán` mới chủ yếu là phần giao diện, chưa có xử lý nghiệp vụ đầy đủ.
- Luồng dữ liệu giữa các phân hệ chưa liên kết chặt:
  - Hộ dân chưa tự động đồng bộ sang công tơ, hóa đơn, sự cố.
  - Công tơ chưa sinh sản lượng điện và tiền điện tự động.
  - Thanh toán chưa cập nhật ngược lại trạng thái hóa đơn.
- Tài khoản đăng nhập đang được hard-code trong mã nguồn.
- Chưa có tìm kiếm, lọc, sắp xếp, phân trang, xuất file hoặc sao lưu dữ liệu.
- Chưa có kiểm tra dữ liệu đầu vào như:
  - Bắt buộc nhập trường
  - Định dạng số điện thoại
  - Chỉ số công tơ mới phải lớn hơn hoặc bằng chỉ số cũ
  - Không cho trùng mã hộ hoặc mã hóa đơn

## 8. Đề xuất cải thiện GUI

### 6.1. Cải thiện tổng thể trải nghiệm

- Thống nhất bộ nhận diện giao diện:
  - dùng chung màu chính, màu cảnh báo, màu thành công, màu lỗi
  - dùng icon cho từng menu
  - thêm trạng thái hover, disabled, selected rõ ràng hơn
- Thay các bảng tĩnh bằng giao diện có:
  - ô tìm kiếm
  - bộ lọc nhanh
  - sắp xếp theo cột
  - chọn dòng để tự đổ dữ liệu lên form
- Thêm `empty state` khi chưa có dữ liệu thay vì bảng trống.
- Thêm `message box` hoặc `toast` sau các hành động như thêm, sửa, xóa, thanh toán.
- Dùng màu trạng thái trực quan:
  - `Đã thanh toán`: xanh lá
  - `Chưa thanh toán`: đỏ hoặc cam
  - `Đang xử lý`: vàng
  - `Hoàn thành`: xanh dương hoặc xanh lá

### 6.2. Đề xuất cho từng màn hình

#### Màn hình đăng nhập

- Thêm nút hiện/ẩn mật khẩu.
- Hỗ trợ nhấn `Enter` để đăng nhập.
- Thêm thông báo nếu bỏ trống tài khoản hoặc mật khẩu.
- Có thể bổ sung logo, tên nhóm, phiên bản phần mềm.

#### Màn hình hộ dân

- Khi chọn một dòng trong bảng, tự động đưa dữ liệu lên form để sửa.
- Bổ sung ô tìm kiếm theo mã hộ, tên chủ hộ, số điện thoại.
- Cảnh báo trước khi xóa hộ dân.
- Gắn nhãn trạng thái hộ đang hoạt động hoặc ngừng sử dụng điện.

#### Màn hình công tơ

- Tự tính sản lượng tiêu thụ = chỉ số mới - chỉ số cũ.
- Chặn nhập sai nếu chỉ số mới nhỏ hơn chỉ số cũ.
- Hiển thị lịch sử theo tháng và theo hộ dân.
- Có nút xem biểu đồ tiêu thụ điện.

#### Màn hình hóa đơn

- Hiển thị rõ:
  - sản lượng điện
  - đơn giá
  - thuế/phụ phí
  - tổng tiền
- Thêm lọc theo kỳ hóa đơn và trạng thái thanh toán.
- Có xem chi tiết hóa đơn ở popup hoặc panel riêng.

#### Màn hình thanh toán

- Khi chọn hóa đơn, cập nhật số tiền và trạng thái theo dữ liệu thật.
- Hỗ trợ nhiều phương thức thanh toán:
  - tiền mặt
  - chuyển khoản
  - ví điện tử
- In hoặc xuất biên lai sau khi thanh toán thành công.

#### Màn hình sự cố

- Thêm mức độ ưu tiên: thấp, trung bình, cao, khẩn cấp.
- Thêm ngày tiếp nhận, người xử lý, thời gian hoàn thành.
- Hỗ trợ lọc sự cố theo trạng thái và loại sự cố.
- Có timeline xử lý để tiện theo dõi.

#### Màn hình báo cáo

- Dùng biểu đồ cột, tròn hoặc đường thay cho các ô thống kê tĩnh.
- Thêm báo cáo:
  - doanh thu theo tháng
  - tỷ lệ thanh toán đúng hạn
  - hộ dân tiêu thụ điện cao
  - số lượng sự cố theo khu vực
- Hỗ trợ xuất `Excel`, `PDF`.

## 9. Đề xuất cải thiện chức năng và nghiệp vụ

### 7.1. Bổ sung tầng dữ liệu

- Tạo và hoàn thiện cơ sở dữ liệu `SQL Server`.
- Tách lớp xử lý dữ liệu riêng:
  - model
  - repository/DAO
  - service nghiệp vụ
- Không để dữ liệu mẫu cố định trong file giao diện.

### 7.2. Liên kết các phân hệ với nhau

- Khi thêm hộ dân mới, dữ liệu phải xuất hiện ở các combobox liên quan.
- Khi cập nhật công tơ, hệ thống phải:
  - tính sản lượng điện
  - làm cơ sở tạo hóa đơn
- Khi thanh toán xong, hóa đơn phải đổi trạng thái ngay.
- Khi phát sinh sự cố, có thể gắn với hộ dân và khu vực cụ thể để báo cáo.

### 7.3. Kiểm tra dữ liệu đầu vào

- Kiểm tra trùng mã.
- Kiểm tra số điện thoại hợp lệ.
- Kiểm tra các trường bắt buộc.
- Kiểm tra định dạng số tiền, chỉ số điện và ngày tháng.

### 7.4. Quản lý tài khoản Admin

- Tách bảng người dùng riêng nhưng chỉ phục vụ tài khoản quản trị.
- Mã hóa mật khẩu thay vì hard-code.
- Không xây dựng tài khoản hoặc cổng tự phục vụ cho hộ dân.
- Ghi nhận lịch sử thao tác theo tài khoản Admin.

### 7.5. Nhật ký và bảo trì hệ thống

- Ghi log thao tác người dùng.
- Lưu lịch sử chỉnh sửa dữ liệu quan trọng.
- Có sao lưu và phục hồi dữ liệu.
- Bổ sung bộ test cho các quy tắc nghiệp vụ chính.

## 10. Thứ tự ưu tiên nên làm tiếp

Nếu phát triển tiếp theo hướng thực tế, nên ưu tiên theo thứ tự:

1. Tạo cơ sở dữ liệu và CRUD thật cho `hộ dân`.
2. Đồng bộ dữ liệu hộ dân sang `công tơ`, `sự cố`, `hóa đơn`.
3. Xây luồng nghiệp vụ `công tơ -> hóa đơn -> thanh toán`.
4. Bổ sung kiểm tra dữ liệu đầu vào và thông báo lỗi.
5. Hoàn thiện báo cáo, tìm kiếm, lọc và xuất file.
6. Bổ sung lịch sử thao tác và bảo mật tài khoản Admin.

## 11. Cách chạy dự án

Tại thư mục gốc dự án:

```powershell
venv\Scripts\python.exe main.py
```

### Cấu hình database

Kiến trúc hiện tại đã được chuẩn bị để hỗ trợ `SQL Server` làm backend chính.

Các biến môi trường hỗ trợ:

```text
DB_BACKEND=sqlserver
DB_SQLSERVER_HOST=localhost
DB_SQLSERVER_PORT=1433
DB_SQLSERVER_DATABASE=ElectricManagement
DB_SQLSERVER_USERNAME=sa
DB_SQLSERVER_PASSWORD=your_password
DB_SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
DB_SQLSERVER_TRUSTED_CONNECTION=0
```

Trong quá trình phát triển cục bộ, nếu máy chưa cài `pyodbc` hoặc chưa có ODBC driver cho SQL Server, có thể dùng tạm:

```text
DB_BACKEND=sqlite
```

Ghi chú:

- `SQL Server` là database mục tiêu của dự án.
- `SQLite` hiện chỉ giữ vai trò fallback để tránh làm vỡ luồng chạy local trước khi môi trường SQL Server hoàn chỉnh.

Thông tin đăng nhập mẫu:

```text
Username: admin
Password: admin123
```

## 12. Ghi chú

- Dự án hiện phù hợp để trình bày ý tưởng, demo giao diện và tiếp tục phát triển thành bản hoàn chỉnh.
- File `BUG_LOG.md` dùng để ghi lại lỗi, nguyên nhân nghi ngờ, cách đã thử sửa và kết quả theo mốc thời gian.
