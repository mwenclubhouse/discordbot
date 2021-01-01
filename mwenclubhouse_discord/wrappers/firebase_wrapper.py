import os
import firebase_admin
from firebase_admin import storage
from firebase_admin.firestore import firestore

firebase_admin.initialize_app()


class FirebaseWrapper:

    def __init__(self):
        discord_id = os.getenv('DISCORD_BOT_ID')
        bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        self.fireDb = firestore.Client().collection(u'discord').document(discord_id)
        self.fire_storage = storage.bucket(bucket_name)
        self.fireDb.set({}, merge=True)

    def user_collection(self, user_id):
        return self.fireDb.collection("users").document(user_id)

    def get_discord_config(self):
        response = self.fireDb.get().to_dict()
        return {} if response is None else response

    def set_discord_config(self, item):
        self.fireDb.set(item, merge=True)

    def get_user_end_time(self, author_id):
        items = self.fireDb.get().to_dict()
        if 'end-time' in items:
            end_time = items['end-time']
            if str(author_id) in end_time:
                return end_time[str(author_id)]
        return None

    def get_user(self, user_id):
        snapshot = self.get_user_snapshot(user_id).get()
        if snapshot.exists:
            return snapshot.to_dict()
        return {}

    def get_user_snapshot(self, user_id):
        return self.user_collection(str(user_id))

    def set_channel(self, user_id, channel_id, status=True):
        new_data = {'channels': {str(channel_id): status}}
        self.get_user_snapshot(user_id).set(new_data, merge=True)

    def set_property(self, user_property, user_id, property_value):
        new_data = {user_property: property_value}
        self.get_user_snapshot(user_id).set(new_data, merge=True)

    def get_property(self, user_property, user_id, default=None):
        user = self.get_user(user_id)
        return user[user_property] if user_property in user else default

    def upload_selection(self, key, user_id, category):
        new_data = {key: category}
        self.get_user_snapshot(user_id).set(new_data, merge=True)

    def select_by_idx(self, key, user_id, idx):
        response = self.get_user(user_id)
        location = response[key] if key in response else []
        return location[idx] if idx < len(location) else None

    def clear_selected(self, key, user_id):
        self.get_user_snapshot(user_id).set({key: []}, merge=True)

    def is_bot_channel(self, channel_id, key_text_channel):
        config = self.get_discord_config()
        if key_text_channel in config:
            return channel_id == int(config[key_text_channel])
        return False

    def is_admin(self, author_id):
        config = self.get_discord_config()
        if config is None:
            return False
        return config['admin'] == author_id if 'admin' in config else False

    def get_blob(self, file_path):
        return self.fire_storage.get_blob(file_path)

    def get_file(self, file_path):
        if self.fire_storage.blob(file_path).exists():
            return self.get_blob(file_path).download_as_bytes()
        return None

    def upload_file(self, file_path, content):
        blob = self.fire_storage.blob(file_path)
        blob.upload_from_string(content, content_type="application/octet-stream")
