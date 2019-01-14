# import websocket

# ws = websocket.WebSocket()
# ws.connect("wss://echo.websocket.org")

from websocket import create_connection
ws = create_connection("ws://demos.kaazing.com/echo")
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result = ws.recv()
print("Received '%s'" % result)
ws.close()
