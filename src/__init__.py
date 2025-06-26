from flask import Flask
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(sys.path)
from services.chat import *

# # insert credentials here
# os.environ['AWS_ACCESS_KEY_ID'] = ""
# os.environ['AWS_SECRET_ACCESS_KEY'] = ""
# os.environ['AWS_SESSION_TOKEN'] = ""
# # or in ~/.aws/credentials file with format:
# # [default]
# # aws_access_key_id = YOUR_ACCESS_KEY
# # aws_secret_access_key = YOUR_SECRET   
# # aws_session_token = YOUR_SESSION_TOKEN

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:3000", "http://localhost:3000"])

chat_service = ChatService()

# @app.route("/")
# def home():
#     return "A"
    
@app.route('/api/chat', methods=['GET', 'POST'])
def answer():
    return chat_service.get_answer()