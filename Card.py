# Имптонтирует Flask для создания сайта, render_template - отрисовка HTML, request - получение данных, redirect - перенаправление (без нее при добавлении функции "добавить слово", ломало всё к х...) 
from flask import Flask, render_template, request, redirect 
import random # Рандомайзер списка
import os # Путь к файлам 
import shutil
# Создание веб-приложения
app = Flask(__name__)


WORDS_DB = {}
USED_WORDS = []
STREAK = 0 
LIVES = 3
CURRENT_LEVEL = "1"


class WordManager:
    def __init__(self):
        self.words_db = {"1": {}, "2": {}, "3": {}}
        self.base_path = os.path.dirname(__file__)
        self.file_path = os.path.join(self.base_path, 'words.txt')
        self.backup_path = os.path.join(self.base_path, 'words.txt.bak')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                pass
        self.load_words()
    def load_words(self):
        try: 
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(';', 3)
                        if len(parts) == 4:
                            eng, rus, info, lvl = [p.strip() for p in parts]
                            if lvl in self.words_db:
                                self.words_db[lvl][eng.lower()] = [rus.lower(), info]
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
    def save_to_file(self):
        lines = []
        for lvl, words in self.words_db.items():
            for eng, data in words.items():
                lines.append(f"{eng};{data[0]};{data[1]};{lvl}")
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))    


WM = WordManager()
show_welcome = True

@app.route('/')
def index():
    global show_welcome, STREAK, USED_WORDS, LIVES, CURRENT_LEVEL

    if request.args.get('reset'):
        show_welcome = True
        STREAK = 0
        LIVES = 3
        USED_WORDS.clear()
        return redirect('/')
    
    if request.args.get('start'):
        show_welcome = False
        LIVES = 3
        return redirect('/')
        
    if show_welcome:
        return render_template('index.html', welcome=True)
    
    if LIVES <=0:
        return render_template('index.html', game_over=True)
    lvl_words = WM.words_db.get(CURRENT_LEVEL, {})
    available_words = [w for w in lvl_words.keys() if w not in USED_WORDS]
    word_from = request.args.get('word')

    if word_from and word_from in lvl_words:
        current_word = word_from
        STREAK = 0
    else:
        if not available_words:
            return render_template('index.html', done=True)
        
        current_word = random.choice(available_words)

    total = len(lvl_words)
    used = len(USED_WORDS)
    progress = (used/total) * 100 if total > 0 else 0
    word_data = lvl_words.get(current_word)
    hint_text = word_data[1] if word_data and len(word_data)> 1 else "Описание отсутствует"
    return render_template('index.html', word=current_word, done=False, streak=STREAK, progress=progress, hint=hint_text, lives=LIVES)

@app.route('/check', methods=['POST'])
def check():
    global STREAK, LIVES, CURRENT_LEVEL #(когда нибудь до опыта дойду Q_Q)
    user_answer = request.form.get('answer', '').lower().strip()
    word_key = request.form.get('word', '')
    lvl_words = WM.words_db.get(CURRENT_LEVEL, {})
    if word_key not in lvl_words:
        return redirect('/')
    
    correct_answer = lvl_words[word_key][0]
    info = lvl_words[word_key][1]

    if user_answer == correct_answer:
        result = "Правильно!"
        color = "green"
        STREAK += 1 
        
        if word_key not in USED_WORDS:
            USED_WORDS.append(word_key)
    else:
        LIVES -= 1
        result = f"Ошибка! Правильно: {correct_answer}"
        color = "red"
        STREAK = 0 #Серия
    return render_template('result.html', result=result, color=color, info=info, streak=STREAK)

# Страница слов
@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html', words=WM.words_db)


@app.route('/add_word', methods=['POST'])
def add_word():
    eng = request.form.get('eng','').lower().strip()
    rus = request.form.get('rus','').lower().strip()
    info = request.form.get('info','').strip()
    lvl = request.form.get('level','1')
    
    if eng and rus and info:
        if lvl not in WM.words_db:
            WM.words_db[lvl] = {}
        WM.words_db[lvl][eng] = [rus, info]
        WM.save_to_file()
    return redirect('/dictionary')  

@app.route('/delete_word/<word_key>')
def delete_word(word_key):
    for lvl in WM.words_db:
        if word_key in WM.words_db[lvl]:
            del WM.words_db[lvl][word_key]
            break
    WM.save_to_fine()
    return redirect('/dictionary')

@app.route('/reset')
def reset():
    global USED_WORDS, STREAK, LIVES
    USED_WORDS.clear() 
    STREAK = 0
    LIVES = 3
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)