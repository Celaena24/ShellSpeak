from datetime import datetime
from config import get_username, save_username


# chat_rooms = {'id_1': [client1, client2], 'id_2': []}


class ChatRoomAgent:
    def __init__(self, db, CHAT_ROOM_LIMIT):
        self.CHAT_ROOM_LIMIT = CHAT_ROOM_LIMIT
        self.db = db
        self.chat_rooms = {}
        self.chat_rooms_private = {}
        
        
        
    ################ Saving chat history ##################

    def save_chat_message(self, room_id, user, message):
        col = self.db[f"chat_history_{room_id}"]
        chat_message = {
            "timestamp": datetime.now(),
            "user": user,
            "message": message
        }
        col.insert_one(chat_message)
        
        
    
    ################ Getting chat history ##################
        
    def get_chat_history(self, room_id):
        chat = self.db[f"chat_history_{room_id}"]
        messages = chat.find().sort("timestamp")
        return list(messages)



    ################ Entering room ##################

    def enter_room(self, c, rooms, current_room_id):
        stop_message = ''
        
        if current_room_id != None:
            c.send(f"You've been added to chat room {current_room_id}. Write 'exit' to disconnect from the chat room and 'disconnect' to disconnect from the server".encode())
            
            
            # Check for user_id and save username
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
            history = self.get_chat_history(current_room_id)
            for msg in history:
                timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                c.send(f"\n[{timestamp}] {msg['user']}: {msg['message']}".encode())
                
            clients_list = rooms[current_room_id]
            
            
            # Messaging starts
            while True:
                message = c.recv(1024).decode()
                
                #exiting chat room
                if message == 'disconnect' or message == 'exit':
                    stop_message = message
                    c.send("You have left the chat room. Bye!".encode())
                    break
                
                self.save_chat_message(current_room_id, user, message)
                self.broadcast(c, clients_list, user, message)
                
            clients_list.remove(c)   
            
        return stop_message




    ################ Broadcasting messages to other clients ##################

    def broadcast(self, c, clients_list, user, message):
        for client in clients_list:
            if client != c:
                client.send(f"{user}: {message}".encode())
                
                
                
                           
        
    ################ Creating new chat room ##################
        
    def create_room(self, c):
        current_room_id = None
        while True:
            c.send("Enter the chat room id: ".encode())
            current_room_id = c.recv(1024).decode()
            c.send("Is the chat room private? y/n".encode())
            priv = c.recv(1024).decode()
            
            if priv == 'y':
                rooms = self.chat_rooms_private
            else:
                rooms = self.chat_rooms
                
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
            
        return current_room_id, rooms


    
    
    ################ Joining existing chat room ##################
    
    def join_existing_room(self, c):
        current_room_id = None
        rooms = None
        c.send("Enter the chat room id: ".encode())
        chat_id = c.recv(1024).decode()
        all_rooms = {**self.chat_rooms_private, **self.chat_rooms}
        
        if chat_id not in all_rooms.keys():
            c.send("The chat room does not exist. ".encode())
        elif len(all_rooms[chat_id]) == self.CHAT_ROOM_LIMIT:
            c.send("Chat room limit reached. ".encode())
        else:   
            current_room_id = chat_id
            if current_room_id in self.chat_rooms:
                rooms = self.chat_rooms
            elif current_room_id in self.chat_rooms_private:
                rooms = self.chat_rooms_private
                
            rooms[current_room_id].append(c)  
            
        return current_room_id, rooms
                
        
        
        

            

