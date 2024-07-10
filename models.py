from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
db = SQLAlchemy(app)
admin = Admin(app)

class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200))
    answer = db.Column(db.String(2000))

admin.add_view(ModelView(KnowledgeBase, db.session))

db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
