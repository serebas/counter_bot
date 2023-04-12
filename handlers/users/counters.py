import sqlite3
from aiogram import types
from aiogram.dispatcher.filters import Command

from keyboards.inline.callback_datas import stat_callback
from keyboards.inline.choice_button import choice
from loader import dp, bot
import methods
from random import randint


@dp.message_handler(commands=['start_count'])
async def start(message: types.Message):
	if str(message.chat.id).startswith('-'):  #если сообщение пришло в групповой чат
		with sqlite3.connect('db/database.db', check_same_thread=False) as db:
			cursor = db.cursor()

			id_chat = str(message.chat.id).lstrip("-")
			if methods.check_table_in_db(cursor, id_chat):  #если таблица уже существует в БД
				await message.reply(text='Счетчик сообщений уже был запущен!')
			else:  # иначе создаем таблицу для данного чата
				cursor.execute(f'''CREATE TABLE chat{id_chat} (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
																user_id INT UNIQUE NOT NULL,
																first_second_name VARCHAR NOT NULL,
																message_amount INT DEFAULT (0),
																voice_amount INT DEFAULT (0),
																video_note_amount INT DEFAULT (0)
																);''')
				db.commit()
				await message.answer('Готово, счетчик сообщений запущен.')


@dp.message_handler(commands=['help'])
async def sorry(message: types.Message):
	await message.reply(text='''<b>Доступные команды</b>:
	▪️/start_count  -  <i>включение счетчика сообщений</i>
	▪️/stat  -  <i>отображение статистики сообщений</i>
	▪️/change_name "новое_имя"  -  <i>смена своего имени в статистике (не более 20 символов)</i>''')


@dp.message_handler(commands=['stat'])
async def send_stat(message: types.Message):
	if str(message.chat.id).startswith('-'):  # если сообщение отправленно в групповой чат
		with sqlite3.connect('db/database.db', check_same_thread=False) as db:
			cursor = db.cursor()
			cursor.execute(f'SELECT user_id FROM chat{str(message.chat.id).lstrip("-")}')
			await message.answer(text='Выбери сообщения, статистику которых хочешь увидеть:', reply_markup=choice)


@dp.message_handler(commands=['change_name'])
async def change_name(message: types.Message, command: Command.CommandObj):
	if str(message.chat.id).startswith('-'):  # если сообщение отправленно в групповой чат
		if command.args:  # если после команды указано имя
			new_name = command.args
			max_length = 20
			if len(new_name) > max_length:
				await message.reply(f'Длина имени не должна превышать {max_length} символов')
			else:
				with sqlite3.connect('db/database.db', check_same_thread=False) as db:
					cursor = db.cursor()

					id_chat = str(message.chat.id).lstrip('-')
					id_user = message.from_user.id
					cursor.execute(f'UPDATE chat{id_chat} SET first_second_name = ? WHERE user_id = ?;', (new_name, id_user))
					db.commit()

					await message.reply('Имя успешно изменено.')
		else:
			await message.reply('После команды необходимо ввести новое имя!')


@dp.message_handler(content_types=('audio', 'video','video_note', 'voice', 'text', 'sticker', 'poll', 'caption', 'animation', 'photo'))
async def message_counter(message: types.Message):
	if str(message.chat.id).startswith('-'):  # если сообщение отправленно в групповой чат
		with sqlite3.connect('db/database.db', check_same_thread=False) as db:
			cursor = db.cursor()
			id_chat = str(message.chat.id).lstrip("-")

			if methods.check_table_in_db(cursor, id_chat):  # если таблица существует в БД
				cursor.execute(f'SELECT user_id FROM chat{id_chat};')
				members_id = list(map(lambda x: x[0], cursor.fetchall()))  # создаем список всех кто писал в чат
				if message.from_user.id not in members_id:  # если написавшего нету в этом чате
					if message.from_user.last_name:
						us_name = f'{message.from_user.first_name} {message.from_user.last_name}'
					else:
						us_name = message.from_user.first_name
					# добавляем этого участника в таблицу чата в БД
					methods.add_new_member(db=db, cursor=cursor, member_id=message.from_user.id, member_name=us_name, chat_id=id_chat)

				methods.update_message_amount(db, cursor, message.from_user.id, chat_id=id_chat)  # +1 к сообщениям участника
				if message.voice:  # если сообщение голосовое
					# +1 в к голосовым участника
					methods.update_voice_amount(db, cursor, message.from_user.id, chat_id=id_chat)
				if message.video_note:  # если это видео сообщение
					# +1 в к видео сообщениям
					methods.update_video_note_amount(db, cursor, message.from_user.id, chat_id=id_chat)


@dp.callback_query_handler(stat_callback.filter(type='voice'))
async def send_voice_stat(call: types.CallbackQuery):
	with sqlite3.connect('db/database.db', check_same_thread=False) as db:
		cursor = db.cursor()

		text = methods.show_stat_voice(cursor, call.message.chat.id)
		await call.answer(cache_time=60)
		await call.message.answer(text)


@dp.callback_query_handler(stat_callback.filter(type='video_note'))
async def send_video_stat(call: types.CallbackQuery):
	with sqlite3.connect('db/database.db', check_same_thread=False) as db:
		cursor = db.cursor()

		text = methods.show_stat_video_note(cursor, call.message.chat.id)
		await call.answer(cache_time=60)
		await call.message.answer(text)


@dp.callback_query_handler(stat_callback.filter(type='all_message'))
async def send_all_stat(call: types.CallbackQuery):
	with sqlite3.connect('db/database.db', check_same_thread=False) as db:
		cursor = db.cursor()

		text = methods.show_stat_all_message(cursor, call.message.chat.id)
		await call.answer(cache_time=60)
		await call.message.answer(text)


@dp.callback_query_handler(text='hide')
async def hide_keyboard(call: types.CallbackQuery):
	await call.answer(cache_time=60)
	await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


