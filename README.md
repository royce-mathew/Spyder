# Spyder

<div align="center">
    <a href="https://github.com/royce-mathew/Spyder">
    <img src="https://cdn.discordapp.com/app-icons/730171191632986234/beda4acd239d66c261541edad187e95e.png" alt="Spyder" height="100" />
    <a/>
    <p>
      Bot written in Python, being hosted on a Raspberry Pi
    </p>
</div>

<hr />

# Features

- 🛠️ **Setting Commands**: Unique prefixes for guilds
- 🔨 **Moderation Commands**: Powerful moderation commands
- ✅ **User Verification**: Verify users according with custom Conditions
- 🎵 **Music Commands**: Listen to Music whenever you want
- 💾 **Datastore**: All Data is stored on a local datastore with
  [LevelDB](https://github.com/google/leveldb)

# Installation

Ensure you have [Python 3.9+](https://www.python.org/downloads/) Installed.

Ensure you have [Pip](https://pip.pypa.io/en/stable/installation/) Installed and
on your Path.

Navigate to the folder where the bot is located and run the following command in
your terminal of choice.

### Linux / MacOs <br/>

Installing Pip: `python3 -m pip install`

```console
python3 setup.py
```

### Windows <br/>

Pip Installation: `python -m pip install`

```console
python setup.py
```

After running the command, setup will ask you to create a `.env` file. <br/>
This file is where _DISCORD_TOKEN_ is stored. Your discord app token can be
retrieved [here](https://discord.com/developers/)<br/><br/>

After entering your bot token, the setup will download all the required modules
/ packages for this file with pip.

# Development

To Start Contributing, all you'll need is Git, Python and a editor of your
choice! After making significant changes, submit a pull request to start
contributing!

If you'd like to set up a virtual environment, follow this tutorial
[here](https://docs.python.org/3/library/venv.html)

# Commands

## Moderation Commands

| Commands                   | Details                                   |
| -------------------------- | ----------------------------------------- |
| **mute** username/userid   | Mute the specified user                   |
| **unmute** username/userid | Unmute the specified user                 |
| **nick** username/userid   | Set the nickname of the specified user    |
| **register**               | Register the current user in the database |
| **settings**               | View the current settings for this guild  |
| **setup** key value        | Change the settings for this guild        |

## Music Commands

| Commands             | Details                                              |
| -------------------- | ---------------------------------------------------- |
| **play** youtube_url | Play the specified youtube song                      |
| **pause**            | Pause the current song                               |
| **resume**           | Resume the current song                              |
| **stop**             | Stop playing music and disconnect from voice channel |
| **queue**            | Display the song queue                               |
| **playing**          | Display the current playing song                     |
| **shuffle**          | Shuffle the current queue                            |

## Developer Commands

| Commands           | Details                      |
| ------------------ | ---------------------------- |
| **load** command   | Load the specified command   |
| **unload** command | Unload the specified command |
| **reload** command | Reload the specified command |

## Other Commands

| Commands                | Details                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **help** `command_name` | Display all commands. Adding optional `command_name` lets you get help for the specified command   |
| **getfact**             | Get a random fact of the day                                                                       |
| **personalitytest**     | Test the personality of a user, saves the userdata after the user run's the command the first time |
| **covidstats**          | Get the Covid-19 Statistics and compare it to when the last time the command was ran               |
| **ping**                | Get the ping of the bot                                                                            |
