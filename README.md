# TCP-Chat-System

I have implemented a very basic Chat system in Python. It consists of 2 parts `server.py` and `client.py`.

## Features

1. This Chat application is Multi-threaded. Every new connection is handeled by new thread. 
2. It buffers messages for those users who are not connected and sends them when they connect.
3. When a new user is connected, every user is notified about it.
4. The receiver gets additional information like Sender's username, IP address and time with message.

Server runs on `127.0.0.1:1234` and the client can run on any IP provided by the user before running the script.

Note that you have to give IP address of client as a command argument in terminal
`(eg. python client.py 127.0.0.7)
