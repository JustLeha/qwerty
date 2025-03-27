import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    
    # Создаем таблицу категорий
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL)''')
    
    # Создаем таблицу вопросов
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category_id INTEGER,
                  question_text TEXT NOT NULL,
                  correct_answer TEXT NOT NULL,
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')
    
    # Создаем таблицу викторин
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  requestor_id INTEGER,
                  created_at TIMESTAMP,
                  status TEXT)''')
    
    # Создаем таблицу вопросов викторины
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  quiz_id INTEGER,
                  question_id INTEGER,
                  participant_answer TEXT,
                  FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
                  FOREIGN KEY (question_id) REFERENCES questions (id))''')
    
    # Создаем таблицу встреч
    c.execute('''CREATE TABLE IF NOT EXISTS meetings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  quiz_id INTEGER,
                  requestor_id INTEGER,
                  participant_email TEXT,
                  scheduled_time TIMESTAMP,
                  status TEXT,
                  FOREIGN KEY (quiz_id) REFERENCES quizzes (id))''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn 