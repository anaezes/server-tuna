import socket
import sqlite3
from urllib import parse
import time

HOST, PORT = '', 8001

list_args = ["name",
             "vehicle",
             "year",
             "minDistTravelled",
             "maxDistTravelled",
             "startLat",
             "startLon",
             "minDate",
             "maxDate",
             "minDuration",
             "maxDuration",
             "maxDepth",
             "minDepth",
             "sensor"]

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



def get_correct_params(key):

    if key == 'sensor':
        return "Sensor.sensorName"

    if key == "minDepth":
        return "maxDepth"

    if key in ["minDuration", "maxDuration"]:
        return "duration"

    if key in ["maxDistTravelled","minDistTravelled"]:
        return "distTravelled"

    if key in ["minDate", "maxDate"]:
        return "cast(date as datetime)"



def get_query(args):
    query = str('SELECT DISTINCT * FROM ')

    if 'sensor' in args:
        query += 'log_sensor, sensor, '

    query += 'log '
    if len(args) > 0:
        query += 'WHERE '

        i = 0
        for key, value in args.items():
            tmp = str()

            if key in [ 'sensor',
                    'minDepth',
                    'minDuration',
                    'maxDuration',
                    'maxDistTravelled',
                    'minDistTravelled',
                    'minDate',
                    'maxDate']:
                tmp += get_correct_params(key)
            else:
                tmp += key

            if key in ["minDepth",
                    "minDuration",
                    "minDate",
                    "minDistTravelled"]:
                tmp += ">=" + value
            elif key in ["maxDepth",
                      "maxDuration",
                      "maxDate",
                      "maxDistTravelled"]:
                tmp += "<=" + value
            else:
                tmp += ' LIKE ' + '\"' + value + '\"'

            query += tmp

            if i < len(args) - 1:
                query += ' AND '
            i += 1

        if 'sensor' in args:
            query += ' AND log_sensor.logName ' \
                     'LIKE log.name AND log_sensor.sensorName' \
                     'LIKE sensor.sensorName ' \
                     'GROUP BY log.name, sensor.sensorName'
        else:
            query += " group by log.name "

    return query



def get_logs(args):

    query = get_query(args)
    print(query)

    c.execute(query)
    rows = c.fetchall()
    print(len(rows))

    return rows



def send_logs(logs):

    http_response = "HTTP/1.1 200 OK\n\n " + str(len(logs))
    #http_response = str(len(logs))
    client_connection.sendall(http_response.encode('utf-8'))
    time.sleep(0.1)
    print(logs)
    http_response = "HTTP/1.1 200 OK\n\n " + str(logs)
    #http_response = str(logs)
    client_connection.sendall(http_response.encode('utf-8'))


while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024).decode('utf-8')

    print('Request: ')
    print(request)
    r = request.split()
    print(r[1])

    args = dict(get_args(r[1]))

    logs = get_logs(args)

    send_logs(logs)

    client_connection.close()