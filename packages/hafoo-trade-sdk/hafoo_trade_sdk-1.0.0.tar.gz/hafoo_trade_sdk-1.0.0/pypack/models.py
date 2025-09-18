"""
数据模型定义
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class TradeSide(Enum):
    """交易方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """订单模型"""
    order_id: str
    code: str
    quantity: float
    price: float
    side: TradeSide
    status: OrderStatus
    created_at: str
    filled_quantity: Optional[float] = 0.0
    filled_price: Optional[float] = 0.0
    remark: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """从字典创建Order对象"""
        return cls(
            order_id=data['order_id'],
            code=data['code'],
            quantity=data['quantity'],
            price=data['price'],
            side=TradeSide(data['side']),
            status=OrderStatus(data['status']),
            created_at=data['created_at'],
            filled_quantity=data.get('filled_quantity', 0.0),
            filled_price=data.get('filled_price', 0.0),
            remark=data.get('remark')
        )


@dataclass
class OrderResponse:
    """订单API响应模型"""
    success: bool
    data: Optional[Order] = None
    error: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class OrderListResponse:
    """订单列表API响应模型"""
    success: bool
    data: Optional[List[Order]] = None
    error: Optional[str] = None
    total: int = 0
    page: int = 1
    page_size: int = 20
    request_id: Optional[str] = None
