from db import db_session
from db_models import Request

class RequestService:
    @staticmethod
    def create_new_request_log(user_id, rpc_service,
                 request_payload, response_status,
                 response_payload, duration_ms):
        
        request = Request(user_id, rpc_service,
                 request_payload, response_status,
                 response_payload, duration_ms)
        
        with db_session.begin():
            db_session.add(request)

        