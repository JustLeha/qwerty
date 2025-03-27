import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class QuizBot:
    def __init__(self):
        self.conn = sqlite3.connect('quiz.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Создаем таблицу категорий
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        ''')
        
        # Создаем таблицу вопросов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL
        )
        ''')
        
        # Создаем таблицу ответов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            answer_text TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
        )
        ''')
        
        # Создаем таблицу викторин
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            requestor_id INTEGER,
            category_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Создаем таблицу встреч
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            requestor_id INTEGER,
            participant_email TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'scheduled',
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
        ''')
        
        self.conn.commit()
    
    def add_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_question(self, question_text):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO questions (question_text) VALUES (?)', (question_text,))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_answer(self, question_id, answer_text, is_correct):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO answers (question_id, answer_text, is_correct)
        VALUES (?, ?, ?)
        ''', (question_id, answer_text, is_correct))
        self.conn.commit()
        return cursor.lastrowid
    
    def create_quiz(self, title, requestor_id, category_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO quizzes (title, requestor_id, category_id)
        VALUES (?, ?, ?)
        ''', (title, requestor_id, category_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def approve_quiz(self, quiz_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE quizzes SET status = ? WHERE id = ?', ('approved', quiz_id))
        self.conn.commit()
    
    def create_meeting(self, quiz_id, requestor_id, participant_email, scheduled_time):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO meetings (quiz_id, requestor_id, participant_email, scheduled_time)
        VALUES (?, ?, ?, ?)
        ''', (quiz_id, requestor_id, participant_email, scheduled_time))
        self.conn.commit()
        return cursor.lastrowid
    
    def submit_answers(self, meeting_id, answers):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE meetings SET status = ? WHERE id = ?', ('completed', meeting_id))
        self.conn.commit()
    
    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM categories')
        return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    def get_questions(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT q.id, q.question_text, 
               GROUP_CONCAT(a.answer_text || '|' || a.is_correct, '||') as answers
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id
        GROUP BY q.id
        ''')
        questions = []
        for row in cursor.fetchall():
            question = {
                'id': row[0],
                'question_text': row[1],
                'answers': []
            }
            if row[2]:  # если есть ответы
                for answer_str in row[2].split('||'):
                    answer_text, is_correct = answer_str.split('|')
                    question['answers'].append({
                        'text': answer_text,
                        'is_correct': bool(int(is_correct))
                    })
            questions.append(question)
        return questions
    
    def get_questions_by_category(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT q.id, q.question_text, q.correct_answer, c.name as category_name
        FROM questions q
        JOIN categories c ON q.category_id = c.id
        WHERE q.category_id = ?
        ''', (category_id,))
        return [{'id': row[0], 'question_text': row[1], 'correct_answer': row[2], 'category_name': row[3]} 
                for row in cursor.fetchall()]
    
    def get_quizzes(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT q.id, q.title, q.status, c.name as category_name, q.category_id
        FROM quizzes q
        LEFT JOIN categories c ON q.category_id = c.id
        WHERE q.status = 'approved'
        ''')
        rows = cursor.fetchall()
        return [{'id': row[0], 'title': row[1], 'status': row[2], 'category_name': row[3], 'category_id': row[4]} 
                for row in rows]
    
    def get_meetings(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT m.id, m.status, m.scheduled_time, m.participant_email,
               q.title as quiz_title, c.name as category_name
        FROM meetings m
        JOIN quizzes q ON m.quiz_id = q.id
        JOIN categories c ON q.category_id = c.id
        ''')
        return [{'id': row[0], 'status': row[1], 'scheduled_time': row[2], 'participant_email': row[3],
                'quiz_title': row[4], 'category_name': row[5]} for row in cursor.fetchall()]
    
    def send_report(self, meeting_id):
        cursor = self.conn.cursor()
        meeting = cursor.execute('''
            SELECT m.*, q.title as quiz_title, r.email as requestor_email
            FROM meetings m
            JOIN quizzes q ON m.quiz_id = q.id
            JOIN users r ON m.requestor_id = r.id
            WHERE m.id = ?
        ''', (meeting_id,)).fetchone()
        
        # Получаем вопросы и ответы
        cursor.execute('''
            SELECT q.question_text, q.correct_answer, qq.participant_answer
            FROM quiz_questions qq
            JOIN questions q ON qq.question_id = q.id
            WHERE qq.quiz_id = ?
        ''', (meeting['quiz_id'],))
        
        questions = cursor.fetchall()
        
        # Формируем отчет
        report = f"""
        Отчет по викторине: {meeting['quiz_title']}
        Участник: {meeting['participant_email']}
        Дата: {meeting['scheduled_time']}
        
        Результаты:
        """
        
        for i, q in enumerate(questions, 1):
            report += f"\n{i}. Вопрос: {q['question_text']}"
            report += f"\n   Правильный ответ: {q['correct_answer']}"
            report += f"\n   Ответ участника: {q['participant_answer']}"
            report += f"\n   {'✓' if q['correct_answer'] == q['participant_answer'] else '✗'}\n"
        
        # Отправляем email (заглушка)
        print(f"Отправка отчета на email {meeting['requestor_email']}:")
        print(report)
    
    def delete_question(self, question_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        self.conn.commit()
    
    def delete_answer(self, answer_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM answers WHERE id = ?', (answer_id,))
        self.conn.commit()
    
    def get_question(self, question_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT q.id, q.question_text, 
               GROUP_CONCAT(a.id || '|' || a.answer_text || '|' || a.is_correct, '||') as answers
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id
        WHERE q.id = ?
        GROUP BY q.id
        ''', (question_id,))
        row = cursor.fetchone()
        if row:
            question = {
                'id': row[0],
                'question_text': row[1],
                'answers': []
            }
            if row[2]:  # если есть ответы
                for answer_str in row[2].split('||'):
                    answer_id, answer_text, is_correct = answer_str.split('|')
                    question['answers'].append({
                        'id': int(answer_id),
                        'text': answer_text,
                        'is_correct': bool(int(is_correct))
                    })
            return question
        return None

# Пример использования
if __name__ == "__main__":
    bot = QuizBot()
    
    # Добавляем категорию
    category_id = bot.add_category("История")
    
    # Добавляем вопросы
    bot.add_question("Кто был первым президентом России?")
    bot.add_question("В каком году началась Вторая мировая война?")
    
    # Создаем викторину
    quiz_id = bot.create_quiz("История России", 1, category_id)
    
    # Одобряем викторину
    bot.approve_quiz(quiz_id)
    
    # Создаем встречу
    meeting_id = bot.create_meeting(
        quiz_id=quiz_id,
        requestor_id=1,
        participant_email="participant@example.com",
        scheduled_time=datetime.now()
    )
    
    # Отправляем ответы
    answers = {
        1: "Борис Ельцин",
        2: "1939"
    }
    bot.submit_answers(meeting_id, answers) 