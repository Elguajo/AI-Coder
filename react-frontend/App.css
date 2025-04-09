import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// URL API бэкенда
const API_URL = 'http://localhost:8000';

function App() {
  // Состояния
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [filename, setFilename] = useState('');
  const [codeToExecute, setCodeToExecute] = useState('');
  const [codeResult, setCodeResult] = useState('');
  const [modelInfo, setModelInfo] = useState(null);
  
  const messagesEndRef = useRef(null);

  // Загрузка информации о модели при первом рендере
  useEffect(() => {
    fetchModelInfo();
    fetchFiles();
  }, []);

  // Прокрутка к последнему сообщению
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Получение информации о модели
  const fetchModelInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/config`);
      const data = await response.json();
      setModelInfo(data);
    } catch (error) {
      console.error('Error fetching model info:', error);
    }
  };

  // Получение списка файлов
  const fetchFiles = async () => {
    try {
      const response = await fetch(`${API_URL}/files`);
      const data = await response.json();
      setFiles(data.files);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  // Отправка сообщения
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          history: messages.map(msg => [msg.content, msg.response || null])
        }),
      });
      
      const data = await response.json();
      
      setMessages(prevMessages => [
        ...prevMessages.slice(0, -1),
        { ...userMessage, response: data.response }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Ошибка отправки сообщения');
    } finally {
      setLoading(false);
    }
  };

  // Обработка нажатия Enter
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Чтение файла
  const readFile = async (filename) => {
    try {
      const response = await fetch(`${API_URL}/files/${filename}`);
      const data = await response.json();
      setSelectedFile(filename);
      setFileContent(data.content);
      setFilename(filename);
    } catch (error) {
      console.error('Error reading file:', error);
      alert('Ошибка чтения файла');
    }
  };

  // Сохранение файла
  const saveFile = async () => {
    if (!filename.trim()) {
      alert('Введите имя файла');
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/files`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: filename,
          content: fileContent
        }),
      });
      
      await response.json();
      alert('Файл успешно сохранен');
      fetchFiles();
    } catch (error) {
      console.error('Error saving file:', error);
      alert('Ошибка сохранения файла');
    }
  };

  // Выполнение кода
  const executeCode = async () => {
    if (!codeToExecute.trim()) {
      alert('Введите код для выполнения');
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: codeToExecute
        }),
      });
      
      const data = await response.json();
      setCodeResult(data.result);
    } catch (error) {
      console.error('Error executing code:', error);
      alert('Ошибка выполнения кода');
    }
  };

  // Очистка чата
  const clearChat = () => {
    setMessages([]);
  };

  // Создание нового файла
  const newFile = () => {
    setSelectedFile('');
    setFileContent('');
    setFilename('');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 Кодинг Чат-бот</h1>
        <p>На основе DeepSeek Coder</p>
      </header>
      
      <nav className="app-nav">
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => setActiveTab('chat')}
        >
          💬 Чат
        </button>
        <button 
          className={activeTab === 'files' ? 'active' : ''} 
          onClick={() => setActiveTab('files')}
        >
          📁 Файлы
        </button>
        <button 
          className={activeTab === 'execute' ? 'active' : ''} 
          onClick={() => setActiveTab('execute')}
        >
          🚀 Выполнение
        </button>
        <button 
          className={activeTab === 'info' ? 'active' : ''} 
          onClick={() => setActiveTab('info')}
        >
          ℹ️ Инфо
        </button>
      </nav>
      
      <main className="app-content">
        {/* Чат */}
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className="message-container">
                  <div className="message user-message">
                    <div className="message-header">
                      <span className="avatar">👤</span>
                      <span className="role">Вы</span>
                    </div>
                    <div className="message-content">{msg.content}</div>
                  </div>
                  
                  {msg.response && (
                    <div className="message bot-message">
                      <div className="message-header">
                        <span className="avatar">🤖</span>
                        <span className="role">Бот</span>
                      </div>
                      <div className="message-content">
                        {msg.response.split('```').map((part, i) => {
                          if (i % 2 === 0) {
                            return (
                              <span key={i} style={{ whiteSpace: 'pre-wrap' }}>
                                {part}
                              </span>
                            );
                          } else {
                            // Это код в тройных бэктиках
                            const codeContent = part.includes('\n')
                              ? part.substring(part.indexOf('\n') + 1)
                              : part;
                            return (
                              <pre key={i} className="code-block">
                                <code>{codeContent}</code>
                              </pre>
                            );
                          }
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="message bot-message">
                  <div className="message-header">
                    <span className="avatar">🤖</span>
                    <span className="role">Бот</span>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            <div className="chat-input">
              <textarea 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Задайте вопрос по программированию..."
                rows={3}
              />
              <div className="chat-actions">
                <button onClick={clearChat} className="clear-btn">Очистить</button>
                <button onClick={sendMessage} className="send-btn">Отправить</button>
              </div>
            </div>
          </div>
        )}
        
        {/* Файлы */}
        {activeTab === 'files' && (
          <div className="files-container">
            <div className="files-sidebar">
              <div className="files-header">
                <h3>Файлы</h3>
                <button onClick={newFile} className="new-file-btn">+ Новый</button>
              </div>
              <div className="files-list">
                {files.length === 0 ? (
                  <p className="no-files">Нет файлов</p>
                ) : (
                  files.map((file, index) => (
                    <div 
                      key={index} 
                      className={`file-item ${selectedFile === file ? 'selected' : ''}`}
                      onClick={() => readFile(file)}
                    >
                      <span className="file-icon">📄</span>
                      <span className="file-name">{file}</span>
                    </div>
                  ))
                )}
              </div>
              <button onClick={fetchFiles} className="refresh-btn">🔄 Обновить</button>
            </div>
            
            <div className="file-editor">
              <div className="file-header">
                <input 
                  type="text"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="Имя файла"
                  className="filename-input"
                />
                <button onClick={saveFile} className="save-btn">💾 Сохранить</button>
              </div>
              <textarea 
                className="file-content" 
                value={fileContent}
                onChange={(e) => setFileContent(e.target.value)}
                placeholder="// Содержимое файла..."
                rows={20}
              />
            </div>
          </div>
        )}
        
        {/* Выполнение кода */}
        {activeTab === 'execute' && (
          <div className="execute-container">
            <div className="code-editor">
              <h3>Код Python</h3>
              <textarea 
                className="code-input" 
                value={codeToExecute}
                onChange={(e) => setCodeToExecute(e.target.value)}
                placeholder="# Введите код Python для выполнения..."
                rows={12}
              />
              <button onClick={executeCode} className="execute-btn">▶️ Выполнить</button>
            </div>
            
            <div className="code-output">
              <h3>Результат выполнения</h3>
              <pre className="output-content">{codeResult || 'Результат будет отображаться здесь...'}</pre>
            </div>
          </div>
        )}
        
        {/* Информация */}
        {activeTab === 'info' && (
          <div className="info-container">
            <h2>Информация о системе</h2>
            {modelInfo ? (
              <div className="model-info">
                <p><strong>Модель:</strong> {modelInfo.model}</p>
                <p><strong>Температура:</strong> {modelInfo.temperature}</p>
                <p><strong>Максимальная длина ответа:</strong> {modelInfo.max_tokens} токенов</p>
                <p><strong>Размер памяти:</strong> {modelInfo.memory_size} сообщений</p>
              </div>
            ) : (
              <p>Загрузка информации...</p>
            )}
            
            <h3>О системе</h3>
            <p>Локальный чат-бот для кодинга использует:</p>
            <ul>
              <li><strong>DeepSeek-coder</strong> - для генерации кода и ответов</li>
              <li><strong>Ollama</strong> - для локального запуска модели</li>
              <li><strong>FastAPI</strong> - для API бэкенда</li>
              <li><strong>React</strong> - для фронтенда</li>
            </ul>
            
            <h3>Возможности</h3>
            <ul>
              <li>Написание и объяснение кода</li>
              <li>Создание и редактирование файлов</li>
              <li>Выполнение Python кода</li>
              <li>Хранение истории диалога</li>
            </ul>
          </div>
        )}
      </main>
      
      <footer className="app-footer">
        <p>Локальный чат-бот для кодинга | Использует DeepSeek-coder через Ollama</p>
      </footer>
    </div>
  );
}

export default App;
