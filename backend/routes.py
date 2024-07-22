from Synapse_Copilot.helper import process_spec_file, \
                                populate_api_selector_icl_examples, \
                                populate_planner_icl_examples
from Synapse_Copilot.model.api_llm import ApiLLM
from flask import Blueprint, jsonify, request
from mongodb import MongoDBHandler
from dotenv import load_dotenv
from datetime import datetime
from places import Places
from bson import ObjectId
from langchain.requests import Requests
from langchain import OpenAI

# import Requests
import requests
import logging
import openai
import time
import json
import os


logger = logging.getLogger()
db = MongoDBHandler()
pl = Places()
load_dotenv()

def users_blueprint():
    users = Blueprint('users', __name__, url_prefix='/api')

    @users.route('/add-user', methods=['POST'])
    def add_user():
        try:
            response = db.add_user()
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @users.route('/me', methods=['DELETE', 'POST'])
    def me():
        email = request.json.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        if request.method == 'POST':
            display_name = request.json.get('display_name')
            refresh_token = request.json.get('refresh_token')
            access_token = request.json.get('access_token')
            update_data = {}
            if display_name:
                update_data['display_name'] = display_name
            if refresh_token:
                update_data['refresh_token'] = refresh_token
            if access_token:
                update_data['access_token'] = access_token

            try:
                user = db.update_user(email, update_data)
                if user and user.get('active', True):
                    dict_user = {
                        "id": str(user['_id']),
                        "display_name": user.get('display_name', ''),
                        "email": user['email']
                    }
                    return jsonify({"user" : dict_user}), 200
                else:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif request.method == 'DELETE':
            try:
                if db.delete_user(email):
                    return jsonify({'message': 'User deleted'}), 200
                else:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @users.route('/add-outing', methods=['POST'])
    def add_outing():
        if request.method == 'POST':
            try:
                name = request.json.get('name')
                latest_location = 'NULL'
                outing_topic = 'NULL'
                user_email = request.json.get('email')
                friend_emails = request.json.get('friend_emails')

                emails = [value for value in friend_emails.values()]
                emails.append(user_email)

                user = db.get_user(user_email)
                if not user or not user.get('active', True):
                    return jsonify({'error': 'User not found'}), 404

                existing_outing = db.find_existing_outing(name, user['_id'])
                if existing_outing:
                    return jsonify({'error': 'Outing already exists'}), 400

                outing = {
                    "name": name,
                    "created_at": datetime.utcnow(),
                    "latest_location": latest_location,
                    "outing_topic": outing_topic,
                    "creator_id": ObjectId(user['_id'])
                }

                # Insert outing document into MongoDB
                result = db.insert_outing(outing)
                outing_id = result.inserted_id

                for friend_email in emails:
                    friend = db.get_user(friend_email)
                    if friend and friend.get('active', True):
                        friend_list_entry = {
                            "outing_id": outing_id,
                            "user_id": ObjectId(friend['_id'])
                        }
                        try:
                            db.insert_friend_list_entry(friend_list_entry)
                        except Exception as e:
                            pass

                dict_outing = {
                    "id": str(outing_id),  # Convert ObjectId to string
                    "name": outing.get('name', ''),
                    "latest_location": outing.get('latest_location', ''),
                    "outing_topic": outing.get('outing_topic', ''),
                    "creator_email": user_email
                }

                return jsonify({'outing': dict_outing}), 201

            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @users.route('/get-outings', methods=['POST'])
    def get_all_outings():
        if request.method == 'POST':
            email = request.json.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400

            try:
                user = db.get_user(email)
                if not user or not user.get('active', True):
                    return jsonify({'error': 'User not found or inactive'}), 404

                user_id = user['_id']

                pipeline = [
                    {
                        '$match': {
                            'user_id': user_id
                        }
                    },
                    {
                        "$lookup": {
                            "from": "Outing",
                            "let": {
                                "oid": "$outing_id"
                            },
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$eq": ["$_id", "$$oid"]
                                        }
                                    }
                                },
                                {
                                    "$project": {
                                        "_id": 1,
                                        "name" : 1
                                    }
                                }
                            ],
                            "as": "outing_details"
                        }
                    },
                    {
                        '$unwind': '$outing_details'
                    },
                    {
                        '$project': {
                            '_id': '$outing_details._id',
                            'name': '$outing_details.name'
                        }
                    }
                ]
                friend_collection = db.db['FriendList']
                outing_data = list(friend_collection.aggregate(pipeline))
                outings_list = [{"id": str(outing['_id']), "name": outing['name']} for outing in outing_data]

                return jsonify({'outings': outings_list}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @users.route('/get-outings/<outing_id>', methods=['GET', 'POST', 'DELETE'])
    def get_outing(outing_id):

        def get_pipeline(outing_id):
            pipeline = [
                {
                    "$match": {
                        "_id": ObjectId(outing_id)
                    }
                },
                {
                    "$lookup": {
                        "from": "Messages",
                        "let": {
                            "outing_id": "$_id"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$messages_group_id", "$$outing_id"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "Message",
                                    "let": {
                                        "msg_id": "$message_id"
                                    },
                                    "pipeline": [
                                        {
                                            "$match": {
                                                "$expr": {
                                                    "$eq": ["$_id", "$$msg_id"]
                                                }
                                            }
                                        },
                                        {
                                            "$lookup": {
                                                "from": "User",
                                                "let": {
                                                    "sender_id": "$send_from"
                                                },
                                                "pipeline": [
                                                    {
                                                        "$match": {
                                                            "$expr": {
                                                                "$eq": ["$_id", "$$sender_id"]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "$project": {
                                                            "email": 1
                                                        }
                                                    }
                                                ],
                                                "as": "sender"
                                            }
                                        },
                                        {
                                            "$unwind": "$sender"
                                        },
                                        {
                                            "$project": {
                                                "content": 1,
                                                "datetime": 1,
                                                "send_from": "$sender.email"
                                            }
                                        }
                                    ],
                                    "as": "message"
                                }
                            },
                            {
                                "$unwind": "$message"
                            },
                            {
                                "$project": {
                                    "content": "$message.content",
                                    "datetime": "$message.datetime",
                                    "send_from": "$message.send_from"
                                }
                            },
                            {
                                "$sort": {
                                    "datetime": 1
                                }
                            }
                        ],
                        "as": "messages"
                    }
                },
                {
                    "$lookup": {
                        "from": "AiMessages",
                        "let": {
                            "outing_id": "$_id"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$ai_messages_group_id", "$$outing_id"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "AiMessage",
                                    "let": {
                                        "ai_msg_id": "$ai_message_id"
                                    },
                                    "pipeline": [
                                        {
                                            "$match": {
                                                "$expr": {
                                                    "$eq": ["$_id", "$$ai_msg_id"]
                                                }
                                            }
                                        },
                                        {
                                            "$lookup": {
                                                "from": "User",
                                                "let": {
                                                    "sender_id": "$send_from"
                                                },
                                                "pipeline": [
                                                    {
                                                        "$match": {
                                                            "$expr": {
                                                                "$eq": ["$_id", "$$sender_id"]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "$project": {
                                                            "email": 1
                                                        }
                                                    }
                                                ],
                                                "as": "ai_sender"
                                            }
                                        },
                                        {
                                            "$unwind": {
                                                "path": "$ai_sender",
                                                "preserveNullAndEmptyArrays": True
                                            }
                                        },
                                        {
                                            "$project": {
                                                "content": 1,
                                                "datetime": 1,
                                                "send_from": {
                                                    "$ifNull": ["$ai_sender.email", "NULL"]
                                                }
                                            }
                                        }
                                    ],
                                    "as": "ai_message"
                                }
                            },
                            {
                                "$unwind": "$ai_message"
                            },
                            {
                                "$project": {
                                    "content": "$ai_message.content",
                                    "datetime": "$ai_message.datetime",
                                    "send_from": "$ai_message.send_from"
                                }
                            },
                            {
                                "$sort": {
                                    "datetime": 1
                                }
                            }
                        ],
                        "as": "ai_messages"
                    }
                },
                {
                    "$lookup": {
                        "from": "User",
                        "localField": "creator_id",
                        "foreignField": "_id",
                        "as": "creator"
                    }
                },
                {
                    "$project": {
                        "name": 1,
                        "latest_location": 1,
                        "outing_topic": 1,
                        "messages": {
                            "$map": {
                                "input": "$messages",
                                "as": "msg",
                                "in": {
                                    "send_from": "$$msg.send_from",
                                    "content": "$$msg.content",
                                    "datetime": "$$msg.datetime"
                                }
                            }
                        },
                        "ai_messages": {
                            "$map": {
                                "input": "$ai_messages",
                                "as": "ai_msg",
                                "in": {
                                    "send_from": "$$ai_msg.send_from",
                                    "content": "$$ai_msg.content",
                                    "datetime": "$$ai_msg.datetime"
                                }
                            }
                        },
                        "creator_email": {
                            "$getField": {
                                "field": "email",
                                "input": {
                                    "$first": "$creator"
                                }
                            }
                        }
                    }
                }
            ]
            return pipeline

        if request.method == 'GET':
            try:
                outing = db.get_outing_by_id(ObjectId(outing_id))
                if not outing:
                    return jsonify({'error': 'Outing not found'}), 404

                pipeline = get_pipeline(outing_id)

                outing_collection = db.db['Outing']
                outing_data = list(outing_collection.aggregate(pipeline))[0]
                outing_data.pop('_id')

                return jsonify({"outing": outing_data}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif request.method == 'POST':
            try:
                location = request.json.get("location")
                outing_topic = request.json.get("outing_topic")

                outing = db.get_outing_by_id(ObjectId(outing_id))
                if not outing:
                    return jsonify({'error': 'Outing not found'}), 404

                if location:
                    outing['latest_location'] = location
                if outing_topic:
                    outing['outing_topic'] = outing_topic

                db.update_outing(ObjectId(outing_id), outing)
                pipeline = get_pipeline(outing_id)

                outing_collection = db.db['Outing']
                outing_data = list(outing_collection.aggregate(pipeline))[0]
                outing_data.pop('_id')

                return jsonify({"outing": outing_data}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif request.method == 'DELETE':
            try:
                outing = db.get_outing_by_id(ObjectId(outing_id))
                if not outing:
                    return jsonify({'error': 'Outing not found'}), 404

                db.delete_friend_list_entries(ObjectId(outing_id))
                db.delete_messages(ObjectId(outing_id))
                db.delete_ai_messages(ObjectId(outing_id))
                db.delete_outing(ObjectId(outing_id))

                return jsonify({'message': 'Outing deleted successfully'}), 200


            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @users.route('/get-outings/<outing_id>/get-friends', methods=['GET'])
    def get_friend_list(outing_id):
        try:
            outing = db.get_outing_by_id(ObjectId(outing_id))
            if not outing:
                return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

            pipeline = [
                {
                    "$match": {
                        "_id": ObjectId(outing_id)
                    }
                },
                {
                    "$lookup": {
                        "from": "FriendList",
                        "let": {
                            "oid": "$_id"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$outing_id", "$$oid"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "User",
                                    "localField": "user_id",
                                    "foreignField": "_id",
                                    "as": "user"
                                }
                            },
                            {
                                "$project": {
                                    "email": {
                                        "$first": "$user.email"
                                    }
                                }
                            }
                        ],
                        "as": "friends"
                    }
                },
                {
                    "$project": {
                        "friend_list": "$friends.email"
                    }
                }
            ]

            outing_collection = db.db['Outing']
            friend_list = list(outing_collection.aggregate(pipeline))[0]
            print(friend_list)
            friend_list.pop('_id')

            return jsonify(friend_list), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @users.route('/get-outings/<outing_id>/add-friend', methods=['POST'])
    def add_friend(outing_id):
        try:
            email = request.json.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400

            outing = db.get_outing_by_id(ObjectId(outing_id))
            if not outing:
                return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

            user = db.get_user(email)
            if not user or not user['active']:
                return jsonify({'error': f'User with email {email} not found'}), 404

            friend_list = db.get_friends_by_outing_id(ObjectId(outing_id))

            friend_list_data = [friend for friend in friend_list]
            friend_list_emails = [db.get_user_by_id(friend['user_id'])['email'] for friend in friend_list_data]
            if email in friend_list_emails:
                return jsonify({'error': 'Email already added'}), 400

            friend_entry = {
                'outing_id': ObjectId(outing_id),
                'user_id': ObjectId(user['_id'])
            }
            db.add_friend_to_outing(friend_entry)

            friend_list_emails.append(email)

            return jsonify({'friend_list': friend_list_emails}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @users.route('/get-outings/<outing_id>/delete-friend', methods=['DELETE'])
    def delete_friend(outing_id):
        try:
            email = request.json.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400

            outing = db.get_outing_by_id(ObjectId(outing_id))
            if not outing:
                return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

            user = db.get_user(email)
            if not user or not user['active']:
                return jsonify({'error': f'User with email {email} not found'}), 404

            friends = db.get_friends_by_outing_id(ObjectId(outing_id))
            if friends:
                for friend in friends:
                    if friend['user_id'] == user['_id']:
                        db.delete_friend_from_outing(outing_id, user['_id'])
                        return jsonify({'message': 'Friend deleted successfully'}), 200

            return jsonify({'error': 'Friend relation not found'}), 404

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @users.route('/get-outings/<outing_id>/chat', methods=['GET'])
    def get_chat(outing_id):
        try:
            outing = db.get_outing_by_id(ObjectId(outing_id))
            if not outing:
                return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

            pipeline = [
                {
                    "$match": {
                        "_id": ObjectId(outing_id)
                    }
                },
                {
                    "$lookup": {
                        "from": "Messages",
                        "let": {
                            "outing_id": "$_id"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$messages_group_id", "$$outing_id"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "Message",
                                    "let": {
                                        "msg_id": "$message_id"
                                    },
                                    "pipeline": [
                                        {
                                            "$match": {
                                                "$expr": {
                                                    "$eq": ["$_id", "$$msg_id"]
                                                }
                                            }
                                        },
                                        {
                                            "$lookup": {
                                                "from": "User",
                                                "let": {
                                                    "sender_id": "$send_from"
                                                },
                                                "pipeline": [
                                                    {
                                                        "$match": {
                                                            "$expr": {
                                                                "$eq": ["$_id", "$$sender_id"]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "$project": {
                                                            "email": 1
                                                        }
                                                    }
                                                ],
                                                "as": "sender"
                                            }
                                        },
                                        {
                                            "$unwind": "$sender"
                                        },
                                        {
                                            "$project": {
                                                "content": 1,
                                                "datetime": 1,
                                                "send_from": "$sender.email"
                                            }
                                        }
                                    ],
                                    "as": "message"
                                }
                            },
                            {
                                "$unwind": "$message"
                            },
                            {
                                "$project": {
                                    "content": "$message.content",
                                    "datetime": "$message.datetime",
                                    "send_from": "$message.send_from"
                                }
                            },
                            {
                                "$sort": {
                                    "datetime": 1
                                }
                            }
                        ],
                        "as": "messages"
                    }
                },
                {
                    "$project": {
                        "messages.content": 1,
                        "messages.datetime": 1,
                        "messages.send_from": 1
                    }
                }
            ]

            outing_collection = db.db['Outing']
            messages_data = list(outing_collection.aggregate(pipeline))[0]
            messages_data.pop('_id')

            return jsonify(messages_data), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching chat messages: {str(e)}'}), 500

    @users.route('/get-outings/<outing_id>/chat/send', methods=['POST'])
    def send_message(outing_id):
        get_all_messages = False  # Change to True if you need all messages

        if request.method == 'POST':
            try:
                outing = db.get_outing_by_id(ObjectId(outing_id))
                if not outing:
                    return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

                send_from_email = request.json.get('send_from')
                content = request.json.get('content')

                if not send_from_email or not content:
                    return jsonify({'error': 'send_from and content are required'}), 400

                user = db.get_user(send_from_email)
                if not user or not user.get('active', False):
                    return jsonify({'error': 'User not found or not active'}), 404

                friend_list = db.get_friends_by_outing_id(ObjectId(outing_id))
                friend_list_emails = [db.get_user_by_id(friend['user_id'])['email'] for friend in friend_list]
                if send_from_email not in friend_list_emails:
                    return jsonify({'error': 'User cannot send message to this outing'}), 400

                message = {
                    'send_from': ObjectId(user['_id']),
                    'datetime': datetime.utcnow(),
                    'content': content
                }
                result = db.insert_message(message)
                message_id = result.inserted_id

                message_add_to_group = {
                    'messages_group_id': ObjectId(outing_id),
                    'message_id': ObjectId(message_id)
                }
                db.insert_message_connection(message_add_to_group)

                if get_all_messages:
                    messages_list = []
                    message_connections = db.get_messages(outing_id)
                    message_connections_list = [con for con in message_connections]
                    for message_connection in message_connections_list:
                        message = db.get_message_by_id(message_connection['message_id'])
                        user = db.get_user_by_id(message['send_from'])

                        message_dict = {
                            "send_from": user['email'],
                            "content": message['content'],
                            "datetime": message['datetime'],
                        }
                        messages_list.append(message_dict)

                    sorted_messages = sorted(messages_list, key=lambda x: x['datetime'])

                    return jsonify({'messages': sorted_messages}), 200
                else:
                    message = db.get_message_by_id(message_id)
                    user = db.get_user_by_id(message['send_from'])
                    return jsonify({'messages': [{'send_from': user['email'], 'content' : message['content'], 'datetime' : message['datetime']}]}), 200

            except Exception as e:
                return jsonify({'error': f'Error sending message: {str(e)}'}), 500

    @users.route('/get-outings/<outing_id>/ai-chat', methods=['GET'])
    def get_ai_chat(outing_id):
        try:
            outing = db.get_outing_by_id(ObjectId(outing_id))
            if not outing:
                return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

            pipeline = [
                {
                    "$match": {
                        "_id": ObjectId(outing_id)
                    }
                },
                {
                    "$lookup": {
                        "from": "AiMessages",
                        "let": {
                            "outing_id": "$_id"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$ai_messages_group_id", "$$outing_id"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "AiMessage",
                                    "let": {
                                        "ai_msg_id": "$ai_message_id"
                                    },
                                    "pipeline": [
                                        {
                                            "$match": {
                                                "$expr": {
                                                    "$eq": ["$_id", "$$ai_msg_id"]
                                                }
                                            }
                                        },
                                        {
                                            "$lookup": {
                                                "from": "User",
                                                "let": {
                                                    "sender_id": "$send_from"
                                                },
                                                "pipeline": [
                                                    {
                                                        "$match": {
                                                            "$expr": {
                                                                "$eq": ["$_id", "$$sender_id"]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "$project": {
                                                            "email": 1
                                                        }
                                                    }
                                                ],
                                                "as": "ai_sender"
                                            }
                                        },
                                        {
                                            "$unwind": {
                                                "path": "$ai_sender",
                                                "preserveNullAndEmptyArrays": True
                                            }
                                        },
                                        {
                                            "$project": {
                                                "content": 1,
                                                "datetime": 1,
                                                "send_from": {
                                                    "$ifNull": ["$ai_sender.email", "NULL"]
                                                }
                                            }
                                        }
                                    ],
                                    "as": "ai_message"
                                }
                            },
                            {
                                "$unwind": "$ai_message"
                            },
                            {
                                "$project": {
                                    "content": "$ai_message.content",
                                    "datetime": "$ai_message.datetime",
                                    "send_from": "$ai_message.send_from"
                                }
                            },
                            {
                                "$sort": {
                                    "datetime": 1
                                }
                            }
                        ],
                        "as": "ai_messages"
                    }
                },
                {
                    "$project": {
                        "ai_messages.content": 1,
                        "ai_messages.datetime": 1,
                        "ai_messages.send_from": 1
                    }
                }
            ]

            outing_collection = db.db['Outing']
            ai_messages_data = list(outing_collection.aggregate(pipeline))[0]
            ai_messages_data.pop('_id')

            return jsonify(ai_messages_data), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching chat messages: {str(e)}'}), 500

    @users.route('/get-outings/<outing_id>/ai-chat/send', methods=['POST'])
    def send_ai_message(outing_id):

        if request.method == 'POST':
            try:
                outing = db.get_outing_by_id(ObjectId(outing_id))
                if not outing:
                    return jsonify({'error': f'Outing with ID {outing_id} not found'}), 404

                send_from_email = request.json.get('send_from')

                location = request.json.get('location')
                outing_topic = request.json.get('outing_topic')
                date = request.json.get('date')

                if not send_from_email or not location or not outing_topic:
                    return jsonify({'error': 'send_from and location details are required'}), 400

                user = db.get_user(send_from_email)
                if not user or not user.get('active', False):
                    return jsonify({'error': 'User not found or not active'}), 404

                if send_from_email != db.get_user_by_id(outing['creator_id'])['email']:
                    return jsonify({'error': 'Only admin can send a message to the AI!'}), 400

                pipeline = [
                    {
                        "$match": {
                            "_id": ObjectId(outing_id)
                        }
                    },
                    {
                        "$lookup": {
                            "from": "FriendList",
                            "let": {
                                "oid": "$_id"
                            },
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$eq": ["$outing_id", "$$oid"]
                                        }
                                    }
                                },
                                {
                                    "$lookup": {
                                        "from": "User",
                                        "localField": "user_id",
                                        "foreignField": "_id",
                                        "as": "user"
                                    }
                                },
                                {
                                    "$project": {
                                        "email": {
                                            "$first": "$user.email"
                                        }
                                    }
                                }
                            ],
                            "as": "friends"
                        }
                    },
                    {
                        "$project": {
                            "friend_list": "$friends.email"
                        }
                    }
                ]

                outing_collection = db.db['Outing']
                friend_dict = list(outing_collection.aggregate(pipeline))[0]
                list_of_friends = friend_dict['friend_list']
                print(list_of_friends)

                # query transformation of outing_topic
                system_message = {
                    "role" : "system",
                    "content" : """You are a helpful assistant that suggest places
                    (e.g., mountain, river, park, cinema, shop, stadium) based on the given outing topic
                    (e.g., walking, swimming, shopping)."""
                }
                examples = [
                    {
                        "role" : "user",
                        "content" : "outing_topic = hiking"
                    },
                    {
                        "role" : "assistant",
                        "content" : "mountain"
                    },
                    {
                        "role" : "user",
                        "content" : "outing_topic = shopping"
                    },
                    {
                        "role" : "assistant",
                        "content" : "shopping mall"
                    },
                    {
                        "role" : "user",
                        "content" : "outing_topic = kayaking"
                    },
                    {
                        "role" : "assistant",
                        "content" : "river"
                    },
                    {
                        "role" : "user",
                        "content" : "outing_topic = you are noob"
                    },
                    {
                        "role" : "assistant",
                        "content" : "Just chill."
                    }
                ]

                def get_suggestion(outing_topic):
                    user_prompt=f"outing_topic = {outing_topic}"

                    messages = [system_message] + examples + [{"role": "user", "content": user_prompt}]

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=50,
                        temperature=0.5,
                        stop=["\n"]
                    )

                    return response.choices[0].message['content']

                suggestion = get_suggestion(outing_topic)

                if not date:
                    content_message = f"Find nearby places in {location} related to {outing_topic}."
                    content_run = f"Find nearby places in {location} related to {suggestion}."
                    scenario = "travelspotter"

                else:
                    scenario = "calendar"
                    content = f"Create event in google calendar with this info : - date and time :{date}; - title : Meeting with my friends in {location} for {outing_topic};"


                # ai_message = {
                #     'send_from': ObjectId(user['_id']),
                #     'datetime': datetime.utcnow(),
                #     'content': content
                # }
                # result = db.insert_ai_message(ai_message)
                # ai_message_id = result.inserted_id

                # ai_message_add_to_group = {
                #     'ai_messages_group_id': ObjectId(outing_id),
                #     'ai_message_id': ObjectId(ai_message_id)
                # }
                # db.insert_ai_message_connection(ai_message_add_to_group)

                if scenario == "travelspotter":
                    populate_api_selector_icl_examples(scenario="calendar")
                    populate_planner_icl_examples(scenario="calendar")

                    llm = OpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.0, max_tokens=1024)

                    for friend_email in list_of_friends:
                        print(friend_email)
                        user = db.get_user(friend_email)
                        api_spec, headers = process_spec_file(
                            file_path="Synapse_Copilot/specs/calendar_oas.json", token=user['access_token']
                        )
                        requests_wrapper = Requests(headers=headers)

                        api_llm = ApiLLM(
                            llm,
                            api_spec=api_spec,
                            scenario="calendar",
                            requests_wrapper=requests_wrapper,
                            simple_parser=False,
                        )

                        start_time = time.time()
                        # result = api_llm.run("What events do I have for next five days!")
                        logger.info(f"Execution Time: {time.time() - start_time}")
                        print("----------------------")
                        # print(result)
                        print("----------------------")

                    # Calculate best nearby places
                    populate_api_selector_icl_examples(scenario="travelspotter")
                    populate_planner_icl_examples(scenario="travelspotter")

                    llm = OpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0, max_tokens=1024)

                    api_spec, headers = process_spec_file(
                        file_path="Synapse_Copilot/specs/travelspotter_oas.json"
                    )
                    headers = {}
                    requests_wrapper = Requests(headers=headers)

                    api_llm_maps = ApiLLM(
                        llm,
                        api_spec=api_spec,
                        scenario=scenario,
                        requests_wrapper=requests_wrapper,
                        simple_parser=False,
                        max_iterations = 1
                    )

                    start_time = time.time()
                    result = api_llm_maps.run(content_run)
                    print("///////////////")
                    print(result)
                    logger.info(f"Execution Time: {time.time() - start_time}")

                    try :
                        result_map = result.split("Get the details of the")[1].split("(ID")[0]
                    except:
                        result_map = "No location found"

                elif scenario == "calendar":
                    populate_api_selector_icl_examples(scenario=scenario)
                    populate_planner_icl_examples(scenario=scenario)

                    llm = OpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0, max_tokens=1024)

                    for friend_email in list_of_friends:
                        print(friend_email)
                        user = db.get_user(friend_email)
                        api_spec, headers = process_spec_file(
                            file_path="Synapse_Copilot/specs/calendar_oas.json", token=user['access_token']
                        )
                        requests_wrapper = Requests(headers=headers)

                        api_llm = ApiLLM(
                            llm,
                            api_spec=api_spec,
                            scenario=scenario,
                            requests_wrapper=requests_wrapper,
                            simple_parser=False,
                        )

                        start_time = time.time()
                        # result = api_llm.run(content)
                        logger.info(f"Execution Time: {time.time() - start_time}")
                        print("----------------------")
                        # print(result)
                        print("----------------------")
                else:
                    raise ValueError(f"Unsupported scenario: {scenario}")

                if not date:
                    dict_reverse = {
                        "dates" : [{"date": "01.07.2024", "time" : {"start" : "17", "finish" : "19"}}],
                        "location" : [f"{result_map}"]
                    }
                    content_reverse = f"""Possible meeting : {dict_reverse['dates'][0]['date']} from {dict_reverse['dates'][0]['time']['start']}-{dict_reverse['dates'][0]['time']['finish']} at {dict_reverse['location'][0]}"""
                else :
                    dict_reverse = {
                        "message" : f"Executing : {content}. Check you calendar for few minutes."
                    }

                    content_reverse = f"Executing : {content}. Check you calendar for few minutes."

                print("------------------------------------------------------------")
                print("             Do a parser for giving a json file             ")
                print("------------------------------------------------------------")

                # ai_message_reverse = {
                #     'send_from': "NULL",
                #     'datetime': datetime.utcnow(),
                #     'content': content_reverse
                # }
                # result_reverse = db.insert_ai_message(ai_message_reverse)
                # ai_message_reverse_id = result_reverse.inserted_id
                #
                # ai_message_reverse_add_to_group = {
                #     'ai_messages_group_id': ObjectId(outing_id),
                #     'ai_message_id': ObjectId(ai_message_reverse_id)
                # }
                # db.insert_ai_message_connection(ai_message_reverse_add_to_group)

                return jsonify(dict_reverse), 200

            except Exception as e:
                return jsonify({'error': f'Error sending message: {str(e)}'}), 500

    return users


def places_blueprint():
    places = Blueprint('places', __name__, url_prefix='/api')

    @places.route('/nearby_places', methods=['POST'])
    def get_nearby_places():

        try:
            req = request.get_json()
            address = req["address"]
            place_type = req["ptype"]

            lat_lng = pl.get_latitude_longitude(address)
            print(lat_lng)

            response = pl.get_nearby_places(lat_lng, place_type)

            data = response.json()
            return jsonify({'results': data['results']}), response.status_code

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return places
