import openai
import os
import markdown
import html
from bs4 import BeautifulSoup
from config import project_config

openai.api_key = project_config.OPENAI_API_KEY

# 初始化 OpenAI 客户端
client = openai.OpenAI(api_key=project_config.OPENAI_API_KEY)

def get_gpt_response(user_message, chat_history, model="gpt-4"):
    """
    调用 OpenAI GPT 模型生成回复。

    :param user_message: 用户输入的消息
    :param chat_history: 聊天历史记录，格式为 [{"role": "user/assistant", "content": "message"}]
    :param model: 要使用的模型，默认为 gpt-4
    :return: GPT 模型的回复
    """
    try:
        # 验证模型名称
        valid_models = ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        if model not in valid_models:
            model = "gpt-4"  # 默认回退到 GPT-4
            
        # 构建消息列表
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        
        # 添加聊天历史
        for message in chat_history:
            messages.append(message)
        
        # 添加用户当前消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用 OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # 返回助手的回复
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        raise Exception(f"Error communicating with OpenAI API: {str(e)}")
    
def process_markdown(markdown_text):
    """
    将 Markdown 文本转换为 HTML。
    
    :param markdown_text: Markdown 格式的文本
    :return: 转换后的 HTML 文本
    """
    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(
        markdown_text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br'
        ]
    )
    
    # 清理和格式化 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 返回处理后的 HTML
    return str(soup)