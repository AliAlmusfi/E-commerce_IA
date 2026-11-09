from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetProductStockByIdRequest(_message.Message):
    __slots__ = ("user_id", "product_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    product_id: int
    def __init__(self, user_id: _Optional[int] = ..., product_id: _Optional[int] = ...) -> None: ...

class GetProductStockByIdResponse(_message.Message):
    __slots__ = ("product_id", "stock")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    stock: int
    def __init__(self, product_id: _Optional[int] = ..., stock: _Optional[int] = ...) -> None: ...

class ReserveProductRequest(_message.Message):
    __slots__ = ("user_id", "product_id", "quantity", "idempotency_key")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    product_id: int
    quantity: int
    idempotency_key: str
    def __init__(self, user_id: _Optional[int] = ..., product_id: _Optional[int] = ..., quantity: _Optional[int] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class ReserveProductResponse(_message.Message):
    __slots__ = ("success", "remaining_stock", "msg")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    REMAINING_STOCK_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    success: bool
    remaining_stock: int
    msg: str
    def __init__(self, success: _Optional[bool] = ..., remaining_stock: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class ReserveOrderItem(_message.Message):
    __slots__ = ("product_id", "quantity")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    quantity: int
    def __init__(self, product_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ReserveOrderRequest(_message.Message):
    __slots__ = ("user_id", "products", "idempotency_key")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    products: _containers.RepeatedCompositeFieldContainer[ReserveOrderItem]
    idempotency_key: str
    def __init__(self, user_id: _Optional[int] = ..., products: _Optional[_Iterable[_Union[ReserveOrderItem, _Mapping]]] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class ReserveOrderResponse(_message.Message):
    __slots__ = ("success", "msg", "failed_product_ids")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    FAILED_PRODUCT_IDS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    msg: str
    failed_product_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, success: _Optional[bool] = ..., msg: _Optional[str] = ..., failed_product_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class UpdateProductQuantityRequest(_message.Message):
    __slots__ = ("user_id", "product_id", "amount", "idempotency_key")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    product_id: int
    amount: int
    idempotency_key: str
    def __init__(self, user_id: _Optional[int] = ..., product_id: _Optional[int] = ..., amount: _Optional[int] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class UpdateProductQuantityResponse(_message.Message):
    __slots__ = ("success", "msg")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    success: bool
    msg: str
    def __init__(self, success: _Optional[bool] = ..., msg: _Optional[str] = ...) -> None: ...

class CreateProductStorageRequest(_message.Message):
    __slots__ = ("user_id", "product_id", "stock", "idempotency_key")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    product_id: int
    stock: int
    idempotency_key: str
    def __init__(self, user_id: _Optional[int] = ..., product_id: _Optional[int] = ..., stock: _Optional[int] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class CreateProductStorageResponse(_message.Message):
    __slots__ = ("product_id", "stock")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    stock: int
    def __init__(self, product_id: _Optional[int] = ..., stock: _Optional[int] = ...) -> None: ...
