"""
SDK客户端，提供API调用接口
"""
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import (
    Order, OrderResponse, OrderListResponse,
    TradeSide, OrderStatus
)
from .exceptions import (
    ApiException, AuthenticationException,
    ParameterException
)


class OrderClient:
    """订单服务客户端"""
    
    def __init__(
        self, 
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.example.com/v1",
        timeout: int = 30,
        debug: bool = False
    ):
        """
        初始化客户端
        
        :param api_key: API密钥
        :param api_secret: API密钥密钥
        :param base_url: API基础URL
        :param timeout: 请求超时时间(秒)
        :param debug: 是否开启调试模式
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"Order-SDK-Python/1.0.0"
        })
    
    def _get_headers(self) -> Dict[str, str]:
        """生成请求头，包含认证信息"""
        # 实际应用中可能需要更复杂的签名机制
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "X-Timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理API响应"""
        if self.debug:
            print(f"API Response: {response.text}")
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ApiException(
                f"Invalid JSON response: {response.text}",
                code=response.status_code,
                request_id=response.headers.get("X-Request-ID")
            )
        
        # 处理HTTP错误状态码
        if not response.ok:
            error_msg = data.get("error", "Unknown error")
            error_code = data.get("code", response.status_code)
            raise ApiException(
                error_msg,
                code=error_code,
                request_id=data.get("request_id") or response.headers.get("X-Request-ID")
            )
            
        return data
    
    def _request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """通用请求方法"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._get_headers()
        
        if self.debug:
            print(f"API Request: {method} {url}, params={params}, data={data}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(f"Request failed: {str(e)}")
        
        return self._handle_response(response)
    
    def place_order(
        self,
        code: str,
        quantity: float,
        price: float,
        side: TradeSide,
        remark: Optional[str] = None
    ) -> OrderResponse:
        """
        下单
        
        :param code: 标的代码
        :param quantity: 数量
        :param price: 价格
        :param side: 交易方向
        :param remark: 备注
        :return: 订单响应
        """
        # 参数验证
        if quantity <= 0:
            raise ParameterException("Quantity must be positive")
        if price <= 0:
            raise ParameterException("Price must be positive")
        if not code or not code.strip():
            raise ParameterException("Code is required")
        
        data = {
            "code": code,
            "quantity": quantity,
            "price": price,
            "side": side.value
        }
        
        if remark:
            data["remark"] = remark
        
        response_data = self._request("POST", "/orders", data=data)
        
        if response_data.get("success") and response_data.get("data"):
            return OrderResponse(
                success=True,
                data=Order.from_dict(response_data["data"]),
                request_id=response_data.get("request_id")
            )
        else:
            return OrderResponse(
                success=False,
                error=response_data.get("error"),
                request_id=response_data.get("request_id")
            )
    
    def get_order(self, order_id: str) -> OrderResponse:
        """
        获取订单详情
        
        :param order_id: 订单ID
        :return: 订单响应
        """
        if not order_id:
            raise ParameterException("Order ID is required")
        
        response_data = self._request("GET", f"/orders/{order_id}")
        
        if response_data.get("success") and response_data.get("data"):
            return OrderResponse(
                success=True,
                data=Order.from_dict(response_data["data"]),
                request_id=response_data.get("request_id")
            )
        else:
            return OrderResponse(
                success=False,
                error=response_data.get("error"),
                request_id=response_data.get("request_id")
            )
    
    def cancel_order(self, order_id: str) -> OrderResponse:
        """
        取消订单
        
        :param order_id: 订单ID
        :return: 订单响应
        """
        if not order_id:
            raise ParameterException("Order ID is required")
        
        response_data = self._request("DELETE", f"/orders/{order_id}")
        
        if response_data.get("success") and response_data.get("data"):
            return OrderResponse(
                success=True,
                data=Order.from_dict(response_data["data"]),
                request_id=response_data.get("request_id")
            )
        else:
            return OrderResponse(
                success=False,
                error=response_data.get("error"),
                request_id=response_data.get("request_id")
            )
    
    def list_orders(
        self,
        code: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        side: Optional[TradeSide] = None,
        page: int = 1,
        page_size: int = 20
    ) -> OrderListResponse:
        """
        列出订单
        
        :param code: 标的代码(可选)
        :param status: 订单状态(可选)
        :param side: 交易方向(可选)
        :param page: 页码
        :param page_size: 每页数量
        :return: 订单列表响应
        """
        params = {
            "page": page,
            "page_size": page_size
        }
        
        if code:
            params["code"] = code
        if status:
            params["status"] = status.value
        if side:
            params["side"] = side.value
        
        response_data = self._request("GET", "/orders", params=params)
        
        if response_data.get("success") and response_data.get("data"):
            orders = [Order.from_dict(item) for item in response_data["data"]]
            return OrderListResponse(
                success=True,
                data=orders,
                total=response_data.get("total", 0),
                page=response_data.get("page", 1),
                page_size=response_data.get("page_size", 20),
                request_id=response_data.get("request_id")
            )
        else:
            return OrderListResponse(
                success=False,
                error=response_data.get("error"),
                request_id=response_data.get("request_id")
            )
