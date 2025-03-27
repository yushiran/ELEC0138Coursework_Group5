document.addEventListener('DOMContentLoaded', async () => {
    // DOM 元素
    const chatHistoryList = document.getElementById('chat-history-list');
    const chatHistoryDiv = document.getElementById('chat-history');
    const sendButton = document.getElementById('send-button');
    const userMessageInput = document.getElementById('user-message');
    const newChatButton = document.getElementById('new-chat-button');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    // 当前聊天的ID和历史记录
    let currentChatId = null;
    let currentChatMessages = [];

    // 侧边栏切换功能
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
    });

    // 加载所有聊天历史
    async function loadChatHistory() {
        try {
            const response = await fetch('/get_chat_history');
            if (!response.ok) {
                throw new Error('Failed to load chat history');
            }

            const data = await response.json();
            chatHistoryList.innerHTML = '';

            if (data.chats && data.chats.length > 0) {
                data.chats.forEach(chat => {
                    const listItem = document.createElement('li');
                    listItem.dataset.chatId = chat.chat_id;
                    listItem.innerHTML = `
                     <div class="chat-title">${chat.title}</div>
                     <div class="chat-time">${chat.updated_at}</div>
                 `;

                    listItem.addEventListener('click', () => {
                        loadSpecificChat(chat.chat_id);

                        // 移除所有活动聊天高亮
                        document.querySelectorAll('#chat-history-list li').forEach(item => {
                            item.classList.remove('active-chat');
                        });

                        // 添加当前聊天高亮
                        listItem.classList.add('active-chat');
                    });

                    chatHistoryList.appendChild(listItem);
                });

                // 如果没有当前聊天ID，加载第一个聊天
                if (!currentChatId && data.chats.length > 0) {
                    loadSpecificChat(data.chats[0].chat_id);
                    document.querySelector('#chat-history-list li').classList.add('active-chat');
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // 加载特定的聊天记录
    async function loadSpecificChat(chatId) {
        try {
            const response = await fetch(`/get_chat/${chatId}`);
            if (!response.ok) {
                throw new Error('Failed to load chat');
            }

            const data = await response.json();
            currentChatId = data.chat_id;
            currentChatMessages = data.messages || [];

            // 清空并重新加载聊天消息
            chatHistoryDiv.innerHTML = '';

            currentChatMessages.forEach(message => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${message.role}`;
                messageDiv.textContent = message.content;
                chatHistoryDiv.appendChild(messageDiv);
            });

            // 滚动到底部
            chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
        } catch (error) {
            console.error('Error loading specific chat:', error);
        }
    }

    // 创建新聊天
    async function createNewChat() {
        try {
            const response = await fetch('/new_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Failed to create new chat');
            }

            const data = await response.json();
            currentChatId = data.chat_id;
            currentChatMessages = [];

            // 清空聊天区域
            chatHistoryDiv.innerHTML = '';

            // 刷新聊天历史列表
            await loadChatHistory();

            // 设置新创建的聊天为活动聊天
            const newChatItem = document.querySelector(`#chat-history-list li[data-chat-id="${currentChatId}"]`);
            if (newChatItem) {
                document.querySelectorAll('#chat-history-list li').forEach(item => {
                    item.classList.remove('active-chat');
                });
                newChatItem.classList.add('active-chat');
            }

            // 聚焦输入框
            userMessageInput.focus();
        } catch (error) {
            console.error('Error creating new chat:', error);
        }
    }

    // 发送消息
    async function sendMessage() {
        const userMessage = userMessageInput.value.trim();
        if (!userMessage) return;

        // 显示用户消息
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user';
        userMessageDiv.textContent = userMessage;
        chatHistoryDiv.appendChild(userMessageDiv);

        // 清空输入框
        userMessageInput.value = '';

        // 滚动到底部
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    chat_id: currentChatId,
                    history: currentChatMessages
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();

            // 更新当前聊天ID（如果是新创建的聊天）
            if (data.chat_id) {
                currentChatId = data.chat_id;
            }

            // 显示助手回复
            const assistantMessageDiv = document.createElement('div');
            assistantMessageDiv.className = 'message assistant';
            assistantMessageDiv.textContent = data.message;
            chatHistoryDiv.appendChild(assistantMessageDiv);

            // 更新当前聊天消息
            currentChatMessages.push(
                { role: 'user', content: userMessage },
                { role: 'assistant', content: data.message }
            );

            // 滚动到底部
            chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;

            // 刷新聊天历史列表
            await loadChatHistory();
        } catch (error) {
            console.error('Error sending message:', error);

            // 显示错误消息
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message system';
            errorDiv.textContent = 'Error: Failed to get response';
            chatHistoryDiv.appendChild(errorDiv);
        }
    }

    // 事件监听器
    newChatButton.addEventListener('click', createNewChat);

    sendButton.addEventListener('click', sendMessage);

    userMessageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 初始化 - 加载聊天历史
    await loadChatHistory();
});