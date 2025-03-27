from quiz_bot import QuizBot
from datetime import datetime, timedelta
import os
import time
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print("=" * 50)
    print(f"{title:^50}")
    print("=" * 50)

def wait_for_enter():
    input("\nНажмите Enter для продолжения...")

def display_ids(bot):
    print_header("Доступные ID в системе")
    
    # Категории
    print("\n📁 КАТЕГОРИИ:")
    print("-" * 50)
    categories = bot.get_categories()
    if categories:
        for category in categories:
            print(f"ID: {category['id']:<5} | {category['name']}")
    else:
        print("Категории отсутствуют")
    
    # Вопросы
    print("\n❓ ВОПРОСЫ:")
    print("-" * 50)
    questions = bot.get_questions()
    if questions:
        for question in questions:
            print(f"ID: {question['id']:<5} | Категория: {question['category_name']}")
            print(f"     Вопрос: {question['question_text'][:50]}...")
            print(f"     Ответ: {question['correct_answer']}")
            print("-" * 50)
    else:
        print("Вопросы отсутствуют")
    
    # Викторины
    print("\n📝 ВИКТОРИНЫ:")
    print("-" * 50)
    quizzes = bot.get_quizzes()
    if quizzes:
        for quiz in quizzes:
            print(f"ID: {quiz['id']:<5} | {quiz['title']}")
            print(f"     Категория: {quiz['category_name']}")
            print(f"     Статус: {quiz['status']}")
            print("-" * 50)
    else:
        print("Викторины отсутствуют")
    
    # Встречи
    print("\n👥 ВСТРЕЧИ:")
    print("-" * 50)
    meetings = bot.get_meetings()
    if meetings:
        for meeting in meetings:
            print(f"ID: {meeting['id']:<5} | Викторина: {meeting['quiz_title']}")
            print(f"     Участник: {meeting['participant_email']}")
            print(f"     Дата: {meeting['scheduled_time']}")
            print(f"     Статус: {meeting['status']}")
            print("-" * 50)
    else:
        print("Встречи отсутствуют")
    
    wait_for_enter()

def add_category(bot):
    print_header("Добавление новой категории")
    name = input("Введите название категории: ").strip()
    if name:
        category_id = bot.add_category(name)
        print(f"\n✅ Категория успешно добавлена с ID: {category_id}")
    else:
        print("\n❌ Ошибка: Название категории не может быть пустым")
    wait_for_enter()

def create_question_bank(bot):
    while True:
        print_header("📚 База вопросов")
        print("\nВыберите действие:")
        print("1. 📝 Добавить новый вопрос")
        print("2. 📋 Показать все вопросы")
        print("3. 🔄 Вернуться в главное меню")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == "1":
            print_header("Добавление нового вопроса")
            
            # Показываем доступные категории
            categories = bot.get_categories()
            if not categories:
                print("\n❌ Ошибка: Сначала необходимо создать хотя бы одну категорию")
                wait_for_enter()
                continue
            
            print("\nДоступные категории:")
            for category in categories:
                print(f"ID: {category['id']:<5} | {category['name']}")
            
            try:
                category_id = int(input("\nВведите ID категории: "))
                if not any(c['id'] == category_id for c in categories):
                    print("\n❌ Ошибка: Неверный ID категории")
                    wait_for_enter()
                    continue
                
                question = input("\nВведите вопрос: ").strip()
                if not question:
                    print("\n❌ Ошибка: Вопрос не может быть пустым")
                    wait_for_enter()
                    continue
                
                answer = input("Введите правильный ответ: ").strip()
                if not answer:
                    print("\n❌ Ошибка: Ответ не может быть пустым")
                    wait_for_enter()
                    continue
                
                question_id = bot.add_question(category_id, question, answer)
                print(f"\n✅ Вопрос успешно добавлен с ID: {question_id}")
            except ValueError:
                print("\n❌ Ошибка: ID категории должен быть числом")
            
            wait_for_enter()
        
        elif choice == "2":
            print_header("База вопросов")
            questions = bot.get_questions()
            
            if questions:
                for question in questions:
                    print(f"\nID: {question['id']:<5} | Категория: {question['category_name']}")
                    print(f"Вопрос: {question['question_text']}")
                    print(f"Ответ: {question['correct_answer']}")
                    print("-" * 50)
            else:
                print("\n❌ В базе пока нет вопросов")
            
            wait_for_enter()
        
        elif choice == "3":
            break
        
        else:
            print("\n❌ Неверный выбор. Попробуйте снова.")
            time.sleep(1)

def take_quiz(bot):
    print_header("🎯 Прохождение викторины")
    
    # Показываем доступные викторины
    quizzes = bot.get_quizzes()
    if not quizzes:
        print("\n❌ Ошибка: Нет доступных викторин")
        wait_for_enter()
        return
    
    print("\nДоступные викторины:")
    for quiz in quizzes:
        print(f"ID: {quiz['id']:<5} | {quiz['title']} | Категория: {quiz['category_name']}")
    
    try:
        quiz_id = int(input("\nВведите ID викторины: "))
        if not any(q['id'] == quiz_id for q in quizzes):
            print("\n❌ Ошибка: Неверный ID викторины")
            wait_for_enter()
            return
        
        # Получаем вопросы для викторины
        questions = bot.get_questions_by_category(quizzes[0]['category_id'])
        if not questions:
            print("\n❌ Ошибка: В этой категории нет вопросов")
            wait_for_enter()
            return
        
        # Перемешиваем вопросы
        random.shuffle(questions)
        
        print("\nНачинаем викторину!")
        print("Для каждого вопроса введите ваш ответ.")
        print("Для завершения введите 'exit'")
        print("-" * 50)
        
        score = 0
        total_questions = len(questions)
        answers = {}
        
        for i, question in enumerate(questions, 1):
            print(f"\nВопрос {i}/{total_questions}")
            print(f"Категория: {question['category_name']}")
            print(f"Вопрос: {question['question_text']}")
            
            answer = input("\nВаш ответ: ").strip()
            if answer.lower() == 'exit':
                break
            
            answers[question['id']] = answer
            
            # Сразу показываем правильный ответ
            print(f"\nПравильный ответ: {question['correct_answer']}")
            if answer.lower() == question['correct_answer'].lower():
                print("✅ Правильно!")
                score += 1
            else:
                print("❌ Неправильно")
            
            wait_for_enter()
        
        # Показываем итоговый результат
        print_header("Результаты викторины")
        print(f"\nВсего вопросов: {total_questions}")
        print(f"Правильных ответов: {score}")
        print(f"Процент правильных ответов: {(score/total_questions)*100:.1f}%")
        
        # Сохраняем результаты
        meeting_id = bot.create_meeting(quiz_id, 1, "user@example.com", datetime.now())
        bot.submit_answers(meeting_id, answers)
        
        wait_for_enter()
    
    except ValueError:
        print("\n❌ Ошибка: ID должен быть числом")
        wait_for_enter()

def main():
    bot = QuizBot()
    
    while True:
        print_header("Quiz Bot - Главное меню")
        print("\nВыберите действие:")
        print("1. 📚 База вопросов")
        print("2. 🎯 Пройти викторину")
        print("3. 🚪 Выход")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == "1":
            create_question_bank(bot)
        elif choice == "2":
            take_quiz(bot)
        elif choice == "3":
            print_header("Завершение работы")
            print("\n👋 До свидания!")
            time.sleep(1)
            break
        else:
            print("\n❌ Неверный выбор. Попробуйте снова.")
            time.sleep(1)

if __name__ == "__main__":
    main() 