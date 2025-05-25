HTML_CHAT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat WebSocket Client</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
            display: grid;
            grid-template-columns: 350px 1fr;
            height: 90vh;
        }

        .sidebar {
            background: #f8f9fa;
            border-right: 1px solid #e9ecef;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            background: #fff;
        }

        .main-chat {
            display: flex;
            flex-direction: column;
            height: 100%;
            /* ИСПРАВЛЕНИЕ: Убеждаемся что контейнер имеет фиксированную высоту */
            overflow: hidden; /* Предотвращаем расширение родителя */
        }

        .chat-header {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            background: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .connection-status {
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .connected {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .disconnected {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .form-section {
            padding: 15px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 15px;
            background: white;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #495057;
        }

        .form-group input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 14px;
        }

        .form-group input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            width: 100%;
            margin-bottom: 8px;
        }

        .btn-primary {
            background: #007bff;
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            background: #0056b3;
        }

        .btn-success {
            background: #28a745;
            color: white;
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
            display: flex;
            flex-direction: column;
            gap: 15px;
            /* ИСПРАВЛЕНИЕ: Принудительно ограничиваем высоту */
            min-height: 0; /* Позволяет flex элементу сжиматься */
            max-height: calc(90vh - 200px); /* Ограничиваем максимальную высоту */
        }

        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            position: relative;
            word-wrap: break-word;
            animation: fadeInUp 0.3s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.own {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .message.other {
            background: white;
            border: 1px solid #e9ecef;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .message.system {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
            align-self: center;
            font-style: italic;
            font-size: 13px;
            max-width: 90%;
        }

        .message-header {
            font-size: 11px;
            opacity: 0.7;
            margin-bottom: 4px;
        }

        .message-text {
            line-height: 1.4;
        }

        .message-footer {
            font-size: 10px;
            opacity: 0.6;
            margin-top: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .message-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
        }

        .message-input-group {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .message-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ced4da;
            border-radius: 25px;
            resize: none;
            font-family: inherit;
            font-size: 14px;
            max-height: 120px;
            min-height: 44px;
        }

        .message-input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }

        .send-btn {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .send-btn:hover:not(:disabled) {
            background: #0056b3;
            transform: scale(1.05);
        }

        .send-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .typing-indicator {
            padding: 10px 16px;
            font-style: italic;
            color: #6c757d;
            font-size: 13px;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }

        .loading::after {
            content: "...";
            animation: dots 1.5s steps(5, end) infinite;
        }

        @keyframes dots {
            0%, 20% { color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
            40% { color: #6c757d; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
            60% { text-shadow: .25em 0 0 #6c757d, .5em 0 0 rgba(0,0,0,0); }
            80%, 100% { text-shadow: .25em 0 0 #6c757d, .5em 0 0 #6c757d; }
        }

        .stats {
            font-size: 12px;
            color: #6c757d;
            text-align: center;
            padding: 10px;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                height: 95vh;
            }

            .sidebar {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Chat Client</h2>

                <!-- Авторизация -->
                <div class="form-section">
                    <h4>Авторизация</h4>
                    <div class="form-group">
                        <label for="authToken">JWT Token:</label>
                        <input type="password" id="authToken" placeholder="Введите JWT токен">
                    </div>
                    <button class="btn btn-primary" onclick="saveToken()" id="saveTokenBtn">Сохранить токен</button>
                </div>

                <!-- Подключение к чату -->
                <div class="form-section">
                    <h4>Чат</h4>
                    <div class="form-group">
                        <label for="chatId">ID Чата:</label>
                        <input type="text" id="chatId" placeholder="UUID чата">
                    </div>
                    <button class="btn btn-success" onclick="joinChat()" id="joinBtn" disabled>Подключиться</button>
                    <button class="btn btn-danger" onclick="leaveChat()" id="leaveBtn" disabled>Отключиться</button>
                </div>

                <div class="stats" id="stats">
                    Готов к подключению
                </div>
            </div>
        </div>

        <!-- Main Chat Area -->
        <div class="main-chat">
            <!-- Chat Header -->
            <div class="chat-header">
                <div>
                    <h3 id="chatTitle">Выберите чат</h3>
                    <div id="typingIndicator" class="typing-indicator" style="display: none;"></div>
                </div>
                <div id="connectionStatus" class="connection-status disconnected">
                    Не подключено
                </div>
            </div>

            <!-- Messages Container -->
            <div id="chatContainer" class="chat-container">
                <div class="loading" id="loadingIndicator" style="display: none;">Загрузка сообщений</div>
            </div>

            <!-- Message Input -->
            <div class="message-input-container">
                <div class="message-input-group">
                    <textarea
                        id="messageInput"
                        class="message-input"
                        placeholder="Введите сообщение..."
                        disabled
                        rows="1"
                    ></textarea>
                    <button onclick="sendMessage()" id="sendBtn" class="send-btn" disabled>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Глобальные переменные
        let socket = null;
        let currentUserId = null;
        let currentChatId = null;
        let isConnected = false;
        let hasToken = false;
        let messageCount = 0;
        let typingTimeout = null;
        let lastTypingTime = 0;

        // Элементы DOM
        const elements = {
            authToken: document.getElementById('authToken'),
            chatId: document.getElementById('chatId'),
            chatContainer: document.getElementById('chatContainer'),
            messageInput: document.getElementById('messageInput'),
            connectionStatus: document.getElementById('connectionStatus'),
            chatTitle: document.getElementById('chatTitle'),
            typingIndicator: document.getElementById('typingIndicator'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            stats: document.getElementById('stats')
        };

        // Валидация токена (без сохранения)
        function saveToken() {
            const token = elements.authToken.value.trim();
            if (!token) {
                alert('Введите JWT токен');
                return;
            }

            hasToken = true;
            updateButtons();
            updateStats('Токен готов. Можно подключаться к чату.');
            addMessage('Токен введен. Введите ID чата и подключайтесь.', 'system');

            // Фокус на поле чата для удобства
            elements.chatId.focus();
        }

        // Подключение к чату
        function joinChat() {
            const chatId = elements.chatId.value.trim();
            const token = elements.authToken.value.trim();

            if (!chatId) {
                alert('Введите ID чата');
                return;
            }

            if (!token) {
                alert('Введите JWT токен');
                return;
            }

            if (socket) {
                socket.close();
            }

            currentChatId = chatId;
            elements.chatTitle.textContent = `Chat: ${chatId.substring(0, 8)}...`;

            // Очищаем чат и показываем загрузку
            clearChat();
            showLoading(true);
            updateConnectionStatus('Подключение...', false);

            // Подключаемся к WebSocket по твоему URL
            const wsUrl = `ws://localhost:8788/chats/${chatId}/ws`;
            socket = new WebSocket(wsUrl);

            socket.onopen = function(event) {
                console.log("WebSocket connected, sending auth...");
                // Отправляем токен сразу после подключения
                socket.send(JSON.stringify({
                    type: "auth",
                    token: token
                }));
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            socket.onclose = function(event) {
                console.log('WebSocket closed:', event.code, event.reason);

                // Проверяем был ли это graceful disconnect (код 1000)
                const wasGraceful = event.code === 1000;
                const reason = event.reason || 'Connection closed';

                updateConnectionStatus('Соединение закрыто', false);
                isConnected = false;
                currentChatId = null;
                currentUserId = null;
                hasToken = false;
                elements.chatTitle.textContent = 'Выберите чат';

                // Разные сообщения в зависимости от причины закрытия
                if (wasGraceful) {
                    addMessage('Вы покинули чат', 'system');
                } else {
                    addMessage(`Соединение закрыто: ${reason}`, 'system');
                }

                showLoading(false);
                updateStats('Отключено. Можно подключиться заново.');

                // Очищаем поля для повторного подключения
                elements.authToken.disabled = false;
                elements.chatId.disabled = false;
                updateButtons();
            };

            socket.onerror = function(error) {
                console.log('WebSocket error:', error);
                updateConnectionStatus('Ошибка подключения', false);
                isConnected = false;
                hasToken = false; // ИСПРАВЛЕНИЕ: Сбрасываем флаг токена при ошибке
                addMessage('Ошибка WebSocket: ' + error, 'system');
                showLoading(false);
                updateStats('Ошибка подключения. Попробуйте еще раз.');

                // ИСПРАВЛЕНИЕ: Разблокируем поля при ошибке
                elements.authToken.disabled = false;
                elements.chatId.disabled = false;
                updateButtons();
            };
        }

        // Отключение от чата
        function leaveChat() {
            console.log('leaveChat called');

            // НОВОЕ: Уведомляем сервер о покидании чата
            if (socket && socket.readyState === WebSocket.OPEN && currentChatId) {
                try {
                    socket.send(JSON.stringify({
                        type: 'leave_chat',
                        chat_id: currentChatId
                    }));
                    console.log('Sent leave_chat message to server');

                    // Даем время серверу обработать сообщение перед закрытием
                    setTimeout(() => {
                        closeConnection();
                    }, 100);
                } catch (error) {
                    console.log('Error sending leave_chat message:', error);
                    closeConnection();
                }
            } else {
                closeConnection();
            }
        }

        // НОВОЕ: Вынесли логику закрытия в отдельную функцию
        function closeConnection() {
            if (socket) {
                socket.close();
                socket = null;
            }

            // Полный сброс состояния
            isConnected = false;
            currentChatId = null;
            currentUserId = null;
            hasToken = false;

            // Разблокируем поля
            elements.authToken.disabled = false;
            elements.chatId.disabled = false;

            // Очищаем заголовок
            elements.chatTitle.textContent = 'Выберите чат';

            // Обновляем интерфейс
            updateConnectionStatus('Не подключено', false);
            updateStats('Готов к новому подключению');
            updateButtons();

            addMessage('Отключение выполнено. Можно подключиться заново.', 'system');
        }

        // Отправка сообщения
        function sendMessage() {
            const messageText = elements.messageInput.value.trim();
            if (!messageText || !socket || !currentChatId || !currentUserId) {
                console.log('Cannot send message:', {
                    hasText: !!messageText,
                    hasSocket: !!socket,
                    hasChatId: !!currentChatId,
                    hasUserId: !!currentUserId
                });
                return;
            }

            const message = {
                type: 'send_message',
                chat_id: currentChatId,
                text: messageText
            };

            socket.send(JSON.stringify(message));
            elements.messageInput.value = '';

            // Останавливаем индикатор печати
            stopTyping();

            // Автоматически изменяем размер textarea
            elements.messageInput.style.height = 'auto';
        }

        // Обработка WebSocket сообщений
        function handleWebSocketMessage(data) {
            console.log('Received message:', data);

            switch (data.type) {
                case 'auth_success':
                    currentUserId = data.user_id;
                    updateConnectionStatus('Подключено к чату', true);
                    isConnected = true;
                    showLoading(false);
                    addMessage(`Добро пожаловать! Ваш ID: ${data.user_id.substring(0, 8)}...`, 'system');
                    updateStats(`Подключен как ${data.user_id.substring(0, 8)}...`);
                    // ВАЖНО: Обновляем кнопки после успешной аутентификации
                    updateButtons();
                    break;

                case 'auth_error':
                    updateConnectionStatus('Ошибка авторизации', false);
                    addMessage(`Ошибка аутентификации: ${data.message}`, 'system');
                    showLoading(false);
                    leaveChat();
                    updateStats('Ошибка авторизации');
                    break;

                case 'chat_history':
                    showLoading(false);
                    loadChatHistory(data.messages, data.total_count);
                    // ВАЖНО: Обновляем кнопки после загрузки истории
                    updateButtons();
                    break;

                case 'new_message':
                    const msg = data.message;
                    const isOwn = msg.sender_id === currentUserId;
                    addMessage(msg.text, isOwn ? 'own' : 'other', {
                        senderId: msg.sender_id,
                        messageId: msg.id,
                        sentAt: msg.sent_at
                    });
                    break;

                case 'messages_read':
                    if (data.read_by !== currentUserId) {
                        addMessage(`Пользователь прочитал ${data.read_count} сообщений`, 'system');
                    }
                    break;

                case 'message_read':
                    addMessage(`Ваше сообщение прочитано`, 'system');
                    break;

                case 'user_joined':
                    if (data.user_id !== currentUserId) {
                        addMessage(`${data.user_id.substring(0, 8)}... присоединился к чату`, 'system');
                    }
                    break;

                case 'user_left':
                    addMessage(`${data.user_id.substring(0, 8)}... покинул чат`, 'system');
                    break;

                case 'user_disconnected':
                    addMessage(`${data.user_id.substring(0, 8)}... отключился`, 'system');
                    break;

                case 'typing':
                    if (data.user_id !== currentUserId) {
                        showTypingIndicator(data.user_id, data.is_typing);
                    }
                    break;

                case 'unread_count':
                    updateStats(`Непрочитанных: ${data.count}`);
                    break;

                case 'error':
                    addMessage(`Ошибка: ${data.message}`, 'system');
                    break;

                default:
                    console.log('Неизвестный тип сообщения:', data);
            }
        }

        // Загрузка истории чата
        function loadChatHistory(messages, totalCount) {
            console.log('loadChatHistory called:', { messages: messages?.length, totalCount });

            if (!messages || messages.length === 0) {
                addMessage('История сообщений пуста. Напишите первое сообщение!', 'system');
                scrollToBottom(); // Добавляем скролл для пустой истории
                return;
            }

            // Отображаем сообщения в хронологическом порядке
            messages.forEach((msg, index) => {
                const isOwn = msg.sender_id === currentUserId;
                console.log(`Adding message ${index + 1}/${messages.length}:`, {
                    isOwn,
                    senderId: msg.sender_id,
                    currentUserId
                });

                addMessage(msg.text, isOwn ? 'own' : 'other', {
                    senderId: msg.sender_id,
                    messageId: msg.id,
                    sentAt: msg.sent_at,
                    skipAnimation: true
                });
            });

            messageCount = messages.length;
            updateStats(`Загружено ${messages.length} из ${totalCount} сообщений`);

            // ИСПРАВЛЕНИЕ: Несколько попыток скролла с разными задержками
            console.log('Attempting to scroll after loading history...');

            scrollToBottom(); // Сразу

            setTimeout(() => {
                console.log('Scroll attempt 1 (100ms)');
                scrollToBottom();
            }, 100);

            setTimeout(() => {
                console.log('Scroll attempt 2 (300ms)');
                scrollToBottom();
            }, 300);

            setTimeout(() => {
                console.log('Scroll attempt 3 (500ms)');
                scrollToBottom();
            }, 500);
        }

        // Индикатор печати
        function handleTyping() {
            if (!socket || !currentChatId || !currentUserId) return;

            const now = Date.now();
            const timeDiff = now - lastTypingTime;

            if (timeDiff > 1000) { // Отправляем не чаще раза в секунду
                socket.send(JSON.stringify({
                    type: 'typing',
                    chat_id: currentChatId,
                    is_typing: true
                }));
                lastTypingTime = now;
            }

            // Останавливаем индикатор через 3 секунды бездействия
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(stopTyping, 3000);
        }

        function stopTyping() {
            if (socket && currentChatId && currentUserId) {
                socket.send(JSON.stringify({
                    type: 'typing',
                    chat_id: currentChatId,
                    is_typing: false
                }));
            }
            clearTimeout(typingTimeout);
        }

        function showTypingIndicator(userId, isTyping) {
            const indicator = elements.typingIndicator;
            if (isTyping) {
                indicator.textContent = `${userId.substring(0, 8)}... печатает...`;
                indicator.style.display = 'block';
            } else {
                indicator.style.display = 'none';
            }
        }

        // UI функции
        function addMessage(text, type = 'other', metadata = {}) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;

            if (!metadata.skipAnimation) {
                messageDiv.style.opacity = '0';
                messageDiv.style.transform = 'translateY(10px)';
            }

            let messageContent = '';

            if (type !== 'system' && metadata.senderId) {
                messageContent += `<div class="message-header">
                    ${metadata.senderId.substring(0, 8)}...
                </div>`;
            }

            messageContent += `<div class="message-text">${escapeHtml(text)}</div>`;

            if (type !== 'system' && metadata.sentAt) {
                const time = new Date(metadata.sentAt).toLocaleTimeString();
                messageContent += `<div class="message-footer">
                    <span>${time}</span>
                </div>`;
            }

            messageDiv.innerHTML = messageContent;

            if (metadata.messageId) {
                messageDiv.dataset.messageId = metadata.messageId;
            }

            elements.chatContainer.appendChild(messageDiv);

            if (!metadata.skipAnimation) {
                // Анимация появления
                setTimeout(() => {
                    messageDiv.style.transition = 'all 0.3s ease';
                    messageDiv.style.opacity = '1';
                    messageDiv.style.transform = 'translateY(0)';
                }, 10);
            }

            scrollToBottom();

            if (type !== 'system') {
                messageCount++;
            }
        }

        function updateConnectionStatus(message, connected) {
            elements.connectionStatus.textContent = message;
            elements.connectionStatus.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            updateButtons();
        }

        function updateButtons() {
            const canConnect = hasToken && !isConnected;
            const canDisconnect = isConnected;
            // ИСПРАВЛЕНИЕ: Можно отправлять сообщения если подключены И есть currentUserId
            const canSendMessages = isConnected && currentUserId && currentChatId;

            document.getElementById('joinBtn').disabled = !canConnect;
            document.getElementById('leaveBtn').disabled = !canDisconnect;
            elements.messageInput.disabled = !canSendMessages;
            document.getElementById('sendBtn').disabled = !canSendMessages;
            // ИСПРАВЛЕНИЕ: Кнопка сохранения токена активна когда НЕ подключены
            document.getElementById('saveTokenBtn').disabled = hasToken || isConnected;
            // ИСПРАВЛЕНИЕ: Поле токена активно когда НЕ подключены
            elements.authToken.disabled = isConnected;
            // ИСПРАВЛЕНИЕ: Поле чата активно когда НЕ подключены
            elements.chatId.disabled = isConnected;

            // Отладочная информация
            console.log('updateButtons:', {
                hasToken,
                isConnected,
                currentUserId: !!currentUserId,
                currentChatId: !!currentChatId,
                canConnect,
                canDisconnect,
                canSendMessages
            });
        }

        function updateStats(message) {
            elements.stats.textContent = message;
        }

        function showLoading(show) {
            elements.loadingIndicator.style.display = show ? 'block' : 'none';
        }

        function clearChat() {
            console.log('clearChat called');
            elements.chatContainer.innerHTML = '';
            messageCount = 0;
            console.log('Chat cleared, container children count:', elements.chatContainer.children.length);
        }

        function scrollToBottom() {
            const container = elements.chatContainer;
            const shouldScroll = container.scrollHeight > container.clientHeight;

            console.log('scrollToBottom called:', {
                scrollHeight: container.scrollHeight,
                clientHeight: container.clientHeight,
                scrollTop: container.scrollTop,
                shouldScroll: shouldScroll
            });

            if (shouldScroll) {
                // Принудительный скролл несколькими способами
                container.scrollTop = container.scrollHeight;

                // Дополнительная попытка через requestAnimationFrame
                requestAnimationFrame(() => {
                    container.scrollTop = container.scrollHeight;
                    console.log('After scroll:', {
                        scrollTop: container.scrollTop,
                        scrollHeight: container.scrollHeight
                    });
                });
            } else {
                console.log('No scroll needed - content fits in container');
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Event listeners
        elements.messageInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            } else if (event.key !== 'Enter') {
                handleTyping();
            }
        });

        elements.messageInput.addEventListener('input', function() {
            // Автоматическое изменение высоты
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        elements.authToken.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                saveToken();
            }
        });

        elements.chatId.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                joinChat();
            }
        });

        // Обработка закрытия вкладки/окна браузера
        window.addEventListener('beforeunload', function(event) {
            // Уведомляем сервер о покидании чата перед закрытием страницы
            if (socket && socket.readyState === WebSocket.OPEN && currentChatId) {
                try {
                    socket.send(JSON.stringify({
                        type: 'leave_chat',
                        chat_id: currentChatId
                    }));
                    console.log('Sent leave_chat on page unload');
                } catch (error) {
                    console.log('Error sending leave_chat on unload:', error);
                }
            }
        });

        // Обработка потери фокуса - помечаем сообщения как прочитанные
        window.addEventListener('focus', function() {
            if (currentChatId && socket && currentUserId) {
                // Можно добавить автоматическую отметку о прочтении
                setTimeout(() => {
                    const messages = elements.chatContainer.querySelectorAll('.message[data-message-id]');
                    if (messages.length > 0) {
                        const lastMessage = messages[messages.length - 1];
                        const lastMessageId = lastMessage.dataset.messageId;
                        if (lastMessageId) {
                            socket.send(JSON.stringify({
                                type: 'mark_read',
                                last_read_message_id: lastMessageId
                            }));
                        }
                    }
                }, 500);
            }
        });

        // Проверка сохраненного токена при загрузке (УБИРАЕМ localStorage)
        window.addEventListener('load', function() {
            // Убираем проверку localStorage
            updateStats('Введите JWT токен');
            updateButtons();
        });

        // Дополнительные функции для отладки
        function requestChatHistory() {
            if (socket && currentChatId) {
                socket.send(JSON.stringify({
                    type: 'get_chat_history',
                    chat_id: currentChatId,
                    limit: 20,
                    offset: 0
                }));
            }
        }

        function getUnreadCount() {
            if (socket && currentChatId) {
                socket.send(JSON.stringify({
                    type: 'get_unread_count',
                    chat_id: currentChatId
                }));
            }
        }

        // Добавляем контекстное меню для отладки
        elements.chatContainer.addEventListener('contextmenu', function(e) {
            e.preventDefault();

            const menu = [
                { text: 'Обновить историю', action: requestChatHistory },
                { text: 'Проверить непрочитанные', action: getUnreadCount },
                { text: 'Очистить чат', action: clearChat }
            ];

            showContextMenu(e, menu);
        });

        function showContextMenu(event, items) {
            // Удаляем существующее меню
            const existingMenu = document.getElementById('contextMenu');
            if (existingMenu) {
                existingMenu.remove();
            }

            const menu = document.createElement('div');
            menu.id = 'contextMenu';
            menu.style.cssText = `
                position: fixed;
                top: ${event.clientY}px;
                left: ${event.clientX}px;
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                padding: 8px 0;
                min-width: 150px;
            `;

            items.forEach(item => {
                const menuItem = document.createElement('div');
                menuItem.style.cssText = `
                    padding: 8px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.2s;
                `;
                menuItem.textContent = item.text;

                menuItem.addEventListener('mouseenter', () => {
                    menuItem.style.background = '#f8f9fa';
                });

                menuItem.addEventListener('mouseleave', () => {
                    menuItem.style.background = 'white';
                });

                menuItem.onclick = () => {
                    item.action();
                    document.body.removeChild(menu);
                };

                menu.appendChild(menuItem);
            });

            document.body.appendChild(menu);

            // Удаляем меню при клике вне его
            setTimeout(() => {
                document.addEventListener('click', function closeMenu() {
                    if (document.body.contains(menu)) {
                        document.body.removeChild(menu);
                    }
                    document.removeEventListener('click', closeMenu);
                }, 100);
            });
        }

        // Инициализация
        console.log('Chat client initialized');
        updateButtons();
    </script>
</body>
</html>
"""
