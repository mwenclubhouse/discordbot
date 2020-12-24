import os
import firebase_admin
from firebase_admin import firestore

firebase_admin.initialize_app()


class FirebaseWrapper:

    def __init__(self):
        discord_id = os.getenv('DISCORD_BOT_ID')
        self.fireDb = firestore.firestore.Client().collection(u'discord').document(discord_id)

    def user_collection(self, user_id):
        return self.fireDb.collection("users").document(user_id)

    def get_discord_config(self):
        return self.fireDb.get().to_dict()

    def get_user(self, user_id):
        return self.user_collection(str(user_id)).get().to_dict()

    def set_channel(self, user_id, channel_id, status=True):
        new_data = {'channels': {str(channel_id): status}}
        self.user_collection(str(user_id)).set(new_data, merge=True)

    def set_location(self, user_id, channel_id):
        new_data = {'location': channel_id}
        self.user_collection(str(user_id)).set(new_data, merge=True)

    def get_location(self, user_id):
        user = self.get_user(user_id)
        return user['location'] if 'location' in user else ''

    def upload_ls(self, user_id, category):
        category = [i.id for i in category]
        new_data = {'ls': category}
        self.user_collection(str(user_id)).set(new_data, merge=True)

    def select_by_idx(self, user_id, idx):
        response = self.user_collection(str(user_id)).get().to_dict()
        location = response['ls'] if 'ls' in response else []
        return location[idx] if idx < len(location) else None

    def clear_selected(self, user_id):
        self.user_collection(str(user_id)).set({'ls': []}, merge=True)

    def is_bot_channel(self, channel_id):
        config = self.get_discord_config()
        if 'bot-command' in config:
            return channel_id == config['bot-command']
        return False
