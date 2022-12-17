# This python file will automatically install all needed files for you
import subprocess
from setuptools import setup
import sys
import os

running_in_virtualenv = "VIRTUAL_ENV" in os.environ

def main():
    print("First Time Setup...")
    print("Setting Discord Token:")
    print("\tWould you like to create your own .env file? n/Y")

    should_create = input() # Get input on whether to automatically create .env file
    
    if should_create.lower() == 'n':
        token = input("\tEnter Discord App Token: ") # Prompt user for input
        with open(".env", "w") as file: # Open .env file
            file.write(f"DISCORD_TOKEN={token}");
        print("Created .env file")

    else:
        print("You selected Yes, Please create a .env file containing 'DISCORD_TOKEN='")



if __name__ == "__main__":
    setup(
        name='spyder',
        description="Discord bot written in Python",
        long_description="-> README.md",
        url="https://github.com/royce-mathew/Spyder",
        version="0.0.1",  
        author="Royce Mathew",
        install_requires=[
            "discord.py[voice]",
            "ffmpeg",
            "lxml",
            "plyvel",
            "pytz",
            "python-dotenv",
            "requests",
            "yt-dlp",
        ],
        python_requires=">=3.9.0",
        license="BSD License",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Topic :: Discord",
            "Topic :: Discord :: Bot",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]
    )

    main()