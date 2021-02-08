# TODO:
# 1. Убрать индексы
# 2. Переработать структуру хранения данных (словарь в словаре)
# 3. Убрать дубли кода

import asyncio
from collections import defaultdict

data_list = defaultdict(dict)


def form_send_string(func_dict):
    empty_string = ''
    list_elem = list(func_dict.items())

    metric_name = list_elem[0][0]

    for dict_metric, dict_values in list_elem[0][1].items():
        empty_string += f'{metric_name} {dict_values} {dict_metric}\n'

    final_string = empty_string
    return final_string


def process_data(data):
    error_string = 'error\nwrong command\n\n'
    right_string = 'ok\n\n'

    request, *info = data.split(' ')
    if request == 'put':
        if len(info) != 3:
            return error_string
        name, value, timestamp = info[0], info[1], info[2]
        try:
            value = float(value)
            timestamp = int(timestamp)
        except ValueError:
            return error_string

        data_list[name][timestamp] = value
        return right_string

    elif request == 'get':
        if len(info) != 1:
            return error_string
        name_request = info[0]
        send_string = 'ok\n'

        if name_request.rstrip('\r\n') == '*':
            for each_element, each_value in data_list.items():
                dict_for_func = {each_element: each_value}
                send_string += form_send_string(dict_for_func)

            send_string += '\n'
            return send_string

        else:
            for each_element, each_value in data_list.items():
                if name_request.rstrip('\r\n') == each_element:
                    dict_for_func = {each_element: each_value}
                    send_string += form_send_string(dict_for_func)

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