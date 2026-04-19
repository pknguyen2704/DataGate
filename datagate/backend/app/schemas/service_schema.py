from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# =============================================================================
# 1. BASE SCHEMAS (Định nghĩa các trường chung)
# =============================================================================

class ServiceBase(BaseModel):
    """
    Schema cơ sở chứa các thông tin cốt lõi của một kết nối Service.
    """
    name: str = Field(..., min_length=1, max_length=100, example="Trino_Production", description="Tên gợi nhớ của dịch vụ")
    description: Optional[str] = Field(None, max_length=500, example="Kết nối tới Data Lakehouse", description="Mô tả chi tiết")
    service_type: str = Field(..., example="trino", description="Loại database: trino, postgres, iceberg...")
    connection_url: str = Field(..., min_length=1, example="trino://user@localhost:8080", description="Chuỗi kết nối (Connection String)")
    integrated_tables: List[str] = Field(default_factory=list, description="Danh sách các bảng đã đăng ký giám sát")

# =============================================================================
# 2. INPUT SCHEMAS (Dữ liệu gửi lên từ Client)
# =============================================================================

class ServiceCreate(ServiceBase):
    """Dữ liệu yêu cầu khi tạo mới một Service."""
    pass

class ServiceUpdate(BaseModel):
    """Dữ liệu yêu cầu khi cập nhật thông tin Service (tất cả các trường là tùy chọn)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    service_type: Optional[str] = None
    connection_url: Optional[str] = None
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động (True=Hiện hữu, False=Xoá mềm)")
    integrated_tables: Optional[List[str]] = None

# =============================================================================
# 3. OUTPUT SCHEMAS (Dữ liệu trả về cho Client)
# =============================================================================

class ServiceOwnerOut(BaseModel):
    """Thông tin rút gọn về người sở hữu Service."""
    id: int
    username: str
    full_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ServiceOut(ServiceBase):
    """Dữ liệu đầy đủ của Service dùng để hiển thị trên giao diện Dashboard/Explore."""
    id: int = Field(..., description="ID định danh duy nhất trong hệ thống")
    is_active: bool = Field(..., description="Trạng thái hoạt động (Quản lý Xoá mềm)")
    owner: Optional[ServiceOwnerOut] = Field(None, description="Thông tin người tạo service")
    created_at: datetime = Field(..., description="Thời điểm tạo kết nối")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")

    model_config = ConfigDict(from_attributes=True)

# =============================================================================
# 4. SPECIAL RESPONSE SCHEMAS
# =============================================================================

class ConnectionTestResult(BaseModel):
    """Kết quả phản hồi khi kiểm tra thử kết nối DB."""
    status: str = Field(..., example="success", description="Trạng thái kết nối (success/error)")
    message: str = Field(..., description="Thông báo chi tiết lỗi hoặc thành công")
    schemas: List[str] = Field(default_factory=list, description="Danh sách các database/schema tìm thấy")
    tables: List[str] = Field(default_factory=list, description="Danh sách các bảng tìm thấy (nếu có)")

class ServiceExplore(BaseModel):
    """Thông tin tổng hợp cho trang Explore."""
    service: ServiceOut
    schemas: List[str]
    tables: List[str]

