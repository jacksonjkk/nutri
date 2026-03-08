
import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Camera, Image as ImageIcon } from 'lucide-react';
import Markdown from 'react-markdown';
import { generateNutritionAdvice, analyzeFoodImage } from '../services/apiService';
import { UserProfile } from '../types';
import { Card, Button, cn } from './UI';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  image?: string;
}

export const NutritionChat = ({ userProfile }: { userProfile?: UserProfile }) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I am Nutri agent, your Ugandan nutrition assistant. How can I help you eat better today?\n You can ask me about local foods, meal planning, or managing health conditions.\n\n**NEW:** You can now upload a photo of your meal for a quick nutritional analysis! 📸" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    const response = await generateNutritionAdvice(userMsg, userProfile);
    setMessages(prev => [...prev, { role: 'assistant', content: response || "I'm sorry, I couldn't process that." }]);
    setIsLoading(false);
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64 = reader.result as string;
      setMessages(prev => [...prev, { 
        role: 'user', 
        content: "Analyzing this meal...",
        image: base64 
      }]);

      const result = await analyzeFoodImage(base64);
      
      if (result.error) {
        setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I couldn't analyze that image. Please try again." }]);
      } else {
        const content = `### 🥗 Meal Analysis\n\n**Identified Foods:** ${result.identified_foods.join(', ')}\n\n**Estimated Nutrition:**\n- ⚡ Calories: ${result.estimates.calories} kcal\n- 💪 Protein: ${result.estimates.protein}g\n- 🍞 Carbs: ${result.estimates.carbs}g\n- 🥑 Fats: ${result.estimates.fats}g\n\n**💡 Agent Insight:** ${result.insight}`;
        setMessages(prev => [...prev, { role: 'assistant', content }]);
      }
      setIsLoading(false);
    };
    reader.readAsDataURL(file);
  };

  return (
    <Card className="flex flex-col h-[600px] max-h-[80vh]">
      <div className="flex items-center justify-between mb-4 border-bottom pb-2">
        <h3 className="text-xl font-serif font-semibold text-stone-800">Chat with Nutri Agent</h3>
        <div className="flex gap-2">
          <span className="text-xs text-stone-400 italic">English / Luganda / Swahili</span>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 scrollbar-hide">
        {messages.map((msg, i) => (
          <div key={i} className={cn(
            "flex gap-3 max-w-[85%]",
            msg.role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
          )}>
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
              msg.role === 'user' ? "bg-[#F27D26]" : "bg-[#5A5A40]"
            )}>
              {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
            </div>
            <div className={cn(
              "p-4 rounded-2xl text-sm leading-relaxed",
              msg.role === 'user' ? "bg-stone-100 text-stone-800 rounded-tr-none" : "bg-[#f5f5f0] text-stone-800 rounded-tl-none border border-stone-200"
            )}>
              {msg.image && (
                <img src={msg.image} alt="Uploaded meal" className="w-full h-48 object-cover rounded-xl mb-3 shadow-inner" />
              )}
              <div className="markdown-body prose prose-stone prose-sm max-w-none">
                <Markdown>{msg.content}</Markdown>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 mr-auto">
            <div className="w-8 h-8 rounded-full bg-[#5A5A40] flex items-center justify-center">
              <Loader2 size={16} className="text-white animate-spin" />
            </div>
            <div className="bg-[#f5f5f0] p-4 rounded-2xl rounded-tl-none border border-stone-200">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2 pt-4 border-t border-stone-100">
        <input 
          type="file" 
          accept="image/*" 
          hidden 
          ref={fileInputRef} 
          onChange={handleImageUpload} 
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-3 text-stone-400 hover:text-[#F27D26] hover:bg-stone-50 rounded-full transition-all"
          title="Analyze Meal Photo"
        >
          <Camera size={20} />
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about Matooke, Mukene, or meal plans..."
          className="flex-1 bg-stone-50 border border-stone-200 rounded-full px-6 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#5A5A40]/20 transition-all"
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="bg-[#5A5A40] text-white p-3 rounded-full hover:bg-[#4A4A30] transition-all active:scale-90 disabled:opacity-50"
        >
          <Send size={20} />
        </button>
      </div>
    </Card>
  );
};
