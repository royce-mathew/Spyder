import discord
import json
import plyvel
import pickle

# Initialize Variables
roles_dict: dict = {};
stats_message_dict = {};
valid_guild_keys: dict = {
    "fact_channel_id": 0,
    "roles_message_id": 0,
    "stats_channel_id": 0,
    "stats_message_id": 0,
    "fact_channel_id": 0,
    "prefix": "!"
}

# Start Databases
user_data = plyvel.DB("Data/Database/user_data", create_if_missing=True)
guild_data = plyvel.DB("Data/Database/guild_data", create_if_missing=True)
print("Started Databases")

with user_data.snapshot() as snap:
    for key, value in snap:
        print(f"LL{key} : {pickle.loads(value)}\n")

with guild_data.snapshot() as snap:
    for key, value in snap:
        print(f"{key} : {pickle.loads(value)}\n")


class UserData:    
    def get_user_data(user_id: str) -> dict:
        if (local_data := user_data.get(user_id.encode(), default=None)) is not None:
            return pickle.loads(local_data)
        else: return None
    
    def set_user_data(user_id: str, key:str, value) -> None:
        local_data = UserData.get_user_data(user_id) # Get the user data
        if local_data is None: local_data = {}
        local_data[key] = value; # Set value at keyy
        serialized_value = pickle.dumps(local_data) # Serialize Dictionary
        user_data.put(user_id.encode(), serialized_value) # Put value in database


class GuildData:    
    def get_guild_data(guild_obj: discord.Guild) -> dict:
        str_id = str(guild_obj.id).encode() # Convert guild id to bytes
        if (local_data := guild_data.get(str_id, default=None)) is not None:
            return pickle.loads(local_data)
        else: return None

    def initialize_guild(guild_obj: discord.Guild):
        str_id = str(guild_obj.id);

        local_data = GuildData.get_guild_data(guild_obj) # Get the user data
        
        if local_data is None:
            local_data = {}
            for key, value in valid_guild_keys.items():
                local_data[key] = value; # Set default value at key
        
        roles_dict[local_data["stats_channel_id"]] = str_id; # Link Back to Guild
        stats_message_dict[local_data["stats_channel_id"]] = str_id;
        
        serialized_value = pickle.dumps(local_data) # Serialize Dictionary
        guild_data.put(str_id.encode(), serialized_value) # Put value in database


    def edit_guild_settings(guild_obj: discord.Guild, edit_info: dict):
        str_id = str(guild_obj.id)

        local_data = GuildData.get_guild_data(guild_obj)
        if local_data is None: return;

        for key, value in edit_info.items(): # Type check things
            if key in valid_guild_keys:
                local_data[key] = value;

        # Set values for guild
        roles_dict[local_data["roles_message_id"]] = str_id # Link Back to Guild
        stats_message_dict[local_data["stats_channel_id"]] = str_id # Link Back to Guild

        serialized_value = pickle.dumps(local_data) # Serialize Dictionary
        guild_data.put(str_id.encode(), serialized_value) # Put value in database
        
