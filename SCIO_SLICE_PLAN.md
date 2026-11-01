# SCIO Slice Technical Specification & Implementation Plan
## Brief B: Team, Roles, Permissions, Assets, and Screens

**Candidate**: Nguyen Ha Anh Kiem  
**Position Applied**: Senior Fullstack Developer  
**Company Target**: OptiSigns  
**Target Document**: Technical Interview Board & Engineering Leadership  
**Delivery Scope**: Brief B (Team, Roles, Permissions, Assets, Screens)  
**Timeline**: 6 Sprints (~12 Weeks Production Delivery) / 4-Week Fast-Track MVP  

---

## 0. EXECUTIVE BRIEF: TRẢ LỜI 4 CÂU HỎI CỐT TỬ CỦA ĐỀ BÀI (DE_BAI.md)

Đề bài Phần 2 yêu cầu: *"Khi đọc xong tài liệu, chúng tôi phải nắm rõ: Bạn sẽ xây dựng những gì? Theo thứ tự nào? Mất bao lâu? Và LÝ DO TẠI SAO với mỗi quyết định?"*. Dưới đây là câu trả lời trực diện:

### CÂU HỎI 1: BẠN SẼ XÂY DỰNG NHỮNG GÌ? (WHAT)
Chúng tôi xây dựng **hệ thống phân quyền đa người dùng và quản lý tài nguyên số (Multi-Tenant Access Control & Digital Signage Resource Management)** hoàn chỉnh từ con số 0, gồm 5 phân hệ tương thích 100% với nền tảng SCIO thực tế:
1. **Unified Workspace Hub (`/app/s/account-members`)**: Mô hình Account $\to$ Workspaces (Teams). Cho phép tạo Team kèm hạn ngạch màn hình (`Number of screens limit`), mời thành viên (`Invite User Modal`), đổi vai trò, xóa/gỡ thành viên (`Remove Member`), và chuyển đổi không gian làm việc.
2. **Dynamic RBAC & Roles Engine**: 4 System Roles cố định (`Owner`, `Admin`, `User`, `Read Only`), loại trừ 2 vai trò `Content Proposal/Approval` theo đề bài; kèm công cụ tạo **Custom Role** với ma trận quyền chuẩn xác 4 module (`Screens`, `Files/Assets`, `Playlists`, `Schedules`) $\times$ 4 hành động (`Create`, `Edit`, `Delete`, `Tags`).
3. **Phân quyền Thư mục Phân tầng (Folder-level ACL)**: Cấu trúc thư mục lồng nhau không giới hạn độ sâu cho cả Assets và Screens. Phân quyền chia sẻ theo Team hoặc User với **2 cấp độ quyền chuẩn hóa: `Edit` và `View`**. Hỗ trợ cơ chế ghi đè quyền (*Explicit Override - Node gần nhất thắng*) kèm hộp thoại cảnh báo nâng quyền (*Elevated Privilege Warning Modal*).
4. **Quản lý Tệp Tin Tải Lên (Assets Subsystem)**: Upload trực tiếp lên Cloud Object Storage thông qua Pre-signed URL an toàn; tìm kiếm, xem trước, thay thế, nhân bản, quản lý tab `Shared with me` và thực thi kiểm soát hạn ngạch dung lượng (Storage Quota).
5. **Quản lý Hạm đội Màn hình (Screens Subsystem)**: Ghép nối thiết bị vật lý bằng giao thức mã 6 ký tự (`6-digit pairing code`), sắp xếp màn hình vào thư mục, gán nội dung hiển thị, và kiểm soát nghiêm ngặt hạn ngạch màn hình của từng Team bằng cơ chế khóa nguyên tử (Atomic Lock).

---

### CÂU HỎI 2: THEO THỨ TỰ TRIỂN KHAI NHƯ THẾ NÀO? (SEQUENCE)
Chúng tôi triển khai theo **6 Sprints tuần tự có chủ đích kiến trúc (Architectural Dependency-First Order)**:
* **Sprint 1 (Nền tảng Đa người thuê - Multi-Tenant Foundation)**: Xây dựng Account, Team, User, Token xác thực và cơ chế cô lập dữ liệu.
* **Sprint 2 (Bộ máy Phân quyền Động - Dynamic RBAC & Custom Roles)**: Xây dựng các Decorator/Guard cấp hệ thống và ma trận quyền Custom Role.
* **Sprint 3 (Cây Thư mục & Phân quyền ACL - Hierarchical Folder Engine)**: Xây dựng cấu trúc phân cấp dùng chung cho cả Assets và Screens bằng PostgreSQL `ltree`, cơ chế kế thừa quyền và chia sẻ `Edit`/`View`.
* **Sprint 4 (Phân hệ Tài sản - Assets & Direct Cloud Upload Pipeline)**: Triển khai upload S3 pre-signed URL, kiểm soát quota dung lượng và áp dụng Folder ACL.
* **Sprint 5 (Phân hệ Màn hình - Screen Fleet & 6-Digit Pairing)**: Triển khai pairing code màn hình, gán thư mục, gán nội dung và chốt hạn ngạch `screen_limit`.
* **Sprint 6 (Kiểm toán, Chống Race Condition & Tối ưu Hiệu năng)**: Bổ sung Security Audit Log, cơ chế khóa chống race condition và bộ kiểm thử tự động toàn diện.

---

### CÂU HỎI 3: MẤT BAO NHIÊU THỜI GIAN HOÀN THÀNH? (TIMELINE / ESTIMATION)
* **Quy mô đội ngũ chuẩn**: 1 Senior Backend Engineer, 1 Senior Frontend Engineer, 0.5 QA/Automation Engineer.
* **Thời gian giao hàng chuẩn Production (Full Enterprise Scope)**: **6 Sprints = 12 Tuần = 110 Person-Days**.
* **Phương án bàn giao thần tốc (Fast-Track MVP)**: **4 Tuần** (1 Senior Fullstack Engineer tập trung: cố định 4 System Roles, upload tệp cơ bản, pairing màn hình 6 ký tự và phân quyền thư mục 1 cấp).

---

### CÂU HỎI 4: VỚI MỖI QUYẾT ĐỊNH TRÊN: LÝ DO TẠI SAO? (WHY & JUSTIFICATION)
1. **Tại sao chọn NestJS (TypeScript) + PostgreSQL 16 (`ltree`) + Next.js 15?**
   - *NestJS*: Hỗ trợ kiến trúc module doanh nghiệp chuẩn mực; native DI, Execution Guards (`@RequirePermissions()`) và Interceptors giúp kiểm soát quyền 100% tại gateway trước khi chạm vào business logic.
   - *PostgreSQL `ltree`*: Thay vì dùng truy vấn đệ quy (Recursive CTE) tốn kém $O(N)$ hoặc $N+1$ query, `ltree` cùng GiST Index cho phép kiểm tra quyền kế thừa của toàn bộ cây thư mục chỉ trong **1 câu lệnh SQL duy nhất với độ trễ < 5ms**.
   - *Next.js 15 (App Router)*: Tận dụng React Server Components để render giao diện bảo mật tức thì, không bị nhấp nháy quyền (permission flash), kết hợp TanStack Query và Tailwind CSS/shadcn-ui cho bảng quản trị mật độ cao.
2. **Tại sao triển khai Team & Roles trước Assets & Screens?**
   - *Nguyên tắc cốt lõi*: Không thể gán quyền hay kiểm tra hạn ngạch trên một tài nguyên (Screen/Asset) nếu hạ tầng Tenant context và Permission Guard chưa tồn tại. Triển khai ngược lại sẽ dẫn đến việc phải viết lại toàn bộ API khi thêm bảo mật.
3. **Tại sao gộp Cây Thư mục (Folders) thành 1 engine duy nhất cho cả Asset và Screen?**
   - Thư mục màn hình và thư mục tài sản có bản chất đại số giống hệt nhau (Path traversal, Share ACL, Inheritance). Xây dựng một bảng `folders` phân loại bằng `folder_type` giúp tái sử dụng 100% logic phân quyền và tối ưu kiểm thử.
4. **Tại sao dùng Pre-signed URL cho Asset Upload?**
   - Không đưa file video/ảnh dung lượng lớn đi qua Backend API Gateway, giúp backend không bị nghẽn băng thông, không tốn RAM và tải trực tiếp từ trình duyệt lên S3/R2 với chi phí thấp nhất.
5. **Tại sao dùng Atomic Database Lock khi ghép nối màn hình?**
   - Giải quyết triệt để rủi ro Race Condition khi nhiều admin cùng nhập mã ghép nối đồng thời vào phút chót, ngăn chặn hoàn toàn việc vượt quá hạn ngạch `screen_limit` của Team.

---

## 1. KHẢO SÁT THỰC NGHIỆM TRÊN HỆ THỐNG LIVE OPTISIGNS (`app.optisigns.com`)

Tài liệu này được xây dựng dựa trên khảo sát thực tế chuyên sâu bằng tự động hóa Playwright trên tài khoản `nguyenhaanhkiem@gmail.com`. Toàn bộ 24 ảnh chụp bằng chứng được lưu trữ tại [`docs/screenshots/deep_audit/`](docs/screenshots/deep_audit/):

```
+--------------------------------------------------------------------------------------------------+
| OPTISIGNS LIVE PRODUCT ARCHITECTURE MAPPING                                                      |
+--------------------------------------------------------------------------------------------------+
| 1. Account Members UI  : https://app.optisigns.com/app/s/account-members                        |
|    - Single-pane view  : Gộp chung Teams và Members, thay thế các route rời cũ đang di trú.     |
| 2. Add Team Modal      : Trường 'Name *', 'Number of screens limit' ('X screens are available')  |
| 3. Manage Roles Modal  : 4 System Roles + Custom Role Matrix (4 Modules x 4 Actions)             |
| 4. Screen Pairing      : Modal 'SCREEN - Add Screen' với 'Pair code *' (6 ký tự)                 |
| 5. Folder Security ACL : Cấu hình 'Security: Select users and teams' với 2 quyền: Edit & View     |
+--------------------------------------------------------------------------------------------------+
```

### Các phát hiện thực tế định hình bản kế hoạch:
1. **Kiến trúc Di trú Giao diện (Experience Migration)**: Các URL cũ như `/app/account/accountMembers`, `/app/s/roles`, `/app/s/teams` đang hiển thị thông báo di trú. SCIO đã quy tụ toàn bộ quyền lực quản trị nhóm về giao diện hợp nhất **`/app/s/account-members`**. Kế hoạch này được thiết kế tương thích trực tiếp với UI thế hệ mới.
2. **Ma trận Quyền Custom Role Thực tế**:
   - 4 System Roles: `Owner` (Đỏ), `Admin` (Xanh lá đậm), `User` (Xanh ngọc), `Read Only` (Xám).
   - Ma trận Custom Role gồm 4 module: `Screens`, `Files/Assets`, `Playlists`, `Schedules` với 4 switch: `Create`, `Edit`, `Delete`, `Tags` (Schedules không có Tags).
3. **Quyền Thư mục Chuẩn hóa (Folder ACL)**:
   - Hệ thống thực tế của OptiSigns sử dụng 2 cấp độ quyền cốt lõi: **`Edit`** (toàn quyền) và **`View`** (chỉ đọc). Quyền quản trị tổng thể thuộc về Team Owner/Admin.
4. **4 Thao tác Chuẩn trên Thành viên (Row Actions)**:
   - `Reset Password` (Lock icon)
   - `Change Role` (Pencil icon)
   - `Remove Member from Team` (User-X icon)
   - `Delete User from Account` (Trash icon)

---

## 2. KIẾN TRÚC DỮ LIỆU QUAN HỆ (POSTGRESQL DDL BLUEPRINT)

```sql
-- Kích hoạt extension ltree phục vụ truy vấn phân cấp cây thư mục
CREATE EXTENSION IF NOT EXISTS ltree;

-- 1. Bảng Khách hàng Doanh nghiệp (Tenant Account)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plan_tier VARCHAR(50) NOT NULL DEFAULT 'standard',
    storage_limit_bytes BIGINT NOT NULL DEFAULT 10737418240, -- 10 GB
    total_screen_licenses INT NOT NULL DEFAULT 10,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Bảng Không gian Làm việc (Teams / Workspaces)
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    screen_limit INT NOT NULL DEFAULT 0,
    purpose TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_team_screen_limit CHECK (screen_limit >= 0)
);
CREATE INDEX idx_teams_account_id ON teams(account_id);

-- 3. Bảng Người dùng & Vai trò
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE, -- NULL cho system roles
    name VARCHAR(100) NOT NULL,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_role_account_name UNIQUE(account_id, name)
);

-- 4. Bảng Ma trận Quyền (Custom Role Matrix theo đúng SCIO Live)
CREATE TABLE role_module_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    module VARCHAR(50) NOT NULL, -- 'screens', 'assets', 'playlists', 'schedules'
    can_create BOOLEAN NOT NULL DEFAULT FALSE,
    can_edit BOOLEAN NOT NULL DEFAULT FALSE,
    can_delete BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_tags BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_role_module UNIQUE(role_id, module)
);

-- 5. Bảng Thành viên Nhóm
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    invitation_status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'pending', 'active'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_team_user UNIQUE (team_id, user_id)
);
CREATE INDEX idx_team_members_lookup ON team_members(user_id, team_id);

-- 6. Bảng Cây Thư mục Phân cấp (Dùng chung cho Assets & Screens)
CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    folder_type VARCHAR(20) NOT NULL, -- 'asset' | 'screen'
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    path ltree NOT NULL, -- Materialized path: e.g. 'root.marketing.q4_promotions'
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_folders_path_gist ON folders USING GIST (path);
CREATE INDEX idx_folders_team_type ON folders(team_id, folder_type);

-- 7. Bảng Phân quyền Thư mục (Folder Security ACL)
CREATE TABLE folder_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    folder_id UUID NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission_level VARCHAR(20) NOT NULL, -- 'edit' | 'view'
    is_elevated_override BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_share_target CHECK (team_id IS NOT NULL OR user_id IS NOT NULL)
);

-- 8. Bảng Tài nguyên Tệp Tin (Assets)
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'image', 'video', 'document'
    mime_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_key VARCHAR(500) NOT NULL,
    thumbnail_key VARCHAR(500),
    tags TEXT[] DEFAULT '{}',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_assets_team_folder ON assets(team_id, folder_id) WHERE is_deleted = FALSE;

-- 9. Bảng Hạm đội Màn hình (Screens)
CREATE TABLE screens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    pairing_code VARCHAR(12) UNIQUE,
    pairing_status VARCHAR(30) NOT NULL DEFAULT 'unpaired', -- 'unpaired', 'paired', 'offline'
    paired_at TIMESTAMPTZ,
    last_ping_at TIMESTAMPTZ,
    assigned_content_type VARCHAR(50), -- 'asset', 'playlist', 'schedule'
    assigned_content_id UUID,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_screens_team_status ON screens(team_id, pairing_status);

-- 10. Bảng Nhật ký Kiểm toán Bảo mật (Audit Logs)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    actor_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- 'member.role_changed', 'screen.paired', 'folder.shared'
    target_resource VARCHAR(100) NOT NULL,
    target_id UUID,
    payload JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_account_created ON audit_logs(account_id, created_at DESC);
```

---

## 3. CƠ CHẾ PHÂN QUYỀN VÀ TRUY VẤN TỐC ĐỘ CAO (PERMISSION ENGINE)

### 3.1 Luồng Quyết định Phân quyền Ngắn mạch (Short-Circuit Waterfall)
```
[User Yêu cầu Hành vi trên Tài nguyên: e.g. Edit Asset trong Folder X]
                          │
                          ▼
1. User có phải là Account Owner hoặc Super Admin? ──► [ALLOW] (Bỏ qua toàn bộ)
                          │ Không
                          ▼
2. User có thuộc Team sở hữu tài nguyên không? ─────► [DENY] (Nếu không thuộc Team)
                          │ Đã xác thực thành viên Team
                          ▼
3. Role chung của User có quyền 'can_edit' trên Module không?
   (Kiểm tra bảng role_module_permissions)
                          │
          ┌───────────────┴───────────────┐
       Có quyền                        Không có quyền
          │                               │
          ▼                               ▼
4. Tài nguyên có nằm trong Folder không?  User có được gán quyền 'edit' trực tiếp
   - Không: ─────────────► [ALLOW]        tại Folder này (Explicit Override)?
   - Có: Kiểm tra Folder ACL:             - Có:  ────────► [ALLOW] (Cảnh báo đã duyệt)
     + Quyền kế thừa từ cha: [ALLOW]      - Không: ──────► [DENY]
     + Bị restrict tại node: [DENY]
```

### 3.2 Tối ưu Truy vấn Kế thừa Thư mục bằng `ltree` (< 5ms)
```sql
-- Lấy quyền có hiệu lực cao nhất trên cây thư mục cho một Asset cụ thể
SELECT fs.permission_level, fs.is_elevated_override
FROM folders f
JOIN folder_shares fs ON fs.folder_id = f.id
WHERE f.path @> (SELECT path FROM folders WHERE id = :targetFolderId)
  AND (fs.user_id = :userId OR fs.team_id = :userTeamId)
ORDER BY nlevel(f.path) DESC
LIMIT 1;
```
*Giải thích kiến trúc*: Toán tử `@>` của `ltree` tận dụng chỉ mục GiST, tìm kiếm toàn bộ tổ tiên của node trong cây phân cấp mà không cần bất kỳ vòng lặp hay đệ quy nào.

---

## 4. CHI TIẾT LỘ TRÌNH TRIỂN KHAI & ƯỚC LƯỢNG (ROADMAP & ESTIMATION)

### 4.1 Bảng Ước lượng 6 Sprints (12 Tuần · 110 Person-Days)

| Sprint | Hạng mục & Gói công việc cụ thể | Backend (Days) | Frontend (Days) | QA/Review (Days) | Tổng Person-Days |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Sprint 1** | **Multi-Tenant Foundation & Workspaces**<br>• DDL Account, Team, User, Team Member.<br>• Token JWT, Session Context Middleware, Team Switcher.<br>• Logic cấp phát & quản lý hạn ngạch `screen_limit` theo Team. | 8 | 7 | 3 | **18** |
| **Sprint 2** | **Dynamic RBAC & Roles Engine**<br>• Seed 4 System Roles + CRUD Custom Role.<br>• Ma trận quyền 4 Module x 4 Action switches.<br>• NestJS `@RequirePermissions()` Guard & Decorators. | 9 | 8 | 4 | **21** |
| **Sprint 3** | **Hierarchical Folder Engine (Assets & Screens)**<br>• PostgreSQL `ltree` schema & API cây thư mục lồng nhau.<br>• Hộp thoại Security/ACL: Phân quyền theo Team/User với `Edit`/`View`.<br>• Xử lý Explicit Override và Warning Modal khi nâng quyền. | 8 | 8 | 4 | **20** |
| **Sprint 4** | **Assets Management & Pre-signed S3 Pipeline**<br>• Upload trực tiếp Cloud Storage qua Pre-signed URL.<br>• Kiểm tra Storage Quota trước khi ký URL upload.<br>• Grid View / List View, tab `Shared with me`, tìm kiếm, thay thế tệp. | 7 | 8 | 3 | **18** |
| **Sprint 5** | **Screens Management & Pairing Subsystem**<br>• Giao thức mã ghép nối 6 ký tự (`Pair code *`).<br>• Quản trị thư mục màn hình, gán nội dung (Asset/Playlist/Schedule).<br>• Khóa nguyên tử (Atomic Lock) chống race condition vượt `screen_limit`. | 7 | 7 | 3 | **17** |
| **Sprint 6** | **Audit Logging, Quota Hardening & E2E Verification**<br>• Đường ống ghi nhật ký kiểm toán bất đồng bộ (Async Audit Trail).<br>• Bảo vệ Owner duy nhất (Last-Owner Protection Invariant).<br>• Bộ kiểm thử tự động E2E phân quyền và kiểm toán hiệu năng tải. | 6 | 5 | 5 | **16** |
| **TỔNG** | **Giao hàng Hoàn chỉnh Production (6 Sprints · 12 Tuần)** | **45** | **43** | **22** | **110 Days** |

---

## 5. PHƯƠNG ÁN BÀN GIAO THẦN TỐC: 4-WEEK FAST-TRACK MVP

Trong trường hợp cần một bản Demo chạy thực tế để nghiệm thu sớm với 1 Senior Fullstack Developer:
* **Tuần 1**: DDL Cơ sở dữ liệu cốt lõi + 4 System Roles cố định (tạm hoãn Custom Roles).
* **Tuần 2**: Quản lý Thành viên Team (`Invite User Modal`) + Upload tệp qua S3 Pre-signed URL.
* **Tuần 3**: Ghép nối Màn hình với mã 6 ký tự + Khóa hạn ngạch `screen_limit` theo Team.
* **Tuần 4**: Cây thư mục 2 cấp + Chia sẻ thư mục cơ bản (`Edit`/`View`) + Demo E2E hoàn chỉnh.

---

## 6. BỘ CÂU HỎI BẢO VỆ KIẾN TRÚC TRONG VÒNG PHỎNG VẤN (INTERVIEW DEFENSE FAQ)

### Q1: Tại sao không dùng Keycloak, Casbin hay OpenFGA cho bài toán này?
* **Trả lời**: Keycloak quá nặng nề và phức tạp cho multi-tenancy SaaS. Casbin hoặc OpenFGA đưa thêm network hops và dependency vào cụm vận hành. Mô hình Dual-Layer RBAC + PostgreSQL `ltree` giải quyết 100% bài toán với tốc độ dưới 5ms, bảo đảm ACID trực tiếp với dữ liệu nghiệp vụ mà không cần thêm bất kỳ cụm server phụ trợ nào.

### Q2: Cơ chế khóa chống Race Condition khi gán màn hình hoạt động như thế nào?
* **Trả lời**: Chúng tôi thực thi điều kiện cập nhật nguyên tử ở tầng cơ sở dữ liệu:
  ```sql
  UPDATE teams 
  SET current_screens = current_screens + 1 
  WHERE id = :teamId AND current_screens < screen_limit;
  ```
  Nếu số bản ghi bị ảnh hưởng = 0 (tức là đã chạm trần `screen_limit`), giao dịch bị hủy bỏ ngay lập tức và trả về mã lỗi 409 Quota Exceeded trước khi tạo bản ghi màn hình mới.

### Q3: Làm sao ngăn chặn việc một Account bị "mất chủ sở hữu" (Orphaned Account)?
* **Trả lời**: Hệ thống áp dụng quy tắc bất biến (Domain Invariant): Mỗi Account luôn phải có **ít nhất 1 thành viên mang vai trò `Owner`**. Quản trị viên `Owner` không thể tự rời nhóm, tự hạ quyền hoặc tự xóa tài khoản của mình cho đến khi quyền sở hữu được chuyển giao thành công cho một thành viên khác.

