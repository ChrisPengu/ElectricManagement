# Thiết kế class và Database SQL Server

## 1. Mục đích tài liệu

Tài liệu này mô tả thiết kế kỹ thuật hiện tại của phần mềm quản lý dịch vụ cung cấp điện tại khu dân cư, tập trung vào:

- kiến trúc các class trong hệ thống
- vai trò của từng tầng `UI`, `DTO`, `Service`, `Repository`, `Model`
- thiết kế cơ sở dữ liệu `SQL Server`
- hướng luồng dữ liệu giữa giao diện và database

Tài liệu này nên được dùng như bản thiết kế nền để tiếp tục mở rộng CRUD, nghiệp vụ tính tiền điện, lập hóa đơn và thanh toán.

## 2. Kiến trúc tổng thể

Phần mềm hiện được tổ chức theo hướng phân tầng để tránh nhồi toàn bộ logic vào giao diện.

```text
UI (PyQt5)
   ->
DTO
   ->
Service
   ->
Repository
   ->
DatabaseManager
   ->
SQL Server
```

Ý nghĩa từng tầng:

- `UI`: hiển thị giao diện, nhận input người dùng, không nên chứa nhiều logic nghiệp vụ.
- `DTO`: đối tượng trung chuyển dữ liệu giữa UI và service.
- `Service`: xử lý nghiệp vụ, kiểm tra điều kiện, điều phối luồng xử lý.
- `Repository`: truy cập dữ liệu, đọc/ghi database.
- `Model/Entity`: biểu diễn dữ liệu miền nghiệp vụ của hệ thống.
- `DatabaseManager`: quản lý kết nối và thao tác nền với database.

## 3. Cấu trúc thư mục kỹ thuật

```text
ElectricManagement/
├─ main.py
├─ app/
│  ├─ core/
│  │  ├─ database.py
│  │  └─ settings.py
│  ├─ dto/
│  │  ├─ requests.py
│  │  ├─ responses.py
│  │  └─ mappers.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ enums.py
│  │  ├─ user.py
│  │  ├─ customer.py
│  │  ├─ tariff.py
│  │  ├─ meter_reading.py
│  │  ├─ invoice.py
│  │  ├─ payment.py
│  │  ├─ incident.py
│  │  └─ entities.py
│  ├─ repositories/
│  │  ├─ auth_repository.py
│  │  ├─ customer_repository.py
│  │  └─ tariff_repository.py
│  └─ services/
│     ├─ app_context.py
│     ├─ auth_service.py
│     ├─ billing_service.py
│     ├─ customer_service.py
│     └─ tariff_service.py
└─ ui/
   ├─ login.py
   ├─ main_window.py
   ├─ hodan.py
   ├─ congto.py
   ├─ hoadon.py
   ├─ thanhtoan.py
   ├─ suco.py
   ├─ report.py
   └─ tariff.py
```

## 4. Thiết kế class theo tầng

## 4.1. Tầng `UI`

Các class giao diện hiện có:

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

- hiển thị dữ liệu
- nhận thao tác người dùng
- gửi dữ liệu sang service thông qua DTO
- không nên thao tác SQL trực tiếp

### `App` trong `main.py`

Class `App` là lớp điều phối giao diện cấp cao:

- tạo `QStackedWidget`
- khởi tạo `LoginForm` và `MainWindow`
- khởi tạo `AppContext`
- gọi `AuthService` để xác thực người dùng

Nhiệm vụ chính:

- quản lý luồng đăng nhập/đăng xuất
- chuyển màn hình
- giữ context chung của ứng dụng

## 4.2. Tầng `Model / Entity`

Model hiện đã được tách theo từng file để dễ bảo trì, còn [app/models/entities.py](</d:/Python/Code/BTL/ElectricManagement/app/models/entities.py:1>) chỉ giữ vai trò tương thích cho các import cũ.

Các entity hiện có:

### `UserAccount`

Mô tả tài khoản quản trị hệ thống.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh duy nhất của tài khoản trong hệ thống. |
| `username` | Tên đăng nhập dùng để xác thực người dùng. |
| `password` | Mật khẩu của tài khoản, dùng trong quá trình đăng nhập. |
| `role` | Vai trò của tài khoản; phiên bản hiện tại chỉ cho phép `Admin` đăng nhập. |
| `display_name` | Tên hiển thị của người dùng trên giao diện. |
| `is_active` | Trạng thái hoạt động của tài khoản; tài khoản bị khóa sẽ không được đăng nhập. |

### `Customer`

Mô tả hộ dân hoặc đơn vị sử dụng điện. Tên class vẫn giữ là `Customer` để tương thích với code hiện tại.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh hộ/đơn vị trong cơ sở dữ liệu. |
| `customer_code` | Mã hộ/đơn vị dùng để liên kết với công tơ, hóa đơn, thanh toán và sự cố. |
| `owner_name` | Tên chủ hộ hoặc đại diện đơn vị ký hợp đồng điện. |
| `address` | Địa chỉ sử dụng điện của hộ/đơn vị. |
| `phone_number` | Số điện thoại liên hệ của hộ/đơn vị. |
| `contract_type` | Loại hợp đồng điện, ví dụ hộ gia đình hoặc nhà máy. |

### `TariffConfig`

Mô tả cấu hình biểu giá điện cho từng loại hợp đồng.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh cấu hình biểu giá. |
| `contract_type` | Loại hợp đồng áp dụng cấu hình giá điện này. |
| `fixed_fee` | Phí cố định được cộng vào hóa đơn trước khi tính tổng tiền cuối cùng. |
| `vat_percent` | Phần trăm thuế VAT áp dụng cho hóa đơn điện. |
| `peak_multiplier` | Hệ số nhân giờ cao điểm hoặc hệ số điều chỉnh giá theo loại hợp đồng. |
| `base_rate` | Đơn giá điện cơ bản dùng trong công thức tính tiền. |
| `formula_note` | Ghi chú mô tả công thức hoặc quy tắc tính giá đang áp dụng. |
| `updated_at` | Thời điểm cấu hình biểu giá được cập nhật lần cuối. |

### `MeterReading`

Mô tả dữ liệu ghi chỉ số công tơ.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh bản ghi chỉ số công tơ. |
| `customer_code` | Mã hộ/đơn vị tương ứng với công tơ được ghi chỉ số. |
| `reading_period` | Kỳ ghi điện, thường biểu diễn theo tháng hoặc chu kỳ thanh toán. |
| `new_index` | Chỉ số công tơ mới ghi nhận trong kỳ hiện tại. |
| `note` | Ghi chú bổ sung khi ghi chỉ số, ví dụ bất thường hoặc điều chỉnh. |
| `created_at` | Thời điểm bản ghi chỉ số được tạo trong hệ thống. |

### `Invoice`

Mô tả hóa đơn điện.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh hóa đơn trong cơ sở dữ liệu. |
| `invoice_code` | Mã hóa đơn dùng để tra cứu và liên kết với giao dịch thanh toán. |
| `customer_code` | Mã hộ/đơn vị được lập hóa đơn. |
| `billing_period` | Kỳ tính tiền điện của hóa đơn. |
| `amount` | Tổng số tiền phải thanh toán sau khi tính tiền điện, phí và thuế. |
| `status` | Trạng thái thanh toán của hóa đơn, ví dụ chưa thanh toán hoặc đã thanh toán. |

### `Payment`

Mô tả giao dịch thanh toán.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh giao dịch thanh toán. |
| `invoice_code` | Mã hóa đơn được thanh toán. |
| `paid_amount` | Số tiền đã được Admin ghi nhận thanh toán. |
| `payment_method` | Phương thức thanh toán, ví dụ tiền mặt hoặc chuyển khoản. |
| `paid_at` | Thời điểm phát sinh hoặc ghi nhận thanh toán. |

### `Incident`

Mô tả sự cố điện.

Thuộc tính chính:

| Thuộc tính | Mô tả |
| --- | --- |
| `id` | Khóa chính định danh sự cố điện. |
| `customer_code` | Mã hộ/đơn vị liên quan đến sự cố. |
| `incident_type` | Loại sự cố, ví dụ mất điện, chập điện hoặc hỏng công tơ. |
| `priority` | Mức độ ưu tiên xử lý sự cố. |
| `description` | Nội dung mô tả chi tiết sự cố được ghi nhận. |
| `status` | Trạng thái xử lý sự cố, ví dụ đã tiếp nhận, đang xử lý hoặc hoàn thành. |
| `received_date` | Ngày hệ thống tiếp nhận thông tin sự cố. |

### Enum dùng trong entity

- `ContractType`
  - `Hộ gia đình`
  - `Nhà máy`
- `InvoiceStatus`
  - `Chưa thanh toán`
  - `Đã thanh toán`
- `IncidentStatus`
  - `Đã tiếp nhận`
  - `Đang xử lý`
  - `Hoàn thành`

## 4.3. Tầng `DTO`

DTO được tạo ra để tách dữ liệu giao tiếp với UI khỏi entity nội bộ.

File:

- [app/dto/requests.py](</d:/Python/Code/BTL/ElectricManagement/app/dto/requests.py:1>)
- [app/dto/responses.py](</d:/Python/Code/BTL/ElectricManagement/app/dto/responses.py:1>)
- [app/dto/mappers.py](</d:/Python/Code/BTL/ElectricManagement/app/dto/mappers.py:1>)

### Request DTO

Dùng để gửi dữ liệu từ UI xuống service.

Các class hiện có:

- `LoginRequestDTO`
- `CustomerCreateDTO`
- `CustomerUpdateDTO`
- `TariffUpsertDTO`
- `MeterReadingCreateDTO`
- `InvoiceCreateDTO`
- `PaymentCreateDTO`
- `IncidentCreateDTO`

Ví dụ:

- màn hình đăng nhập tạo `LoginRequestDTO`
- màn hình biểu giá tạo `TariffUpsertDTO`

### Response DTO

Dùng để trả dữ liệu từ service lên UI.

Các class hiện có:

- `UserDTO`
- `CustomerDTO`
- `TariffConfigDTO`
- `MeterReadingDTO`
- `InvoiceDTO`
- `PaymentDTO`
- `IncidentDTO`

### Mapper

Mapper chịu trách nhiệm chuyển đổi:

- `Entity -> Response DTO`
- `Request DTO -> payload hoặc dữ liệu nghiệp vụ`

Lợi ích:

- UI không cần biết cấu trúc entity đầy đủ
- dễ thay đổi database hoặc entity mà ít ảnh hưởng giao diện
- giảm phụ thuộc giữa các tầng

## 4.4. Tầng `Repository`

Repository là lớp chuyên truy cập database.

### `AuthRepository`

Chức năng:

- tìm người dùng theo `username`

Đầu ra:

- trả `UserAccount` hoặc `None`

### `CustomerRepository`

Chức năng:

- lấy danh sách hộ/đơn vị sử dụng điện

Đầu ra:

- trả danh sách `Customer`

### `TariffRepository`

Chức năng:

- lấy cấu hình biểu giá theo `contract_type`
- lưu cấu hình biểu giá

Lưu ý:

- với `SQLite` dùng `ON CONFLICT`
- với `SQL Server` dùng `MERGE`

## 4.5. Tầng `Service`

Service là nơi xử lý nghiệp vụ.

### `AppContext`

File: [app/services/app_context.py](</d:/Python/Code/BTL/ElectricManagement/app/services/app_context.py:1>)

Vai trò:

- khởi tạo `DatabaseManager`
- khởi tạo repository
- khởi tạo service
- cung cấp một điểm truy cập chung cho toàn bộ app

### `AuthService`

Vai trò:

- nhận `LoginRequestDTO`
- kiểm tra tài khoản
- trả `UserDTO`

### `CustomerService`

Vai trò:

- lấy dữ liệu hộ/đơn vị sử dụng điện từ repository
- chuyển sang `CustomerDTO` cho UI sử dụng

### `TariffService`

Vai trò:

- lấy cấu hình biểu giá theo loại hợp đồng
- lưu cấu hình biểu giá
- nhận/trả DTO thay vì để UI thao tác entity trực tiếp

### `BillingService`

Vai trò:

- xử lý tính tiền điện
- là nền tảng cho luồng `công tơ -> hóa đơn`

Hiện tại đã có:

- tính tiền điện hộ gia đình theo bậc mẫu
- tính tiền điện nhà máy theo `base_rate * peak_multiplier`
- cộng `fixed_fee`
- cộng VAT

## 4.6. Tầng `Core`

### `DatabaseSettings`

File: [app/core/settings.py](</d:/Python/Code/BTL/ElectricManagement/app/core/settings.py:1>)

Chức năng:

- đọc cấu hình database từ biến môi trường
- chọn backend sử dụng
- giữ thông tin kết nối SQL Server

Các cấu hình chính:

- `DB_BACKEND`
- `DB_SQLSERVER_HOST`
- `DB_SQLSERVER_PORT`
- `DB_SQLSERVER_DATABASE`
- `DB_SQLSERVER_USERNAME`
- `DB_SQLSERVER_PASSWORD`
- `DB_SQLSERVER_DRIVER`
- `DB_SQLSERVER_TRUSTED_CONNECTION`

### `DatabaseManager`

File: [app/core/database.py](</d:/Python/Code/BTL/ElectricManagement/app/core/database.py:1>)

Vai trò:

- tạo kết nối đến database
- hỗ trợ backend `SQL Server`
- giữ fallback `SQLite` cho giai đoạn phát triển cục bộ
- khởi tạo schema
- seed dữ liệu mẫu
- cung cấp helper:
  - `fetch_one`
  - `fetch_all`
  - `execute`
  - `executemany`

## 5. Luồng dữ liệu chuẩn trong hệ thống

Ví dụ luồng đăng nhập:

```text
LoginForm
-> tạo LoginRequestDTO
-> AuthService.authenticate()
-> AuthRepository.get_by_username()
-> DatabaseManager
-> SQL Server
-> UserAccount
-> UserDTO
-> App / MainWindow
```

Ví dụ luồng cấu hình biểu giá:

```text
TariffForm
-> tạo TariffUpsertDTO
-> TariffService.save_config()
-> TariffRepository.save()
-> DatabaseManager.execute()
-> SQL Server
```

## 6. Thiết kế Database SQL Server

Database mục tiêu: `SQL Server`

Tên database đề xuất:

- `ElectricManagement`

## 6.1. Danh sách bảng

Các bảng hiện đang được mô hình hóa:

- `users`
- `customers`
- `tariff_configs`
- `meter_readings`
- `invoices`
- `payments`
- `incidents`

## 6.2. Thiết kế bảng chi tiết

### Bảng `users`

Mục đích:

- lưu tài khoản đăng nhập hệ thống

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `username` `NVARCHAR(50)` `UNIQUE NOT NULL`
- `password` `NVARCHAR(255)` `NOT NULL`
- `role` `NVARCHAR(50)` `NOT NULL`
- `display_name` `NVARCHAR(100)` `NOT NULL`
- `is_active` `BIT NOT NULL DEFAULT 1`

Ghi chú:

- hiện tại mật khẩu mới đang ở dạng text để demo
- sau này cần băm mật khẩu trước khi lưu

### Bảng `customers`

Mục đích:

- lưu thông tin hộ dân hoặc đơn vị sản xuất

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `customer_code` `NVARCHAR(50)` `UNIQUE NOT NULL`
- `owner_name` `NVARCHAR(100)` `NOT NULL`
- `address` `NVARCHAR(255)` `NOT NULL`
- `phone_number` `NVARCHAR(20)` `NOT NULL`
- `contract_type` `NVARCHAR(50)` `NOT NULL`

Ghi chú:

- `contract_type` hiện có 2 giá trị chính:
  - `Hộ gia đình`
  - `Nhà máy`

### Bảng `tariff_configs`

Mục đích:

- lưu cấu hình tính tiền điện theo từng loại hợp đồng

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `contract_type` `NVARCHAR(50)` `UNIQUE NOT NULL`
- `fixed_fee` `INT NOT NULL`
- `vat_percent` `FLOAT NOT NULL`
- `peak_multiplier` `FLOAT NOT NULL`
- `base_rate` `INT NOT NULL`
- `formula_note` `NVARCHAR(500)` `NOT NULL`
- `updated_at` `DATETIME2 NOT NULL`

Ý nghĩa:

- `fixed_fee`: phí cố định theo kỳ
- `vat_percent`: thuế VAT
- `peak_multiplier`: hệ số cao điểm
- `base_rate`: đơn giá cơ sở
- `formula_note`: mô tả công thức

### Bảng `meter_readings`

Mục đích:

- lưu chỉ số công tơ theo kỳ

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `customer_code` `NVARCHAR(50)` `NOT NULL`
- `reading_period` `NVARCHAR(20)` `NOT NULL`
- `new_index` `INT NOT NULL`
- `note` `NVARCHAR(500)` `NOT NULL`
- `created_at` `DATETIME2 NOT NULL DEFAULT SYSDATETIME()`

Ghi chú:

- giai đoạn sau có thể bổ sung `old_index`
- hoặc tốt hơn là lấy `old_index` từ kỳ gần nhất trước đó

### Bảng `invoices`

Mục đích:

- lưu hóa đơn điện

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `invoice_code` `NVARCHAR(50)` `UNIQUE NOT NULL`
- `customer_code` `NVARCHAR(50)` `NOT NULL`
- `billing_period` `NVARCHAR(20)` `NOT NULL`
- `amount` `INT NOT NULL`
- `status` `NVARCHAR(50)` `NOT NULL`

Ghi chú:

- có thể mở rộng thêm:
  - `consumption_kwh`
  - `vat_amount`
  - `fixed_fee`
  - `issued_at`

### Bảng `payments`

Mục đích:

- lưu lịch sử thanh toán

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `invoice_code` `NVARCHAR(50)` `NOT NULL`
- `paid_amount` `INT NOT NULL`
- `payment_method` `NVARCHAR(50)` `NOT NULL`
- `paid_at` `DATETIME2 NOT NULL DEFAULT SYSDATETIME()`

### Bảng `incidents`

Mục đích:

- lưu sự cố điện

Các cột:

- `id` `INT IDENTITY PRIMARY KEY`
- `customer_code` `NVARCHAR(50)` `NOT NULL`
- `incident_type` `NVARCHAR(100)` `NOT NULL`
- `priority` `NVARCHAR(50)` `NOT NULL`
- `description` `NVARCHAR(500)` `NOT NULL`
- `status` `NVARCHAR(50)` `NOT NULL`
- `received_date` `DATE NULL`

## 6.3. Quan hệ giữa các bảng

Quan hệ logic hiện tại:

- `customers` 1 - n `meter_readings`
- `customers` 1 - n `invoices`
- `customers` 1 - n `incidents`
- `invoices` 1 - n `payments`
- `tariff_configs` 1 - 1 theo từng `contract_type`

Quan hệ nên bổ sung ở bước sau:

- foreign key thật giữa:
  - `meter_readings.customer_code -> customers.customer_code`
  - `invoices.customer_code -> customers.customer_code`
  - `incidents.customer_code -> customers.customer_code`
  - `payments.invoice_code -> invoices.invoice_code`

## 6.4. Lý do chọn SQL Server

SQL Server phù hợp nếu phần mềm hướng tới:

- môi trường doanh nghiệp hoặc cơ quan
- dữ liệu tăng dần theo thời gian
- cần backup, restore, phân quyền và quản trị tốt
- dễ tích hợp với hệ sinh thái Windows

## 6.5. Cấu hình kết nối SQL Server

Biến môi trường hiện hỗ trợ:

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

## 7. Đề xuất mở rộng tiếp theo

## 7.1. Mở rộng class

Nên bổ sung thêm:

- `MeterReadingRepository`
- `MeterReadingService`
- `InvoiceRepository`
- `InvoiceService`
- `PaymentRepository`
- `PaymentService`
- `IncidentRepository`
- `IncidentService`

## 7.2. Mở rộng database

Nên bổ sung:

- khóa ngoại
- index cho `customer_code`, `invoice_code`, `billing_period`
- bảng `audit_logs` để lưu nhật ký thao tác

## 7.3. Mở rộng nghiệp vụ

- tạo hóa đơn tự động từ chỉ số công tơ
- cập nhật trạng thái hóa đơn khi có thanh toán
- đồng bộ loại hợp đồng với biểu giá tương ứng
- báo cáo doanh thu theo tháng và theo loại hợp đồng

## 8. Kết luận

Thiết kế hiện tại đã có nền tảng tương đối tốt để phát triển theo hướng phần mềm có cấu trúc:

- giao diện tách khỏi tầng dữ liệu
- có entity, DTO, repository, service
- đã chuẩn bị cho SQL Server
- có thể tiếp tục mở rộng CRUD thật và nghiệp vụ tính tiền điện

Tài liệu này nên được cập nhật mỗi khi:

- thêm bảng mới
- thêm service/repository mới
- đổi luồng nghiệp vụ
- chỉnh sửa công thức tính tiền điện
