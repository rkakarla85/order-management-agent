import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Send, User, Bot, Loader2 } from 'lucide-react'

function ChatInterface({ sessionId }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your Electronics Shop Assistant. How can I help you today?' }
    ])
    const [inputText, setInputText] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async (e) => {
        e.preventDefault()
        if (!inputText.trim() || isLoading) return

        const userMessage = inputText
        setInputText('')
        setIsLoading(true)

        // Add user message to UI
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])

        try {
            const response = await axios.post('http://localhost:8000/chat', {
                message: userMessage,
                session_id: sessionId
            })

            const aiMessage = response.data.response
            setMessages(prev => [...prev, { role: 'assistant', content: aiMessage }])
        } catch (error) {
            console.error("Error sending message:", error)
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error. Please try again." }])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="chat-interface">
            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div key={index} className={`message-wrapper ${msg.role}`}>
                        <div className={`avatar ${msg.role}`}>
                            {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className="message-bubble">
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message-wrapper assistant">
                        <div className="avatar assistant">
                            <Bot size={20} />
                        </div>
                        <div className="message-bubble loading">
                            <Loader2 className="spin" size={20} />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form className="input-area" onSubmit={sendMessage}>
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Type your order here..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading || !inputText.trim()}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    )
}

export default ChatInterface
