import socket

hostname, sld, tld, port = 'www', 'tuna-server', 'pt', 80
target = '{}.{}.{}'.format(hostname, sld, tld)

list_args = ["name", "vehicle", "year", "distTravelled", "startLat", "startLon", "date", "duration", "maxDepth", "minDepth", "sensor"]


# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
client.connect(('0.0.0.0', 8001))

def get_str_args():
        args = str("/?")

        was_previous = False
        for arg in list_args:
                print(arg + ":")
                tmp = input()
                if tmp != "":
                    if was_previous:
                        args += "&"
                    args += arg + "=" + tmp
                    was_previous = True

        return args

args = get_str_args()
print(args)

data = 'GET ' + args + ' HTTP/1.1\r\nHost: {}.{}\r\n\r\n'

# send some data (in this case a HTTP GET request)
client.send(data.format(sld, tld).encode('utf-8'))

# receive the response data (4096 is recommended buffer size)
n_results = int(client.recv(32).decode('utf-8'))

print(n_results)

response = eval(client.recv(32768*n_results).decode('utf-8'))

i = 0
while i < len(response):
    print(str(i+1) + ": " + str(response[i]))
    i += 1