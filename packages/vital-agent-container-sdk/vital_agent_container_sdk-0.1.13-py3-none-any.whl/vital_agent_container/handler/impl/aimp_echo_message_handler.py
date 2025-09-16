import asyncio
from typing import Optional, Dict, Any
import httpx
from starlette.websockets import WebSocket
from vital_agent_container.handler.aimp_message_handler_inf import AIMPMessageHandlerInf


class AIMPEchoMessageHandler(AIMPMessageHandlerInf):
    async def process_message(self, *, app_config: Dict[str, Any], client: httpx.AsyncClient, websocket: WebSocket, data: str, started_event: asyncio.Event, jwt_payload: Optional[Dict[str, Any]] = None):
        try:
            print(f"Received Message: {data}")
            
            # Log JWT payload information if available
            if jwt_payload:
                if isinstance(jwt_payload, dict):
                    # Handle both single JWT payload and dual JWT payload formats
                    if 'jwt_token' in jwt_payload or 'jwt_auth_token' in jwt_payload:
                        # Dual JWT format from payload authentication
                        transport_jwt = jwt_payload.get('jwt_token')
                        auth_jwt = jwt_payload.get('jwt_auth_token')
                        if transport_jwt:
                            print(f"Transport JWT - Subject: {transport_jwt.get('sub', 'unknown')}")
                        if auth_jwt:
                            print(f"Auth JWT - Subject: {auth_jwt.get('sub', 'unknown')}, Permissions: {auth_jwt.get('permissions', [])}")
                    else:
                        # Single JWT payload from header authentication
                        print(f"JWT - Subject: {jwt_payload.get('sub', 'unknown')}, Permissions: {jwt_payload.get('permissions', [])}")
                else:
                    print(f"JWT payload type: {type(jwt_payload)}")
            else:
                print("No JWT payload provided")
            
            await websocket.send_text(data)
            print(f"Sent Message: {data}")
            # await websocket.close(1000, "Processing Complete")
            # print(f"Websocket closed.")
            started_event.set()
            print(f"Completed Event.")
        except asyncio.CancelledError:
            # log canceling
            raise




