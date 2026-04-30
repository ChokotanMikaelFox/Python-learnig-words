from flask import Flask, render_template, request, redirect 
import random #
import os 
import shutil
app = Flask(__name__)


WORDS_DB = {}
USED_WORDS = []
STREAK = 0 
LIVES = 3
XP = 0
CURRENT_LEVEL = "all"
REWARDS = {
    "Основы": 10,
    "Типы данных": 15,
    "Списки": 20,
    "Функции": 20,
    "Строки": 20,
    "Математика": 25,
    "Случайные числа": 25,
    "Работа с ОС": 30,
    "Дата и время": 30,
    "Работа с файлами": 35,
    "Статистика": 35,
    "Ошибки": 35,
    "all": 25
}
def user_level(current_xp):
    """Уровень: до 10-го по 100 XP, после — по 250 XP"""
    limit = 10 * 100
    if current_xp <= limit:
        return (current_xp // 100) + 1
    else:
        extra_xp = current_xp - limit
        return 10 + (extra_xp // 250) + 1
    
class WordManager:
    def __init__(self):
        self.words_db = {}
        self.base_path = os.path.dirname(__file__)
        self.file_path = os.path.join(self.base_path, 'words.txt')
        self.backup_path = os.path.join(self.base_path, 'words.txt.bak')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                pass
        self.load_words()
    def load_words(self): 
        self.words_db={}
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(';', 3)
                        if len(parts) == 4:
                            eng, rus, info, theme = [p.strip() for p in parts]
                            if theme not in self.words_db:
                                self.words_db[theme]={}
                            self.words_db[theme][eng.lower()] = [rus.lower(), info]
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
    global show_welcome, STREAK, USED_WORDS, LIVES, CURRENT_LEVEL, XP
    set_lvl=request.args.get('set_lvl')
    if set_lvl:
        CURRENT_LEVEL=set_lvl
        STREAK = 0
        LIVES = 3
        USED_WORDS.clear()

    if request.args.get('reset'):
        show_welcome=True
        return redirect('/')
    
    if request.args.get('start'):
        show_welcome = False
        LIVES = 3
        return redirect('/')
        
    if show_welcome:
        return render_template('index.html', welcome=True, themes=WM.words_db.keys(), xp=XP, level=user_level(XP))
    
    if LIVES <=0:
        return render_template('index.html', game_over=True, xp=XP, level=user_level(XP))
  
    lvl_words = {}
    if CURRENT_LEVEL=="all":
        for theme in WM.words_db:
            lvl_words.update(WM.words_db[theme])
    else:
        lvl_words=WM.words_db.get(CURRENT_LEVEL, {})
    available_words = [w for w in lvl_words.keys() if w not in USED_WORDS]
    word_from = request.args.get('word')

    if word_from and word_from in lvl_words:
        current_word = word_from
        if request.args.get("show_hint"):
            STREAK = 0
    else:
        if not available_words:
            return render_template('index.html', done=True, xp=XP, level=user_level(XP))
        
        current_word = random.choice(available_words)

    total = len(lvl_words)
    used = len(USED_WORDS)
    progress = (used/total) * 100 if total > 0 else 0
    word_data = lvl_words.get(current_word)
    hint_text = word_data[1] if word_data and len(word_data)> 1 else "Описание отсутствует"
    return render_template('index.html', word=current_word, done=False, streak=STREAK, progress=progress, hint=hint_text, lives=LIVES, themes=WM.words_db.keys(), current_level=CURRENT_LEVEL, xp=XP, level=user_level(XP))

@app.route('/check', methods=['POST'])
def check():
    global STREAK, LIVES, CURRENT_LEVEL, XP
    user_answer = request.form.get('answer', '').lower().strip()
    word_key = request.form.get('word', '')
    correct_answer, info, word_theme = None, None, "all"
    for theme, words in WM.words_db.items():
        if word_key in words:
            correct_answer = words[word_key][0]
            info = words[word_key][1]
            word_theme = theme
            break
    if correct_answer is None:
        return redirect('/')
    

    if user_answer == correct_answer:
        u_level = user_level(XP)
        base_reward = REWARDS.get(word_theme, 10)
        level_multiplier = 1 + (u_level // 5) * 0.1 
        
        gained_xp = int((base_reward + (STREAK * 2)) * level_multiplier)
        XP += gained_xp

        result = "Правильно!"
        color = "green"
        STREAK += 1 
        
        if word_key not in USED_WORDS:
            USED_WORDS.append(word_key)
    else:
        LIVES -= 1
        result = f"Ошибка! Правильно: {correct_answer}"
        color = "red"
        STREAK = 0 
    return render_template('result.html', result=result, color=color, info=info, streak=STREAK, xp=XP, level=user_level(XP))


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html', words=WM.words_db)


@app.route('/add_word', methods=['POST'])
def add_word():
    eng = request.form.get('eng','').lower().strip()
    rus = request.form.get('rus','').lower().strip()
    info = request.form.get('info','').strip()
    lvl = request.form.get('level','Основы')
    
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
    WM.save_to_file()
    return redirect('/dictionary')

@app.route('/reset')
def reset():
    global USED_WORDS, STREAK, LIVES, XP, show_welcome
    USED_WORDS.clear() 
    STREAK = 0
    LIVES = 3
    XP = 0
    show_welcome = False
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)