# Electric Management

Ứng dụng desktop quản lý dịch vụ cung cấp điện tại khu dân cư, xây dựng bằng `Python` và `PyQt5`.

## Chức Năng Chính

- Quản lý hộ dân hoặc đơn vị sử dụng điện.
- Ghi nhận và sửa chỉ số công tơ theo kỳ.
- Lập hóa đơn tiền điện từ chỉ số công tơ và biểu giá đang cấu hình, có xem chi tiết từng thành phần tính tiền.
- Ghi nhận thanh toán, tạo biên nhận và cập nhật công nợ.
- Cấu hình biểu giá điện cho cả hộ gia đình và nhà máy, gồm phí cố định, VAT, công thức/ghi chú áp dụng, đơn giá nhà máy, hệ số cao điểm và bậc giá hộ gia đình.
- Xuất hóa đơn dạng PDF để lưu trữ hoặc in ấn.
- Thống kê doanh thu, sản lượng tiêu thụ và top hộ dân dùng điện cao nhất.
- Theo dõi sự cố điện và nhật ký thao tác Admin.

## Tài Khoản Mặc Định

```text
Username: admin
Password: admin123
Role: Admin
```

## Cấu Trúc Dự Án

```text
ElectricManagement/
├── main.py
├── app/
│   ├── core/              # settings, database, schema SQL Server
│   ├── dto/               # request/response DTO
│   ├── models/            # entity và enum nghiệp vụ
│   ├── repositories/      # truy cập MongoDB/SQL Server/SQLite
│   └── services/          # xử lý nghiệp vụ
├── ui/                    # giao diện PyQt5
└── data/                  # file xuất báo cáo/hóa đơn PDF, SQLite local
```

## Cách Chạy

Tạo hoặc chỉnh file `.env` từ mẫu:

```powershell
Copy-Item .env.example .env
```

Chạy ứng dụng:

```powershell
venv\Scripts\python.exe main.py
```

Nếu thiếu package:

```powershell
venv\Scripts\python.exe -m pip install PyQt5 pymongo pyodbc
```

## Chọn Database Backend

Ứng dụng chọn backend bằng biến `DB_BACKEND` trong `.env`.

```text
DB_BACKEND=mongodb     # dùng MongoDB
DB_BACKEND=sqlserver   # dùng SQL Server
DB_BACKEND=sqlite      # fallback local
```

Luồng code không đổi khi chuyển database:

```text
UI -> DTO -> Service -> Repository -> DatabaseManager -> Database
```

Lưu ý: đổi backend không tự migrate dữ liệu giữa MongoDB và SQL Server. Nếu cần chuyển dữ liệu thật, cần export/import riêng.

## Cấu Hình MongoDB

Ví dụ MongoDB local:

```text
DB_BACKEND=mongodb
DB_MONGODB_URI=mongodb://localhost:27017
DB_MONGODB_DATABASE=ElectricManagement
DB_MONGODB_SERVER_SELECTION_TIMEOUT_MS=20000
```

Ví dụ MongoDB Atlas:

```text
DB_BACKEND=mongodb
DB_MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_MONGODB_DATABASE=ElectricManagement
DB_MONGODB_SERVER_SELECTION_TIMEOUT_MS=20000
```

Khi chạy, ứng dụng tự tạo collection, index và seed dữ liệu mẫu nếu chưa có.

## Cấu Hình SQL Server

Ứng dụng hỗ trợ SQL Server qua `pyodbc`. Cần cài:

- SQL Server hoặc SQL Server Express.
- ODBC Driver 17 hoặc 18 for SQL Server.
- Python package `pyodbc`.

Ví dụ dùng SQL Authentication:

```text
DB_BACKEND=sqlserver
DB_SQLSERVER_HOST=localhost
DB_SQLSERVER_PORT=1433
DB_SQLSERVER_DATABASE=ElectricManagement
DB_SQLSERVER_USERNAME=sa
DB_SQLSERVER_PASSWORD=your_password
DB_SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
DB_SQLSERVER_TRUSTED_CONNECTION=0
DB_SQLSERVER_ENCRYPT=0
DB_SQLSERVER_TRUST_SERVER_CERTIFICATE=1
```

Ví dụ dùng Windows Authentication:

```text
DB_BACKEND=sqlserver
DB_SQLSERVER_HOST=localhost
DB_SQLSERVER_PORT=1433
DB_SQLSERVER_DATABASE=ElectricManagement
DB_SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
DB_SQLSERVER_TRUSTED_CONNECTION=1
DB_SQLSERVER_ENCRYPT=0
DB_SQLSERVER_TRUST_SERVER_CERTIFICATE=1
```

Nếu dùng named instance:

```text
DB_SQLSERVER_HOST=localhost\SQLEXPRESS
```

Khi `DB_BACKEND=sqlserver`, app sẽ:

- Kết nối SQL Server qua `pyodbc`.
- Tự tạo database nếu chưa có và tài khoản có quyền `CREATE DATABASE`.
- Tự tạo bảng, cột bổ sung, index và seed dữ liệu Admin/cấu hình ban đầu.

## Tạo Database SQL Server Bằng Script

Nếu muốn tạo database thủ công trong SQL Server Management Studio, copy toàn bộ nội dung file này và chạy:

```text
app/core/sqlserver_schema.sql
```

File trên được viết theo kiểu SQL cơ bản thường dùng trong bài tập: `CREATE DATABASE`, `CREATE TABLE`, khóa chính, khóa ngoại, index và `INSERT` dữ liệu mẫu. Script này không phải migration chạy lặp nhiều lần. Nếu muốn chạy lại từ đầu, hãy xóa database `ElectricManagement` trong SSMS trước hoặc đổi tên database trong file SQL.

## Cấu Hình SQLite

Dùng khi cần chạy local nhanh mà không có MongoDB/SQL Server:

```text
DB_BACKEND=sqlite
DB_SQLITE_PATH=data/electric_management.db
```

## Ghi Chú Về SQL Server Schema

Schema SQL Server dùng để copy qua SSMS nằm ở:

```text
app/core/sqlserver_schema.sql
```

`DatabaseManager` cũng có phần tự khởi tạo/migration trong code để app chạy ổn khi bật backend SQL Server. Nếu sửa bảng trong tương lai, cần cập nhật cả:

- `app/core/database.py`
- `app/core/sqlserver_schema.sql`

## Biểu Giá Điện

Màn hình `Biểu giá & hợp đồng` cho phép cập nhật:

- Phí cố định theo kỳ.
- VAT.
- Công thức/ghi chú áp dụng riêng cho từng loại hợp đồng.
- Hộ gia đình: tính tiền theo các bậc kWh, lưu trong `tariff_configs.price_tiers`.
- Nhà máy: tính tiền theo đơn giá cơ sở, hệ số giờ cao điểm và sản lượng tiêu thụ.

Công thức tổng quát:

```text
Hộ gia đình = Phí cố định + Tổng(kWh từng bậc x đơn giá bậc) + VAT
Nhà máy     = Phí cố định + (kWh x đơn giá cơ sở x hệ số cao điểm) + VAT
```

Hóa đơn tạo sau thời điểm cập nhật sẽ dùng cấu hình mới. Hóa đơn đã lập không tự tính lại.

## Hóa Đơn Và Xuất PDF

Màn hình `Quản lý hóa đơn` hỗ trợ:

- Tạo hóa đơn theo khách hàng và kỳ hóa đơn từ chỉ số công tơ đã ghi nhận.
- Xem chi tiết hóa đơn với thông tin khách hàng, loại hợp đồng, sản lượng kWh, bảng tính tiền, phí cố định, VAT, tổng thanh toán và trạng thái.
- Với hộ gia đình, chi tiết hóa đơn hiển thị breakdown theo từng bậc giá.
- Với nhà máy, chi tiết hóa đơn hiển thị đơn giá cơ sở, hệ số cao điểm và đơn giá hiệu lực.
- Xuất hóa đơn ra file PDF trong thư mục `data/` theo tên mã hóa đơn, ví dụ:

```text
data/HDON-HD001-052026-083841.pdf
```

File PDF được render từ mẫu hóa đơn trong app bằng PyQt5 `QPrinter`, không cần cài thêm thư viện xuất PDF riêng.
