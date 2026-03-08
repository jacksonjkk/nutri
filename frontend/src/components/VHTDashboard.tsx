
import React, { useState, useEffect } from 'react';
import {
    Users, UserPlus, Search, ArrowRight, Activity,
    MapPin, Phone, Mail, Calendar, LogOut, CheckCircle2,
    TrendingUp, Target, Heart, Baby, ChevronRight
} from 'lucide-react';
import { Card, Button, Badge, cn } from './UI';
import { getVHTDashboard, registerIndividual, logout } from '../services/apiService';
import { UserProfile, Language } from '../types';

const UGANDA_REGIONS: Record<string, string[]> = {
    'Central': ['Kampala', 'Mukono', 'Wakiso', 'Masaka', 'Mpigi', 'Luwero', 'Mubende', 'Kayunga', 'Rakai', 'Sembabule', 'Lyantonde', 'Mityana', 'Nakaseke'],
    'Western': ['Mbarara', 'Kabale', 'Fort Portal', 'Kasese', 'Bushenyi', 'Hoima', 'Ibanda', 'Kisoro', 'Masindi', 'Ntungamo', 'Rukungiri', 'Kamwenge'],
    'Eastern': ['Jinja', 'Mbale', 'Soroti', 'Tororo', 'Iganga', 'Busia', 'Kapchorwa', 'Kamuli', 'Bugiri', 'Mayuge', 'Butaleja', 'Namutumba'],
    'Northern': ['Gulu', 'Lira', 'Arua', 'Moroto', 'Kitgum', 'Apac', 'Adjumani', 'Nebbi', 'Yumbe', 'Kotido', 'Amuru', 'Oyam', 'Pader']
};

export const VHTDashboard = () => {
    const [view, setView] = useState<'list' | 'register'>('list');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    // Register Form State
    const [regForm, setRegForm] = useState({
        full_name: '',
        phone_number: '',
        age: 30,
        gender: 'male',
        height: 170,
        weight: 65,
        activity_level: 'moderate',
        goal: 'maintenance',
        region: '',
        district: '',
        muac_cm: 14.5,
        whz_score: 0
    });
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [selectedIndividual, setSelectedIndividual] = useState<any>(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        const res = await getVHTDashboard();
        if (res) setData(res);
        setLoading(false);
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage(null);

        const res = await registerIndividual(regForm);
        if (!res.error) {
            setMessage({ type: 'success', text: 'Individual registered successfully!' });
            setRegForm({
                full_name: '', phone_number: '',
                age: 30, gender: 'male', height: 170, weight: 65,
                activity_level: 'moderate', goal: 'maintenance',
                region: '', district: '',
                muac_cm: 14.5, whz_score: 0
            });
            fetchData();
            setTimeout(() => setView('list'), 2000);
        } else {
            setMessage({ type: 'error', text: res.error || 'Registration failed' });
        }
        setIsSaving(false);
    };

    const filteredIndividuals = data?.individuals.filter((i: any) =>
        i.profile?.full_name?.toLowerCase().includes(search.toLowerCase())
    ) || [];

    if (loading) return (
        <div className="min-h-screen bg-[#f5f5f0] flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-[#F27D26] border-t-transparent rounded-full animate-spin" />
                <p className="text-stone-500 font-bold uppercase tracking-widest text-xs">Loading Health Records...</p>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#f5f5f0] text-stone-800 font-sans pb-20">
            {/* VHT Header */}
            <header className="bg-white border-b border-stone-200 px-6 py-4 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-[#5A5A40] rounded-2xl flex items-center justify-center text-white shadow-lg">
                            <Activity size={24} />
                        </div>
                        <div>
                            <h1 className="text-xl font-serif font-black text-stone-800">VHT Dashboard</h1>
                            <p className="text-[10px] uppercase font-black text-[#F27D26] tracking-widest">Village Health Team • {data?.vht_name}</p>
                        </div>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => { logout(); window.location.reload(); }}
                        className="text-stone-400 hover:text-red-500 border-none px-2"
                    >
                        <LogOut size={20} />
                    </Button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto p-6 space-y-8">
                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="p-6 bg-white border-none shadow-sm flex items-center gap-6">
                        <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center">
                            <Users size={28} />
                        </div>
                        <div>
                            <p className="text-[10px] uppercase font-black text-stone-400 tracking-widest mb-1">Total Registered</p>
                            <p className="text-3xl font-mono font-black">{data?.registered_count || 0}</p>
                        </div>
                    </Card>

                    <Card className="md:col-span-2 p-6 bg-[#F27D26] text-white border-none shadow-xl flex justify-between items-center">
                        <div className="space-y-1">
                            <h3 className="text-lg font-serif font-bold">Register Individual</h3>
                            <p className="text-white/70 text-xs">Onboard a new community member and track their metrics.</p>
                        </div>
                        <Button
                            onClick={() => setView('register')}
                            className="bg-white text-[#F27D26] hover:bg-stone-50 rounded-2xl px-6 py-3 font-bold shadow-lg"
                        >
                            <UserPlus size={18} className="mr-2" />
                            Launch Form
                        </Button>
                    </Card>
                </div>

                {view === 'list' ? (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-serif font-bold">Community Records</h2>
                            <div className="relative">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-400" size={16} />
                                <input
                                    type="text"
                                    placeholder="Search by name or email..."
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="bg-white border-none shadow-sm rounded-full pl-12 pr-6 py-3 text-sm focus:ring-2 focus:ring-[#5A5A40]/10 outline-none w-64 md:w-80"
                                />
                            </div>
                        </div>

                        {filteredIndividuals.length === 0 ? (
                            <Card className="p-20 text-center border-dashed border-2 border-stone-200 bg-transparent shadow-none">
                                <Users size={48} className="mx-auto text-stone-300 mb-4" />
                                <h3 className="text-xl font-serif font-bold text-stone-400">No records found</h3>
                                <p className="text-stone-400 text-sm mt-2">Start registering individuals to track their progress.</p>
                            </Card>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {filteredIndividuals.map((individual: any) => (
                                    <Card key={individual.id} className="p-6 bg-white border-none shadow-sm hover:shadow-md transition-all group">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 bg-stone-100 rounded-2xl flex items-center justify-center text-stone-400 group-hover:bg-[#5A5A40]/5 group-hover:text-[#5A5A40] transition-colors">
                                                    <TrendingUp size={24} />
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-stone-800">{individual.profile?.full_name || 'Anonymous User'}</h4>
                                                    <p className="text-xs text-stone-400 flex items-center gap-1">
                                                        <Phone size={12} /> {individual.profile?.phone_number || 'No Phone Registered'}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                                <Badge className={individual.onboarding_completed ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"}>
                                                    {individual.onboarding_completed ? 'Profile Live' : 'Pending'}
                                                </Badge>
                                                {individual.screening && (
                                                    <Badge className={cn(
                                                        "font-black text-[9px]",
                                                        individual.screening.classification === 'SAM' ? "bg-red-500 text-white" :
                                                        individual.screening.classification === 'MAM' ? "bg-orange-400 text-white" :
                                                        "bg-emerald-500 text-white"
                                                    )}>
                                                        {individual.screening.classification}
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-stone-50">
                                            <div className="space-y-1">
                                                <p className="text-[10px] uppercase font-black text-stone-300 tracking-widest">Region</p>
                                                <p className="text-xs font-bold text-stone-600 truncate">{individual.profile?.region || 'N/A'}</p>
                                            </div>
                                            <div className="space-y-1">
                                                <p className="text-[10px] uppercase font-black text-stone-300 tracking-widest">Weight</p>
                                                <p className="text-xs font-bold text-stone-600">{individual.profile?.weight || '--'} kg</p>
                                            </div>
                                            <div className="space-y-1">
                                                <p className="text-[10px] uppercase font-black text-stone-300 tracking-widest">Contact</p>
                                                <p className="text-xs font-bold text-stone-600">{individual.profile?.phone_number || 'No Phone'}</p>
                                            </div>
                                        </div>

                                        <button 
                                            onClick={() => { setSelectedIndividual(individual); setShowModal(true); }}
                                            className="w-full mt-6 py-3 rounded-xl bg-stone-50 text-stone-400 font-bold text-[10px] uppercase tracking-widest flex items-center justify-center gap-2 group-hover:bg-[#5A5A40] group-hover:text-white transition-all"
                                        >
                                            {individual.screening?.type === 'pediatric_clinical' ? 'Clinical Follow Up' : 'View Health Profile'}
                                            <ChevronRight size={14} />
                                        </button>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="animate-in fade-in slide-in-from-bottom-4">
                        <div className="flex items-center gap-4 mb-8">
                            <button onClick={() => setView('list')} className="p-2 hover:bg-stone-200 rounded-full transition-colors">
                                <ArrowRight className="rotate-180" size={24} />
                            </button>
                            <h2 className="text-2xl font-serif font-bold">Register Community Individual</h2>
                        </div>

                        <Card className="p-8 bg-white border-none shadow-xl max-w-3xl mx-auto">
                            <form onSubmit={handleRegister} className="space-y-8">
                                <div className="space-y-4">
                                    <h3 className="text-sm font-black uppercase text-stone-400 tracking-widest flex items-center gap-2">
                                        <Users size={16} /> Profile Details
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <input
                                            type="text" placeholder="Full Name" required
                                            value={regForm.full_name} onChange={e => setRegForm({ ...regForm, full_name: e.target.value })}
                                            className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none focus:ring-2 focus:ring-[#F27D26]/10"
                                        />
                                        <input
                                            type="text" placeholder="Phone Number"
                                            value={regForm.phone_number} onChange={e => setRegForm({ ...regForm, phone_number: e.target.value })}
                                            className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none focus:ring-2 focus:ring-[#F27D26]/10"
                                        />
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Gender</label>
                                            <select
                                                value={regForm.gender} onChange={e => setRegForm({ ...regForm, gender: e.target.value })}
                                                className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                            >
                                                <option value="male">Male</option>
                                                <option value="female">Female</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Activity Level</label>
                                            <select
                                                value={regForm.activity_level} onChange={e => setRegForm({ ...regForm, activity_level: e.target.value })}
                                                className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                            >
                                                <option value="sedentary">Sedentary (Little movement)</option>
                                                <option value="moderate">Moderate (Active 1-3 days)</option>
                                                <option value="active">Active (Daily gym/work)</option>
                                                <option value="very_active">Very Active (Heavy athlete)</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Age</label>
                                            <input
                                                type="number" value={regForm.age} onChange={e => setRegForm({ ...regForm, age: parseInt(e.target.value) })}
                                                className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Weight (kg)</label>
                                            <input
                                                type="number" value={regForm.weight} onChange={e => setRegForm({ ...regForm, weight: parseFloat(e.target.value) })}
                                                className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Height (cm)</label>
                                            <input
                                                type="number" value={regForm.height} onChange={e => setRegForm({ ...regForm, height: parseFloat(e.target.value) })}
                                                className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">Nutrition Goal</label>
                                        <select
                                            value={regForm.goal} onChange={e => setRegForm({ ...regForm, goal: e.target.value })}
                                            className="w-full bg-white border border-stone-200 rounded-2xl px-6 py-4 text-sm outline-none shadow-sm focus:ring-2 focus:ring-[#F27D26]/10"
                                        >
                                            <option value="maintenance">Maintenance (General Health)</option>
                                            <option value="malnutrition">Gain Weight (Target Malnutrition)</option>
                                            <option value="obesity">Lose Weight (Target Obesity)</option>
                                            <option value="pregnancy">Maternal Health (Pregnancy)</option>
                                            <option value="child_growth">Child Growth (Infant/Child)</option>
                                        </select>
                                    </div>

                                    {/* Conditional Child Section - Only for children/adolescents under 18 */}
                                    {(regForm.age <= 18 && (regForm.goal === 'child_growth' || regForm.goal === 'malnutrition')) && (
                                        <div className="p-6 bg-amber-50/50 rounded-3xl border border-amber-100 space-y-4 animate-in fade-in slide-in-from-top-2">
                                            <h4 className="text-[10px] font-black uppercase text-amber-600 tracking-widest flex items-center gap-2">
                                                <Baby size={14} /> Pediatric Clinical Screening (Under 18)
                                            </h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">MUAC (cm)</label>
                                                    <input
                                                        type="number" step="0.1" value={regForm.muac_cm} onChange={e => setRegForm({ ...regForm, muac_cm: parseFloat(e.target.value) })}
                                                        placeholder="Arm Circumference"
                                                        className="w-full bg-white border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none shadow-sm"
                                                    />
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-2">WHZ Score</label>
                                                    <input
                                                        type="number" step="0.1" value={regForm.whz_score} onChange={e => setRegForm({ ...regForm, whz_score: parseFloat(e.target.value) })}
                                                        placeholder="Weight-for-Height Z"
                                                        className="w-full bg-white border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none shadow-sm"
                                                    />
                                                </div>
                                            </div>
                                            <p className="text-[9px] text-amber-500 italic px-2">MUAC/WHZ are specialized metrics for pediatric assessment only.</p>
                                        </div>
                                    )}
                                </div>


                                <div className="space-y-4">
                                    <h3 className="text-sm font-black uppercase text-stone-400 tracking-widest flex items-center gap-2">
                                        <MapPin size={16} /> Location
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <select
                                            value={regForm.region}
                                            onChange={e => setRegForm({ ...regForm, region: e.target.value, district: '' })}
                                            className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none"
                                        >
                                            <option value="">Select Region</option>
                                            {Object.keys(UGANDA_REGIONS).map(r => (
                                                <option key={r} value={r}>{r}</option>
                                            ))}
                                        </select>
                                        <select
                                            value={regForm.district}
                                            onChange={e => setRegForm({ ...regForm, district: e.target.value })}
                                            disabled={!regForm.region}
                                            className="w-full bg-stone-50 border border-stone-100 rounded-2xl px-6 py-4 text-sm outline-none shadow-sm disabled:opacity-50"
                                        >
                                            <option value="">Select District</option>
                                            {regForm.region && UGANDA_REGIONS[regForm.region].map(d => (
                                                <option key={d} value={d}>{d}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {message && (
                                    <div className={cn(
                                        "p-4 rounded-2xl text-sm font-bold flex items-center gap-3",
                                        message.type === 'success' ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600"
                                    )}>
                                        <CheckCircle2 size={20} />
                                        {message.text}
                                    </div>
                                )}

                                <div className="pt-6 flex gap-4">
                                    <Button
                                        type="submit"
                                        disabled={isSaving}
                                        className="flex-1 bg-[#5A5A40] text-white py-4 rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all"
                                    >
                                        {isSaving ? 'Registering...' : 'Save Member Record'}
                                    </Button>
                                    <Button
                                        type="button"
                                        onClick={() => setView('list')}
                                        variant="outline"
                                        className="px-8"
                                    >
                                        Cancel
                                    </Button>
                                </div>
                            </form>
                        </Card>

                        <div className="mt-8 bg-stone-800 rounded-3xl p-6 text-white flex items-center gap-6 max-w-3xl mx-auto">
                            <div className="w-12 h-12 bg-[#F27D26] rounded-full flex items-center justify-center shrink-0">
                                <Target size={24} />
                            </div>
                            <p className="text-sm text-stone-300 leading-relaxed italic">
                                "The data you enter here will be analyzed by the NutriAgent AI to provide specialized local nutrition pathways for this individual."
                            </p>
                        </div>
                    </div>
                )}
            </main>

            {/* Follow Up Modal */}
            {showModal && selectedIndividual && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-stone-900/60 backdrop-blur-sm animate-in fade-in">
                    <Card className="w-full max-w-2xl bg-white border-none shadow-2xl overflow-hidden rounded-[2rem]">
                        <div className="p-8 bg-[#5A5A40] text-white flex justify-between items-start">
                            <div className="space-y-1">
                                <h2 className="text-2xl font-serif font-bold">{selectedIndividual.profile?.full_name}</h2>
                                <p className="text-white/60 text-[10px] uppercase font-black tracking-widest font-sans">Clinical Follow-up Profile</p>
                            </div>
                            <button onClick={() => setShowModal(false)} className="bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors text-white">
                                <ChevronRight className="rotate-90" size={24} />
                            </button>
                        </div>

                        <div className="p-8 space-y-8 overflow-y-auto max-h-[70vh]">
                            {selectedIndividual.screening ? (
                                <>
                                    <div className="flex items-center gap-6 p-6 rounded-3xl bg-stone-50 border border-stone-100">
                                        <div className={cn(
                                            "w-16 h-16 rounded-2xl flex items-center justify-center text-white text-xl font-black",
                                            selectedIndividual.screening.classification === 'SAM' ? "bg-red-500 shadow-lg shadow-red-200" :
                                            selectedIndividual.screening.classification === 'MAM' ? "bg-orange-400 shadow-lg shadow-orange-200" :
                                            "bg-emerald-500 shadow-lg shadow-emerald-200"
                                        )}>
                                            {selectedIndividual.screening.classification}
                                        </div>
                                        <div>
                                            <p className="text-[10px] uppercase font-black text-stone-400 tracking-widest mb-2">Primary Assessments</p>
                                            <div className="space-y-2">
                                                {Array.isArray(selectedIndividual.screening.clinical_notes) ? (
                                                    selectedIndividual.screening.clinical_notes.map((note: string, i: number) => (
                                                        <div key={i} className="flex items-start gap-2 text-xs font-bold text-stone-700 leading-tight">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                                                            <span>{note}</span>
                                                        </div>
                                                    ))
                                                ) : (
                                                    <p className="text-sm font-bold text-stone-700">{selectedIndividual.screening.clinical_notes}</p>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <h3 className="text-sm font-black uppercase text-stone-400 tracking-widest flex items-center gap-2">
                                            <Target size={16} /> Treatment Pathway
                                        </h3>
                                        <div className="grid grid-cols-1 gap-3">
                                            {selectedIndividual.screening.recommendations.map((rec: string, idx: number) => (
                                                <div key={idx} className="flex gap-4 items-start p-4 rounded-2xl bg-white border border-stone-100 shadow-sm">
                                                    <div className="w-6 h-6 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 text-xs font-black">
                                                        {idx + 1}
                                                    </div>
                                                    <p className="text-sm text-stone-600 leading-relaxed">{rec}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {selectedIndividual.screening && (
                                        <div className={cn(
                                            "p-6 rounded-3xl border",
                                            selectedIndividual.screening.risk_level === 'High' ? "bg-red-50 border-red-100" : 
                                            selectedIndividual.screening.risk_level === 'Medium' ? "bg-amber-50 border-amber-100" :
                                            "bg-emerald-50 border-emerald-100"
                                        )}>
                                            <p className={cn(
                                                "text-xs font-bold flex items-center gap-2 uppercase tracking-wide",
                                                selectedIndividual.screening.risk_level === 'High' ? "text-red-600" : 
                                                selectedIndividual.screening.risk_level === 'Medium' ? "text-amber-600" :
                                                "text-emerald-600"
                                            )}>
                                                <Activity size={16} /> 
                                                {selectedIndividual.screening.title || "Health Assessment"}
                                            </p>
                                            <p className="text-stone-600 text-sm mt-3 leading-relaxed">
                                                The NutriAgent Brain has classified this individual as: <b>{selectedIndividual.screening.badge}</b>. 
                                                Suggested follow-up protocol: <b>Every {selectedIndividual.screening.monitoring_freq}</b>.
                                            </p>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="text-center py-12">
                                    <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4 text-stone-300">
                                        <Heart size={32} />
                                    </div>
                                    <p className="text-stone-400 font-bold italic">No specialized screening data available for this record type.</p>
                                </div>
                            )}

                            <Button onClick={() => setShowModal(false)} className="w-full py-4 rounded-2xl bg-[#5A5A40] text-white font-bold shadow-xl">
                                Close Assessment
                            </Button>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
};
