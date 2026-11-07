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
    def reset(self)->"RequestBuilder":
        self.user_id = None
        self.rpc_service = None
        self.request_payload = {}
        self.response_status = None
        self.response_payload = {}
        self.duration_ms = None
    
    def set_user_id(self, user_id: int)->"RequestBuilder":
        self.user_id = user_id
        return self

    def set_rpc_service(self, rpc_service: RPCServiceEnum)->"RequestBuilder":
        self.rpc_service = rpc_service
        return self

    def set_request_payload(self, request_payload: dict)->"RequestBuilder":
        self.request_payload = request_payload
        return self

    def set_response_status(self, response_status: grpc.StatusCode)->"RequestBuilder":
        self.response_status = response_status
        return self

    def set_response_payload(self, response_payload: dict)->"RequestBuilder":
        self.response_payload = response_payload
        return self

    def set_duration_ms(self, duration_ms: int)->"RequestBuilder":
        self.duration_ms = duration_ms
        return self

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

        return request


    @staticmethod
    def create_request_log(req:Request):
        with db_session.begin():
            db_session.add(req)



