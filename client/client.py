import socket
import os

def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    # raise NotImplementedError('Your implementation here.')
    message=bytearray()
    while True:
        packet=active_socket.recv(buffer_size)
        if packet[-len(eof_token):]==eof_token:
            message+=packet[:-len(eof_token)]
            break
        message+=packet
    return message



def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """

    # print('Connected to server at IP:', host, 'and Port:', port)
    # print('Handshake Done. EOF is:', eof_token)
    #raise NotImplementedError('Your implementation here.')

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print('Connected to server at IP:', host, 'and Port:', port)
    EOF = s.recv(10)
    print('Handshake Done. EOF is:', EOF.decode())

    message = receive_message_ending_with_token(s, 1024, EOF)
    print('CWD of server is '+message.decode())
    return s,EOF


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    #raise NotImplementedError('Your implementation here.')
    client_socket.sendall((command_and_arg).encode()+eof_token)
    resp=receive_message_ending_with_token(client_socket,1024,eof_token)
    print(resp.decode())

def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall(command_and_arg.encode()+eof_token)
    resp = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(resp.decode())

def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    #raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode()+eof_token)
    resp = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(resp.decode())


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    #raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode()+eof_token)
    list = command_and_arg.split()
    with open(list[1], 'rb') as f:
        file_content = f.read()

    file_content+=eof_token

    client_socket.sendall(file_content)
    resp = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(resp.decode())


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """
    client_socket.sendall(command_and_arg.encode()+eof_token)
    list = command_and_arg.split()
    resp=receive_message_ending_with_token(client_socket, 1024, eof_token)
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script, list[1])

    with open(my_filename, "wb") as f:
        f.write(resp)

    resp = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(resp.decode())

def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65413 # The port used by the server

    # initialize
    s, EOF = initialize(HOST, PORT)
    # call the corresponding command function or exit
    while True:
        command=input("Please enter the command you want to execute ")
        list = command.split()
        if(list[0]=='cd'):
            issue_cd(command,s,EOF)
        elif(list[0]=='mkdir'):
            issue_mkdir(command,s,EOF)
        elif(list[0]=='rm'):
            issue_rm(command,s,EOF)
        elif(list[0]=='ul'):
            issue_ul(command,s,EOF)
        elif(list[0]=='dl'):
            issue_dl(command,s,EOF)
        elif(list[0]=='exit'):
            print('Exiting the application.')
            s.close()
            break


if __name__ == '__main__':
    main()