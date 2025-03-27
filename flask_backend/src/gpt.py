import openai
import os
from config import project_config

openai.api_key = project_config.OPENAI_API_KEY

# 初始化 OpenAI 客户端
client = openai.OpenAI(api_key=project_config.OPENAI_API_KEY)

def get_gpt_response(user_message, chat_history):
    """
    调用 OpenAI GPT 模型生成回复。

    :param user_message: 用户输入的消息
    :param chat_history: 聊天历史记录，格式为 [{"role": "user/assistant", "content": "message"}]
    :return: GPT 模型的回复
    """
    try:
        # 构建消息列表
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        
        # 添加聊天历史
        for message in chat_history:
            messages.append(message)
        
        # 添加用户当前消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        # 返回助手的回复
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error communicating with OpenAI API: {str(e)}")