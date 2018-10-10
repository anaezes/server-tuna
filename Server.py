import socket
import sqlite3
from urllib.parse import urlparse, parse_qs
import time

HOST, PORT = '', 8001

operatorType = {"minDepth": " >= ",
                "minDuration": " >= ",
                "minDate": " >= ",
                "minDistTravelled": " >= ",
                "maxDepth": " <= ",
                "maxDuration": " <= ",
                "maxDate": " <= ",
                "maxDistTravelled": " <= ",
                "year": " = ",
                "name": " LIKE ",
                "type": " LIKE ",
                "vehicle": " LIKE "}

argSeparator = {"name": "\"",
                "type": "\"",
                "vehicle": "\"",
                "year": ""}

list_args = ["name",
             "vehicle",
             "type",
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
             "sensor",
             "all-vehicles",
             "all-years",
             "all-types"]

query_sensor = ' AND log_sensor.logName ' \
               'LIKE log.name AND log_sensor.sensorName' \
               'LIKE sensor.sensorName ' \
               'GROUP BY log.name, sensor.sensorName'

base = "SELECT DISTINCT "

queries = {"all-types": 'type FROM log group by log.type',
           "all-vehicles": 'vehicle FROM log group by log.vehicle',
           "all-years": 'year FROM log group by log.year',
           "all-warnings&errors": 'warnings, errors FROM ',
           "all-info": 'name, vehicle, type, year, distTravelled, startLat, startLon, date, duration, '
                       'maxDepth, maxAltitude FROM '}


listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)


conn = sqlite3.connect("../database.db")
c = conn.cursor()


def get_correct_params(key):

    if key == 'sensor':
        return "Sensor.sensorName"

    if key in ["minDepth", "maxDepth"]:
        return "maxDepth"

    if key in ["minDuration", "maxDuration"]:
        return "duration"

    if key in ["maxDistTravelled","minDistTravelled"]:
        return "distTravelled"

    if key in ["minDate", "maxDate"]:
        return "cast(date as datetime)"

    return ""



def get_operator(key,value):

    if key == "name":
        return key + operatorType['name'] + value[0]

    if key in ["vehicle", "type", "year"]:
        tmp = str('')
        i = 0
        if len(value) > 1:
            tmp += "( "
            while i < len(value) - 1:
                tmp += key + operatorType[key] + argSeparator[key] + value[i] + argSeparator[key] + ' OR '
                i = i+1
            tmp += key + operatorType[key] + argSeparator[key] + value[len(value) - 1] + argSeparator[key] + ") "
        else:
            tmp += key + operatorType[key] + argSeparator[key] + value[len(value) - 1] + argSeparator[key]

        return tmp

    return get_correct_params(key) + operatorType[key] + value[0]



def get_query(args):

    if('all-vehicles' in args):
        return base + queries['all-vehicles']

    if('all-years' in args):
        return base + queries['all-years']

    if ('all-types' in args):
        return base + queries['all-types']

    if ('name' in args):
        query = base + queries['warnings&errors']
    else:
        query = base + queries['all-info']

    if 'sensor' in args:
        query += 'log_sensor, sensor, '

    query += 'log '

    if len(args) > 0:
        query += 'WHERE '

        i = 0
        for key, value in args.items():
            query += get_operator(key, value)

            if i < len(args) - 1:
                query += ' AND '
            i += 1

        if 'sensor' in args:
            query += query_sensor
        else:
            query += " group by log.name "

    return query



def get_logs(args):

    query = get_query(args)
    print(query)

    c.execute(query)
    rows = c.fetchall()
    print(rows)
    print(len(rows))

    return rows



def send_logs(logs):

    http_response = "HTTP/1.1 200 OK\n\n " + str(len(logs))
    client_connection.sendall(http_response.encode('utf-8'))
    time.sleep(0.1)
    print(logs)
    http_response = "HTTP/1.1 200 OK\n\n " + str(logs)
    client_connection.sendall(http_response.encode('utf-8'))


while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024).decode('utf-8')
    print("REQUEST:")
    print(request)
    r = request.split()

    parsed_url = urlparse(r[1])

    logs = get_logs(parse_qs(parsed_url.query))

    send_logs(logs)

    client_connection.close()