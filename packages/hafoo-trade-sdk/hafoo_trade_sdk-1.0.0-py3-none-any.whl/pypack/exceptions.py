"""
自定义异常类
"""


class SDKException(Exception):
    """SDK基础异常类"""
    pass


class ApiException(SDKException):
    """API调用异常"""
    def __init__(self, message: str, code: int = 0, request_id: str = None):
        self.message = message
        self.code = code
        self.request_id = request_id
        super().__init__(f"API Error {code}: {message} (Request ID: {request_id})")


class AuthenticationException(SDKException):
    """认证异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class ParameterException(SDKException):
    """参数异常"""
    def __init__(self, message: str = "Invalid parameters"):
        super().__init__(message)
