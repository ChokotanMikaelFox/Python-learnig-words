# Имптонтирует Flask для создания сайта, render_template - отрисовка HTML, request - получение данных, redirect - перенаправление (без нее при добавлении функции "добавить слово", ломало всё к х...) 
from flask import Flask, render_template, request, redirect 
import random # Рандомайзер списка
import os # Путь к файлам 

# Создание веб-приложения
app = Flask(__name__)

# Функция, читающая текст из текстового файла
def load_words():
    words = {} # Создает пустой словарь для хранения данных
    base_path = os.path.dirname(__file__) # Обозначение папки, где лежит скрипт 
    file_path = os.path.join(base_path, 'words.txt') # Соединение пути к папке с файлом 
    try: 
        with open(file_path, 'r', encoding='utf-8') as f: # Открытие файла для чтения с поддержкой русского языка
            for line in f:
                parts = line.strip().split(';', 2) #Деление строки на 3 части по символу
                if len(parts) == 3:
                    words[parts[0].lower().strip()] = [parts[1].lower().strip(), parts[2].strip()] # Сохранение по типу ключ - английское слово, значение - перевод и описание
    except: # Если нет текстового файла (или ошибка с ним), то слово по умолчанию
        words = {"python": ["Питон", "Пайтон"]}
    return words

# Загрузка слова один раз при старте приложения
WORDS_DB = load_words()
# Создаем список показанных слова
USED_WORDS = []

@app.route('/')
def index():
    # Составляем список слов, которых ЕЩЕ НЕТ в списке использованных
    available_words = [w for w in WORDS_DB.keys() if w not in USED_WORDS]
    if not available_words:
        return render_template('index.html', done=True)
    # Выбираем случайное слово из оставшихся
    random_word = random.choice(available_words)
    return render_template('index.html', word=random_word, done=False)

@app.route('/check', methods=['POST'])
def check():
    user_answer = request.form.get('answer', '').lower().strip()
    word_key = request.form.get('word', '')
    if word_key not in WORDS_DB:
        return redirect('/')
    # Срабатывает в момент проверки
    if word_key not in USED_WORDS:
        USED_WORDS.append(word_key)
    correct_answer = WORDS_DB[word_key][0]
    info = WORDS_DB[word_key][1]
    if user_answer == correct_answer:
        result = "Правильно!"
        color = "green"
    else:
        result = f"Ошибка! Правильно: {correct_answer}"
        color = "red"
    return render_template('result.html', result=result, color=color, info=info)

# Страница слов
@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html', words=WORDS_DB)

#Новые слова
@app.route('/add_word', methods=['POST'])
def add_word():
    eng = request.form.get('eng','').lower().strip()
    rus = request.form.get('rus','').lower().strip()
    info = request.form.get('info','').strip()

    if eng and rus and info:
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'words.txt')
        # чтоб не крашился при добавлении слова
        file_is_empty = os.path.getsize(file_path) == 0 if os.path.exists(file_path) else True
        with open(file_path, 'a', encoding='utf-8') as f:
            if not file_is_empty:
                f.write('\n')
            f.write(f"\n{eng};{rus};{info}")

        WORDS_DB[eng] = [rus, info]
    return redirect('/dictionary')
# Удаление слов
@app.route('/delete_word/<word_key>')
def delete_word(word_key):
    if word_key in WORDS_DB:
        del WORDS_DB[word_key]

    # Перезапись текста без слова
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'words.txt')

    # Чтение всех строк, кроме удаленной (при корректировки проверки слов, он удалил содержимое текстового документа (заметка: доделать адекватный словарь и его копию хранить дубликатом!)
    remaining_lines = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f: 
                if not line.strip(): continue 
                    # Проверка только английского слова
                current_word = line.split(';')[0].lower().strip() 
                if current_word != word_key.lower().strip():
                    remaining_lines.append(line.strip()) 
        with open(file_path, 'w', encoding='utf-8' ) as f:
            f.write("\n".join(remaining_lines))  
    return redirect('/dictionary')       

# Чтобы можно было начать заново
@app.route('/reset')
def reset():
    USED_WORDS.clear() 
    return "Прогресс сброшен! <a href='/'>Вернуться на главную</a>"

if __name__ == '__main__':
    app.run(debug=True)