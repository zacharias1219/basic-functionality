from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_project']

# KnowledgeBase collection
knowledge_base = db['knowledge_base']

class KnowledgeBase:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def save_to_db(self):
        knowledge_base.insert_one({
            "question": self.question,
            "answer": self.answer
        })

    @staticmethod
    def find_by_question(question):
        return knowledge_base.find_one({"question": question})

    @staticmethod
    def get_all():
        return knowledge_base.find()

if __name__ == '__main__':
    # Example usage
    kb_item = KnowledgeBase(question="What is AI?", answer="AI stands for Artificial Intelligence.")
    kb_item.save_to_db()

    # Fetching an item
    result = KnowledgeBase.find_by_question("What is AI?")
    if result:
        print(f"Question: {result['question']}, Answer: {result['answer']}")

    # Fetching all items
    for item in KnowledgeBase.get_all():
        print(f"Question: {item['question']}, Answer: {item['answer']}")
