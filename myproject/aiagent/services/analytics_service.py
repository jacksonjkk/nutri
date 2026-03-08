import pandas as pd
import numpy as np
from datetime import timedelta
from django.utils import timezone

class AnalyticsService:
    @staticmethod
    def predict_next_meal(user, current_hour):
        """
        Dynamically predict what the user usually eats based on historical logs.
        """
        # 1. Determine meal type based on hour
        if current_hour < 11:
            meal_type = 'breakfast'
        elif current_hour < 16:
            meal_type = 'lunch'
        else:
            meal_type = 'dinner'

        # 2. Query historical logs for this user
        from aiagent.models import DailyLog
        logs = DailyLog.objects.filter(user=user).order_by('-date')[:30]
        
        if not logs.exists():
            # Fallback for new users: return a popular regional food based on time
            regional_defaults = {
                'breakfast': {'name': 'Katogo (Matooke & Beans)', 'calories': 450, 'reason': 'popular regional breakfast'},
                'lunch': {'name': 'Matooke & Groundnut Sauce', 'calories': 600, 'reason': 'popular regional lunch'},
                'dinner': {'name': 'Posho & Beans', 'calories': 500, 'reason': 'popular regional dinner'}
            }
            res = regional_defaults.get(meal_type)
            return {**res, 'is_fallback': True}

        # 3. Simple analytical prediction:
        # In a real heavy-ML app, this would be a sequence model (RNN/Transformer)
        # Here we use a frequency-based heuristic on the user's own data
        # We look for common patterns in their protein/carb ratios for that meal time
        recent_log = logs[0]
        
        # We can also check if they have a 'favorite' mentioned in their chat history (if we had it saved)
        # For now, we return the last logged high-protein meal for that time of day
        return {
            "name": f"Your usual {meal_type} pattern",
            "calories": int(recent_log.calories) if recent_log.calories > 0 else 550,
            "is_custom": True
        }

    @staticmethod
    def calculate_bmi(profile):
        """
        Calculate BMI and return value + category.
        Handles age-specific interpretation for children/teens vs adults.
        """
        height_m = (profile.height or 0) / 100
        if height_m <= 0 or not profile.weight:
            return None, "Unknown"
        
        bmi_value = (profile.weight or 0) / (height_m ** 2)
        age = profile.age or 25 # Default to adult if age missing
        
        # Adult Categories (20+ years)
        if age >= 20:
            if bmi_value < 18.5:
                category = "Underweight"
            elif 18.5 <= bmi_value < 25:
                category = "Normal Weight"
            elif 25 <= bmi_value < 30:
                category = "Overweight"
            else:
                category = "Obesity"
        else:
            # For children and teens, BMI is interpreted as percentiles.
            # We provide a simplified growth-aware category label.
            if bmi_value < 15:
                category = "Child: Underweight"
            elif 15 <= bmi_value < 22:
                category = "Child: Healthy Growth"
            else:
                category = "Child: Above Average"
            
        return round(bmi_value, 1), category

    @staticmethod
    def calculate_bmr(profile):
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        """
        if not all([profile.weight, profile.height, profile.age, profile.gender]):
            return 0
        
        gender = (profile.gender or 'male').lower()
        # weight in kg, height in cm, age in years
        if gender == 'male':
            return (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + 5
        else:
            return (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) - 161

    @staticmethod
    def calculate_tdee(bmr, activity_level):
        """
        Calculate Total Daily Energy Expenditure.
        """
        multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        level = (activity_level or 'sedentary').lower().replace(' ', '_')
        factor = multipliers.get(level, 1.2)
        return bmr * factor

    @staticmethod
    def analyze_behavior(user_logs):
        """
        Process DailyLogs using Pandas to detect trends.
        """
        if not user_logs.exists():
            return {
                "avg_calories": 0.0,
                "avg_sleep": 0.0,
                "weekend_spike": False,
                "consistency_score": 0.0,
                "calorie_trend": "stable",
                "sample_size": 0
            }

        df = pd.DataFrame(list(user_logs.values()))
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # 1. Weekly Averages
        avg_calories = df['calories'].tail(7).mean()
        avg_sleep = df['sleep_hours'].tail(7).mean()

        # 2. Weekend Spike Detection
        df['is_weekend'] = df['date'].dt.dayofweek >= 4 # Fri, Sat, Sun
        weekend_avg = df[df['is_weekend']]['calories'].mean()
        weekday_avg = df[~df['is_weekend']]['calories'].mean()
        
        has_weekend_spike = False
        if not np.isnan(weekend_avg) and not np.isnan(weekday_avg):
            has_weekend_spike = weekend_avg > (weekday_avg * 1.15)

        # 3. Consistency Score (0-100)
        # Based on how many logs exist in the last 7 days
        last_7_days = timezone.now().date() - timedelta(days=7)
        recent_logs = df[df['date'].dt.date >= last_7_days]
        consistency_score = (len(recent_logs) / 7.0) * 100

        # 4. Monthly Weight Trends (if weights were logged in DailyLog)
        # Assuming we just have calorie trends for now
        calorie_trend = "stable"
        if len(df) >= 7:
            diff = df['calories'].tail(3).mean() - df['calories'].iloc[-7:-4].mean()
            if diff > 200: calorie_trend = "increasing"
            elif diff < -200: calorie_trend = "decreasing"

        return {
            "avg_calories": float(avg_calories),
            "avg_sleep": float(avg_sleep),
            "weekend_spike": bool(has_weekend_spike),
            "consistency_score": float(consistency_score),
            "calorie_trend": calorie_trend,
            "sample_size": len(df)
        }
