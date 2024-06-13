import socket
import threading


def receive_messages(s):
    while True:
        data = s.recv(1024).decode()
        print(data)

    

def main():
    # host = '127.0.0.1'
    host = 'localhost'
    
    port = 12345
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.connect((host, port))
    
    
    receive_thread = threading.Thread(target=receive_messages, args=(s, ))
    receive_thread.start()
    
    while True:
        message = input("->")
        s.send(message.encode())
        # data = s.recv(1024).decode()
        # print(data)

    
if __name__ == '__main__':
    main()
    ## To run, open terminal and type "python client1.py"