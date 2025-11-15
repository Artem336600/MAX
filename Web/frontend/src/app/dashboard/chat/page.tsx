'use client'

import { useState, useEffect, useRef } from 'react'
import api from '@/lib/api'
import { MessageSquare, Send, Loader2 } from 'lucide-react'

interface Message {
  id: string
  role: string
  content: string
  created_at: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Добавляем сообщение пользователя сразу
    const tempUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await api.post('/chat/message', {
        message: userMessage,
        conversation_id: conversationId
      })

      // Обновляем conversation_id если это первое сообщение
      if (!conversationId) {
        setConversationId(response.data.conversation_id)
      }

      // Добавляем ответ ИИ
      setMessages(prev => [...prev, response.data.message])
    } catch (error) {
      console.error('Error sending message:', error)
      // Удаляем временное сообщение при ошибке
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Чат с ИИ</h1>
        </div>
        <p className="text-gray-600 mt-1">Ваш персональный ИИ-ассистент на базе DeepSeek</p>
      </div>

      {/* Messages */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Начните диалог
                </h3>
                <p className="text-gray-600">
                  Задайте вопрос или попросите помощь
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    <div
                      className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(message.created_at).toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSend} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Напишите сообщение..."
              className="flex-1 px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span>Отправить</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
