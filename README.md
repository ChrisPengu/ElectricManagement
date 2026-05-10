# Electric Management

Phần mềm desktop quản lý dịch vụ cung cấp điện tại khu dân cư, xây dựng bằng `Python` và `PyQt5`. Ứng dụng được định hướng chỉ dành cho `Admin`; hộ dân hoặc đơn vị sử dụng điện không đăng nhập vào phần mềm.

## Mục Tiêu

- Quản lý hồ sơ hộ dân và đơn vị sử dụng điện.
- Ghi nhận chỉ số công tơ theo kỳ.
- Cấu hình biểu giá điện theo loại hợp đồng.
- Lập và quản lý hóa đơn điện.
- Admin ghi nhận giao dịch thu tiền, đối soát công nợ và cập nhật trạng thái hóa đơn.
- Tiếp nhận, phân loại và theo dõi sự cố điện.
- Xem báo cáo tổng quan doanh thu, hóa đơn, công nợ và vận hành.

## Tài Khoản Admin

Tài khoản mẫu khi chạy local:

```text
Username: admin
Password: admin123
Role: Admin
```

`AuthService` chỉ cho phép tài khoản có vai trò `Admin` truy cập hệ thống.

## Cấu Trúc Dự Án

```text
ElectricManagement/
├── main.py
├── app/
│   ├── core/
│   │   ├── database.py
│   │   ├── settings.py
│   │   └── sqlserver_schema.sql
│   ├── dto/
│   ├── models/
│   ├── repositories/
│   └── services/
├── ui/
│   ├── login.py
│   ├── main_window.py
│   ├── hodan.py
│   ├── congto.py
│   ├── hoadon.py
│   ├── thanhtoan.py
│   ├── suco.py
│   ├── report.py
│   └── tariff.py
└── data/
```

## Các Màn Hình Chính

- `Đăng nhập`: cổng đăng nhập dành riêng cho Admin.
- `Quản lý hộ dân`: quản lý hộ dân hoặc đơn vị sử dụng điện.
- `Quản lý công tơ`: ghi nhận chỉ số công tơ mới theo kỳ.
- `Quản lý hóa đơn`: quản lý hóa đơn điện, kỳ hóa đơn và trạng thái công nợ.
- `Quản lý thu tiền`: Admin ghi nhận khoản thu, lập mã biên nhận, đối soát và cập nhật hóa đơn.
- `Quản lý sự cố`: tiếp nhận và theo dõi sự cố điện.
- `Báo cáo - thống kê`: tổng quan doanh thu, hóa đơn, công nợ.
- `Biểu giá & hợp đồng`: cấu hình biểu giá và loại hợp đồng.

## Cấu Hình Hợp Đồng Trong Biểu Giá

Màn hình `Biểu giá & hợp đồng` dùng để cấu hình các tham số tính tiền điện theo từng loại hợp đồng. Hiện hệ thống hỗ trợ 2 nhóm hợp đồng chính:

- `Hộ gia đình`: áp dụng cho hộ dân, căn hộ, nhà ở trong khu dân cư.
- `Nhà máy`: áp dụng cho xưởng sản xuất, doanh nghiệp hoặc đơn vị dùng điện với sản lượng lớn.

Các tham số cấu hình gồm:

- `Loại hợp đồng`: chọn nhóm hợp đồng cần xem hoặc cập nhật cấu hình.
- `Phí cố định / kỳ`: khoản phí cộng cố định vào mỗi hóa đơn của kỳ đó, ví dụ phí duy trì dịch vụ hoặc phí quản lý.
- `VAT`: phần trăm thuế giá trị gia tăng áp dụng sau khi tính tiền điện và phí cố định.
- `Hệ số giờ cao điểm`: hệ số nhân dùng cho nhóm `Nhà máy`, phản ánh chi phí điện cao hơn trong khung giờ cao điểm.
- `Đơn giá nhà máy`: đơn giá cơ sở theo kWh cho nhóm hợp đồng `Nhà máy`.

Với hợp đồng `Hộ gia đình`, hệ thống tính tiền theo mô hình bậc thang. Sản lượng tiêu thụ được lấy từ chênh lệch giữa chỉ số công tơ kỳ hiện tại và kỳ trước, sau đó chia vào các bậc giá minh họa:

```text
0 - 50 kWh       x 1.806 VND/kWh
51 - 100 kWh     x 1.866 VND/kWh
101 - 200 kWh    x 2.167 VND/kWh
201 - 300 kWh    x 2.729 VND/kWh
301 - 400 kWh    x 3.050 VND/kWh
Trên 400 kWh     x 3.151 VND/kWh
```

Công thức tổng quát:

```text
Tiền hộ gia đình = Phí cố định + Tổng tiền theo bậc kWh + VAT
```

Với hợp đồng `Nhà máy`, hệ thống dùng đơn giá cơ sở và hệ số cao điểm:

```text
Tiền nhà máy = Phí cố định + (Sản lượng kWh x Đơn giá cơ sở x Hệ số cao điểm) + VAT
```

Khi Admin bấm `Áp dụng cấu hình`, dữ liệu được lưu vào bảng/collection `tariff_configs`. Các màn hình lập hóa đơn sẽ đọc cấu hình này để tính số tiền hóa đơn. Vì vậy, nếu thay đổi phí cố định, VAT, đơn giá hoặc hệ số cao điểm, các hóa đơn tạo sau thời điểm cập nhật sẽ sử dụng cấu hình mới.

Phần `Xem trước công thức` và `Khung giá minh họa` trong giao diện giúp Admin kiểm tra nhanh logic tính tiền trước khi lưu cấu hình. Đây là khu vực hỗ trợ đối chiếu nghiệp vụ, tránh nhập sai tham số làm ảnh hưởng đến hóa đơn.

## Backend

Backend của ứng dụng nằm trong thư mục `app/` và được tổ chức theo hướng tách lớp nghiệp vụ rõ ràng. Giao diện PyQt5 không thao tác trực tiếp với database, mà đi qua DTO, service và repository.

Luồng xử lý tổng quát:

```text
UI -> DTO Request -> Service -> Repository -> DatabaseManager -> Database
Database -> Repository -> Model -> DTO Response -> UI
```

Các thư mục chính:

- `app/core/`: cấu hình và quản lý kết nối database.
- `app/models/`: định nghĩa entity nghiệp vụ như `Customer`, `Invoice`, `Payment`, `MeterReading`, `Incident`, `TariffConfig`, `UserAccount`.
- `app/dto/`: định nghĩa dữ liệu truyền vào/ra giữa UI và service.
- `app/repositories/`: lớp truy cập dữ liệu, chịu trách nhiệm đọc/ghi database.
- `app/services/`: lớp nghiệp vụ, kiểm tra điều kiện, tính toán và điều phối repository.

### Core

`app/core/settings.py` đọc cấu hình từ biến môi trường hoặc file `.env`. Các cấu hình chính gồm:

```text
DB_BACKEND=mongodb
DB_MONGODB_URI=mongodb://localhost:27017
DB_MONGODB_DATABASE=ElectricManagement
```

`app/core/database.py` chứa `DatabaseManager`, là điểm tập trung quản lý database. Lớp này có nhiệm vụ:

- Chọn backend theo `DB_BACKEND`.
- Kết nối MongoDB, SQLite hoặc SQL Server.
- Tạo index/schema cần thiết.
- Seed dữ liệu mẫu.
- Cung cấp collection MongoDB hoặc các hàm SQL helper cho repository.
- Sinh mã tăng dần cho MongoDB thông qua collection `counters`.

Hiện tại ứng dụng đang ưu tiên MongoDB. SQLite và SQL Server vẫn được giữ lại để hỗ trợ phát triển hoặc chuyển đổi backend.

### Models

Models là các dataclass mô tả dữ liệu nghiệp vụ nội bộ. Ví dụ:

- `Customer`: thông tin hộ dân hoặc đơn vị dùng điện.
- `MeterReading`: chỉ số công tơ theo kỳ.
- `Invoice`: hóa đơn tiền điện.
- `Payment`: giao dịch thu tiền.
- `Incident`: sự cố kỹ thuật.
- `TariffConfig`: cấu hình biểu giá hợp đồng.
- `UserAccount`: tài khoản Admin.

Models không phụ thuộc UI. Repository trả dữ liệu về dạng model, sau đó service chuyển sang DTO để UI sử dụng.

### DTO

DTO nằm trong `app/dto/` và chia làm 2 nhóm:

- `requests.py`: dữ liệu UI gửi vào service, ví dụ `LoginRequestDTO`, `CustomerCreateDTO`, `MeterReadingCreateDTO`, `PaymentCreateDTO`.
- `responses.py`: dữ liệu service trả về UI, ví dụ `CustomerDTO`, `InvoiceDTO`, `PaymentDTO`, `IncidentDTO`.

`mappers.py` chứa các hàm chuyển đổi từ model sang DTO. Cách này giúp UI không phải biết chi tiết cấu trúc model hoặc database.

### Repositories

Repository là lớp làm việc trực tiếp với database. Mỗi nhóm nghiệp vụ có repository riêng:

- `CustomerRepository`: quản lý collection/bảng `customers`.
- `MeterReadingRepository`: quản lý `meter_readings`.
- `InvoiceRepository`: quản lý `invoices`.
- `PaymentRepository`: quản lý `payments`.
- `IncidentRepository`: quản lý `incidents`.
- `TariffRepository`: quản lý `tariff_configs`.
- `AuthRepository`: lấy thông tin tài khoản đăng nhập.
- `AuditLogRepository`: ghi nhật ký thao tác Admin.

Repository có xử lý riêng cho từng backend. Với MongoDB, repository dùng collection API như `find_one`, `find`, `insert_one`, `update_one`. Với SQL/SQLite, repository dùng các helper `fetch_one`, `fetch_all`, `execute` của `DatabaseManager`.

### Services

Service là nơi xử lý nghiệp vụ chính. UI gọi service thay vì gọi repository trực tiếp.

Một số service quan trọng:

- `AuthService`: kiểm tra đăng nhập, hash mật khẩu và quyền Admin.
- `CustomerService`: kiểm tra dữ liệu hộ dân trước khi thêm/sửa/xóa.
- `MeterReadingService`: ghi chỉ số công tơ, không cho nhập âm, không cho trùng kỳ, không cho chỉ số kỳ mới thấp hơn tháng trước.
- `InvoiceService`: lập hóa đơn từ chỉ số công tơ, tính sản lượng tiêu thụ, lấy biểu giá và sinh mã hóa đơn.
- `PaymentService`: ghi nhận giao dịch thu, tạo biên nhận và chuyển hóa đơn sang `Đã thanh toán`.
- `IncidentService`: tiếp nhận sự cố, cập nhật trạng thái và mô tả xử lý.
- `TariffService`: lưu và đọc cấu hình biểu giá hợp đồng.
- `ReportService`: tổng hợp số liệu báo cáo, doanh thu, công nợ và dữ liệu biểu đồ.

Ví dụ luồng lập hóa đơn:

```text
HoaDonForm
-> InvoiceService.create_invoice_for_customer()
-> CustomerRepository.get_by_code()
-> MeterReadingRepository.get_for_customer_period()
-> MeterReadingRepository.get_previous_for_reading()
-> TariffRepository.get_by_contract_type()
-> BillingService.calculate_amount()
-> InvoiceRepository.create()
```

Ví dụ luồng ghi nhận thu tiền:

```text
ThanhToanForm
-> PaymentService.create_payment()
-> InvoiceRepository.get_by_code()
-> PaymentRepository.create()
-> InvoiceRepository.mark_paid()
-> AuditLogService.record()
```

### AppContext

`app/services/app_context.py` là nơi khởi tạo toàn bộ backend khi ứng dụng mở:

- Tạo `DatabaseManager`.
- Gọi `database.initialize()`.
- Tạo repository.
- Tạo service.
- Chia sẻ các service cho UI.

Nhờ `AppContext`, các màn hình chỉ cần nhận `context` và gọi service phù hợp, ví dụ:

```python
self.context.customer_service.list_customers()
self.context.invoice_service.create_invoice_for_customer(...)
self.context.payment_service.create_payment(...)
```

### Audit Log

Các thao tác quan trọng của Admin được ghi vào `audit_logs`, ví dụ:

- Thêm hộ dân.
- Ghi chỉ số công tơ.
- Tạo hóa đơn.
- Ghi nhận thanh toán.
- Cập nhật sự cố.

Audit log giúp truy vết người thao tác, loại hành động, đối tượng bị tác động và mô tả nghiệp vụ.

## Kiến Trúc

Luồng tổng quát:

```text
UI -> DTO -> Service -> Repository -> DatabaseManager -> SQL Server
```

Vai trò từng tầng:

- `ui/`: hiển thị giao diện PyQt5 và nhận thao tác Admin.
- `app/dto/`: dữ liệu vào/ra giữa UI và service.
- `app/models/`: entity nghiệp vụ.
- `app/repositories/`: truy cập database.
- `app/services/`: xử lý nghiệp vụ.
- `app/core/database.py`: kết nối, tạo schema và seed dữ liệu.

## Database

Database mục tiêu là `SQL Server`. SQLite chỉ dùng fallback khi chạy local hoặc khi máy chưa có SQL Server/ODBC driver.

Các bảng chính:

- `users`: tài khoản quản trị, chỉ vai trò `Admin`.
- `customers`: hộ dân hoặc đơn vị sử dụng điện.
- `tariff_configs`: cấu hình biểu giá.
- `meter_readings`: chỉ số công tơ, có Admin ghi nhận.
- `invoices`: hóa đơn điện, có Admin lập hóa đơn.
- `payments`: giao dịch thu tiền, có Admin ghi nhận khoản thu.
- `incidents`: sự cố điện, có Admin tiếp nhận.
- `audit_logs`: nhật ký thao tác quản trị.

File SQL Server đầy đủ nằm tại:

```text
app/core/sqlserver_schema.sql
```

Một phần schema quan trọng:

```sql
CREATE TABLE payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    receipt_code NVARCHAR(50) UNIQUE NOT NULL,
    invoice_code NVARCHAR(50) NOT NULL,
    paid_amount INT NOT NULL,
    payment_method NVARCHAR(50) NOT NULL,
    payer_name NVARCHAR(100) NOT NULL DEFAULT '',
    collected_by_user_id INT NOT NULL,
    note NVARCHAR(500) NOT NULL DEFAULT '',
    paid_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_payments_invoices FOREIGN KEY (invoice_code) REFERENCES invoices(invoice_code),
    CONSTRAINT FK_payments_users FOREIGN KEY (collected_by_user_id) REFERENCES users(id)
);
```

Thiết kế này thể hiện đúng nghiệp vụ: Admin không phải người thanh toán tiền điện; Admin là người ghi nhận khoản thu và đối soát công nợ.

## Cấu Hình SQL Server

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

Nếu dùng Windows Authentication:

```text
DB_SQLSERVER_TRUSTED_CONNECTION=1
```

Khi chưa có SQL Server local, có thể dùng:

```text
DB_BACKEND=sqlite
```

## Cách Chạy

Tại thư mục gốc dự án:

```powershell
venv\Scripts\python.exe main.py
```

Không nên chạy trực tiếp các file trong `ui/` trừ khi đang debug riêng từng màn hình.

## Tài Liệu Chi Tiết

Thiết kế class, quan hệ bảng và mã SQL Server đầy đủ được mô tả trong:

```text
DESIGN_README.md
```
