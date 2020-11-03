import socket
from _thread import *
import threading
from threading import Thread,current_thread
import pickle
from inputimeout import inputimeout,TimeoutOccurred
from datetime import datetime
import time




S_IP= '127.0.0.1'
S_PORT=1234

users={}
msgQueue=[]
unsendQueue={}
threads=[]
accept=True
connection=0

class ExitThread(Thread):
    def __init__(self,name,forwarder):
        Thread.__init__(self)
        self.setName(name)
        self.forwarder=forwarder
        self.daemon=True

    def run(self):
        global threads,accept
        while True:
            exit=input("want to exit?? :")
            if exit=='exit':
                self.forwarder.active=False
                accept=False
                for thread in threads:
                    thread.active=False

                return



class ForwarderThread(Thread):
    def __init__(self,name):
        Thread.__init__(self)
        self.setName(name)
        self.active=True
        self.daemon=True

    def run(self):
        global msgQueue,users

        while self.active:
            try:
                sender,receiver,msg,timestamp=msgQueue.pop(0)
            except:
                # print("queue empty")
                time.sleep(1)
                continue
            try:
                con,addr=users[receiver]
                obj=(timestamp,sender,addr,msg)
                con.send(pickle.dumps(obj))
                # If more than 1 msg to same client it cannot process all request at the same speed. Hence msgs might get lost.
                time.sleep(1)
            except:
                # print("User not online")
                try:
                    # add msg to recevier's unsend msgs list

                    unsendQueue[receiver].append((sender,receiver,msg,timestamp))
                except:
                    # Initialize recevier's unsend msgs list 

                    unsendQueue[receiver]=[]
                    unsendQueue[receiver].append((sender,receiver,msg,timestamp))
                
                time.sleep(1)
        return



class ConnectionThread(Thread):
    
    def __init__(self,name,con,addr):
        Thread.__init__(self)
        self.setName(name)
        self.con=con
        self.addr=addr
        self.active=True
        self.daemon=True


    def run(self):
        global users,msgQueue,connection,unsendQueue
        print("Connection established and thread successfully running")

        userlist=list(users.keys())
        self.con.send(pickle.dumps(userlist))

        #Implements Unique username
        flag=1
        while flag==1:
            try:
                username=(self.con.recv(1024)).decode('utf-8')
            except:
                continue
            # print(username)
            if username in userlist:
                self.con.send(bytes("1","utf-8"))

            else:
                self.con.send(bytes("0","utf-8"))
                users[username]=(self.con,self.addr[0])
                flag=0

        for u,c in users.items():
            if username!=u:
                now = datetime.now()
                timestamp=now.strftime("%d/%m/%Y %I:%M %p")
                msgQueue.append((username,u,"I'm Online",timestamp))


        while True:
            try:
                msgQueue.append(unsendQueue[username].pop(0))
            except:
                print("No pending msgs")
                break
            


# Receiving functionality
        while self.active:
            try:
                msg=(self.con.recv(1024)).decode("utf-8")
            except:
                # print("Timeout")
                continue
            if msg=="exit":
                self.active=False
                self.con.close()
                break
            
            receiver,msg=msg.split(":")
            print(receiver,msg)
            # timestamp=datetime.datetime.now()
            now = datetime.now()
            timestamp=now.strftime("%d/%m/%Y %I:%M %p")
            msgQueue.append((username,receiver,msg,timestamp))   
    
        users.pop(username)
        connection=connection-1
        
        return
        



s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((S_IP,S_PORT))

s.settimeout(10)

forwarder=ForwarderThread("GlobalForwarder")
forwarder.start()

exiter=ExitThread("GlobalExiter",forwarder)
exiter.start()

while connection<10 and accept:
    s.listen(1)
    try:
        con, addr= s.accept()
    except:
        # print("Wait timeout")
        continue

    thread=ConnectionThread(f"Thread{connection}",con,addr)
    threads.append(thread)
    thread.start() 
    connection=connection+1

for thread in threads:
    thread.join(5)

forwarder.join(5)
exiter.join(5)