from aiogram import Dispatcher
from aiogram.filters import Command

from src.common.common_services.common_services import cmd_start, cmd_status, cmd_help

def register_common_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_help, Command("help"))