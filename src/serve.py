from textual_serve.server import Server

server = Server("textual run --dev src\main.py", host="192.168.1.53")
server.serve()