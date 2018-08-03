import socket

hostname, sld, tld, port = 'www', 'integralist', 'co.uk', 80
target = '{}.{}.{}'.format(hostname, sld, tld)

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
client.connect(('0.0.0.0', 8001))

def get_str_args():
        args = str("/?")

        # todo ver como é possivel fazer as junções com os "&"

        print("Name: ")
        name = input()
        #if name != "":
        args += "name=" + name

        print("Year: ")
        year = input()
       # if year != "":
        args += "&year=" + year

        print("Vehicle: ")
        vehicle = input()
       # if vehicle != "":
        args += "&vehicle=" + vehicle

        print("Sensor: ")
        sensor = input()
        #if sensor != "":
        args += "&sensor=" + sensor

        print("Depth min: ")
        minDepth = input()
        #if minDepth != "":
        args += "&minDepth=" + minDepth

        print("Depth max: ")
        maxDepth = input()
        #if maxDepth != "":
        args += "&maxDepth=" + maxDepth


        return args


args = get_str_args()
print(args)

data = 'GET ' + args + ' HTTP/1.1\r\nHost: {}.{}\r\n\r\n'

# send some data (in this case a HTTP GET request)
client.send(data.format(sld, tld).encode('utf-8'))

# receive the response data (4096 is recommended buffer size)
n_results = int(client.recv(32).decode('utf-8'))

print(n_results)

for i in range(n_results):
    response = client.recv(32768).decode('utf-8') #TODO LIMIT 4096 
    print(str(i) + ": " + response)