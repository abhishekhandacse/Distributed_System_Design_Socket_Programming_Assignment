import socket
import string
from threading import Thread
import os
from pathlib import Path
import secrets


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    alphabet = string.ascii_letters + string.digits
    eof_token = ''.join(secrets.choice(alphabet) for i in range(8))
    eof_token='<'+ eof_token+'>'
    return eof_token.encode()
    #raise NotImplementedError('Your implementation here.')
    #return '<12345678>'.encode()

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


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    os.chdir(current_working_directory)
    os.chdir(new_working_directory)
    current_working_directory=os.getcwd()
    return os.getcwd()


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    mode = 0o666
    path = os.path.join(current_working_directory, directory_name)
    os.mkdir(path,mode)

def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    path=os.path.join(current_working_directory, object_name)
    isFile = os.path.isfile(path)
    if(isFile==True):
        os.remove(object_name)
    else:
        isdir= os.path.isdir(object_name)
        if(isdir):
            os.rmdir(object_name)


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """
    #raise NotImplementedError('Your implementation here.')

    resp=receive_message_ending_with_token(service_socket,1024,eof_token)
    with open(file_name, 'wb') as f:
        f.write(resp)

def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    with open(file_name, 'rb') as f:
        file_content = f.read()
    file_content += eof_token
    service_socket.sendall(file_content)

class ClientThread(Thread):

    def __init__(self, service_socket : socket.socket, address : str, client_number:int, cwd):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address
        self.client_number=client_number
        self.cwd=cwd
    def run(self):
        print ("Connection from : ", self.address)

        # initialize the connection
        # send random eof token
        EOF=generate_random_eof_token()
        self.service_socket.sendall(EOF)
        # establish working directory
        print('the cwd is '+self.cwd +" the client number is"+str(self.client_number) )
        # send the current dir info
        self.service_socket.sendall(str.encode(self.cwd)+EOF)
        while True:
            data = receive_message_ending_with_token(self.service_socket,1024,EOF)
            if not data:
                break
            # get the command and arguments and call the corresponding method
            list = data.decode().split()
            if(list[0]=='cd'):
                self.cwd=handle_cd(self.cwd,list[1])
            elif(list[0] =='mkdir'):
                handle_mkdir(self.cwd,list[1])
            elif (list[0] == 'rm'):
                handle_rm(self.cwd,list[1])
            elif (list[0] == 'ul'):
                handle_ul(self.cwd,list[1],self.service_socket,EOF)
            elif (list[0] == 'dl'):
                handle_dl(self.cwd,list[1],self.service_socket,EOF)
            elif(list[0] == 'exit'):
                self.service_socket.close()
                break
            # send current dir info
            self.service_socket.sendall(get_working_directory_info(os.path.abspath(self.cwd)).encode() + EOF)

        print('Connection closed from:', self.address)

def main():
    HOST = "127.0.0.1"
    PORT = 65420
    client_number=0
    path=os.getcwd()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            client_thread=ClientThread(conn, addr,client_number,path)
            client_thread.start()
            print("The Client Number is ",str(client_number) )
            client_number=client_number+1

if __name__ == '__main__':
    main()


