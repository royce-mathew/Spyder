import json

# Singleton class, Only allow one instance of the children class to run
class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class UserData(Singleton):
    def __init__(self):
        self.main_array: dict = {};

        try: # Try reading userdata.json
            with open("Data/userdata.json", "r") as file:
                self.main_array = json.load(file)
        except FileNotFoundError: # File errored, write empty array
            self._save_to_json()

    def _save_to_json(self): 
        with open("Data/userdata.json", "w") as file:
            file.write(
                json.dumps(self.main_array, indent=4)
            ) # Save values to file
    
    def get_user_data(self, user_id):
        return self.main_array.get(str(user_id), None)

    def set_user_data(self, user_id:int, key:str, value=None):
        if value is None:
            self.main_array[str(user_id)] = {}
        else:
            self.main_array[str(user_id)][key] = value;

        self._save_to_json(); # Save changes in the main array to the json file


class GuildData(Singleton):
    def __init__(self):
        self.guild_dict: dict = {};
        self.roles_dict: dict = {};
        self.stats_message_dict = {};
        self.valid_keys: dict = {
            "fact_channel_id": 0,
            "roles_message_id": 0,
            "stats_channel_id": 0,
            "stats_message_id": 0,
            "fact_channel_id": 0,
            "prefix": "!"
        }

        try: # Open the json file
            with open("Data/guild_data.json", "r") as settings_file:
                self.guild_list: list = json.load(settings_file)
        except FileNotFoundError:
            self._save()


    def _save(self) -> None: 
        with open("Data/guild_data.json", "w") as file:
             # Serialize the Json
            json_object = json.dumps(self.guild_dict, indent=4)
            file.write(json_object) # Write serialized json data to file
    
    def get_guild_data(self, guild_obj) -> dict:
        return self.guild_dict.get(str(guild_obj), None)

    def set_guild(self, guild_obj):
        str_id = str(guild_obj.id);

        if str_id not in self.guild_dict: # Check if new guild joined
            for key, value in enumerate(self.valid_keys): # Set Default Key Values to 0
                self.guild_dict[str_id][key] = value;

        # Set the roles message id 
        self.roles_dict[self.guild_dict[str_id]["roles_message_id"]] = str_id # Link Back to Guild
        self.stats_message_dict[self.guild_dict[str_id]["stats_channel_id"]] = str_id # Link Back to Guild


    def new_guild(self, guild_obj):
        self.set_guild(guild_obj=guild_obj)
        self._save()

    def edit_guild_settings(self, guild_obj, edit_info):
        str_id = str(guild_obj.id)

        for key, value in enumerate(edit_info): # Type check things
            if key in self.valid_keys and type(value) == int:
                self.guild_dict[str_id][key] = value;

        # Update roles again
        self.roles_dict[self.guild_dict[str_id]["roles_message_id"]] = str_id

        # Save edits to file
        self._save()

