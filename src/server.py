import socket
from _thread import *
import threading
import pymongo
from datetime import datetime
from chat_room_functions import ChatRoomAgent as cra





client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chat_db"]
CHAT_ROOM_LIMIT = 10

agent = cra(db, CHAT_ROOM_LIMIT)
            
            

################ Starting a new thread ##################

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
                c.send(f"{list(agent.chat_rooms.keys())} \n".encode())
                
            elif choice == '2': # Create a new chat room
                
                current_room_id, rooms = agent.create_room(c)
                
                if current_room_id:
                    stop_message = agent.enter_room(c, rooms, current_room_id)
                    if stop_message == 'exit':
                        current_room_id = None
                    elif stop_message == 'disconnect':
                        break
                
                
            elif choice == '3': # Join an existing chat room
                current_room_id, rooms = agent.join_existing_room(c)
                    
                if current_room_id:
                    stop_message = agent.enter_room(c, rooms, current_room_id)
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



################ Setting up the server and accepting client requests ##################
            
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
        print('Connected to:', addr[0], ':', addr[1])
        
        client_handler = threading.Thread(target=threaded, args=(c, addr))
        client_handler.start()
    
        
    
if __name__ == '__main__':
    main()
    ## To run, open terminal and type "python server.py"