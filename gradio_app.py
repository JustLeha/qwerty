import gradio as gr
from quiz_bot import QuizBot
import json
from datetime import datetime

# Инициализация бота
bot = QuizBot()

def add_question(question_text):
    try:
        question_id = bot.add_question(question_text)
        return f"Вопрос успешно добавлен! ID: {question_id}"
    except Exception as e:
        return f"Ошибка при добавлении вопроса: {str(e)}"

def add_answer(question_id, answer_text, is_correct):
    try:
        bot.add_answer(question_id, answer_text, is_correct)
        return f"Ответ успешно добавлен!"
    except Exception as e:
        return f"Ошибка при добавлении ответа: {str(e)}"

def delete_question(question_id):
    try:
        bot.delete_question(question_id)
        return f"Вопрос успешно удален!"
    except Exception as e:
        return f"Ошибка при удалении вопроса: {str(e)}"

def delete_answer(answer_id):
    try:
        bot.delete_answer(answer_id)
        return f"Ответ успешно удален!"
    except Exception as e:
        return f"Ошибка при удалении ответа: {str(e)}"

def get_questions():
    questions = bot.get_questions()
    return json.dumps(questions, ensure_ascii=False, indent=2)

def get_question(question_id):
    question = bot.get_question(question_id)
    return json.dumps(question, ensure_ascii=False, indent=2) if question else "Вопрос не найден"

# Создаем интерфейс
with gr.Blocks(title="Quiz Bot") as demo:
    gr.Markdown("# Quiz Bot")
    
    with gr.Tab("Добавление вопроса"):
        with gr.Row():
            question_text = gr.Textbox(label="Текст вопроса")
            add_question_btn = gr.Button("Добавить вопрос")
        question_output = gr.Textbox(label="Результат")
        add_question_btn.click(add_question, inputs=[question_text], outputs=[question_output])
    
    with gr.Tab("Добавление ответа"):
        with gr.Row():
            question_id = gr.Number(label="ID вопроса", precision=0)
            answer_text = gr.Textbox(label="Текст ответа")
            is_correct = gr.Checkbox(label="Правильный ответ")
            add_answer_btn = gr.Button("Добавить ответ")
        answer_output = gr.Textbox(label="Результат")
        add_answer_btn.click(add_answer, inputs=[question_id, answer_text, is_correct], outputs=[answer_output])
    
    with gr.Tab("Удаление"):
        with gr.Row():
            delete_question_id = gr.Number(label="ID вопроса для удаления", precision=0)
            delete_question_btn = gr.Button("Удалить вопрос")
        delete_question_output = gr.Textbox(label="Результат")
        delete_question_btn.click(delete_question, inputs=[delete_question_id], outputs=[delete_question_output])
        
        with gr.Row():
            delete_answer_id = gr.Number(label="ID ответа для удаления", precision=0)
            delete_answer_btn = gr.Button("Удалить ответ")
        delete_answer_output = gr.Textbox(label="Результат")
        delete_answer_btn.click(delete_answer, inputs=[delete_answer_id], outputs=[delete_answer_output])
    
    with gr.Tab("Просмотр"):
        with gr.Row():
            questions_display = gr.Textbox(label="Список всех вопросов", lines=10)
            refresh_questions_btn = gr.Button("Обновить список")
        refresh_questions_btn.click(get_questions, outputs=[questions_display])
        
        with gr.Row():
            view_question_id = gr.Number(label="ID вопроса для просмотра", precision=0)
            view_question_btn = gr.Button("Просмотреть вопрос")
            question_details = gr.Textbox(label="Детали вопроса", lines=10)
        view_question_btn.click(get_question, inputs=[view_question_id], outputs=[question_details])

if __name__ == "__main__":
    demo.launch() 
    