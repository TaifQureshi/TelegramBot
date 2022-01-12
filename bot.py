from telegram import Bot, TelegramError, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from typing import Callable, List, Any
import threading
from time import sleep

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

        self.dispatcher.add_error_handler(self.error)

        self.get_update_thread = threading.Thread(name="bot_update", target=self.get_update)
        self.run = True
        self.last_update_id = 0
        self.interval = 0

    def start_polling(self, interval=1.0):
        self.interval = interval
        self.get_update_thread.start()

    def clean_updates(self):
        logger.debug('Cleaning updates from Telegram server')
        updates = self.bot.get_updates()
        while updates:
            updates = self.bot.get_updates(updates[-1].update_id + 1)

    def stop_polling(self):
        self.run = False
        self.get_update_thread.join()

    def get_update(self):
        while self.run:
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

            sleep(self.interval)

    @staticmethod
    def error(update, context) -> None:
        """

        :param update:
        :param context:

        logs the error while handling bot command
        :return:
        """
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        logger.error(context.error)

    def set_commands(self, commands) -> None:
        """

        :param commands:
            can be list of tuples or tuple
            tuple -> (command, description)

            set the command to the bot
        :return:
        """
        list_commands = []
        if type(commands) == list:
            for command in commands:
                list_commands.append(BotCommand(command[0], command[1]))

        elif type(commands) == tuple:
            list_commands.append(BotCommand(commands[0], commands[1]))

        self.bot.set_my_commands(list_commands)

    def add_command(self, command, callback: Callable) -> None:
        """
        :param command:
            bot command
        :param callback:
            callback function to run when command is received
        :return:
        """

        self.dispatcher.add_handler(CommandHandler(command, callback))

    def add_message_handler(self, callback: Callable) -> None:
        """
        :param callback:
            set the callback function when user enter message
        :return:
        """
        self.dispatcher.add_handler(MessageHandler(Filters.text, callback))

    @staticmethod
    def send_message(update, message: str) -> None:
        """
        :param update:
            update in callback function on command or message
        :param message:
            text which has to be send to user
        :return:
        """
        update.message.replay_text(message)

    @staticmethod
    def smart_keyboard(elements: List[Any], columns=2) -> List:
        """
        :param elements:
            list of telegram InlineKeyboardButton, or any element
        :param columns:
            no to columns to arrange the element
        :return:
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
