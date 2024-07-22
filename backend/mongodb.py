import os
from pymongo import MongoClient
from flask import request, jsonify
from dotenv import load_dotenv
import json
from bson.json_util import loads
from bson.objectid import ObjectId
load_dotenv()

class MongoDBHandler:
    def __init__(self):
        self.client = self.connect()
        self.db = self.client.devpost

    def connect(self):
        uri = os.getenv('connection_uri')
        if not uri:
            raise Exception("No MongoDB connection URL found in environment variables")
        client = MongoClient(uri)

        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise e

        return client

    def add_user(self):
        req = request.get_json()
        if not req or 'email' not in req:
            return jsonify({"error": "Invalid request payload"}), 400

        email = req.get('email')
        display_name = req.get('name')
        refresh_token = req.get('refresh_token')
        access_token = req.get('access_token')

        result = self.db.User.find_one({"email": email})
        if result:
            return jsonify({"error": "User already exists"}), 403

        user = ({
            "email": email,
            "display_name": display_name,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "active" : True
        })

        self.db.User.insert_one(user)

        created_user = self.db.User.find_one({"email": email})
        if created_user:
            dict_user = {
                "id": str(created_user['_id']),
                "display_name" : created_user.get('display_name', ''),
                "email" : created_user['email']
            }
            return jsonify({'user': dict_user}), 201
        else : return jsonify({"error": "Something went wrong!"}), 500

    def get_user(self, email):
        return self.db.User.find_one({"email": email})

    def update_user(self, email, update_data):
        return self.db.User.find_one_and_update(
            {"email": email},
            {"$set": update_data},
            return_document=True
        )

    def delete_user_data(self, user_id):
        self.db.FriendList.delete_many({"user_id": ObjectId(user_id)})
        # self.db.Message.delete_many({"send_from": user_id})
        # self.db.AiMessage.delete_many({"send_from": user_id})
        self.db.User.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"active": False}}
        )

    def delete_user(self, email):
        user = self.get_user(email)
        if user:
            self.delete_user_data(user['_id'])
            return True
        return False

    def insert_outing(self, outing):
        return self.db.Outing.insert_one(outing)

    def find_existing_outing(self, name, creator_id):
        return self.db.Outing.find_one({"name": name, "creator_id": creator_id})

    def insert_friend_list_entry(self, friend_list_entry):
        return self.db.FriendList.insert_one(friend_list_entry)

    def get_outings_for_user(self, user_id):
        return self.db.Outing.find({"creator_id": ObjectId(user_id)})

    def get_friend_outings(self, user_id):
        friend_outings = self.db.FriendList.find({"user_id": ObjectId(user_id)})
        outing_ids = [entry['outing_id'] for entry in friend_outings]
        return self.db.Outing.find({"_id": {"$in": outing_ids}})

    def get_user_by_id(self, user_id):
        return self.db.User.find_one({'_id': user_id})

    def get_outing_by_id(self, outing_id):
        return self.db.Outing.find_one({'_id': outing_id})

    def update_outing(self, outing_id, outing_data):
        self.db.Outing.update_one({'_id': ObjectId(outing_id)}, {'$set': outing_data})

    def delete_friend_list_entries(self, outing_id):
        self.db.FriendList.delete_many({'outing_id': ObjectId(outing_id)})

    def delete_messages(self, outing_id):
        self.db.Messages.delete_many({'messages_group_id': ObjectId(outing_id)})

    def delete_ai_messages(self, outing_id):
        self.db.AiMessages.delete_many({'ai_messages_group_id': ObjectId(outing_id)})

    def delete_outing(self, outing_id):
        self.db.Outing.delete_one({'_id': ObjectId(outing_id)})

    def get_friends_by_outing_id(self, outing_id):
        return self.db.FriendList.find({'outing_id': outing_id})

    def add_friend_to_outing(self, friend_entry):
        return self.db.FriendList.insert_one(friend_entry)

    def delete_friend_from_outing(self, outing_id, user_id):
        return self.db.FriendList.delete_one({'outing_id': ObjectId(outing_id), 'user_id': ObjectId(user_id)})

    def insert_message(self, message):
        return self.db.Message.insert_one(message)

    def insert_message_connection(self, message_connection):
        return self.db.Messages.insert_one(message_connection)

    def insert_ai_message(self, ai_message):
        return self.db.AiMessage.insert_one(ai_message)

    def insert_ai_message_connection(self, ai_message_connection):
        return self.db.AiMessages.insert_one(ai_message_connection)

    def get_messages(self, outing_id):
        return self.db.Messages.find({'messages_group_id': ObjectId(outing_id)})
    def get_message_by_id(self, message_id):
        return self.db.Message.find_one({'_id': ObjectId(message_id)})
    def get_ai_messages(self, outing_id):
        return self.db.AiMessages.find({'ai_messages_group_id': ObjectId(outing_id)})
    def get_ai_message_by_id(self, ai_message_id):
        return self.db.AiMessage.find_one({'_id': ObjectId(ai_message_id)})






    def get_chats(self):
        # req = request.get_json()
        # if not req or 'oid' not in req:
        #     return jsonify({"error": "Invalid request payload"}), 400

        # oid = req['oid']
        oid = request.headers.get('oid')
        # if not oid:
        #     return jsonify({"error": "Invalid request payload"}), 400
        result = self.db.chats.find({"oid": oid})
        result = loads(json.dumps(list(result), default=str))

        return list(result)

    def add_chat(self):
        req = request.get_json()
        if not req or 'oid' not in req or 'token' not in req or 'message' not in req:
            return jsonify({"error": "Invalid request payload"}), 400

        oid = req['oid']
        token = req['token']
        message = req['message']

        result = self.db.chats.find_one({"oid": oid})

        if result and result['token'] != token:
            return jsonify({"error": "Unauthorized access"}), 401

        if not result:
            messages = [message]
            self.db.chats.insert_one({"oid": oid, "token": token, "messages": messages})
        else:
            result['messages'].append(message)
            self.db.chats.update_one({"oid": oid}, {"$set": {"messages": result['messages']}})


    def get_role(self):
        try:
            db = self.client.Main.users
            req = request.get_json()
            if not req or 'uid' not in req:
                return jsonify({"error": "Invalid request payload"}), 400

            uid = req['uid']
            result = db.find_one({"user_id": uid})
            if not result:
                return jsonify({"error": "User not found"}), 404

            return jsonify({'role': result['role']}), 200
        except Exception as e:
            print(f"Error occurred: {e}")
            return jsonify({"error": "An error occurred"}), 500
        # finally:
        #     if self.client:
        #         self.client.close()

    def get_users(self):
        result = self.db.users.find()
        return loads(json.dumps(list(result), default=str))

    def get_outings(self):
        email = request.headers.get('email')
        result = self.db.users.find({"email": email})
        return loads(json.dumps(list(result), default=str))
