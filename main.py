from flask import Flask, request, render_template, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 创建 Flask 应用
app = Flask(__name__)

# 设置上传目录
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 如果上传目录不存在，则创建它
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    """主页路由"""
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    # 获取用户输入的聊天内容
    user_input = request.form.get('message')
    # 获取上传的文件
    uploaded_file = request.files.get('file')

    # 检查是否提供了聊天内容或上传文件
    if not user_input and not uploaded_file:
        return jsonify({'success': False, 'message': '未提供聊天内容或上传文件'})

    # 创建消息列表
    messages = []

    # 处理上传的文件
    if uploaded_file:
        # 保存上传的文件到本地
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(uploaded_file.filename))
        uploaded_file.save(file_path)
        
        # 上传文件到 OpenAI API
        with open(file_path, 'rb') as f:
            file_object = client.files.create(file=f, purpose="file-extract")
        
        # 将文件内容添加到消息列表中
        file_content = client.files.content(file_id=file_object.id).text
        messages.append({"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一些涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"})
        messages.append({"role": "system", "content": file_content})

    # 添加用户输入的聊天内容到消息列表中
    if user_input:
        messages.append({"role": "user", "content": user_input})

    # 调用 OpenAI API 进行聊天
    completion = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=messages,
        temperature=0.3,
    )

    # 获取 AI 回复的内容
    ai_response_text = completion.choices[0].message.content

    # 返回 AI 的回复
    return jsonify({'text': ai_response_text})

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
