from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
from functools import partial
from typing import Callable, Union, List, Any
import asyncio
from twisted.internet import reactor

logger = logging.getLogger("TelegramBot")


class TelegramBot(object):
    """
    TelegramBot
    Args:
        object (_type_): _description_
    """
    def __init__(self, token: str) -> None:
        self._token = token
        self._application = Application.builder().token(self._token).build()
        self._application.add_error_handler(partial(self.error, self))
        self.error_callback: Union[None, Callable] = None

    
    def start(self, run_in_reactor = False):
        if run_in_reactor:
            reactor.callFromThread(self._application.run_polling, allowed_updates=Update.ALL_TYPES)
        else:
            self._application.run_polling(allowed_updates=Update.ALL_TYPES)


    def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        if self.error_callback:
            self.error_callback(update, context)

    
    def add_error_handler(self, callback: Callable):
        self.error_callback = callback

    def add_message_handler(self, callback: Callable):
        self._application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, partial(self.async_callback, self, callback)))

    async def async_callback(self, callback: Callable,update: Update, context: ContextTypes.DEFAULT_TYPE):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, callback, update, context)

    def add_command(self, command: str, callback: Callable):
        self._application.add_handler(CommandHandler(command, partial(self.async_callback, self, callback)))

    def send_message(self, update: Update, message: str):
        asyncio.run(update.message.reply_text(message))

    def add_call_back_query_handler(self, callback: Callable):
        self._application.add_handler(CallbackQueryHandler(partial(self.async_callback, self, callback)))

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