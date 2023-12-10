from util import verify_flag, FLAG_RE
import socket
import socketserver
import sys
import threading
import os
import time
import logging as l  # noqa: E741

TIMEOUT = int(os.getenv('FLAGBOT_TIMEOUT', 10))
if 'SERVICE_COUNT' not in os.environ:
    l.warning('missing SERVICE_COUNT, assuming 1')
SERVICE_COUNT = int(os.getenv('SERVICE_COUNT', 1))
FLAGS = dict()
for i in range(SERVICE_COUNT):
    flag_key = 'SERVICE_%02d_FLAG' % i
    if flag_key not in os.environ:
        l.warning('missing flag for service %02d (SERVICE_%02d_FLAG)' % (i, i))
    flag = os.getenv(
        flag_key,
        'enotraining{missing flag for service %02d}' % i,
    )
    thresh_key = 'SERVICE_%02d_THRESHOLD' % i
    if thresh_key not in os.environ:
        l.warning(
            '''missing threshold for service %02d (SERVICE_%02d_THRESHOLD), '''
            '''assuming 40''' % (i, i)
        )
    thresh = int(os.getenv(thresh_key, 40))
    FLAGS[i] = (flag, thresh)


def close_request(handler):
    time.sleep(TIMEOUT)
    try:
        handler.request.shutdown(socket.SHUT_RDWR)
        handler.request.close()
    except OSError:
        pass


class FlagbotRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.t = threading.Thread(target=close_request, args=(self, ))
        self.t.start()

        self.flags = set()
        self.flags_per_service = dict()

    def _readline(self):
        buffer = b''
        while True:
            try:
                in_ = self.request.recv(4096)
                if not in_:
                    break
                buffer += in_
            except OSError:
                break
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                yield line

    def _handle_flag(self, flag):
        if not FLAG_RE.match(flag):
            self.request.send(b'inv\n')
            return
        result, info = verify_flag(flag)
        if result == 'invalid':
            self.request.send(b'inv\n')
            return
        if result == 'expired':
            self.request.send(b'exp\n')
            return
        if flag in self.flags:
            self.request.send(b'dup\n')
            return
        self.flags.add(flag)

        service, team = info
        if service not in self.flags_per_service:
            self.flags_per_service[service] = 1
        else:
            self.flags_per_service[service] += 1

        if service not in FLAGS:
            l.error('received flag for unknown service %02d' % service)
        else:
            flag, thresh = FLAGS[service]
            if self.flags_per_service[service] >= thresh:
                self.request.send(flag.encode() + b'\n')
                return

        self.request.send(b'ok!\n')

    def handle(self):
        for line in self._readline():
            try:
                self._handle_flag(line)
            except ConnectionResetError:
                return

    def finish(self):
        self.t.join()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = 1337 if len(sys.argv) < 2 else int(sys.argv[1])

    socketserver.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(
        (HOST, PORT),
        FlagbotRequestHandler
    )
    with server:
        try:
            server.serve_forever(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
