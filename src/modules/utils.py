import discord
import datetime

import requests
import re  # Regex
from lxml import html

import json

maincolor = 0x000
avatar_url = "https://cdn.discordapp.com/avatars/730171191632986234/beda4acd239d66c261541edad187e95e.webp?size=1024"


def print_options():
    print("1. Settings")
    print("2. Run")
    return input("Enter Option: ")


def print_settings():
    print("1. Set roles message ID")
    print("2. Set command prefix")
    return input("Enter Option: ")


def get_fact():
    page = requests.get("https://uselessfacts.jsph.pl/random.html?language=en")
    json_fact = page.json()
    # tree = html.fromstring(page.content)
    # fact_elem = tree.xpath("/html/body/div/div[2]/div/blockquote")[0]
    # fact_regex = re.compile("^[\s\t]+")
    # result = re.sub(fact_regex, "", fact_elem.text)
    result = json_fact["text"]

    return result if result is not None else "Error getting data"


def create_embed(title, description=None):
    embed = discord.Embed(
        title=title,
        description=description,
        colour=maincolor,
        timestamp=datetime.datetime.now(),
    )
    embed.set_footer(text="Spyder", icon_url=avatar_url)  # , icon_url=client_array[0].user.avatar_url
    return embed
