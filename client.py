import socket
import time
from collections import defaultdict


class ClientError(Exception):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.sock = socket.create_connection((host, port), timeout)
        # self.sock = socket.socket()
        # self.sock.connect((host, port))
        self.sock.settimeout(self.timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def put(self, name, value, timestamp=None):  # Send a string to server
        try:
            if timestamp is None:
                timestamp = int(time.time())

            if type(name) is not str:
                raise ClientError
            if not (isinstance(value, int) or isinstance(value, float)):
                raise ClientError
            if type(timestamp) is not int:
                raise ClientError

            string = f"put {name} {value} {timestamp}\n"
            encoded_string = string.encode(encoding="utf-8")
            self.sock.send(encoded_string)

            raw_data_put = self.sock.recv(1024)
            decode_data = raw_data_put.decode("utf-8")
            status, *_ = decode_data.split('\n')
            if status != 'ok':
                raise ClientError
        except socket.timeout:
            raise ClientError

    def get(self, name):  # Try to get data from server.
        request = f"get {name}\n"
        encoded_request = request.encode(encoding="utf-8")
        self.sock.send(encoded_request)
        try:
            raw_data = self.sock.recv(1024)
            response = raw_data.decode("utf-8")
        except socket.timeout:
            raise ClientError

        status, *rows = response.split('\n')
        if status != 'ok':
            raise ClientError

        result = defaultdict(list)
        for row in rows:
            if not row:
                continue

            try:
                metric, value, timestamp = row.split(' ')
                result[metric].append((int(timestamp), float(value)))
            except ValueError:
                raise ClientError

        for metric, values in result.items():
            result[metric] = sorted(values, key=lambda pair: pair[0])

        if name == '*':
            return dict(result)
        return {name: result[name]} if name in result else {}


if __name__ == '__main__':
    with Client('127.0.0.1', 8181, 5) as client:
        print(client.get('temperature'))
        # client.put('palm.cpu', 2.1, 11553123412)
