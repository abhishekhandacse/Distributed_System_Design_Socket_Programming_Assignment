# Distributed_System_Design_Socket_Programming_Assignment

Department of Computer Science & Software Engineering
COMP6231 Fall 2022
Assignment 1:
Socket Programming
Problem Description
In this programming assignment, you will implement a simple version of an interactive remote
terminal application with sockets in Python. The application uses the client-server architecture,
where a central server listens to upcoming connections from one or more clients. A client sends
the user's command to the server, which executes it and displays back the Current Working
Directory (CWD) to the client with the latest changes, if any. Figure 1 shows a flow chart of both
the server and client.
Figure 1: Flow chart of the server and client.
2
Server: The server initializes its socket and internal variables and awaits upcoming connections
from clients. When a client connects to the designated socket (pre-defined), the server handles
the connection in a new thread and awaits connections from other clients. In the client thread,
the server and client interact with each other to execute the upcoming client commands until the
client terminates. When initializing the connection, the server sends the client a random token of
size 10 bytes, which both the client and server will use to indicate the end of their messages
(EOF). The server sends the CWD info to the client before receiving each command. To support
multiple clients, the server maintains a cwd variable per client.
Client: The client initializes its internal variables, establishes a connection to the designated
server socket, gets the random EOF token, and awaits the user's command. Before each
command, the client displays the received CWD info from the server to the user. After the server
has executed the command and sent back the latest directory info, the client displays it to the
user and awaits the next command. If the user enters the exit command, the client terminates
the connection exits gracefully. For simplicity of our application, we assume a fixed current
working directory on the client, i.e. the user might upload/download files to/from the CWD on
the server (mutable), but these files are uploaded/downloaded from/to the directory where the
client script is executed (immutable).
In this assignment, you will implement the following functionalities on both the client and server:
Command Functionality Example
cd Changes the current working directory on the
server to a parent or child directory.
cd products
cd ..
mkdir Creates a new directory on the server inside the
current working directory.
mkdir client_1_files
rm Removes a file or directory from the current
working directory on the server.
rm about.txt
rm animals
ul Uploads a file from the client to the current
working directory on the server.
ul orca.jpg
dl Downloads a file from the current working
directory on the server to the client.
dl about.txt
exit Exits the applications. exit
You are given a client template and a server template, your task is to fill-in the missing code
indicated by a raised NotImplementedError. Along with the client, you are given sample
files. After implementing the missing functionalities, your code should be able to create the
following directory tree at the server (next to server.py):
3
For all messages between the server and client, use a buffer (packet) size of 1024 bytes. Start
by implementing the helper methods in both the client and server. Then implement the main
methods that contain the logics of the client and server, including multi-threading the server.
Finally, implement the different methods corresponding to each command on both the client and
server.
