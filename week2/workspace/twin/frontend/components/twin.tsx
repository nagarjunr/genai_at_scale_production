'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function Twin() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // const response = await fetch('http://localhost:8000/chat', {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            // Add error message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl border border-cyan-200/50 overflow-hidden">
            {/* Elegant Header */}
            <div className="relative bg-gradient-to-r from-cyan-600 via-sky-500 to-cyan-600 text-white p-5 md:p-6">
                <div className="absolute inset-0 bg-white/5 backdrop-blur-sm" />
                <div className="relative flex items-center gap-3 md:gap-4">
                    <div className="w-10 h-10 md:w-12 md:h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center ring-2 ring-white/30">
                        <Bot className="w-6 h-6 md:w-7 md:h-7 text-white" />
                    </div>
                    <div>
                        <h2 className="text-lg md:text-xl font-bold tracking-tight">Chat with Nagarjun's Twin</h2>
                        <p className="text-xs md:text-sm text-cyan-50/90 font-light mt-1.5">AI-Powered Digital Assistant</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 bg-gradient-to-b from-white/40 via-cyan-50/20 to-sky-50/30">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="relative">
                            <div className="absolute inset-0 bg-cyan-400/20 blur-2xl rounded-full" />
                            <div className="relative w-20 h-20 md:w-24 md:h-24 bg-gradient-to-br from-cyan-500 to-sky-500 rounded-3xl flex items-center justify-center shadow-xl mb-6">
                                <Bot className="w-12 h-12 md:w-14 md:h-14 text-white" />
                            </div>
                        </div>
                        <h3 className="text-xl md:text-2xl font-bold text-cyan-700 mb-2">Welcome</h3>
                        <p className="text-sm md:text-base text-cyan-600/70 max-w-md">
                            How can I help you today?
                        </p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0">
                                <div className="w-9 h-9 md:w-11 md:h-11 bg-gradient-to-br from-cyan-500 to-sky-600 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-cyan-200/50">
                                    <Bot className="w-5 h-5 md:w-6 md:h-6 text-white" />
                                </div>
                            </div>
                        )}

                        <div
                            className={`max-w-[75%] md:max-w-[80%] rounded-3xl p-4 md:p-5 shadow-lg transition-all hover:shadow-xl ${
                                message.role === 'user'
                                    ? 'bg-gradient-to-br from-cyan-600 to-sky-600 text-white'
                                    : 'bg-white/90 backdrop-blur-sm border border-cyan-100/50 text-gray-800'
                            }`}
                        >
                            <p className="whitespace-pre-wrap text-sm md:text-base leading-relaxed">{message.content}</p>
                            <p
                                className={`text-xs mt-2 font-light ${
                                    message.role === 'user' ? 'text-cyan-50/80' : 'text-cyan-500/70'
                                }`}
                            >
                                {message.timestamp.toLocaleTimeString()}
                            </p>
                        </div>

                        {message.role === 'user' && (
                            <div className="flex-shrink-0">
                                <div className="w-9 h-9 md:w-11 md:h-11 bg-gradient-to-br from-cyan-400 to-sky-400 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-cyan-200/50">
                                    <User className="w-5 h-5 md:w-6 md:h-6 text-white" />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="flex-shrink-0">
                            <div className="w-9 h-9 md:w-11 md:h-11 bg-gradient-to-br from-cyan-500 to-sky-600 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-cyan-200/50 animate-pulse">
                                <Bot className="w-5 h-5 md:w-6 md:h-6 text-white" />
                            </div>
                        </div>
                        <div className="bg-white/90 backdrop-blur-sm border border-cyan-100/50 rounded-3xl p-4 md:p-5 shadow-lg">
                            <div className="flex space-x-2">
                                <div className="w-2.5 h-2.5 bg-gradient-to-r from-cyan-500 to-sky-500 rounded-full animate-bounce" />
                                <div className="w-2.5 h-2.5 bg-gradient-to-r from-sky-500 to-cyan-500 rounded-full animate-bounce delay-100" />
                                <div className="w-2.5 h-2.5 bg-gradient-to-r from-cyan-500 to-sky-500 rounded-full animate-bounce delay-200" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Elegant Input */}
            <div className="border-t border-cyan-200/50 p-5 md:p-6 bg-white/50 backdrop-blur-sm">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Ask a question..."
                        className="flex-1 px-5 md:px-6 py-3 md:py-4 border border-cyan-200/60 rounded-2xl focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-cyan-400 text-gray-800 bg-white/80 placeholder-cyan-400/60 text-sm md:text-base shadow-sm transition-all"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="px-5 md:px-7 py-3 md:py-4 bg-gradient-to-r from-cyan-600 to-sky-600 text-white rounded-2xl hover:from-cyan-700 hover:to-sky-700 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}