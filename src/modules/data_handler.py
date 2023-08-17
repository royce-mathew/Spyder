import discord
import json
import plyvel
import pickle

# Initialize Variables
valid_guild_keys: dict = {
    "fact_channel_id": 0,
    "role_messages": [
        # Role message id
    ],
    "stats_channel_id": 0,
    "stats_message_id": 0,
    "fact_channel_id": 0,
    "chatlogs_channel_id": 0,
    "moderation_logs_channel_id": 0,
    "prefix": "!",
    "terms_and_conditions": "",
}

# Start Databases
user_db = plyvel.DB("./data/user_data", create_if_missing=True)
guild_data = plyvel.DB("./data/guild_data", create_if_missing=True)
print("Started Databases")

# with user_data.snapshot() as snap:
#     for key, value in snap:
#         print(f"LL{key} : {pickle.loads(value)}\n")

# with guild_data.snapshot() as snap:
#     for key, value in snap:
#         print(f"{key} : {pickle.loads(value)}\n")

# Exceptions


class GuildNotInitialized(Exception):
    "Raised when the Guild's Data is not initialized"
    pass


class UserNotInitalized(Exception):
    "Raised when the User's Data is not initialized"
    pass


class UserData:
    def get_user_data(user_id: str) -> dict:
        if (local_data := user_db.get(user_id.encode(), default=None)) is not None:
            return pickle.loads(local_data)
        else:
            raise UserNotInitalized

    def set_user_data(user_id: str, key: str, value) -> None:
        try:
            local_data = UserData.get_user_data(user_id)  # Get the user data
        except UserNotInitalized:
            local_data = {}
        finally:
            local_data[key] = value
            # Set value at keyy
            serialized_value = pickle.dumps(local_data)  # Serialize Dictionary
            user_db.put(user_id.encode(), serialized_value)  # Put value in database


class GuildData:
    def _get_guild_data(guild_id_bytes: bytes) -> dict:
        if (local_data := guild_data.get(guild_id_bytes, default=None)) is not None:
            return pickle.loads(local_data)
        else:
            raise GuildNotInitialized

    def get_guild_data(guild_obj: discord.Guild) -> dict:
        str_id = str(guild_obj.id).encode()  # Convert guild id to bytes
        return GuildData._get_guild_data(str_id)

    def get_guild_data_from_id(guild_id: int) -> dict:
        str_id = str(guild_id).encode()
        return GuildData._get_guild_data(str_id)

    def initialize_guild(guild_obj: discord.Guild):
        try:
            GuildData.get_guild_data(guild_obj)  # Get the user data
        except GuildNotInitialized:  #  Create new entry
            local_data = {}

            # Deep Copy
            for key, value in valid_guild_keys.items():
                local_data[key] = value
                # Set default value at key

            serialized_value = pickle.dumps(local_data)  # Serialize Dictionary
            guild_data.put(str(guild_obj.id).encode(), serialized_value)  # Put value in database

    def edit_guild_settings(guild_obj: discord.Guild, edit_info: dict) -> bool:
        local_data = GuildData.get_guild_data(guild_obj)

        for key, value in edit_info.items():  # Type check things
            if key in valid_guild_keys:
                if type(valid_guild_keys[key]) == int:
                    try:
                        value = int(value)
                        local_data[key] = value
                    except:
                        return False
                        # Error in Value Type
                elif type(valid_guild_keys[key]) == list:
                    try:
                        local_data[key].append(value)
                    except AttributeError:
                        local_data[key] = [value]
                else:
                    local_data[key] = value
            else:
                return False
                # Invalid Key

        serialized_value = pickle.dumps(local_data)  # Serialize Dictionary
        guild_data.put(str(guild_obj.id).encode(), serialized_value)  # Put value in database
        return True
        # Return Success

    def get_value(guild_obj: discord.Guild, key: str):
        local_data = GuildData.get_guild_data(guild_obj)
        if key in valid_guild_keys.keys() and (local_data.get(key, None) is None):  # If Key does not exist, set the key
            local_data[key] = valid_guild_keys[key]
        return local_data[key]

    def get_value_default(guild_obj: discord.Guild, key: str, default_value):
        local_data = GuildData.get_guild_data(guild_obj)
        if key in valid_guild_keys.keys():
            return local_data.get(key, default_value)
        return default_value
        # Invalid Key

    def delete_guild(guild_obj: discord.Guild):
        guild_data.delete(str(guild_obj.id).encode())

    def get_valid_keys():
        return valid_guild_keys
