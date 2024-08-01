import os
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
import asyncio
import logging
from datetime import datetime
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from utils import create_link_list_from_csv, find_phone_number, save_to_csv, find_word_near_phone, write_string_to_txt, \
    decrypt_text_file

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Фильтрация"), KeyboardButton(text="Изм. Ключевые слова")]],
                         resize_keyboard=True)

flag = True


class Form(StatesGroup):
    waiting_for_keywords = State()


@dp.message(Command('start'))
async def start(msg: Message):
    await msg.answer('Отправьте файл формата CSV', reply_markup=kb)


@dp.message(F.document)
async def save_file(msg: Message):
    try:
        if os.path.exists(r'phones.csv'):
            os.remove(r'phones.csv')
    except Exception as e:
        print(f"Ошибка при удалении файла phones.csv: {e}")

    file_id = msg.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "links.csv")

    await msg.answer('Файл сохранен')
    links = create_link_list_from_csv(r"links.csv")
    if links:
        for link in links:

            try:
                keywords = decrypt_text_file('key.txt', delimiter=',')
                find_phone_number(link, flag, keywords)
            except Exception as e:
                print(f"Ошибка при обработке ссылки {link}: {e}")

    try:
        time.sleep(5)
        out = FSInputFile("phones.csv")
        await bot.send_document(chat_id=msg.chat.id, document=out)
        print("все ок")
    except Exception as e:
        await msg.answer(f'Номеров не найдено')


@dp.message(F.text == "Изм. Ключевые слова")
async def keywords(msg: Message, state: FSMContext):
    await msg.answer("Введите ключевые слова через запятую")
    await state.set_state(Form.waiting_for_keywords)


@dp.message(Form.waiting_for_keywords)
async def save_keywords(msg: Message, state: FSMContext):
    write_string_to_txt('key.txt', msg.text)
    await msg.answer("Ключевые слова сохранены")
    await state.clear()


@dp.message(F.text == 'Фильтрация')
async def filtr(msg: Message):
    global flag
    if flag:
        await msg.answer("Фильтрация выключена")
        flag = False
    else:
        await msg.answer("Фильтрация включена")
        flag = True


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
