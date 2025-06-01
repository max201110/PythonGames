from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 用于存储最高分的文件
SCORES_FILE = 'high_scores.json'

def load_high_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {'high_score': 0}

def save_high_score(score):
    scores = load_high_scores()
    if score > scores['high_score']:
        scores['high_score'] = score
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f)
    return scores

@app.route('/')
def index():
    return render_template('index.html', high_score=load_high_scores()['high_score'])

@app.route('/api/scores', methods=['GET', 'POST'])
def handle_scores():
    if request.method == 'POST':
        data = request.get_json()
        score = data.get('score', 0)
        scores = save_high_score(score)
        return jsonify(scores)
    return jsonify(load_high_scores())

if __name__ == '__main__':
    app.run(debug=True) 