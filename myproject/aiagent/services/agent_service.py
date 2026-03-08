from types import SimpleNamespace
from .ml_service import MLService
from .ai_service import AIService
from .analytics_service import AnalyticsService
from ..models import HealthAssessment

class HealthAgentService:
    """
    The Orchestration Layer for the NutriAgent AI.
    Features "Agentic Memory" to track user progress over time.
    """
    def __init__(self):
        self.ml = MLService()
        self.ai = AIService()
        self.analytics = AnalyticsService()

    def assess_individual(self, user, activity_logs=None):
        """
        Main entry point for "Thinking" about an individual.
        Now includes 'Long-term Memory' by checking previous assessments.
        """
        p = user.profile
        profile_dict = {
            'age': p.age,
            'gender': p.gender,
            'weight': p.weight,
            'height': p.height,
            'muac_cm': p.muac_cm,
            'whz_score': p.whz_score,
            'goal': p.goal
        }
        
        # 1. Memory Layer (Retrieve History)
        history = HealthAssessment.objects.filter(user=user).order_by('-created_at')[:3]
        last_assessment = history[0] if history.exists() else None
        
        # 2. Perception Layer (Calculate basics)
        p_obj = SimpleNamespace(**profile_dict)
        bmi_val, bmi_cat = self.analytics.calculate_bmi(p_obj)
        perception = {
            'bmi': bmi_val,
            'bmi_category': bmi_cat,
            'bmr': self.analytics.calculate_bmr(p_obj),
            'history': list(history)
        }

        # 3. Decision Layer (Which "Brain" to use?)
        if (p.age or 30) <= 18 and (p.goal == 'child_growth' or p.goal == 'malnutrition'):
            assessment = self._pediatric_agent(profile_dict, last_assessment)
        else:
            assessment = self._adult_agent(profile_dict, perception, last_assessment)

        # 4. Persistence Layer (Update Memory)
        # We only save if there's significant data or its first assessment
        self._save_assessment(user, assessment, profile_dict)
        
        return assessment

    def _save_assessment(self, user, assessment, data):
        """Persists the agent's thought process for future follow-ups"""
        HealthAssessment.objects.create(
            user=user,
            assessment_type=assessment['type'],
            risk_level=assessment['risk_level'],
            classification=assessment['classification'],
            clinical_notes=assessment['clinical_notes'],
            recommendations=assessment['recommendations'],
            weight=data.get('weight'),
            muac_cm=data.get('muac_cm'),
            whz_score=data.get('whz_score'),
            monitoring_freq=assessment['monitoring_freq']
        )

    def _pediatric_agent(self, data, last_assessment=None):
        """Logic for child growth with trend awareness"""
        child_metrics = {
            'age_months': (data.get('age') or 2) * 12,
            'weight_kg': data.get('weight') or 10,
            'height_cm': data.get('height') or 80,
            'muac_cm': data.get('muac_cm') or 13.5,
            'whz_score': data.get('whz_score') or 0
        }
        
        result = self.ml.classify_malnutrition(child_metrics)
        notes = result['clinical_notes']
        
        # Trend Reasoning
        if last_assessment and last_assessment.muac_cm:
            diff = child_metrics['muac_cm'] - last_assessment.muac_cm
            if diff > 0.2:
                notes.append(f"📈 Positive Trend: MUAC improved by {diff:.1f}cm since last visit.")
            elif diff < -0.2:
                notes.append(f"⚠️ Warning Trend: MUAC declined by {abs(diff):.1f}cm. Review feeding frequency.")

        return {
            "type": "pediatric_clinical",
            "title": "Pediatric Clinical Assessment",
            "badge": result['classification'],
            "classification": result['classification'],
            "risk_level": "High" if result['classification'] in ['SAM', 'MAM'] else "Low",
            "clinical_notes": notes,
            "recommendations": result['recommendations'],
            "monitoring_freq": "7 days" if result['classification'] != 'Normal' else "30 days"
        }

    def _adult_agent(self, data, perception, last_assessment=None):
        """Logic for adult health with trend awareness"""
        goal = data.get('goal')
        bmi = perception.get('bmi', 0)
        
        notes = []
        recommendations = []
        
        # Trend Reasoning (Weight)
        if last_assessment and last_assessment.weight:
            w_diff = (data.get('weight') or 0) - last_assessment.weight
            if abs(w_diff) > 0.5:
                trend = "gained" if w_diff > 0 else "lost"
                notes.append(f"Trend: You have {trend} {abs(w_diff):.1f}kg since your last assessment.")

        if bmi > 25:
            label = "Overweight Risk"
            notes.append(f"BMI baseline: {bmi:.1f} (Elevated)")
            recommendations.append("Prioritize high-fiber local vegetables (Nakati, Cabbage)")
        elif bmi < 18.5:
            label = "Underweight Risk"
            notes.append(f"BMI baseline: {bmi:.1f} (Low)")
            recommendations.append("Focus on calorie-dense local staples (G-nuts, Avocado)")
        else:
            label = "Stable"
            notes.append(f"BMI baseline: {bmi:.1f} (Healthy)")
            recommendations.append("Maintain current activity with balanced macronutrients")

        if goal == 'malnutrition':
            notes.append("Adult weight-gain protocol activated")
            recommendations.append("Increase daily intake by 500 kcal using energy-dense local foods")

        return {
            "type": "adult_wellbeing",
            "title": "Adult Wellness Profile",
            "badge": label,
            "classification": label,
            "risk_level": "Medium" if bmi > 30 or bmi < 17 else "Low",
            "clinical_notes": notes,
            "recommendations": recommendations,
            "monitoring_freq": "14 days" if label != 'Stable' else "90 days"
        }
