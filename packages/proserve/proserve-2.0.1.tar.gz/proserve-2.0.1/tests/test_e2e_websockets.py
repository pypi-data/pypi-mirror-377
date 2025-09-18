"""
ProServe E2E WebSocket Tests
Real-time communication, broadcasting, and WebSocket connection management
"""

import pytest
import asyncio
import websockets
import json
from .test_framework import ProServeTestFramework


@pytest.mark.asyncio
async def test_websocket_basic_connection(framework: ProServeTestFramework):
    """Test basic WebSocket connection and message exchange"""
    manifest_path = framework.create_test_manifest(
        'test-websocket-basic',
        endpoints=[
            {'path': '/ws/echo', 'method': 'websocket', 'handler': 'echo_handler.handle'},
        ]
    )
    
    echo_handler = '''
import json

async def handle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                response = {
                    "type": "echo",
                    "original": data,
                    "timestamp": str(datetime.now()),
                    "connection_id": id(ws)
                }
                await ws.send_str(json.dumps(response))
            except:
                await ws.send_str(json.dumps({"error": "Invalid JSON"}))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
    
    return ws
'''
    
    framework.create_test_handler('echo_handler.py', echo_handler)
    
    service = await framework.start_test_service(manifest_path, 'websocket_test')
    manifest = service.manifest
    ws_url = f"ws://{manifest.host}:{manifest.port}/ws/echo"
    
    # Test WebSocket connection
    async with websockets.connect(ws_url) as websocket:
        # Test message sending and receiving
        test_message = {"message": "Hello WebSocket", "id": 1}
        await websocket.send(json.dumps(test_message))
        
        response = await websocket.recv()
        response_data = json.loads(response)
        
        assert response_data["type"] == "echo"
        assert response_data["original"]["message"] == "Hello WebSocket"
        assert response_data["original"]["id"] == 1
        
        # Test multiple messages
        messages_sent = []
        messages_received = []
        
        for i in range(3):
            msg = {"test": f"message_{i}", "number": i}
            messages_sent.append(msg)
            await websocket.send(json.dumps(msg))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            messages_received.append(response_data["original"])
        
        assert len(messages_received) == 3
        assert messages_sent == messages_received
    
    return {
        "connection_established": True,
        "echo_test_passed": True,
        "multiple_messages_count": len(messages_received)
    }


@pytest.mark.asyncio
async def test_websocket_broadcasting(framework: ProServeTestFramework):
    """Test WebSocket broadcasting to multiple clients"""
    manifest_path = framework.create_test_manifest(
        'test-websocket-broadcast',
        endpoints=[
            {'path': '/ws/broadcast', 'method': 'websocket', 'handler': 'broadcast_handler.handle'},
            {'path': '/api/broadcast', 'method': 'post', 'handler': 'broadcast_handler.handle'},
        ]
    )
    
    broadcast_handler = '''
import json
import weakref
from aiohttp import web

# Global set to track all WebSocket connections
active_connections = set()

async def handle(request):
    path = str(request.url.path)
    
    if path == '/ws/broadcast':
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add connection to active set
        active_connections.add(ws)
        
        try:
            # Send welcome message
            welcome = {
                "type": "welcome",
                "message": "Connected to broadcast channel",
                "connection_count": len(active_connections)
            }
            await ws.send_str(json.dumps(welcome))
            
            # Keep connection alive and handle incoming messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("type") == "ping":
                            await ws.send_str(json.dumps({"type": "pong"}))
                    except:
                        pass
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        finally:
            # Remove connection when closed
            active_connections.discard(ws)
        
        return ws
    
    elif path == '/api/broadcast':
        try:
            data = await request.json()
            message = {
                "type": "broadcast",
                "data": data,
                "timestamp": str(datetime.now()),
                "recipients": len(active_connections)
            }
            
            # Broadcast to all connected clients
            disconnected = set()
            for ws in active_connections:
                try:
                    await ws.send_str(json.dumps(message))
                except:
                    disconnected.add(ws)
            
            # Clean up disconnected clients
            for ws in disconnected:
                active_connections.discard(ws)
            
            return {
                "status": "broadcasted",
                "message": data,
                "recipients": len(active_connections),
                "cleaned_up": len(disconnected)
            }
        except:
            return {"error": "Invalid JSON"}, 400
    
    return {"error": "Not found"}, 404
'''
    
    framework.create_test_handler('broadcast_handler.py', broadcast_handler)
    
    service = await framework.start_test_service(manifest_path, 'broadcast_test')
    manifest = service.manifest
    ws_url = f"ws://{manifest.host}:{manifest.port}/ws/broadcast"
    api_url = f"http://{manifest.host}:{manifest.port}/api/broadcast"
    
    # Connect multiple WebSocket clients
    clients = []
    received_messages = []
    
    try:
        # Connect 3 clients
        for i in range(3):
            client = await websockets.connect(ws_url)
            clients.append(client)
            
            # Receive welcome message
            welcome = await client.recv()
            welcome_data = json.loads(welcome)
            assert welcome_data["type"] == "welcome"
        
        # Trigger broadcast via API
        broadcast_data = {"message": "Hello all clients!", "event": "test_broadcast"}
        
        import requests
        broadcast_response = requests.post(api_url, json=broadcast_data)
        assert broadcast_response.status_code == 200
        broadcast_result = broadcast_response.json()
        
        assert broadcast_result["status"] == "broadcasted"
        assert broadcast_result["recipients"] == 3
        
        # Receive broadcast messages from all clients
        for i, client in enumerate(clients):
            message = await client.recv()
            message_data = json.loads(message)
            
            assert message_data["type"] == "broadcast"
            assert message_data["data"]["message"] == "Hello all clients!"
            received_messages.append(message_data)
        
        # Test ping/pong
        ping_message = {"type": "ping"}
        await clients[0].send(json.dumps(ping_message))
        pong_response = await clients[0].recv()
        pong_data = json.loads(pong_response)
        assert pong_data["type"] == "pong"
        
    finally:
        # Close all connections
        for client in clients:
            await client.close()
    
    return {
        "clients_connected": len(clients),
        "broadcast_recipients": broadcast_result["recipients"],
        "messages_received": len(received_messages),
        "ping_pong_works": pong_data["type"] == "pong"
    }


@pytest.mark.asyncio
async def test_websocket_chat_room(framework: ProServeTestFramework):
    """Test WebSocket chat room functionality with user management"""
    manifest_path = framework.create_test_manifest(
        'test-websocket-chat',
        endpoints=[
            {'path': '/ws/chat/{room_id}', 'method': 'websocket', 'handler': 'chat_handler.handle'},
            {'path': '/api/chat/{room_id}/users', 'method': 'get', 'handler': 'chat_handler.handle'},
        ]
    )
    
    chat_handler = '''
import json
from collections import defaultdict

# Room management
chat_rooms = defaultdict(dict)  # room_id -> {connections: set, messages: list}
user_connections = {}  # ws -> user_info

async def handle(request):
    path = str(request.url.path)
    
    if '/ws/chat/' in path:
        room_id = request.match_info.get('room_id')
        username = request.query.get('username', f'user_{id(request)}')
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Initialize room if needed
        if 'connections' not in chat_rooms[room_id]:
            chat_rooms[room_id]['connections'] = set()
            chat_rooms[room_id]['messages'] = []
        
        # Add user to room
        chat_rooms[room_id]['connections'].add(ws)
        user_connections[ws] = {'username': username, 'room_id': room_id}
        
        # Notify room of new user
        join_message = {
            "type": "user_joined",
            "username": username,
            "room_id": room_id,
            "users_count": len(chat_rooms[room_id]['connections']),
            "timestamp": str(datetime.now())
        }
        
        # Broadcast join message to all users in room
        for conn in chat_rooms[room_id]['connections']:
            if conn != ws:  # Don't send to self
                try:
                    await conn.send_str(json.dumps(join_message))
                except:
                    pass
        
        # Send chat history to new user
        history = {
            "type": "chat_history",
            "messages": chat_rooms[room_id]['messages'][-10:],  # Last 10 messages
            "room_id": room_id
        }
        await ws.send_str(json.dumps(history))
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        if data.get("type") == "chat_message":
                            chat_message = {
                                "type": "chat_message",
                                "username": username,
                                "message": data.get("message", ""),
                                "room_id": room_id,
                                "timestamp": str(datetime.now())
                            }
                            
                            # Store message
                            chat_rooms[room_id]['messages'].append(chat_message)
                            
                            # Broadcast to all users in room
                            for conn in chat_rooms[room_id]['connections']:
                                try:
                                    await conn.send_str(json.dumps(chat_message))
                                except:
                                    pass
                        
                    except:
                        error = {"type": "error", "message": "Invalid message format"}
                        await ws.send_str(json.dumps(error))
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        
        finally:
            # Clean up on disconnect
            chat_rooms[room_id]['connections'].discard(ws)
            if ws in user_connections:
                del user_connections[ws]
            
            # Notify room of user leaving
            leave_message = {
                "type": "user_left",
                "username": username,
                "room_id": room_id,
                "users_count": len(chat_rooms[room_id]['connections']),
                "timestamp": str(datetime.now())
            }
            
            for conn in chat_rooms[room_id]['connections']:
                try:
                    await conn.send_str(json.dumps(leave_message))
                except:
                    pass
        
        return ws
    
    elif '/api/chat/' in path and path.endswith('/users'):
        room_id = request.match_info.get('room_id')
        
        if room_id in chat_rooms:
            users = []
            for conn in chat_rooms[room_id]['connections']:
                if conn in user_connections:
                    users.append(user_connections[conn]['username'])
            
            return {
                "room_id": room_id,
                "users": users,
                "user_count": len(users),
                "message_count": len(chat_rooms[room_id].get('messages', []))
            }
        
        return {"room_id": room_id, "users": [], "user_count": 0, "message_count": 0}
    
    return {"error": "Not found"}, 404
'''
    
    framework.create_test_handler('chat_handler.py', chat_handler)
    
    service = await framework.start_test_service(manifest_path, 'chat_test')
    manifest = service.manifest
    room_id = "test_room_123"
    
    # Connect multiple users to chat room
    user1_ws = await websockets.connect(f"ws://{manifest.host}:{manifest.port}/ws/chat/{room_id}?username=Alice")
    user2_ws = await websockets.connect(f"ws://{manifest.host}:{manifest.port}/ws/chat/{room_id}?username=Bob")
    
    try:
        # User1 should receive history (empty initially)
        history1 = await user1_ws.recv()
        history1_data = json.loads(history1)
        assert history1_data["type"] == "chat_history"
        
        # User2 should receive history and join notification
        history2 = await user2_ws.recv()  # History
        join_notification = await user1_ws.recv()  # Alice receives Bob's join
        
        join_data = json.loads(join_notification)
        assert join_data["type"] == "user_joined"
        assert join_data["username"] == "Bob"
        
        # Test chat messaging
        # Alice sends message
        alice_message = {
            "type": "chat_message",
            "message": "Hello everyone!"
        }
        await user1_ws.send(json.dumps(alice_message))
        
        # Both users should receive the message
        alice_received = await user1_ws.recv()
        bob_received = await user2_ws.recv()
        
        alice_msg_data = json.loads(alice_received)
        bob_msg_data = json.loads(bob_received)
        
        assert alice_msg_data["type"] == "chat_message"
        assert alice_msg_data["username"] == "Alice"
        assert alice_msg_data["message"] == "Hello everyone!"
        assert alice_msg_data == bob_msg_data
        
        # Bob replies
        bob_message = {
            "type": "chat_message", 
            "message": "Hi Alice! How are you?"
        }
        await user2_ws.send(json.dumps(bob_message))
        
        # Both should receive Bob's message
        alice_received_bob = await user1_ws.recv()
        bob_received_echo = await user2_ws.recv()
        
        # Test API endpoint for user list
        import requests
        users_response = requests.get(f"http://{manifest.host}:{manifest.port}/api/chat/{room_id}/users")
        users_data = users_response.json()
        
        assert users_data["user_count"] == 2
        assert "Alice" in users_data["users"]
        assert "Bob" in users_data["users"]
        
    finally:
        await user1_ws.close()
        await user2_ws.close()
    
    return {
        "chat_room_created": True,
        "users_connected": 2,
        "messages_exchanged": 2,
        "join_notifications_work": join_data["type"] == "user_joined",
        "api_user_list_works": users_data["user_count"] == 2
    }
