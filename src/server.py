import socket
from _thread import *
import threading

# chat_rooms = {'id_1': [], 'id_2': []}
chat_rooms = {}

def enter_room(c, addr, current_room_id):
    stop_message = ''
    
    if current_room_id != None:
        c.send(f"You've been added to chat room {current_room_id}. Write 'exit' to disconnect from the chat room and 'disconnect' to disconnect from the server".encode())
        clients_list = chat_rooms[current_room_id]
            
        while True:
            data = c.recv(1024).decode()
            if data == 'disconnect' or data == 'exit':
                stop_message = data
                c.send("You have left the chat room. Bye!".encode())
                # print_lock.release()
                break
            
            for client in clients_list:
                if client != c:
                    client.send(f"{addr[1]}: {data}".encode())
            
        clients_list.remove(c)   
    return stop_message
    

def threaded(c, addr):
    current_room_id = None
    try:
        while True:
            c.send("Choose an option: ".encode())
            c.send('''
                1. List all existing chat rooms
                2. Create a new chat room
                3. Join an existing chat room
                
            Write "disconnect" to disconnect from the server
            '''.encode())
            
            choice = c.recv(1024).decode()
            
        
            if choice == '1': # List all existing chat rooms
                c.send("Listing existing chat rooms".encode())
                c.send(f"{list(chat_rooms.keys())} \n".encode())
                
            elif choice == '2': # Create a new chat room
                chat_id = str(len(chat_rooms)+1)
                chat_rooms[chat_id] = [c]
                current_room_id = chat_id
                c.send(f"Created new chat room {current_room_id}".encode())
                stop_message = enter_room(c, addr, current_room_id)
                if stop_message == 'exit':
                    current_room_id = None
                elif stop_message == 'disconnect':
                    break
                
            elif choice == '3': # Join an existing chat room
                c.send("Enter the chat room id: ".encode())
                chat_id = c.recv(1024).decode()
                if chat_id not in chat_rooms.keys():
                    c.send("The chat room does not exist. ".encode())
                else:    
                    chat_rooms[chat_id].append(c)
                    current_room_id = chat_id
                    stop_message = enter_room(c, addr, current_room_id)
                    if stop_message == 'exit':
                        current_room_id = None
                    elif stop_message == 'disconnect':
                        break
                    
            elif choice == 'disconnect':
                break
                
            else:
                c.send("invalid option".encode())
    
    except ConnectionResetError:
        print("Client forcibly closed the connection.")
    finally:
        print("Closing client socket.")
        print(f"Bye {addr[1]}")
        c.close()
        
            
def main():
    host = ""
    
    port = 12345
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)
    
    
    s.listen(5) 
    print("socket is listening")       
    
    while True:
        c, addr = s.accept()
        # print_lock.acquire()
        print('Connected to:', addr[0], ':', addr[1])
        
        client_handler = threading.Thread(target=threaded, args=(c, addr))
        client_handler.start()
    
        
    
if __name__ == '__main__':
    main()
    
    ## To run, open terminal and type "python server.py"