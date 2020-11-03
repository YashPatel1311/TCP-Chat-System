import socket
import threading
from threading import Thread,current_thread
import pickle
import sys,datetime,time

S_IP= '127.0.0.1'
S_PORT=1234

C_IP=sys.argv[1]
C_PORT=1234


active=True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    RED = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ChatThread(Thread):
    def __init__(self,name,socket):
        Thread.__init__(self)
        self.setName(name)
        self.socket=socket
        self.daemon=True
        

    def run(self):
        global active
        while active:
            msg=input()
            self.socket.send(bytes(msg,'utf-8'))
            if msg=="exit":
                active=False
                self.socket.close()
                return
            


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((C_IP,C_PORT))

s.connect((S_IP,S_PORT))
print("\nConnection successfull")
flag=1

try:
    userlist=pickle.loads(s.recv(2048))
    if len(userlist)>0:
        print("\nCurrent active users are:")
        for num,name in enumerate(userlist,start=1):
            print(num, name)

    else:
        print("\nWelcome!!!!. You are the first one here.")


except:
    print("\nConnection terminated")


while flag==1:
    username=input("\nEnter unique username: ")
    if username!="":
        s.send(bytes(username,"utf-8"))
        flag=int((s.recv(10)).decode("utf-8"))

sender=ChatThread("sender",s)
sender.start()

while active:
    try:
        timestamp,sender,addr,msg=pickle.loads(s.recv(1024))
    except:
        print("Connection terminated")
        active=False
        break
    if msg!="":
        print()
        print(f"{bcolors.RED}{sender}<{addr}> on {timestamp}{bcolors.ENDC}:".rjust(182))
        print(f"{bcolors.OKBLUE}{bcolors.BOLD}{msg}{bcolors.ENDC}".rjust(182)) #182 total


s.close()
try:
    sender.join(5)
except:
    pass
