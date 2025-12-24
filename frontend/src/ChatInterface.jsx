import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Send, User, Bot, Loader2, Mic, MicOff, X, Volume2, Image as ImageIcon, Globe } from 'lucide-react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'

function ChatInterface({ sessionId, businessId, businessName }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: `Hello! Welcome to ${businessName}. I am your assistant. How can I help you today?` }
    ])

    // Reset chat when business changes
    useEffect(() => {
        setMessages([
            { role: 'assistant', content: `Hello! Welcome to ${businessName}. I am your assistant. How can I help you today?` }
        ])
    }, [businessName])
    const [inputText, setInputText] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [isVoiceMode, setIsVoiceMode] = useState(false)
    const [audioUrl, setAudioUrl] = useState(null)
    const [isSpeaking, setIsSpeaking] = useState(false)
    const [selectedImage, setSelectedImage] = useState(null)
    const [previewUrl, setPreviewUrl] = useState(null)
    const [language, setLanguage] = useState('en-US')
    const [isStarting, setIsStarting] = useState(false)
    const fileInputRef = useRef(null)

    // Voice Recognition Hooks
    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition,
        isMicrophoneAvailable
    } = useSpeechRecognition()

    const messagesEndRef = useRef(null)
    const audioPlayerRef = useRef(null)
    const silenceTimerRef = useRef(null)

    // Scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, listening])

    // Clear starting state when listening begins or after timeout
    useEffect(() => {
        let timeoutId;
        if (listening && isStarting) {
            setIsStarting(false)
        } else if (isStarting && !listening) {
            // Safety timeout: if checking permissions or starting takes too long
            timeoutId = setTimeout(() => {
                setIsStarting(false);
            }, 5000);
        }
        return () => {
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [listening, isStarting])

    // Handle Transcript Changes (Auto-submit logic)
    useEffect(() => {
        if (isVoiceMode && listening && transcript) {
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current)

            silenceTimerRef.current = setTimeout(() => {
                handleVoiceSubmit(transcript)
            }, 1500)
        }
    }, [transcript, listening, isVoiceMode])

    // Cleanup
    useEffect(() => {
        return () => {
            if (audioUrl) URL.revokeObjectURL(audioUrl)
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current)
            SpeechRecognition.stopListening()
        }
    }, [])

    const handleImageSelect = (e) => {
        const file = e.target.files[0]
        if (file) {
            const reader = new FileReader()
            reader.onloadend = () => {
                setSelectedImage(reader.result)
                setPreviewUrl(URL.createObjectURL(file))
            }
            reader.readAsDataURL(file)
        }
    }

    const clearImage = () => {
        setSelectedImage(null)
        setPreviewUrl(null)
        if (fileInputRef.current) fileInputRef.current.value = ''
    }

    const handleVoiceSubmit = async (text) => {
        if (!text.trim()) return

        SpeechRecognition.stopListening()
        resetTranscript()
        setIsLoading(true)

        setMessages(prev => [...prev, { role: 'user', content: text }])

        try {
            const payload = {
                message: text,
                session_id: sessionId,
                image: selectedImage,
                business_id: businessId
            }

            const API_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';
            const chatRes = await axios.post(`${API_URL}/chat`, payload)
            const aiText = chatRes.data.response

            setMessages(prev => [...prev, { role: 'assistant', content: aiText }])
            clearImage()
            await playTextToSpeech(aiText)

        } catch (error) {
            console.error("Error in voice flow:", error)
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I had trouble processing that." }])
            if (isVoiceMode) SpeechRecognition.startListening({ continuous: true, language: language })
        } finally {
            setIsLoading(false)
        }
    }

    const playTextToSpeech = async (text) => {
        try {
            setIsSpeaking(true)
            const response = await axios.post(`${import.meta.env.PROD ? '' : 'http://localhost:8000'}/tts`, { text, language }, { responseType: 'blob' })
            const url = URL.createObjectURL(response.data)

            if (audioUrl) URL.revokeObjectURL(audioUrl)
            setAudioUrl(url)

            const audio = new Audio(url)
            audioPlayerRef.current = audio

            audio.onended = () => {
                setIsSpeaking(false)
                // Resume listening after AI finishes
                if (isVoiceMode) {
                    resetTranscript()
                    SpeechRecognition.startListening({ continuous: true, language: language })
                }
            }

            audio.play()
        } catch (e) {
            console.error("TTS Error", e)
            setIsSpeaking(false)
            if (isVoiceMode) SpeechRecognition.startListening({ continuous: true, language: language })
        }

    }

    const toggleVoiceMode = () => {
        if (!browserSupportsSpeechRecognition) {
            alert("Browser doesn't support speech recognition.")
            return
        }

        if (isVoiceMode) {
            setIsVoiceMode(false)
            setIsStarting(false)
            SpeechRecognition.stopListening()
            if (audioPlayerRef.current) {
                audioPlayerRef.current.pause()
                audioPlayerRef.current = null
            }
        } else {
            setIsVoiceMode(true)
            setIsStarting(true)
            resetTranscript()
            SpeechRecognition.startListening({ continuous: true, language: language })
        }
    }

    // Restart listening if language changes while active
    useEffect(() => {
        if (isVoiceMode && !isSpeaking && !isLoading) {
            SpeechRecognition.stopListening()
            setTimeout(() => {
                SpeechRecognition.startListening({ continuous: true, language: language })
            }, 100)
        }
    }, [language])

    const sendMessage = async (e) => {
        e.preventDefault()
        if ((!inputText.trim() && !selectedImage) || isLoading) return

        const userMessage = inputText
        const imageToSend = selectedImage

        setInputText('')
        clearImage()
        setIsLoading(true)

        setMessages(prev => [
            ...prev,
            { role: 'user', content: userMessage, image: previewUrl }
        ])

        try {
            const API_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';
            const response = await axios.post(`${API_URL}/chat`, {
                message: userMessage,
                session_id: sessionId,
                image: imageToSend,
                business_id: businessId
            })
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }])
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Error sending message." }])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="chat-interface">
            <div className="language-selector-bar">
                <Globe size={16} />
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    disabled={isVoiceMode}
                    className="lang-select"
                >
                    <option value="en-US">English (US)</option>
                    <option value="en-IN">English (India)</option>
                    <option value="hi-IN">Hindi (हिंदी)</option>
                    <option value="te-IN">Telugu (తెలుగు)</option>
                    <option value="kn-IN">Kannada (ಕನ್ನಡ)</option>
                </select>
            </div>

            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div key={index} className={`message-wrapper ${msg.role}`}>
                        <div className={`avatar ${msg.role}`}>
                            {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className="message-content-col">
                            {msg.image && (
                                <img src={msg.image} alt="User Upload" className="message-image-preview" />
                            )}
                            {msg.content && (
                                <div className="message-bubble">
                                    {msg.content}
                                </div>
                            )}
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

            {/* Voice Mode Status */}
            {isVoiceMode && (
                <div className="voice-status-bar">
                    {!browserSupportsSpeechRecognition ? (
                        <div className="status error">Browser not supported</div>
                    ) : !isMicrophoneAvailable ? (
                        <div className="status error">Mic access denied</div>
                    ) : isStarting ? (
                        <div className="status processing">
                            <Loader2 className="spin" size={18} />
                            <span>Connecting...</span>
                        </div>
                    ) : isSpeaking ? (
                        <div className="status speaking">
                            <Volume2 className="pulse-icon" size={18} />
                            <span>Speaking...</span>
                        </div>
                    ) : isLoading ? (
                        <div className="status processing">
                            <Loader2 className="spin" size={18} />
                            <span>Processing...</span>
                        </div>
                    ) : listening ? (
                        <div className="status recording">
                            <Mic className="pulse-icon" size={18} />
                            <span>Listening... ({language})</span>
                            <div className="transcript-preview">{transcript}</div>
                        </div>
                    ) : (
                        <button
                            className="status"
                            style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer' }}
                            onClick={() => SpeechRecognition.startListening({ continuous: true, language: language })}
                        >
                            <MicOff size={18} />
                            <span>Paused (Click to Resume)</span>
                        </button>
                    )}

                    <button className="exit-voice-btn" onClick={toggleVoiceMode}>
                        <X size={18} /> Exit Voice
                    </button>
                </div>
            )}

            {previewUrl && (
                <div className="image-preview-bar">
                    <img src={previewUrl} alt="Preview" />
                    <button className="close-preview" onClick={clearImage}>
                        <X size={16} />
                    </button>
                    <span>Image attached</span>
                </div>
            )}

            <form className="input-area" onSubmit={sendMessage}>
                <input
                    type="file"
                    accept="image/*"
                    ref={fileInputRef}
                    onChange={handleImageSelect}
                    style={{ display: 'none' }}
                />

                <button
                    type="button"
                    className={`icon-btn ${selectedImage ? 'active' : ''}`}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading}
                    title="Upload Image"
                >
                    <ImageIcon size={20} />
                </button>

                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={isVoiceMode ? "Listening..." : "Type your order..."}
                    disabled={isLoading || isVoiceMode}
                />

                <button
                    type="button"
                    className={`voice-toggle-btn ${isVoiceMode ? 'active' : ''}`}
                    onClick={toggleVoiceMode}
                    title={isVoiceMode ? "Exit Voice Mode" : "Start Voice Conversation"}
                >
                    {isVoiceMode ? <MicOff size={20} /> : <Mic size={20} />}
                </button>

                <button type="submit" disabled={isLoading || isVoiceMode || (!inputText.trim() && !selectedImage)}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    )
}

export default ChatInterface
