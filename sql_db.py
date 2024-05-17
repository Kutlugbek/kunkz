import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

def sql_insert(teacher, username, password):
	cursor.execute(f'''CREATE TABLE IF NOT EXISTS {teacher} (
				username TEXT PRIMARY KEY,
				password TEXT
	)''')
	connection.commit()
	
	cursor.execute(f"INSERT OR REPLACE INTO {teacher} (username, password) VALUES (?, ?)", (username, password))
	connection.commit()

def sql_select(teacher):
	cursor.execute(f"SELECT username, password FROM {teacher}")
	rows = cursor.fetchall()
	
	return rows