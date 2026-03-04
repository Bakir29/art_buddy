import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/useAuthStore';
import { aiApi } from '@/services/api';
import { 
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
  model_used?: string;
}

const SAMPLE_PROMPTS = [
  "What are the primary colors and how do they mix to create secondary colors?",
  "How do I create depth and perspective in my drawings?",
  "What's the difference between digital and traditional art techniques?",
  "How can I improve my portrait drawing skills?",
  "Explain color theory and how it applies to painting",
  "What are the basic drawing techniques every artist should know?"
];

export function TutorPage() {
  const { user } = useAuthStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Get knowledge base stats for RAG testing info
  const { data: knowledgeStats } = useQuery({
    queryKey: ['knowledge-stats'],
    queryFn: () => aiApi.getKnowledgeStats(),
    refetchOnWindowFocus: false,
  });

  const askAIMutation = useMutation({
    mutationFn: (question: string) => aiApi.askQuestion({
      user_id: user?.id || '',
      question,
      context: `I am a ${user?.skill_level || 'beginner'} learning about art fundamentals`
    }),
    onSuccess: (response) => {
      const assistantMessage: ChatMessage = {
        id: Date.now().toString() + '-assistant',
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources?.map(s => s.source) || [],
        model_used: response.model_used
      };
      setMessages(prev => [...prev, assistantMessage]);
    },
    onError: (error: any) => {
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '-error',
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const handleSendMessage = (message: string = inputMessage) => {
    if (!message.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString() + '-user',
      role: 'user', 
      content: message,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    askAIMutation.mutate(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-black uppercase text-zinc-100 flex items-center">
          <ChatBubbleLeftRightIcon className="h-7 w-7 mr-3 text-orange-500" />
          AI Art Tutor
        </h1>
        <p className="mt-1 text-sm text-zinc-400 uppercase tracking-widest">
          Get personalized guidance using RAG-powered AI with {knowledgeStats?.total_knowledge_chunks ?? 'multiple'} knowledge sources.
        </p>
      </div>

      {/* RAG Testing Info */}
      <div className="bg-zinc-900 border border-zinc-700 p-4 mb-6">
        <div className="flex items-center mb-2">
          <LightBulbIcon className="h-5 w-5 text-orange-500 mr-2" />
          <h3 className="text-sm font-black uppercase tracking-widest text-zinc-200">RAG System Status</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="font-bold text-zinc-400 uppercase tracking-widest text-xs">Knowledge Sources:</span>
            <span className="ml-1 text-zinc-200">{knowledgeStats === undefined ? 'Loading...' : knowledgeStats.knowledge_sources}</span>
          </div>
          <div>
            <span className="font-bold text-zinc-400 uppercase tracking-widest text-xs">Total Chunks:</span>
            <span className="ml-1 text-zinc-200">{knowledgeStats === undefined ? 'Loading...' : knowledgeStats.total_knowledge_chunks}</span>
          </div>
          <div>
            <span className="font-bold text-zinc-400 uppercase tracking-widest text-xs">Available Sources:</span>
            <span className="ml-1 text-zinc-200">{knowledgeStats?.available_sources?.length || 0}</span>
          </div>
        </div>
      </div>

      {/* Sample Prompts */}
      {messages.length === 0 && (
        <div className="bg-zinc-900 border border-zinc-800 p-6 mb-6">
          <h3 className="text-lg font-black uppercase text-zinc-100 mb-4 flex items-center">
            <AcademicCapIcon className="h-5 w-5 mr-2 text-orange-500" />
            Try These RAG Test Questions:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {SAMPLE_PROMPTS.map((prompt, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(prompt)}
                className="text-left p-3 border border-zinc-700 hover:border-orange-500 hover:bg-zinc-800 transition-colors"
              >
                <div className="text-sm text-zinc-300">{prompt}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 bg-zinc-900 border border-zinc-800 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-orange-500 text-black'
                  : 'bg-zinc-800 text-zinc-200 border border-zinc-700'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-zinc-600">
                    <div className="text-xs text-zinc-400">
                      <strong>Sources:</strong> {message.sources.join(', ')}
                    </div>
                  </div>
                )}
                {message.model_used && (
                  <div className="text-xs text-zinc-500 mt-1">
                    Model: {message.model_used}
                  </div>
                )}
                <div className="text-xs text-zinc-500 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {askAIMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-zinc-800 border border-zinc-700 text-zinc-300 px-4 py-2">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500 mr-2"></div>
                  AI is thinking...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-zinc-800 p-4">
          <div className="flex space-x-4">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about art techniques, color theory, drawing, or any art topic..."
              className="flex-1 bg-zinc-800 border border-zinc-700 px-3 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-orange-500 resize-none"
              rows={3}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || askAIMutation.isPending}
              className="bg-orange-500 hover:bg-orange-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-black px-4 py-2 transition-colors flex items-center"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}






