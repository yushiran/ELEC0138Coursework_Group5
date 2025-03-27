document.addEventListener('DOMContentLoaded', async () => {
    // DOM 元素
    const chatHistoryList = document.getElementById('chat-history-list');
    const chatHistoryDiv = document.getElementById('chat-history');
    const sendButton = document.getElementById('send-button');
    const userMessageInput = document.getElementById('user-message');
    const newChatButton = document.getElementById('new-chat-button');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const modelOptions = document.querySelectorAll('.model-option');
    const currentModelElement = document.querySelector('.current-model');
    const fileUpload = document.getElementById('file-upload');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');

    // 当前聊天的ID和历史记录
    let currentChatId = null;
    let currentChatMessages = [];
    let currentModel = 'gpt-4'; // 默认模型
    let currentFile = null;

    // 文件上传处理
    fileUpload.addEventListener('change', function () {
        if (this.files.length > 0) {
            currentFile = this.files[0];
            fileName.textContent = currentFile.name;
            fileInfo.style.display = 'flex';
        } else {
            clearFileSelection();
        }
    });

    // 移除文件处理
    removeFileBtn.addEventListener('click', function () {
        clearFileSelection();
    });

    // 清除文件选择
    function clearFileSelection() {
        currentFile = null;
        fileUpload.value = '';
        fileName.textContent = '';
        fileInfo.style.display = 'none';
    }

    // 初始化模型选项
    modelOptions.forEach(option => {
        option.addEventListener('click', async function () {
            // 更新当前选定的模型
            const newModel = this.dataset.model;

            // 如果有当前聊天，更新该聊天的模型
            if (currentChatId) {
                try {
                    const response = await fetch(`/update_chat_model/${currentChatId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            model: newModel
                        })
                    });

                    if (response.ok) {
                        // 更新成功，更新当前模型
                        currentModel = newModel;
                        currentModelElement.textContent = this.textContent;

                        // 更新活动状态
                        modelOptions.forEach(opt => opt.classList.remove('active'));
                        this.classList.add('active');

                        // 添加系统消息告知用户模型已切换
                        const systemMessageDiv = document.createElement('div');
                        systemMessageDiv.className = 'message system';
                        systemMessageDiv.textContent = `Model switched to ${this.textContent}`;
                        chatHistoryDiv.appendChild(systemMessageDiv);

                        // 滚动到底部
                        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
                    } else {
                        console.error('Failed to update chat model');
                    }
                } catch (error) {
                    console.error('Error updating chat model:', error);
                }
            } else {
                // 没有当前聊天时，只更新选定的模型
                currentModel = newModel;
                currentModelElement.textContent = this.textContent;

                // 更新活动状态
                modelOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
            }
        });

        // 设置初始激活状态
        if (option.dataset.model === currentModel) {
            option.classList.add('active');
        }
    });

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

    // 修改 loadSpecificChat 函数，添加文件显示功能
    async function loadSpecificChat(chatId) {
        try {
            const response = await fetch(`/get_chat/${chatId}`);
            if (!response.ok) {
                throw new Error('Failed to load chat');
            }

            const data = await response.json();
            currentChatId = data.chat_id;
            currentChatMessages = data.messages || [];

            // 设置当前模型（如果聊天记录中有模型信息）
            if (data.model) {
                currentModel = data.model;
                const modelOption = Array.from(modelOptions).find(opt => opt.dataset.model === currentModel);
                if (modelOption) {
                    currentModelElement.textContent = modelOption.textContent;
                    modelOptions.forEach(opt => opt.classList.remove('active'));
                    modelOption.classList.add('active');
                } else {
                    currentModelElement.textContent = currentModel;
                }
            }

            // 清空并重新加载聊天消息
            chatHistoryDiv.innerHTML = '';

            currentChatMessages.forEach((message, index) => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${message.role}`;
                messageDiv.textContent = message.content;

                // 如果消息包含文件，添加文件下载链接
                if (message.file) {
                    const fileDiv = document.createElement('div');
                    fileDiv.className = 'file-attachment';

                    // 计算文件大小，转换为KB或MB
                    const fileSize = message.file.size;
                    let fileSizeStr = '';
                    if (fileSize < 1024 * 1024) {
                        fileSizeStr = `${(fileSize / 1024).toFixed(2)} KB`;
                    } else {
                        fileSizeStr = `${(fileSize / (1024 * 1024)).toFixed(2)} MB`;
                    }

                    // 根据文件类型选择图标
                    let fileIcon = 'fa-file';
                    const filename = message.file.filename.toLowerCase();
                    if (filename.endsWith('.pdf')) {
                        fileIcon = 'fa-file-pdf';
                    } else if (filename.endsWith('.txt')) {
                        fileIcon = 'fa-file-alt';
                    } else if (filename.endsWith('.doc') || filename.endsWith('.docx')) {
                        fileIcon = 'fa-file-word';
                    }

                    fileDiv.innerHTML = `
                    <i class="fas ${fileIcon}"></i>
                    <a href="/download_file/${currentChatId}/${index}" target="_blank" download>
                        ${message.file.filename} (${fileSizeStr})
                    </a>
                `;
                    messageDiv.appendChild(fileDiv);
                }

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
                body: JSON.stringify({
                    model: currentModel
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create new chat');
            }

            const data = await response.json();
            currentChatId = data.chat_id;
            currentChatMessages = [];

            // 清空聊天区域
            chatHistoryDiv.innerHTML = '';

            // 清空文件选择
            clearFileSelection();

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

    // 发送消息函数需更新清除文件的部分
    async function sendMessage() {
        const userMessage = userMessageInput.value.trim();
        if (!userMessage && !currentFile) return;  // 需要至少有消息或文件
        
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
            let formData = new FormData();
            formData.append('message', userMessage);
            formData.append('chat_id', currentChatId || '');
            formData.append('model', currentModel);
            
            // 如果有文件，添加到请求中
            if (currentFile) {
                formData.append('file', currentFile);
                
                // 显示文件上传提示
                const fileUploadDiv = document.createElement('div');
                fileUploadDiv.className = 'message system';
                fileUploadDiv.textContent = `Uploading file: ${currentFile.name}`;
                chatHistoryDiv.appendChild(fileUploadDiv);
            }
            
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
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
            
            // 清空文件选择
            clearFileSelection();
            
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
            
            // 清空文件选择
            clearFileSelection();
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