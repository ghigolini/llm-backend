from flask import Flask
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.chat import *

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:3000", "http://localhost:3000"])

chat_service = ChatService(sys_prompt="Rispondi in modo quanto più dettagliato possibile.")

# @app.route("/")
# def home():
#     return "A"
    
@app.route('/api/chat', methods=['POST'])
def answer():
    return chat_service.get_answer()

@app.route('/api/chat/reset', methods=['GET'])
def reset():
    return chat_service.reset_chat()

@app.route('/api/chat/guardrails', methods=['POST'])
def set_guardrails():
    return chat_service.set_guardrails()

@app.route('/api/chat/rag', methods=['POST'])
def set_rag():
    return chat_service.set_rag()

@app.route('/api/chat/set-rag-files', methods=['POST']) 
def set_rag_files():
    return chat_service.set_rag_files()