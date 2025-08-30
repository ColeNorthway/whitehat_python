import socket


target_host = input("what is the target ip or domain-name? ")
target_port = int(input("what is the target port? "))


#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#connect the client
client.connect((target_host,target_port))


#send some data
file_name = input("what do file you want to send? ")


#opening the file and encoding it to send
data_bytes = ''
try:
    with open(file_name, 'r') as data:
        data = data.read()
        data_bytes = data.encode()
        client.send(data_bytes)
except Exception as e:
    print(f'{e}')




#receive some data
while True:
    chunk = client.recv(4096)
    if not chunk:
        break
    response += chunk
    print(response.decode())

client.close()
