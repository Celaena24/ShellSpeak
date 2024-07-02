import socket
from _thread import *
import threading
import pymongo
from datetime import datetime
import os
import json


# chat_rooms = {'id_1': [client1, client2], 'id_2': []}
CHAT_ROOM_LIMIT = 2
chat_rooms = {}
chat_rooms_private = {}
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chat_db"]

############################ Handling Config files

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def get_username(user_id):
    config = load_config()
    return config.get(user_id)

def save_username(user_id, username):
    config = load_config()
    config[user_id] = username
    save_config(config)




###################################### Saving chat history 


def save_chat_message(room_id, user, message):
    col = db[f"chat_history_{room_id}"]
    chat_message = {
        "timestamp": datetime.now(),
        "user": user,
        "message": message
    }
    col.insert_one(chat_message)
    
    
def get_chat_history(room_id):
    chat = db[f"chat_history_{room_id}"]
    messages = chat.find().sort("timestamp")
    return list(messages)



def enter_room(c, addr, rooms, current_room_id):
    stop_message = ''
    
    if current_room_id != None:
        c.send(f"You've been added to chat room {current_room_id}. Write 'exit' to disconnect from the chat room and 'disconnect' to disconnect from the server".encode())
        
        c.send("\nEnter your user ID: ".encode())
        user_id = c.recv(1024).decode()
        user = get_username(user_id)
        if not user:
            c.send("\nEnter your username: ".encode())
            user = c.recv(1024).decode()
            save_username(user_id, user)
            c.send(f"Welcome {user}!".encode())
        else:
            c.send(f"Welcome back, {user}!".encode())
            
        # Display previous chat history
        history = get_chat_history(current_room_id)
        for msg in history:
            timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            c.send(f"\n[{timestamp}] {msg['user']}: {msg['message']}".encode())
            
        clients_list = rooms[current_room_id]
            
        while True:
            message = c.recv(1024).decode()
            if message == 'disconnect' or message == 'exit':
                stop_message = message
                c.send("You have left the chat room. Bye!".encode())
                # print_lock.release()
                break
            
            save_chat_message(current_room_id, user, message)
            for client in clients_list:
                if client != c:
                    client.send(f"{addr[1]}: {message}".encode())
            
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
                while True:
                    c.send("Enter the chat room id: ".encode())
                    current_room_id = c.recv(1024).decode()
                    c.send("Is the chat room private? y/n".encode())
                    priv = c.recv(1024).decode()
                    
                    if priv == 'y':
                        rooms = chat_rooms_private
                    else:
                        rooms = chat_rooms
                        
                    if current_room_id in rooms:
                        c.send("The room already exists. Do you want to give a different room id? y/n".encode())
                        keep_going = c.recv(1024).decode()
                        if keep_going != 'y':
                            current_room_id = None
                            break
                    else:
                        break
                
                if current_room_id:
                    rooms[current_room_id] = [c]
                    c.send(f"Created new chat room {current_room_id}".encode())
                    
                    stop_message = enter_room(c, addr, rooms, current_room_id)
                    if stop_message == 'exit':
                        current_room_id = None
                    elif stop_message == 'disconnect':
                        break
                
            elif choice == '3': # Join an existing chat room
                c.send("Enter the chat room id: ".encode())
                chat_id = c.recv(1024).decode()
                all_rooms = {**chat_rooms_private, **chat_rooms}
                
                if chat_id not in all_rooms.keys():
                    c.send("The chat room does not exist. ".encode())
                elif len(all_rooms[chat_id]) == CHAT_ROOM_LIMIT:
                    c.send("Chat room limit reached. ".encode())
                else:   
                    current_room_id = chat_id
                    if current_room_id in chat_rooms:
                        rooms = chat_rooms
                    elif current_room_id in chat_rooms_private:
                        rooms = chat_rooms_private
                    
                    rooms[current_room_id].append(c)   
                    stop_message = enter_room(c, addr, rooms, current_room_id)
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