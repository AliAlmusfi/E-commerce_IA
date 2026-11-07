import grpc
from db import db_session
from db_models import Request, RPCServiceEnum


class RequestBuilder:
    def __init__(self):
        self.user_id:int = None
        self.rpc_service:RPCServiceEnum = None
        self.request_payload:dict = {}
        self.response_status:grpc.StatusCode = None
        self.response_payload:dict = {}
        self.duration_ms:int = None
    def reset(self)->None:
        self.user_id = None
        self.rpc_service = None
        self.request_payload = {}
        self.response_status = None
        self.response_payload = {}
        self.duration_ms = None
    
    def set_user_id(self, user_id: int)->None:
        self.user_id = user_id

    def set_rpc_service(self, rpc_service: RPCServiceEnum)->None:
        self.rpc_service = rpc_service

    def set_request_payload(self, request_payload: dict)->None:
        self.request_payload = request_payload

    def set_response_status(self, response_status: grpc.StatusCode)->None:
        self.response_status = response_status

    def set_response_payload(self, response_payload: dict)->None:
        self.response_payload = response_payload

    def set_duration_ms(self, duration_ms: int)->None:
        self.duration_ms = duration_ms

    def get_result(self)->Request:
        if self.user_id is None:
            return None
        if self.rpc_service is None:
            return None
        if self.response_status is None:
            return None
        if self.duration_ms is None:
            return None
        
        request = Request(
            self.user_id,
            self.rpc_service,
            self.request_payload,
            self.response_status,
            self.response_payload,
            self.duration_ms
        )
                
        with db_session.begin():
            db_session.add(request)

