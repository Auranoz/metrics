# TODO:
# 1. Убрать индексы
# 2. Переработать структуру хранения данных (словарь в словаре)
# 3. Убрать дубли кода

import asyncio

data_list = list()


def process_data(data):
    error_string = 'error\nwrong command\n\n'
    right_string = 'ok\n\n'

    request, *info = data.split(' ')
    if request == 'put':
        if len(info) != 3:
            return error_string
        try:
            info[1] = float(info[1])
            info[2] = int(info[2].rstrip('\r\n'))
        except ValueError:
            return error_string

        if data_list:
            count = -1
            for elements in data_list:
                count += 1
                if info[0] in elements and info[2] in elements:
                    data_list[count] = info
                    return right_string

        data_list.append(info)
        return right_string

    elif request == 'get':
        if len(info) != 1:
            return error_string

        name_request = info[0]
        if name_request.rstrip('\r\n') == '*':
            send_string = 'ok\n'
            for each_metric in data_list:
                metric_string = f'{each_metric[0]} {each_metric[1]} {each_metric[2]}\n'
                send_string += metric_string
            send_string += '\n'
            return send_string

        else:
            send_string = 'ok\n'
            for each_metric in data_list:
                if name_request.rstrip('\r\n') in each_metric:
                    metric_string = f'{each_metric[0]} {each_metric[1]} {each_metric[2]}\n'
                    send_string += metric_string
            send_string += '\n'
            return send_string
    else:
        return error_string


class ClientServerProtocol(asyncio.Protocol):
    def __init__(self, *args, **kwargs):
        self.transport = None
        super().__init__(*args, **kwargs)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = process_data(data.decode())
        self.transport.write(resp.encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    run_server('127.0.0.1', 8888)