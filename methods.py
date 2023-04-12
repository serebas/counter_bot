# добавляет нового участника чата в таблицу БД
def add_new_member(db, cursor, member_id: int, member_name: str, chat_id):
	cursor.execute(f'INSERT INTO chat{chat_id} (user_id, first_second_name) VALUES (?, ?)', (member_id, member_name))
	db.commit()

# обновляет счетчик голосовых сообщений участника
def update_voice_amount(conn, cursor, user_id: int, chat_id):
	cursor.execute(f'UPDATE chat{chat_id} SET voice_amount = voice_amount + 1 WHERE user_id = ?;', (user_id,))
	conn.commit()

# обновляет счетчик видео сообщений участника
def update_video_note_amount(conn, cursor, user_id: str, chat_id):
	cursor.execute(f'UPDATE chat{chat_id} SET video_note_amount = video_note_amount + 1 WHERE user_id = ?;', (user_id,))
	conn.commit()

# счетчик всех сообщений
def update_message_amount(conn, cursor, user_id, chat_id):
	cursor.execute(f'UPDATE chat{chat_id} SET message_amount = message_amount + 1 WHERE user_id = ?;', (user_id,))
	conn.commit()


#отображение статистики всех сообщений
def show_stat_all_message(cursor, chat_id):
	id_chat = str(chat_id).lstrip("-")
	check_query = f'SELECT user_id FROM chat{id_chat};'
	query = f'SELECT first_second_name, message_amount FROM chat{id_chat};'
	title = '<b>Топ флудеров:</b>\n'
	first_descr = '(уснул на клавиатуре)'
	second_descr = '(тоже уснул, но позже)'
	stat = former_stat(cursor=cursor, check_query=check_query, query=query, title=title, first_descr=first_descr, second_descr=second_descr)
	return stat


#отображение статистики по голосовым сообщениям
def show_stat_voice(cursor, chat_id):
	id_chat = str(chat_id).lstrip("-")
	check_query = f'SELECT user_id FROM chat{id_chat} WHERE voice_amount > 0;'
	query = f'SELECT first_second_name, voice_amount FROM chat{id_chat} WHERE voice_amount > 0;'
	title = '<b>Топ переговорщиков:</b>\n'
	first_descr = '(его голосовые никто не слушает)'
	second_descr = '(черный пояс по голосовым сообщениям)'
	stat = former_stat(cursor=cursor, check_query=check_query, query=query, title=title, first_descr=first_descr, second_descr=second_descr)
	return stat


#отображение статистики по видео сообщениям
def show_stat_video_note(cursor, chat_id):
	id_chat = str(chat_id).lstrip("-")
	check_query = f'SELECT user_id FROM chat{id_chat} WHERE video_note_amount > 0;'
	query = f'SELECT first_second_name, video_note_amount FROM chat{id_chat} WHERE video_note_amount > 0;'
	title = '<b>Топ видеоблогеров:</b>\n'
	first_descr = '(не знает как в тг переключиться на голосовые)'
	stat = former_stat(cursor=cursor, check_query=check_query, query=query, title=title, first_descr=first_descr)
	return stat

def former_stat(cursor, check_query, query, title, first_descr='', second_descr=''):
	cursor.execute(check_query)
	if len(cursor.fetchall()) < 3:
		return 'Недостаточно статистики для ее корректного отображения'
	cursor.execute(query)
	members = cursor.fetchall()
	members.sort(key=lambda x: int(x[1]), reverse=True)
	result = ''
	for position, member in enumerate(members, 1):
		name, amount = member
		if position == 1:
			result += f'<u>{position})</u> 🥇 <i>{name}</i>: <b>{amount}</b> {first_descr}\n'
		elif position == 2:
			result += f'<u>{position})</u> 🥈 <i>{name}</i>: <b>{amount}</b> {second_descr}\n'
		elif position == 3:
			result += f'<u>{position})</u> 🥉 <i>{name}</i>: <b>{amount}</b>\n'
		else:
			result += f'<u>{position})</u> ➖ <i>{name}</i>: <b>{amount}</b>\n'
	return title + result


def check_table_in_db(cursor, id_chat):
	cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='chat{id_chat}';")
	return cursor.fetchone()[0]