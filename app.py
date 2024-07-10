from flask import Flask, request, jsonify, render_template
import openai
from pymongo import MongoClient
from models import db, KnowledgeBase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
db.init_app(app)

client = MongoClient('mongodb://localhost:27017/')
db_mongo = client['chatbot']
leads_collection = db_mongo['leads']

openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt')
    model = data.get('model', 'gpt-3.5-turbo')
    response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=150)
    return jsonify({'response': response.choices[0].text.strip()})

@app.route('/lead', methods=['POST'])
def lead():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    leads_collection.insert_one({'name': name, 'email': email})
    return jsonify({'message': 'Lead captured successfully'})

@app.route('/faq', methods=['POST'])
def faq():
    data = request.json
    question = data.get('question')
    kb_item = KnowledgeBase.query.filter_by(question=question).first()
    if kb_item:
        return jsonify({'answer': kb_item.answer})
    else:
        return jsonify({'answer': 'I do not know the answer to that question.'})

if __name__ == '__main__':
    app.run(debug=True)
