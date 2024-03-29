# This python file will automatically install all needed files for you
import os
import subprocess
import sys

running_in_virtualenv = "VIRTUAL_ENV" in os.environ


def main():
    print("First Time Setup...")
    print("On some distributions you might need to install the libleveldb-dev package to run plyvel")

    print("Downloading All required packages")
    if running_in_virtualenv:
        print("Detected Running in Virtual Environment")

    # Check if ffmpeg is installed to path
    try:
        subprocess.check_call(["ffmpeg", "-version"])
    except subprocess.CalledProcessError as err:
        print("You do not have ffmpeg installed to path.")
        return

    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\n\nSetting Discord Token:")
    should_create = input("\tWould you like to create your own .env file? n/Y: ")  # Get input on whether to automatically create .env file

    if should_create.lower() == "n":
        token = input("\tEnter Discord App Token: ")
        with open(".env", "w") as file:
            file.write(f"DISCORD_TOKEN={token}")
        print("Created .env file")

    else:
        print('You selected Yes, Please create a .env file containing `DISCORD_TOKEN=""`')


if __name__ == "__main__":
    main()
