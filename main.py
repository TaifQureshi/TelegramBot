from bot import TelegramBot
with open("token.txt", 'r') as f:
    token = f.read()

bot = TelegramBot(token)


def help(update, context):
    bot.send_message(update, "this in help function")


# help the set the command in telegram so user can see when / is enter
bot.add_command(("help", "help function"))

bot.set_command("help", help)

bot.start_bot()
