from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from starlette.websockets import WebSocketState
import json

router = APIRouter()

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    try:
        while True:
            message = await websocket.receive_text()
            message_data = json.loads(message)

            if message_data['type'] == 'init':
                # Store session ID when received in init message
                session_id = message_data['session_id']
                continue
            
            if message_data['type'] == 'message':
                app = websocket.app
                response = await app.state.ai_agent.get_response(
                    message_data['content'], 
                    message_data['session_id']
                )

            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(response)
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(f"Error: {str(e)}")