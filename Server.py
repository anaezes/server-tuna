import socket
import sqlite3
from urllib import parse
import time

HOST, PORT = '', 8001

list_args = ["name", "vehicle", "year", "distTravelled", "startLat", "startLon", "date", "duration", "maxDepth", "minDepth", "sensor"]

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)


conn = sqlite3.connect("../database.db")
c = conn.cursor()

def get_args(r):
    args = {}
    for arg in list_args:
        try:
            query = parse.parse_qs(parse.urlparse(r).query)[arg][0]
            print(arg + ": " + query)
            args[arg] = query
        except KeyError:
            continue
    return args

def get_logs(args):

    query = str('SELECT DISTINCT * FROM ')

    if 'sensor' in args:
        query += 'log_sensor, sensor, '

    query += 'log '
    if len(args) > 0:
        query += 'WHERE '

        i = 0
        for key, value in args.items():
            tmp = str()

            if key == 'sensor':
                tmp = "Sensor.sensorName"
            elif key == "minDepth":
                tmp += "maxDepth"
            else:
                tmp += key

            if key == "minDepth":
                tmp += ">" + value
            elif key == "maxDepth":
                tmp += "<" + value
            else:
                tmp +=' LIKE ' + '\"' + value + '\"'

            query += tmp

            if i < len(args) - 1:
                query += ' AND '
            i+=1

        if 'sensor' in args:
            query += ' AND log_sensor.logName ' \
                     'LIKE log.name AND log_sensor.sensorName' \
                     'LIKE sensor.sensorName ' \
                     'GROUP BY log.name, sensor.sensorName'
        else:
            query += " group by log.name "


    print(query)

    c.execute(query)
    rows = c.fetchall()

    print(len(rows))

    return rows

def send_logs(logs):

    http_response = str(len(logs))
    client_connection.sendall(http_response.encode('utf-8'))
    time.sleep(0.1)

    http_response = str(logs)
    client_connection.sendall(http_response.encode('utf-8'))


while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024).decode('utf-8')
    print(request)
    r = request.split()
    print(r[1])

    args = dict(get_args(r[1]))

    logs = get_logs(args)

    send_logs(logs)

    client_connection.close()