HTML_CHAT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat WebSocket Client</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }

        .container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .connection-status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
        }

        .connected { background-color: #d4edda; color: #155724; }
        .disconnected { background-color: #f8d7da; color: #721c24; }

        .chat-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            height: 300px;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 20px;
            background-color: #fafafa;
        }

        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 5px;
        }

        .message.own {
            background-color: #007bff;
            color: white;
            margin-left: 20%;
        }

        .message.other {
            background-color: #e9ecef;
            margin-right: 20%;
        }

        .message.system {
            background-color: #fff3cd;
            color: #856404;
            text-align: center;
            font-style: italic;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }

        input, select, button {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        input[type="text"] {
            flex: 1;
        }

        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            min-width: 80px;
        }

        button:hover {
            background-color: #0056b3;
        }

        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }

        .controls {
            display: grid;
            gap: 10px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        label {
            min-width: 120px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat WebSocket Client</h1>

        <div id="status" class="connection-status disconnected">
            Не подключено
        </div>

        <div class="controls">
            <div class="form-group">
                <label for="token">JWT Token:</label>
                <input type="text" id="token" placeholder="Введите JWT токен">
                <button onclick="connect()" id="connectBtn">Подключиться</button>
                <button onclick="disconnect()" id="disconnectBtn" disabled>Отключиться</button>
            </div>

            <div class="form-group">
                <label for="chatId">ID Чата:</label>
                <input type="text" id="chatId" placeholder="UUID чата">
                <button onclick="joinChat()" id="joinBtn" disabled>Войти в чат</button>
                <button onclick="leaveChat()" id="leaveBtn" disabled>Покинуть чат</button>
            </div>
        </div>

        <div id="chatContainer" class="chat-container"></div>

        <div class="input-group">
            <input type="text" id="messageInput" placeholder="Введите сообщение..." disabled onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendBtn" disabled>Отправить</button>
        </div>

        <div class="controls">
            <div class="form-group">
                <label>Действия:</label>
                <button onclick="markTyping(true)" id="typingBtn" disabled>Печатаю</button>
                <button onclick="markTyping(false)" id="stopTypingBtn" disabled>Не печатаю</button>
                <button onclick="clearChat()">Очистить чат</button>
            </div>
        </div>
    </div>

    <script>
        let socket = null;
        let currentUserId = null;
        let currentChatId = null;
        let isConnected = false;

        function updateStatus(message, isConnected) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;

            // Обновляем состояние кнопок
            document.getElementById('connectBtn').disabled = isConnected;
            document.getElementById('disconnectBtn').disabled = !isConnected;
            document.getElementById('joinBtn').disabled = !isConnected;
            document.getElementById('leaveBtn').disabled = !isConnected || !currentChatId;
            document.getElementById('messageInput').disabled = !isConnected || !currentChatId;
            document.getElementById('sendBtn').disabled = !isConnected || !currentChatId;
            document.getElementById('typingBtn').disabled = !isConnected || !currentChatId;
            document.getElementById('stopTypingBtn').disabled = !isConnected || !currentChatId;
        }

        function connect() {
            const token = document.getElementById('token').value.trim();
            if (!token) {
                alert('Введите JWT токен');
                return;
            }

            if (socket) {
                socket.close();
            }

            // Подключаемся к WebSocket
            const wsUrl = "ws://localhost:8788/chats/" + chatId.value + "/ws";
            socket = new WebSocket(wsUrl);

            socket.onopen = function(event) {
                // Отправляем токен сразу после подключения
                socket.send(JSON.stringify({
                    type: "auth",
                    token: token
                }));
                console.log("Connected to WebSocket");
                updateStatus('Подключено', true);
                isConnected = true;
                addMessage('Подключение установлено', 'system');
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            socket.onclose = function(event) {
                updateStatus('Соединение закрыто', false);
                isConnected = false;
                currentChatId = null;
                addMessage('Соединение закрыто', 'system');
            };

            socket.onerror = function(error) {
                updateStatus('Ошибка подключения', false);
                isConnected = false;
                addMessage('Ошибка WebSocket: ' + error, 'system');
            };
        }

        function disconnect() {
            if (socket) {
                socket.close();
                socket = null;
            }
        }

        function joinChat() {
            const chatId = document.getElementById('chatId').value.trim();
            if (!chatId || !socket) {
                alert('Введите ID чата и убедитесь, что подключение активно');
                return;
            }

            const message = {
                type: 'join_chat',
                chat_id: chatId
            };

            socket.send(JSON.stringify(message));
            currentChatId = chatId;
            updateStatus(`Подключено к чату ${chatId}`, true);
        }

        function leaveChat() {
            if (!currentChatId || !socket) return;

            const message = {
                type: 'leave_chat',
                chat_id: currentChatId
            };

            socket.send(JSON.stringify(message));
            currentChatId = null;
            updateStatus('Подключено', true);
        }

        function sendMessage() {
            const messageText = document.getElementById('messageInput').value.trim();
            if (!messageText || !socket || !currentChatId) return;

            const message = {
                type: 'send_message',
                chat_id: currentChatId,
                text: messageText
            };

            socket.send(JSON.stringify(message));
            document.getElementById('messageInput').value = '';
        }

        function markTyping(isTyping) {
            if (!socket || !currentChatId) return;

            const message = {
                type: 'typing',
                chat_id: currentChatId,
                is_typing: isTyping
            };

            socket.send(JSON.stringify(message));
        }

        function handleWebSocketMessage(data) {
            switch (data.type) {
                case 'connection_established':
                    currentUserId = data.user_id;
                    addMessage(`Подключен как пользователь ${data.user_id}`, 'system');
                    break;

                case 'joined_chat':
                    addMessage(`Вошли в чат ${data.chat_id}`, 'system');
                    break;

                case 'new_message':
                    const msg = data.message;
                    const isOwn = msg.sender_id === currentUserId;
                    addMessage(
                        `${msg.sender_id}: ${msg.text}`,
                        isOwn ? 'own' : 'other'
                    );
                    break;

                case 'user_joined':
                    addMessage(`Пользователь ${data.user_id} присоединился к чату`, 'system');
                    break;

                case 'user_left':
                    addMessage(`Пользователь ${data.user_id} покинул чат`, 'system');
                    break;

                case 'typing':
                    if (data.user_id !== currentUserId) {
                        addMessage(
                            `Пользователь ${data.user_id} ${data.is_typing ? 'печатает...' : 'перестал печатать'}`,
                            'system'
                        );
                    }
                    break;

                case 'message_read':
                    addMessage(`Сообщение прочитано пользователем ${data.read_by}`, 'system');
                    break;

                case 'error':
                    addMessage(`Ошибка: ${data.message}`, 'system');
                    break;

                default:
                    console.log('Неизвестный тип сообщения:', data);
            }
        }

        function addMessage(text, type = 'other') {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function clearChat() {
            document.getElementById('chatContainer').innerHTML = '';
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Инициализация
        updateStatus('Не подключено', false);
    </script>
</body>
</html>
"""
# HTML_CHAT = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Chat</title>
# </head>
# <body>
#     <h1>WebSocket Chat</h1>
#     <form action="" onsubmit="sendMessage(event)">
#         <label>Chat ID: <input type="text" id="chatId" autocomplete="off" value="123e4567-e89b-12d3-a456-426614174000"/></label>
#         <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
#         <button onclick="connect(event)">Connect</button>
#         <hr>
#         <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
#         <button>Send</button>
#     </form>
#     <ul id='messages'></ul>

#     <script>
#         var ws = null;
#         var isAuthenticated = false;

#         function connect(event) {
#             var chatId = document.getElementById("chatId");
#             var token = document.getElementById("token");

#             ws = new WebSocket("ws://localhost:8788/chats/" + chatId.value + "/ws");
#             ws.onopen = function(event) {
#                 console.log("Connected to WebSocket");
#                 // Отправляем токен сразу после подключения
#                 ws.send(JSON.stringify({
#                     type: "auth",
#                     token: token.value
#                 }));
#             };

#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages');
#                 var message = document.createElement('li');

#                 try {
#                     var data = JSON.parse(event.data);
#                     var content;

#                     if (data.type === "auth_success") {
#                         isAuthenticated = true;
#                         content = document.createTextNode('✅ Successfully authenticated');
#                         message.style.color = 'green';
#                     } else if (data.type === "auth_error") {
#                         isAuthenticated = false;
#                         content = document.createTextNode('❌ Authentication failed: ' + data.message);
#                         message.style.color = 'red';
#                     } else if (data.type === "message") {
#                         content = document.createTextNode(data.sender + ': ' + data.text);
#                     } else {
#                         content = document.createTextNode(event.data);
#                     }
#                 } catch (e) {
#                     content = document.createTextNode(event.data);
#                 }

#                 message.appendChild(content);
#                 messages.appendChild(message);

#                 // Автоскролл вниз
#                 messages.scrollTop = messages.scrollHeight;
#             };

#             ws.onerror = function(event) {
#                 console.error("WebSocket error:", event);
#                 var messages = document.getElementById('messages');
#                 var message = document.createElement('li');
#                 message.style.color = 'red';
#                 var content = document.createTextNode('❌ Connection error');
#                 message.appendChild(content);
#                 messages.appendChild(message);
#             };

#             ws.onclose = function(event) {
#                 console.log("WebSocket connection closed");
#                 isAuthenticated = false;
#                 var messages = document.getElementById('messages');
#                 var message = document.createElement('li');
#                 message.style.color = 'orange';
#                 var content = document.createTextNode('Connection closed');
#                 message.appendChild(content);
#                 messages.appendChild(message);
#             };

#             event.preventDefault();
#         }

#         function sendMessage(event) {
#             event.preventDefault();

#             if (!ws || ws.readyState !== WebSocket.OPEN) {
#                 alert("Please connect first!");
#                 return;
#             }

#             if (!isAuthenticated) {
#                 alert("Please wait for authentication!");
#                 return;
#             }

#             var input = document.getElementById("messageText");
#             var messageText = input.value.trim();

#             if (!messageText) {
#                 return;
#             }

#             // Отправляем сообщение в JSON формате
#             ws.send(JSON.stringify({
#                 type: "message",
#                 text: messageText
#             }));

#             input.value = '';
#         }

#         // Обработка Enter в поле ввода сообщения
#         document.getElementById("messageText").addEventListener("keypress", function(event) {
#             if (event.key === "Enter") {
#                 sendMessage(event);
#             }
#         });
#     </script>
# </body>
# </html>
# """
