"""

Created by Taif Qureshi
Github: https://github.com/TaifQureshi

"""

from telegram import Bot, TelegramError, BotCommand, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from typing import Callable, List, Any
from twisted.internet import task

logger = logging.getLogger("bot")


class TelegramBot(object):
    def __init__(self, token):
        """
        :param token:
            telegram bot token
        """
        self.bot = Bot(token)
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # self.dispatcher.add_error_handler(self.error)

        self.get_update_task = task.LoopingCall(self.get_update)
        self.last_update_id = 0

    def start_bot(self):
        """
        :return:

        Run the bot
        """
        print("Bot started")
        self.updater.start_polling()
        self.updater.idle()

    def start_polling(self, interval=1.0):
        """
        :param interval:
            interval to poll
        :return:

        Function to use while using Twisted reactor
        """
        print("Bot started")
        self.get_update_task.start(interval)

    def clean_updates(self):
        logger.debug('Cleaning updates from Telegram server')
        updates = self.bot.get_updates()
        while updates:
            updates = self.bot.get_updates(updates[-1].update_id + 1)

    def stop_polling(self):
        self.get_update_task.stop()

    def get_update(self):
        """
        Twisted looping task to get update
        :return:
        """
        print("Bot started")
        updates = None
        try:
            updates = self.bot.get_updates(
                self.last_update_id,
                timeout=10,
                read_latency=2.0)
        except TelegramError as e:
            self.dispatcher.dispatch_error(e, e)

        if updates:
            for update in updates:
                try:
                    self.dispatcher.process_update(update)
                    self.last_update_id = updates[-1].update_id + 1
                except TelegramError as e:
                    self.dispatcher.dispatch_error(update, e)

    @staticmethod
    def error(update, context) -> None:
        """

        :param update:
            telegram Update
        :param context:
            telegram context
        :return:

        logs the error while handling bot command
        """
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        logger.error(context.error)

    def add_command(self, commands) -> None:
        """

        :param commands:
            can be list of tuples or tuple
            tuple -> (command, description)
        :return:

        set the command to the bot
        """
        list_commands = []
        if type(commands) == list:
            for command in commands:
                list_commands.append(BotCommand(command[0], command[1]))

        elif type(commands) == tuple:
            list_commands.append(BotCommand(commands[0], commands[1]))

        self.bot.set_my_commands(list_commands)

    def set_command(self, command, callback: Callable) -> None:
        """
        :param command:
            bot command
        :param callback:
            callback function to run when command is received
        :return:

        bind the telegram command to the function
        """

        self.dispatcher.add_handler(CommandHandler(command, callback))

    def add_message_handler(self, callback: Callable) -> None:
        """
        :param callback:
            set the callback function when user enter message
        :return:
        """
        self.dispatcher.add_handler(MessageHandler(Filters.text, callback))

    def send_message(self, update: Update, message: str) -> None:
        """
        :param update:
            update in callback function on command or message
        :param message:
            text which has to be send to user
        :return:

        send the message to user
        """
        update.message.reply_text(message)

    @staticmethod
    def smart_keyboard(elements: List[Any], columns=2) -> List:
        """
        :param elements:
            list of telegram InlineKeyboardButton, or any element
        :param columns:
            no to columns to arrange the element
        :return:
            list of list containing elements
        rearranged element in specified shape or columns and row
        """
        kb = []
        ele = []
        column_count = 1

        for element in elements:
            ele.append(element)
            if column_count == columns:
                kb.append(ele)
                ele = []
                column_count = 1
            else:
                column_count = column_count + 1

        if len(ele) > 0:
            kb.append(ele)

        return kb
