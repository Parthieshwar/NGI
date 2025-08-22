import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, Moon, Sun, Loader2, Mic, Camera } from 'lucide-react';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [listening, setListening] = useState(false);

  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    document.body.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const getBackendResponse = async (userPrompt) => {
    setIsLoading(true);
  
    // Add the user message
    setMessages((prev) => [...prev, { sender: 'user', text: userPrompt }]);
  
    let aiMessage = '';
  
    // Add an empty AI message immediately so we can update it
    setMessages((prev) => [...prev, { sender: 'ai', text: '' }]);
  
    const eventSource = new EventSource(
      `http://127.0.0.1:8000/stream?question=${encodeURIComponent(userPrompt)}`
    );
  
    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        eventSource.close();
        setIsLoading(false);
        return;
      }
  
      aiMessage += event.data;
  
      // Always update the last AI message
      setMessages((prev) => {
        const updated = [...prev];
        // Find the last AI message and update it
        for (let i = updated.length - 1; i >= 0; i--) {
          if (updated[i].sender === 'ai') {
            updated[i] = { sender: 'ai', text: aiMessage };
            break;
          }
        }
        return updated;
      });
    };
  
    eventSource.onerror = () => {
      eventSource.close();
      setMessages((prev) => {
        const updated = [...prev];
        // Update last AI message to show error instead of creating a new one
        for (let i = updated.length - 1; i >= 0; i--) {
          if (updated[i].sender === 'ai') {
            updated[i] = { sender: 'ai', text: 'Error: Could not connect to backend.' };
            break;
          }
        }
        return updated;
      });
      setIsLoading(false);
    };
  };   

  const handleSend = () => {
    const textToSend = input.trim();
    if (textToSend === '') return;
    getBackendResponse(textToSend);
    setInput('');
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      getBackendResponse(transcript);
    };

    recognition.start();
  };

  const handleCameraClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setMessages((prev) => [
        ...prev,
        { sender: 'user', text: `📷 Sent an image: ${file.name}` }
      ]);
      // TODO: Handle upload or AI image processing here
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        
        {/* Navbar */}
        <div className="navbar">
          <div className="nav-left">
            <Bot size={24} className="bot-icon" />
            <span className="nav-title">AI Chat</span>
          </div>
          <button onClick={() => setIsDarkMode(!isDarkMode)} className="theme-toggle">
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>

        {/* Chat Window */}
        <div className="chat-window">
          {messages.length === 0 && (
            <div className="welcome-screen">
              <h2>Hello, I'm a Chatbot!</h2>
              <p>How can I assist you today?</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`msg-row ${msg.sender}`}>
              <div className={`msg-bubble ${msg.sender}`}>{msg.text}</div>
            </div>
          ))}

          {isLoading && (
            <div className="msg-row ai">
              {/* <div className="msg-bubble ai">
                {<Loader2 size={20} className="loading-icon" />}
                {<span>Typing...</span> }
              </div> */}
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="input-bar">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
            placeholder="Message AI Chat..."
            disabled={isLoading}
          />
          
          {/* Hidden input for camera */}
          <input
            type="file"
            accept="image/*"
            capture="environment"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />

          {/* Camera button */}
          <button onClick={handleCameraClick} className="camera-btn">
            <Camera size={20} />
          </button>

          {/* Mic button */}
          <button 
            onClick={handleVoiceInput} 
            disabled={isLoading || listening} 
            className={`mic-btn ${listening ? 'listening' : ''}`}>
            <Mic size={20} />
          </button>

          {/* Send button */}
          <button 
            onClick={handleSend} 
            disabled={isLoading || input.trim() === ''} 
            className="send-btn">
            <Send size={20} />
          </button>
        </div>

      </div>
    </div>
  );
};

export default App;
