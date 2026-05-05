# Thiết Kế Class Phần Mềm Electric Management

Tài liệu này mô tả chi tiết các class trong phần mềm quản lý dịch vụ cung cấp điện. Phần mềm được thiết kế theo hướng phân tầng, chỉ dành cho tài khoản `Admin`.

## 1. Kiến Trúc Class Tổng Quan

Luồng phụ thuộc chính:

```text
main.py
  -> ui/*
  -> app/dto/*
  -> app/services/*
  -> app/repositories/*
  -> app/core/database.py
  -> SQL Server / SQLite fallback
```

Nguyên tắc thiết kế:

- UI chỉ hiển thị giao diện và nhận thao tác.
- DTO chuẩn hóa dữ liệu truyền giữa UI và service.
- Service xử lý nghiệp vụ.
- Repository truy cập database.
- Model biểu diễn dữ liệu nghiệp vụ.
- Core quản lý cấu hình và kết nối database.

## 2. Entry Point

### `App`

File: `main.py`

Vai trò:

- Kế thừa `QStackedWidget`.
- Khởi tạo `AppContext`.
- Khởi tạo `LoginForm` và `MainWindow`.
- Điều phối đăng nhập, đăng xuất.
- Chỉ cho phép tài khoản Admin đi vào màn hình chính.

Thuộc tính chính:

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `context` | Chứa toàn bộ service/repository/database |
| `login` | Màn hình đăng nhập |
| `main_window` | Màn hình quản trị chính |

Phương thức chính:

| Phương thức | Ý nghĩa |
| --- | --- |
| `handle_login()` | Lấy username/password, gọi `AuthService.authenticate()` |
| `handle_logout()` | Xác nhận đăng xuất và quay lại màn hình login |

## 3. Tầng UI

Các class UI nằm trong thư mục `ui/`. Tất cả đều dùng PyQt5.

### `LoginForm`

File: `ui/login.py`

Vai trò:

- Hiển thị cổng đăng nhập dành riêng cho Admin.
- Cung cấp input username/password.
- Cung cấp nút đăng nhập.

Thuộc tính quan trọng:

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `input_username` | Ô nhập tên đăng nhập |
| `input_password` | Ô nhập mật khẩu |
| `btn_login` | Nút đăng nhập |

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `build_ui()` | Dựng giao diện |
| `build_metric()` | Tạo thẻ chỉ số ở panel giới thiệu |
| `build_feature_card()` | Tạo thẻ mô tả tính năng |
| `clear_inputs()` | Xóa nội dung đăng nhập sau khi vào hệ thống |

### `MainWindow`

File: `ui/main_window.py`

Vai trò:

- Là layout quản trị chính sau đăng nhập.
- Chứa sidebar menu.
- Chứa `QStackedWidget` để chuyển giữa các phân hệ.
- Hiển thị thông tin Admin hiện tại.

Thuộc tính quan trọng:

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `display_name` | Tên hiển thị của Admin |
| `role` | Vai trò, mặc định `Admin` |
| `menu_buttons` | Danh sách nút menu |
| `page_meta` | Metadata cho từng phân hệ |
| `stack` | Vùng hiển thị các màn hình con |
| `btn_logout` | Nút đăng xuất |

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `build_ui()` | Dựng giao diện quản trị |
| `build_stat_card()` | Tạo thẻ thống kê nhỏ |
| `switch_page()` | Chuyển phân hệ đang mở |
| `set_user_info()` | Cập nhật thông tin Admin sau đăng nhập |

### `HoDanForm`

File: `ui/hodan.py`

Vai trò:

- Giao diện quản lý hộ dân/đơn vị sử dụng điện.
- Hiển thị form nhập thông tin cơ bản.
- Hiển thị bảng danh sách mẫu.

Các trường UI chính:

- `txt_ma`
- `txt_ten`
- `txt_diachi`
- `txt_sdt`
- `table`

### `CongToForm`

File: `ui/congto.py`

Vai trò:

- Giao diện ghi nhận chỉ số công tơ mới theo kỳ.
- Chỉ nhập chỉ số mới; chỉ số cũ định hướng lấy từ database.
- Hiển thị lịch sử ghi chỉ số mẫu.

Các trường UI chính:

- `cbo_hodan`
- `cbo_contract`
- `date_period`
- `txt_moi`
- `txt_note`
- `table`

### `HoaDonForm`

File: `ui/hoadon.py`

Vai trò:

- Giao diện quản lý hóa đơn điện.
- Lọc theo trạng thái.
- Hiển thị bảng hóa đơn mẫu.

Các thành phần chính:

- Ô tìm kiếm hóa đơn.
- Combobox trạng thái.
- Nút tạo hóa đơn, xem chi tiết, in hóa đơn.
- Bảng danh sách hóa đơn.

### `ThanhToanForm`

File: `ui/thanhtoan.py`

Vai trò:

- Giao diện quản lý thu tiền, không phải giao diện để Admin thanh toán.
- Admin ghi nhận giao dịch thu từ hộ dân/đơn vị.
- Theo dõi công nợ và đối soát.
- Hiển thị lịch sử giao dịch thu gần đây.

Thuộc tính quan trọng:

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `receivable_data` | Dữ liệu mẫu cho hóa đơn cần thu |
| `cbo_bill` | Chọn hóa đơn cần xử lý |
| `lbl_amount` | Số tiền phải thu |
| `lbl_status` | Trạng thái công nợ |
| `lbl_method` | Kênh thu/đối soát |
| `lbl_collector` | Admin ghi nhận |
| `table` | Bảng lịch sử giao dịch |

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `build_ui()` | Dựng giao diện quản lý thu tiền |
| `build_stat_card()` | Tạo thẻ thống kê |
| `update_receivable_info()` | Cập nhật thông tin hóa đơn đang chọn |

### `SuCoForm`

File: `ui/suco.py`

Vai trò:

- Giao diện tiếp nhận và quản lý sự cố điện.
- Gắn sự cố với hộ dân/đơn vị sử dụng điện.
- Theo dõi mức ưu tiên và trạng thái xử lý.

### `ReportForm`

File: `ui/report.py`

Vai trò:

- Giao diện báo cáo tổng quan.
- Lọc theo khoảng ngày.
- Hiển thị các chỉ số tổng hợp và vùng placeholder biểu đồ.

### `TariffForm`

File: `ui/tariff.py`

Vai trò:

- Giao diện cấu hình biểu giá điện.
- Chọn loại hợp đồng.
- Điều chỉnh phí cố định, VAT, hệ số cao điểm, đơn giá cơ sở.
- Xem trước công thức tính tiền.

## 4. Tầng DTO

DTO nằm trong thư mục `app/dto/`.

### Request DTO

File: `app/dto/requests.py`

Các class:

| Class | Ý nghĩa |
| --- | --- |
| `LoginRequestDTO` | Dữ liệu đăng nhập |
| `CustomerCreateDTO` | Dữ liệu tạo hộ/đơn vị |
| `CustomerUpdateDTO` | Dữ liệu cập nhật hộ/đơn vị |
| `TariffUpsertDTO` | Dữ liệu thêm/cập nhật biểu giá |
| `MeterReadingCreateDTO` | Dữ liệu ghi chỉ số công tơ |
| `InvoiceCreateDTO` | Dữ liệu tạo hóa đơn |
| `PaymentCreateDTO` | Dữ liệu Admin ghi nhận khoản thu |
| `IncidentCreateDTO` | Dữ liệu tạo sự cố |

Ví dụ `PaymentCreateDTO`:

```python
@dataclass(slots=True)
class PaymentCreateDTO:
    receipt_code: str
    invoice_code: str
    paid_amount: int
    payment_method: str
    payer_name: str
    collected_by_user_id: int
    note: str = ""
```

Ý nghĩa: Admin không thanh toán tiền điện; Admin ghi nhận khoản thu bằng `collected_by_user_id`.

### Response DTO

File: `app/dto/responses.py`

Các class:

| Class | Ý nghĩa |
| --- | --- |
| `UserDTO` | Dữ liệu tài khoản trả về UI |
| `CustomerDTO` | Dữ liệu hộ/đơn vị |
| `TariffConfigDTO` | Dữ liệu cấu hình biểu giá |
| `MeterReadingDTO` | Dữ liệu chỉ số công tơ |
| `InvoiceDTO` | Dữ liệu hóa đơn |
| `PaymentDTO` | Dữ liệu giao dịch thu tiền |
| `IncidentDTO` | Dữ liệu sự cố |

### Mapper

File: `app/dto/mappers.py`

Vai trò:

- Chuyển `Model -> Response DTO`.
- Chuyển một số request DTO sang payload dict khi cần.

Các hàm chính:

| Hàm | Ý nghĩa |
| --- | --- |
| `to_user_dto()` | `UserAccount -> UserDTO` |
| `to_customer_dto()` | `Customer -> CustomerDTO` |
| `to_tariff_config_dto()` | `TariffConfig -> TariffConfigDTO` |
| `to_meter_reading_dto()` | `MeterReading -> MeterReadingDTO` |
| `to_payment_dto()` | `Payment -> PaymentDTO` |
| `tariff_upsert_dto_to_payload()` | `TariffUpsertDTO -> dict` |
| `meter_reading_create_dto_to_payload()` | `MeterReadingCreateDTO -> dict` |

## 5. Tầng Model

Model nằm trong `app/models/`.

### `UserAccount`

File: `app/models/user.py`

Đại diện tài khoản Admin.

```python
@dataclass(slots=True)
class UserAccount:
    id: Optional[int]
    username: str
    password: str
    role: str
    display_name: str
    is_active: bool = True
```

### `Customer`

File: `app/models/customer.py`

Đại diện hộ dân hoặc đơn vị sử dụng điện.

### `TariffConfig`

File: `app/models/tariff.py`

Đại diện cấu hình biểu giá điện.

### `MeterReading`

File: `app/models/meter_reading.py`

Đại diện bản ghi chỉ số công tơ.

### `Invoice`

File: `app/models/invoice.py`

Đại diện hóa đơn điện.

### `Payment`

File: `app/models/payment.py`

Đại diện giao dịch thu tiền do Admin ghi nhận.

Thuộc tính quan trọng:

- `receipt_code`
- `invoice_code`
- `paid_amount`
- `payment_method`
- `payer_name`
- `collected_by_user_id`
- `note`
- `paid_at`

### `Incident`

File: `app/models/incident.py`

Đại diện sự cố điện.

### Enum

File: `app/models/enums.py`

| Enum | Giá trị |
| --- | --- |
| `ContractType` | `HOUSEHOLD`, `FACTORY` |
| `InvoiceStatus` | `UNPAID`, `PAID` |
| `IncidentStatus` | `RECEIVED`, `PROCESSING`, `DONE` |

## 6. Tầng Repository

Repository nằm trong `app/repositories/`. Tầng này chịu trách nhiệm truy cập database.

### `AuthRepository`

File: `app/repositories/auth_repository.py`

Vai trò:

- Tìm user theo username.
- Trả về `UserAccount` hoặc `None`.

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `get_by_username(username)` | Lấy tài khoản theo username |

### `CustomerRepository`

File: `app/repositories/customer_repository.py`

Vai trò:

- Lấy danh sách hộ dân/đơn vị.
- Chuyển row database thành `Customer`.

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `list_all()` | Lấy toàn bộ customers |

### `TariffRepository`

File: `app/repositories/tariff_repository.py`

Vai trò:

- Lấy biểu giá theo loại hợp đồng.
- Lưu hoặc cập nhật biểu giá.
- Hỗ trợ cả SQL Server và SQLite.

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `get_by_contract_type(contract_type)` | Lấy cấu hình biểu giá |
| `save(config)` | Lưu cấu hình biểu giá |

## 7. Tầng Service

Service nằm trong `app/services/`. Tầng này xử lý nghiệp vụ.

### `AppContext`

File: `app/services/app_context.py`

Vai trò:

- Khởi tạo `DatabaseManager`.
- Khởi tạo repository.
- Khởi tạo service.
- Gom dependency để UI dùng một điểm truy cập duy nhất.

Thuộc tính:

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `database` | DatabaseManager |
| `auth_repository` | AuthRepository |
| `customer_repository` | CustomerRepository |
| `tariff_repository` | TariffRepository |
| `auth_service` | AuthService |
| `billing_service` | BillingService |
| `customer_service` | CustomerService |
| `tariff_service` | TariffService |

### `AuthService`

File: `app/services/auth_service.py`

Vai trò:

- Xác thực đăng nhập.
- Chặn tài khoản không active.
- Chặn sai mật khẩu.
- Chỉ cho role `Admin`.

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `authenticate(request)` | Trả về `UserDTO` nếu hợp lệ, ngược lại `None` |

### `CustomerService`

File: `app/services/customer_service.py`

Vai trò:

- Lấy danh sách customer từ repository.
- Chuyển sang `CustomerDTO` cho UI.

### `TariffService`

File: `app/services/tariff_service.py`

Vai trò:

- Lấy cấu hình biểu giá.
- Lưu cấu hình biểu giá.
- Chuyển `TariffUpsertDTO` thành `TariffConfig`.

### `BillingService`

File: `app/services/billing_service.py`

Vai trò:

- Tính tiền điện.
- Hộ gia đình: tính theo bậc.
- Nhà máy/đơn vị sản xuất: tính theo đơn giá cơ sở và hệ số.
- Cộng phí cố định và VAT.

Phương thức:

| Phương thức | Ý nghĩa |
| --- | --- |
| `calculate_amount()` | Tính tổng tiền hóa đơn |
| `_calculate_household_cost()` | Tính tiền điện hộ gia đình theo bậc |

## 8. Tầng Core

### `DatabaseSettings`

File: `app/core/settings.py`

Vai trò:

- Đọc cấu hình database từ biến môi trường.
- Hỗ trợ `sqlserver` và `sqlite`.

Biến môi trường chính:

```text
DB_BACKEND
DB_SQLSERVER_HOST
DB_SQLSERVER_PORT
DB_SQLSERVER_DATABASE
DB_SQLSERVER_USERNAME
DB_SQLSERVER_PASSWORD
DB_SQLSERVER_DRIVER
DB_SQLSERVER_TRUSTED_CONNECTION
DB_SQLITE_PATH
```

### `DatabaseManager`

File: `app/core/database.py`

Vai trò:

- Kết nối SQL Server hoặc SQLite.
- Tạo schema.
- Seed dữ liệu mẫu.
- Cung cấp helper đọc/ghi.

Phương thức chính:

| Phương thức | Ý nghĩa |
| --- | --- |
| `connect()` | Tạo connection theo backend |
| `session()` | Context manager đóng connection tự động |
| `fetch_one()` | Lấy một dòng |
| `fetch_all()` | Lấy nhiều dòng |
| `execute()` | Chạy một câu SQL ghi dữ liệu |
| `executemany()` | Chạy nhiều câu ghi dữ liệu |
| `initialize()` | Tạo schema và seed dữ liệu |
| `_sqlite_schema_statements()` | Schema SQLite |
| `_sqlserver_schema_statements()` | Schema SQL Server |

File SQL Server đầy đủ:

```text
app/core/sqlserver_schema.sql
```

## 9. Luồng Tương Tác Chính

### Đăng nhập

```text
LoginForm
  -> App.handle_login()
  -> LoginRequestDTO
  -> AuthService.authenticate()
  -> AuthRepository.get_by_username()
  -> DatabaseManager.fetch_one()
  -> UserAccount
  -> UserDTO
  -> MainWindow.set_user_info()
```

### Lấy danh sách hộ dân

```text
HoDanForm
  -> CustomerService.list_customers()
  -> CustomerRepository.list_all()
  -> DatabaseManager.fetch_all()
  -> Customer
  -> CustomerDTO
```

### Cấu hình biểu giá

```text
TariffForm
  -> TariffUpsertDTO
  -> TariffService.save_config()
  -> TariffConfig
  -> TariffRepository.save()
  -> DatabaseManager.execute()
  -> TariffConfigDTO
```

### Tính tiền điện

```text
MeterReading / Invoice workflow
  -> BillingService.calculate_amount()
  -> ContractType
  -> fixed_fee + energy_cost + VAT
  -> invoice.amount
```

### Admin ghi nhận khoản thu

```text
ThanhToanForm
  -> PaymentCreateDTO
  -> Payment service/repository trong bước mở rộng
  -> payments.receipt_code
  -> payments.collected_by_user_id
  -> invoices.status
  -> audit_logs
```

## 10. Quan Hệ Class Và Database

| Class | Bảng database |
| --- | --- |
| `UserAccount` | `users` |
| `Customer` | `customers` |
| `TariffConfig` | `tariff_configs` |
| `MeterReading` | `meter_readings` |
| `Invoice` | `invoices` |
| `Payment` | `payments` |
| `Incident` | `incidents` |

## 11. Ghi Chú Mở Rộng

Các class đã có nền tảng cho các nghiệp vụ chính. Những phần nên bổ sung tiếp:

- `MeterReadingRepository` và `MeterReadingService`.
- `InvoiceRepository` và `InvoiceService`.
- `PaymentRepository` và `PaymentService`.
- `IncidentRepository` và `IncidentService`.
- `AuditLogRepository` và `AuditLogService`.
- Hash mật khẩu Admin thay vì lưu text.
- Đồng bộ UI với dữ liệu SQL Server thật thay vì dữ liệu mẫu.
