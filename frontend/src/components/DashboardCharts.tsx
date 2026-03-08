
import React from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import { format, parseISO } from 'date-fns';

interface ChartProps {
  data: { date: string; calories: number; protein: number; carbs: number; fats: number }[];
}

export const DashboardCharts = ({ data }: ChartProps) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-stone-50 rounded-2xl border-2 border-dashed border-stone-100 text-stone-400 text-sm">
        Log some meals to see your nutritional trends
      </div>
    );
  }

  // Ensure data is sorted by date
  const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  
  // Format dates for display
  const displayData = sortedData.map(item => ({
    ...item,
    displayDate: format(parseISO(item.date), 'MMM d')
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 shadow-xl rounded-2xl border border-stone-100">
          <p className="text-[10px] font-bold text-stone-400 uppercase tracking-tighter mb-2">{label}</p>
          <div className="space-y-1">
            <p className="text-sm font-bold text-stone-800">{payload[0].value} <span className="text-[10px] font-normal opacity-60">kcal</span></p>
            <div className="flex gap-2">
              <span className="text-[8px] font-bold text-emerald-500">P: {payload[0].payload.protein}g</span>
              <span className="text-[8px] font-bold text-amber-500">C: {payload[0].payload.carbs}g</span>
              <span className="text-[8px] font-bold text-blue-500">F: {payload[0].payload.fats}g</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <div className="h-[240px] w-full min-h-[240px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={240}>
          <AreaChart data={displayData}>
            <defs>
              <linearGradient id="colorCal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F27D26" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#F27D26" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis 
              dataKey="displayDate" 
              axisLine={false} 
              tickLine={false} 
              tick={{fill: '#a8a29e', fontSize: 10}}
              dy={10}
            />
            <YAxis 
              hide 
              domain={['dataMin - 500', 'dataMax + 200']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="calories" 
              stroke="#F27D26" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorCal)" 
              animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex items-center justify-between text-[10px] font-bold text-stone-400 uppercase tracking-widest px-2">
        <span>7 Day Calorie Trend</span>
        <div className="flex gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#F27D26]" />
            <span>Actual Intake</span>
          </div>
        </div>
      </div>
    </div>
  );
};
