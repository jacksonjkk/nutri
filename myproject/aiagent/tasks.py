from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import NutriUser, DailyLog, AIInsight, UserProfile
from .services.analytics_service import AnalyticsService
from .services.ai_service import AIService
from .services.ml_service import MLService
from .services.email_service import EmailService

@shared_task
def process_ai_insights_task(user_id):
    """
    Background task implementing Hybrid AI:
    1. Analytics (Math)
    2. ML Service (Logic Brain - Local)
    3. AI Service (Communicator - Groq)
    """
    try:
        user = NutriUser.objects.get(id=user_id)
        profile = user.profile
        logs = DailyLog.objects.filter(user=user).order_by('-date')

        # 1. Run Core Analytics
        analytics = AnalyticsService.analyze_behavior(logs)
        
        # 2. Run the "ML Brain" (Local Logic)
        ml_service = MLService()
        ml_nutrition = ml_service.predict_nutrition_score({"age": profile.age, "goal": profile.goal})
        
        # 3. Call "AI Communicator" (Groq) to explain results
        ai_service = AIService()
        profile_data = {
            "goal": profile.goal,
            "conditions": profile.medical_conditions,
            "age": profile.age
        }
        
        # Prepare the hybrid data package
        ml_results = {
            "nutrition_prediction": ml_nutrition,
            "behavior_metircs": analytics
        }
        
        insight_json = ai_service.generate_hybrid_insight(profile_data, ml_results)

        # 4. Save to DB for Dashboard (CRITICAL)
        AIInsight.objects.create(
            user=user,
            insight_type='general',
            summary=insight_json.get('summary', 'AI Analysis Complete'),
            behavioral_insight=insight_json.get('behavioral_insight', ''),
            risk_level=insight_json.get('risk_level', 'Low'),
            recommendations=insight_json.get('recommendations', []),
            motivation=insight_json.get('motivation', '')
        )

        # 5. Email Notification (PROACTIVE AGENT)
        EmailService.send_ai_notification(
            user=user,
            title="Insights for Your Recent Meals",
            summary=insight_json.get('summary', ''),
            insight=insight_json.get('behavioral_insight', ''),
            recommendations=insight_json.get('recommendations', []),
            motivation=insight_json.get('motivation', ''),
            severity=insight_json.get('risk_level', 'Low')
        )
        
        return f"Successfully generated Hybrid AI insight and sent email to {user.email}"
    except Exception as e:
        return f"Hybrid Task failed: {str(e)}"
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def send_morning_briefing_task():
    """
    Morning Briefing Task (Runs Daily at 7AM):
    1. Loop through all users
    2. Analyze last 3 days
    3. Generate "Mission for the Day"
    4. Save to DB + Send Email
    """
    users = NutriUser.objects.filter(onboarding_completed=True)
    ai_service = AIService()
    
    for user in users:
        try:
            profile = user.profile
            three_days_ago = timezone.now().date() - timedelta(days=3)
            logs = DailyLog.objects.filter(user=user, date__gte=three_days_ago)
            
            # Simple log data for AI
            logs_data = list(logs.values('date', 'calories', 'protein', 'water_intake', 'weight'))
            
            profile_data = {
                "goal": profile.goal,
                "conditions": profile.medical_conditions
            }
            
            briefing = ai_service.generate_morning_briefing(profile_data, logs_data)
            
            if briefing:
                # 1. Save to DB
                AIInsight.objects.create(
                    user=user,
                    insight_type='briefing',
                    summary=briefing['summary'],
                    behavioral_insight=briefing['message'],
                    risk_level='Low',
                    recommendations=[briefing['recommendation']],
                    motivation=briefing['motivation']
                )
                
                # 2. Send Beautiful Email
                EmailService.send_ai_notification(
                    user=user,
                    title=f"☀️ Morning Mission: {briefing['summary']}",
                    summary=f"Mission of the day for your goal: {profile.goal}",
                    insight=briefing['message'],
                    recommendations=[briefing['recommendation']],
                    motivation=briefing['motivation'],
                    severity='Low'
                )
        except Exception as e:
            print(f"Briefing failed for {user.email}: {e}")
            
    return "Mass briefing distribution complete."
