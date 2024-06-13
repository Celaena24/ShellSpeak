import socket
import threading


def receive_messages(s):
    try:
        while True:
            data = s.recv(1024).decode()
            print(data)
    except:
        print("Bye!")

    

def main():
    # host = '127.0.0.1'
    host = 'localhost'
    port = 12345
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    try:
        receive_thread = threading.Thread(target=receive_messages, args=(s, ))
        receive_thread.start()
        
        while True:
            message = input("->")
            s.send(message.encode())
            if message == 'disconnect':
                break
            
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("Closing client socket.")
        s.close()

    
if __name__ == '__main__':
    main()
    ## To run, open terminal and type "python client.py"