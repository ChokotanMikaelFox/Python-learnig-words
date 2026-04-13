from flask import Flask, render_template, request
import random
import os

app = Flask(__name__)

def load_words():
    words = {}
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'words.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(';', 2)
                if len(parts) == 3:
                    
                    words[parts[0].lower().strip()] = [parts[1].lower().strip(), parts[2].strip()]
    except:
        words = {"python": ["питон", "язык программирования"]}
    return words

@app.route('/')
def index():
    words_db = load_words()
    random_word = random.choice(list(words_db.keys()))
    return render_template('index.html', word=random_word)

@app.route('/check', methods=['POST'])
def check():
    words_db = load_words()
    user_answer = request.form.get('answer', '').lower().strip()
    word_key = request.form.get('word', '')
    
    correct_answer = words_db[word_key][0]
    info = words_db[word_key][1]

    if user_answer == correct_answer:
        result = "Правильно!"
        color = "green"
    else:
        result = f"Ошибка! Правильно: {correct_answer}"
        color = "red"
        
    return render_template('result.html', result=result, color=color, info=info)

if __name__ == '__main__':
    app.run(debug=True)