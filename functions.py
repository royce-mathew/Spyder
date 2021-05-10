# Checks
def is_bot_owner(ctx):
    return ctx.message.author.id == 461509995444437003
        

def is_server_owner(ctx):
    return ctx.message.author == ctx.message.guild.owner


def is_server_admin(ctx):
    return ctx.message.author.guild_permissions.administrator


def print_options():
    print("1. Settings")
    print("2. Run")
    return input("Enter Option: ")


def print_settings():
    print("1. Set roles message ID")
    print("2. Set command prefix")
    return input("Enter Option: ")
