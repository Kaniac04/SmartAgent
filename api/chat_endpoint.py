from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from starlette.websockets import WebSocketState
import json

router = APIRouter()

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        session_id = None
        
        while True:
            try:
                message = await websocket.receive_text()
                message_data = json.loads(message)

                if message_data['type'] == 'init':
                    session_id = message_data['session_id']
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "message": "Connected successfully"
                    }))
                    continue

                if message_data['type'] == 'message':
                    if not session_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Session not initialized"
                        }))
                        continue

                    response = await websocket.app.state.ai_agent.get_response(
                        message_data['content'], 
                        session_id
                    )
                    await websocket.send_text(response)

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid message format"
                }))
                
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))