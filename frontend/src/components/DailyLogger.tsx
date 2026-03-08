import React, { useState, useEffect } from 'react';
import { Calendar, Flame, Beef, Droplets, Moon, Dumbbell, Save, CheckCircle2, AlertCircle, Plus, Trash2, Utensils } from 'lucide-react';
import { Card, Button, Badge, cn } from './UI';
import { saveDailyLog, getDailyLogs, getFoods, getMe } from '../services/apiService';
import { FoodItem } from '../types';

interface DailyLoggerProps {
    onLogSaved?: () => void;
}

export const DailyLogger = ({ onLogSaved }: DailyLoggerProps) => {
    const today = new Date().toISOString().split('T')[0];
    const [selectedFoods, setSelectedFoods] = useState<{ food: FoodItem, quantity: number }[]>([]);
    const [formData, setFormData] = useState({
        date: today,
        calories: 0,
        protein: 0,
        carbs: 0,
        fats: 0,
        sleep_hours: 8,
        exercise_minutes: 0,
        water_intake: 2.0
    });
    const [foods, setFoods] = useState<FoodItem[]>([]);
    const [filteredFoods, setFilteredFoods] = useState<FoodItem[]>([]);
    const [userProfile, setUserProfile] = useState<any>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // Initial Data Fetch
    useEffect(() => {
        const loadInitialData = async () => {
            // 1. Fetch User Profile
            const userData = await getMe();
            if (userData) {
                setUserProfile(userData);
            }

            // 2. Fetch Foods
            const foodData = await getFoods();
            if (Array.isArray(foodData)) {
                setFoods(foodData);
            }

            // 3. Fetch Logs
            const logs = await getDailyLogs();
            if (Array.isArray(logs) && logs.length > 0) {
                const todayLog = logs.find((l: any) => l.date === today);
                if (todayLog) {
                    setFormData(prev => ({
                        ...prev,
                        water_intake: todayLog.water_intake,
                        sleep_hours: todayLog.sleep_hours
                    }));
                }
            }
        };
        loadInitialData();
    }, [today]);

    // Intelligent Food Filtering
    useEffect(() => {
        if (foods.length === 0) return;

        let filtered = [...foods];

        if (userProfile && userProfile.profile_summary) {
            const profile = userProfile.profile_summary;
            const goal = (profile.goal || '').toLowerCase();
            const region = (profile.region || '').toLowerCase();
            const conditions = profile.medical_conditions || [];

            // 1. Regional Filter (Prioritize)
            // If the user is from a specific region, we don't exclude others, but we could sort them higher.
            // For now, let's filter to keep the UI clean if we have many foods.
            if (region) {
                const regionalFoods = foods.filter(f => (f.region || '').toLowerCase().includes(region));
                if (regionalFoods.length > 0) {
                    filtered = regionalFoods;
                }
            }

            // 2. Goal-Based Filtering
            if (goal.includes('gain') || goal.includes('weight')) {
                // High calorie/protein
                filtered = filtered.sort((a, b) => (b.calories + b.protein * 4) - (a.calories + a.protein * 4));
            } else if (goal.includes('lose') || goal.includes('diabetes')) {
                // Low glycemic index / low calorie
                filtered = filtered.filter(f => f.glycemic_index < 55 || f.calories < 150);
            }
        }

        setFilteredFoods(filtered.slice(0, 12)); // Show top 12 relevant
    }, [foods, userProfile]);

    const addFood = (food: FoodItem) => {
        const newList = [...selectedFoods, { food, quantity: 1 }];
        setSelectedFoods(newList);
        updateMacros(newList);
    };

    const removeFood = (index: number) => {
        const newList = selectedFoods.filter((_, i) => i !== index);
        setSelectedFoods(newList);
        updateMacros(newList);
    };

    const updateMacros = (list: { food: FoodItem, quantity: number }[]) => {
        const totals = list.reduce((acc, item) => ({
            calories: acc.calories + (item.food.calories * item.quantity),
            protein: acc.protein + (item.food.protein * item.quantity),
            carbs: acc.carbs + (item.food.carbs * item.quantity),
            fats: acc.fats + (item.food.fat * item.quantity)
        }), { calories: 0, protein: 0, carbs: 0, fats: 0 });

        setFormData(prev => ({
            ...prev,
            ...totals
        }));
    };

    const handleSubmit = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        setIsSaving(true);
        setMessage(null);

        // Get the name of the last added food to trigger AI risk check in backend
        const lastFood = selectedFoods.length > 0 ? selectedFoods[selectedFoods.length - 1].food.name : undefined;
        
        const result = await saveDailyLog({
            ...formData,
            food_name: lastFood
        });

        if (!result.error) {
            setMessage({ 
                type: 'success', 
                text: 'Daily log updated successfully!',
                swap: result.swap_suggestion 
            } as any);
            // Clear plate after saving to avoid double-adding if they log again
            setSelectedFoods([]);
            if (onLogSaved) onLogSaved();
        } else {
            setMessage({ type: 'error', text: 'Failed to save log. Please try again.' });
        }
        setIsSaving(false);
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Food Selection */}
                <Card className="lg:col-span-2 p-6 bg-white border-none shadow-sm">
                    <header className="mb-6 flex justify-between items-center">
                        <div>
                            <h3 className="text-xl font-serif font-bold text-stone-800 flex items-center gap-2">
                                <Utensils size={20} className="text-[#F27D26]" />
                                What did you eat today?
                            </h3>
                            <p className="text-stone-500 text-xs mt-1">Select local foods to automatically calculate nutrition.</p>
                        </div>
                        <input
                            type="date"
                            value={formData.date}
                            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                            className="bg-stone-50 border border-stone-100 rounded-xl px-4 py-2 text-xs font-bold text-stone-600 outline-none"
                        />
                    </header>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-8">
                        {filteredFoods.map(food => (
                            <button
                                key={food.id}
                                onClick={() => addFood(food)}
                                className="flex flex-col items-start p-3 rounded-2xl border border-stone-100 hover:border-[#F27D26]/30 hover:bg-orange-50/30 transition-all text-left group"
                            >
                                <div className="flex justify-between w-full">
                                    <span className="font-bold text-sm text-stone-700 group-hover:text-[#F27D26]">{food.name}</span>
                                    {food.is_processed && <Badge className="text-[6px] h-3 bg-red-100 text-red-600 border-none">Proc.</Badge>}
                                </div>
                                <span className="text-[10px] text-stone-400 italic">{food.category}</span>
                                <div className="mt-2 flex items-center gap-1 text-[10px] font-mono font-bold text-stone-500">
                                    <Plus size={10} /> {food.calories} kcal
                                </div>
                            </button>
                        ))}
                        {filteredFoods.length === 0 && (
                            <div className="col-span-full py-10 text-center text-stone-400 text-xs italic">
                                Loading matching foods for your profile...
                            </div>
                        )}
                    </div>

                    {selectedFoods.length > 0 && (
                        <div className="space-y-3 border-t border-stone-50 pt-6">
                            <h4 className="text-[10px] uppercase tracking-widest font-black text-stone-400">Current Plate</h4>
                            <div className="space-y-2">
                                {selectedFoods.map((item, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-3 bg-stone-50 rounded-xl animate-in slide-in-from-left-2">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-[#5A5A40] shadow-sm">
                                                <Utensils size={14} />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-stone-700">{item.food.name}</p>
                                                <p className="text-[10px] text-stone-400">Standard Portion</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => removeFood(idx)}
                                            className="p-2 text-stone-300 hover:text-red-500 transition-colors"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </Card>

                {/* Right Column: Nutrition Summary & Lifestyle */}
                <Card className="p-6 bg-[#5A5A40] text-white">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <div className="flex justify-between items-center text-xs opacity-70 uppercase tracking-widest font-bold">
                                <span>Plate Nutrition</span>
                                <Flame size={14} />
                            </div>
                            <p className="text-4xl font-mono font-black">{Math.round(formData.calories)} <span className="text-sm opacity-50">kcal</span></p>
                        </div>

                        <div className="grid grid-cols-3 gap-4 border-t border-white/10 pt-6">
                            <div className="text-center">
                                <p className="text-[10px] opacity-60 font-bold uppercase mb-1">Protein</p>
                                <p className="font-mono font-bold text-sm">{Math.round(formData.protein)}g</p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] opacity-60 font-bold uppercase mb-1">Carbs</p>
                                <p className="font-mono font-bold text-sm">{Math.round(formData.carbs)}g</p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] opacity-60 font-bold uppercase mb-1">Fats</p>
                                <p className="font-mono font-bold text-sm">{Math.round(formData.fats)}g</p>
                            </div>
                        </div>

                        {/* Sliders for Lifestyle */}
                        <div className="space-y-5 pt-4">
                            <div className="space-y-2">
                                <div className="flex justify-between items-center text-[10px] font-bold uppercase opacity-70">
                                    <span>Water Intake</span>
                                    <Droplets size={12} />
                                </div>
                                <input
                                    type="range" min="0" max="5" step="0.5"
                                    value={formData.water_intake}
                                    onChange={(e) => setFormData({ ...formData, water_intake: parseFloat(e.target.value) })}
                                    className="w-full accent-[#F27D26]"
                                />
                                <div className="flex justify-between text-xs font-mono">
                                    <span>{formData.water_intake} L</span>
                                    <span className="opacity-50">Goal: 2.5L</span>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between items-center text-[10px] font-bold uppercase opacity-70">
                                    <span>Last Night Sleep</span>
                                    <Moon size={12} />
                                </div>
                                <input
                                    type="range" min="0" max="15" step="0.5"
                                    value={formData.sleep_hours}
                                    onChange={(e) => setFormData({ ...formData, sleep_hours: parseFloat(e.target.value) })}
                                    className="w-full accent-[#F27D26]"
                                />
                                <div className="flex justify-between text-xs font-mono">
                                    <span>{formData.sleep_hours} Hrs</span>
                                    <span className="opacity-50">Goal: 8h</span>
                                </div>
                            </div>
                        </div>

                        {message && (
                            <div className="space-y-4">
                                <div className={cn(
                                    "p-3 rounded-xl text-[10px] font-bold flex items-center gap-2",
                                    message.type === 'success' ? "bg-emerald-500/20 text-emerald-100 border border-emerald-500/20" : "bg-red-500/20 text-red-100 border border-red-500/20"
                                )}>
                                    {message.type === 'success' ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
                                    {message.text}
                                </div>
                                
                                {message.type === 'success' && (message as any).swap && (message as any).swap.is_risky && (
                                    <div className="bg-white/10 p-4 rounded-xl border border-white/10 animate-in zoom-in-95">
                                        <h5 className="text-[10px] font-black uppercase text-amber-400 mb-2 flex items-center gap-2">
                                            <AlertCircle size={12} /> Smart Agent Suggestion
                                        </h5>
                                        <p className="text-xs font-medium leading-relaxed mb-3">
                                            {(message as any).swap.reason}
                                        </p>
                                        {(message as any).swap.swap_suggestion && (
                                            <div className="bg-white/5 p-2 rounded-lg flex items-center justify-between">
                                                <div>
                                                    <p className="text-[8px] opacity-60 uppercase font-black">Try this instead:</p>
                                                    <p className="text-xs font-bold font-serif">{(message as any).swap.swap_suggestion.food_name}</p>
                                                </div>
                                                <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/20 text-[8px]">Healthier</Badge>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        <Button
                            type="submit"
                            disabled={isSaving || (formData.calories === 0 && formData.water_intake === 0)}
                            className="w-full py-4 bg-[#F27D26] hover:bg-[#d96a1b] text-white shadow-xl shadow-black/10 transition-transform active:scale-95 border-none"
                        >
                            {isSaving ? 'Syncing with AI...' : 'Save Today\'s Record'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};
