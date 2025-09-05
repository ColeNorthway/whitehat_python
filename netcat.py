import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


'''
recieves a command
strips newlines/spaces
if empty then exit
then split that command to its components(args)
and return sterr with the stdout
return the output decoded
'''
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return

    try:
        output = subprocess.check_output(shlex.split(cmd), text=True, stderr=subprocess.STDOUT)
        return output
    except OSError as e:
        return 'The command you ran is not an actual executable'
    except subprocess.CalledProcessError as e:
        return 'There was an error with the command you ran'

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

            
    def send(self):
        try:
            self.socket.connect((self.args.target, self.args.port))
            print('Connected!')
        except Exception as e:
            print(f'{e}')
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''

                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break

                if response: #you could prob make this loop exit on buffer = exit
                    print(response)
                    buffer = input('> ')
                    try:
                        self.socket.send(buffer.encode())
                        print('Sent res!')###############
                    except Exception as e:
                        print(f'{e}')

        except KeyboardInterrupt:
            print('user termed conn')
            self.socket.close()
            sys.exit()


    def listen(self):
        try:
            self.socket.bind((self.args.target, self.args.port))
            self.socket.listen(5)
            print('Successfully listening')
        except Exception as e:
            print(f'{e}')

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()


    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''

            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)

                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            recv_len = 1
            client_socket.send(b'Shell Connected') #send confirmation of connection
            while True:
                try:
                    while recv_len:
                        cmd_buffer = client_socket.recv(4096)
                        recv_len = len(cmd_buffer)
                        if recv_len < 4096:
                            break
                        
                    #read cmd from client, exit on exit
                    if cmd_buffer == b'exit':
                        client_socket.send(b'Connect Killed')
                        self.socket.close()
                        sys.exit()
                        break
                        
                    response = execute(cmd_buffer.decode())

                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Coles Python Netcat', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example: 
    netcat.py -t <ip> -p <port> -l -c #command shell
    netcat.py -t <ip> -p <port> -l -u=<filename> #upload to a file
    netcat.py -t <ip> -p <port> -l -e=\"<sys cmd>\" #execute command
    echo 'ABC' | ./netcat.py -t <ip> -p <port> #echo text to server port <port>
    netcat.py -t <ip> -p <port> #connect to server
    '''))
    
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = '' #sys.stdin.read()
        #robust this

    nc = NetCat(args, buffer.encode())
    nc.run()
