"""
订单服务SDK
提供简单易用的接口来访问订单服务API
"""

from .client import OrderClient
from .exceptions import SDKException, ApiException, AuthenticationException
from .models import Order, OrderStatus, TradeSide

__version__ = "1.0.0"
__author__ = "KuBoy"
__all__ = [
    "OrderClient", 
    "SDKException", 
    "ApiException", 
    "AuthenticationException",
    "Order",
    "OrderStatus",
    "TradeSide"
]
