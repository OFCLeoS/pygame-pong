import socket
host = input(" host -> ") 
port = int(input(" port -> "))  
s = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
s.bind((host, port))
print("Server Started")
while True:
    data, address = s.recvfrom(1024)
    data = data.decode('utf-8')
    if not data: break
    print("Message from: " + str(address))
    print("Received : ")
    print(data)
    data = data.upper()
    print("Sending: ")
    print(data)
    s.sendto(data.encode('utf-8'),address)
s.close()
