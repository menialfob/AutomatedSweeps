from textual_serve.server import Server

from utils import get_ip
import sys


def run_server():
    """Starts the server with a new event loop."""
    local_ip = get_ip()
    if getattr(sys, "frozen", False):
        server = Server(r"AutomatedSweeps.exe --noservebtn", host=local_ip)
    # When running as an executable
    else:
        server = Server("textual run src\main.py --noservebtn", host=local_ip)

    server.serve(debug=True)


# def run_server():
#     """Starts the server with a new event loop."""
#     local_ip = get_ip()
#     if getattr(sys, "frozen", False):
#         server = Server(r"AutomatedSweeps.exe --serve", host=local_ip)
#     # When running as an executable
#     else:
#         server = Server("textual run src\main.py --serve", host=local_ip)

#     new_loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(new_loop)

#     try:
#         new_loop.create_task(server.serve())  # Schedule the server task
#         new_loop.run_forever()  # Keep the event loop running
#     except Exception as e:
#         print(f"Error in server: {e}")
#     finally:
#         new_loop.close()  # Properly close the event loop when done
