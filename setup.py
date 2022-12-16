# This python file will automatically install all needed files for you
import subprocess
import sys
import os

running_in_virtualenv = "VIRTUAL_ENV" in os.environ

def main():
    print("First Time Setup...")
    print("Setting Discord Token:")
    print("\tWould you like to create your own .env file? N/y")

    should_create = input() # Get input on whether to automatically create .env file
    
    if should_create.lower() == 'n':
        token = input("\tEnter Discord App Token: ")
        with open(".env", "w") as file:
            file.write(f"DISCORD_TOKEN={token}");
        print("Created .env file")

    else:
        print("You selected Yes, Please create a .env file containing `DISCORD_TOKEN=`")

    print("Downloading All required packages")
    if running_in_virtualenv:
        print("Detected Running in Virtual Environment")

    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


if __name__ == "__main__":
    main()