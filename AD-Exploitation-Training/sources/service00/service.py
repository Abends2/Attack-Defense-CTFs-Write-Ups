from util import gen_flag
import socketserver
import os

BASE_PORT = int(os.getenv('BASE_PORT', 10000))
TEAM_COUNT = int(os.getenv('SERVICE_00_TEAM_COUNT', 1))


class FlagbotRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.send(gen_flag(0, self.server.team_id) + b'\n')


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = BASE_PORT + 1

    socketserver.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(
        (HOST, PORT),
        FlagbotRequestHandler
    )
    server.team_id = 1
    with server:
        try:
            server.serve_forever(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
