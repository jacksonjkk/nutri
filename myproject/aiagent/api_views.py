from rest_framework import status, views
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import DailyLog, AIInsight, UserProfile, NutriUser, FoodItem
from .serializers import (
    DailyLogSerializer, ProfileSerializer, AIInsightSerializer, 
    UserSerializer, FoodItemSerializer, NutriTokenObtainPairSerializer
)

class NutriTokenObtainPairView(TokenObtainPairView):
    serializer_class = NutriTokenObtainPairSerializer
from .services.analytics_service import AnalyticsService
from .services.ai_service import AIService
from .services.ml_service import MLService
from .services.email_service import EmailService
from .tasks import process_ai_insights_task
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny

class APIRoot(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "message": "NutriAgent Headless API is LIVE 🚀",
            "status": "Healthy",
            "version": "1.0.0",
            "endpoints": [
                "/api/token/ (Login)",
                "/api/signup/ (Register)",
                "/api/dashboard/ (Protected)",
                "/api/logs/ (Protected)",
                "/api/foods/ (General)"
            ]
        })

class FoodListAPIView(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        foods = FoodItem.objects.all()
        # Optional: Filter by region if provided
        region = request.query_params.get('region')
        if region:
            foods = foods.filter(region__icontains=region)
            
        serializer = FoodItemSerializer(foods, many=True)
        return Response(serializer.data)

class DashboardAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Profile Check (Onboarding Check)
        if not user.onboarding_completed:
            return Response({
                "message": "Onboarding required",
                "onboarding_completed": False,
                "role": user.role,
                "username": user.username
            }, status=status.HTTP_200_OK)

        # 2. Get Data
        profile = user.profile
        logs = DailyLog.objects.filter(user=user).order_by('-date')
        latest_insight = AIInsight.objects.filter(user=user).order_by('-created_at').first()
        
        # 3. Process Analytics (Fast mathematical stuff)
        bmr = AnalyticsService.calculate_bmr(profile)
        tdee = AnalyticsService.calculate_tdee(bmr, profile.activity_level or 'sedentary')
        bmi_value, bmi_category = AnalyticsService.calculate_bmi(profile)
        behavior = AnalyticsService.analyze_behavior(logs)

        # 4. Construct Response
        data = {
            "username": user.username,
            "email": user.email,
            "profile_summary": ProfileSerializer(profile).data,
            "goal_progress": {
                "bmr": bmr,
                "tdee": tdee,
                "bmi": bmi_value,
                "bmi_category": bmi_category,
                "target_goal": profile.goal
            },
            "nutrition_metrics": behavior,
            "trend_data": list(logs[:7].values('date', 'calories', 'protein', 'carbs', 'fats')),
            "ai_insight": AIInsightSerializer(latest_insight).data if latest_insight else None,
            "predicted_meal": AnalyticsService.predict_next_meal(user, timezone.now().hour),
            "role": user.role
        }
        
        return Response(data)

class DailyLogAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        date_str = request.data.get('date')
        if not date_str:
            return Response({"error": "Date is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Get or create the log for this user and date
        log, created = DailyLog.objects.get_or_create(user=request.user, date=date_str)

        # 2. Accumulate nutritional values (Adding on)
        log.calories += int(request.data.get('calories', 0))
        log.protein += float(request.data.get('protein', 0.0))
        log.carbs += float(request.data.get('carbs', 0.0))
        log.fats += float(request.data.get('fats', 0.0))
        log.exercise_minutes += int(request.data.get('exercise_minutes', 0))

        # 3. Update lifestyle values (Take the latest slider position)
        if 'water_intake' in request.data:
            log.water_intake = float(request.data.get('water_intake', 0.0))
        
        if 'sleep_hours' in request.data:
            log.sleep_hours = float(request.data.get('sleep_hours', 0.0))

        log.save()
        
        # SMART FOOD SWAP CHECK (AGENT REASONING)
        swap_data = None
        food_name = request.data.get('food_name') or request.data.get('description')
        
        if food_name:
            ai_service = AIService()
            profile_data = {
                "goal": request.user.profile.goal,
                "conditions": request.user.profile.medical_conditions
            }
            
            # 1. AI Reasoning for the 'Why'
            ai_risk = ai_service.check_food_risk_ai(food_name, profile_data)
            
            if ai_risk and ai_risk.get('is_risky'):
                # 2. Local ML Model for the 'What' (Similarity)
                from .services.ml_service import get_ml_service
                ml_service = get_ml_service()
                sim_results = ml_service.recommend_similar_foods(food_name, n=1)
                
                swap_data = {
                    "is_risky": True,
                    "reason": ai_risk.get('reason'),
                    "severity": ai_risk.get('severity'),
                    "swap_suggestion": sim_results['similar_foods'][0] if sim_results['similar_foods'] else None
                }
                
                # 3. PROACTIVE EMAIL ALERT
                EmailService.send_ai_notification(
                    user=request.user,
                    title=f"⚠️ Food Safety Alert: {food_name}",
                    summary=f"We noticed you logged {food_name}, which might be risky for your profile.",
                    insight=ai_risk.get('reason'),
                    recommendations=[f"Try swapping with: {swap_data['swap_suggestion']['food_name']}"] if swap_data['swap_suggestion'] else [],
                    severity=ai_risk.get('severity', 'Medium')
                )

        # TRIGGER CELERY TASK (Async AI Processing)
        try:
            process_ai_insights_task.delay(request.user.id)
        except Exception as e:
            # Safe Fallback: If Redis is missing or Celery fails, don't crash the meal logging
            print(f"⚠️ Background Insight Task skipped: {e}")
        
        serializer = DailyLogSerializer(log)
        resp_data = serializer.data
        if swap_data:
            resp_data['swap_suggestion'] = swap_data

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(resp_data, status=status_code)

    def get(self, request):
        logs = DailyLog.objects.filter(user=request.user).order_by('-date')[:30]
        serializer = DailyLogSerializer(logs, many=True)
        return Response(serializer.data)

class SignupAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Create a mutable copy of data
        data = request.data.copy()
        
        # Normalize email
        email = data.get('email', '').lower().strip()
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if NutriUser.objects.filter(email=email).exists():
            return Response({
                "error": "An account with this email already exists. Please log in.",
                "code": "user_exists"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ensure username is unique
        base_username = data.get('username') or email.split('@')[0]
        username = base_username
        counter = 1
        while NutriUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        data['username'] = username
            
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = data.get('role', 'user')
            if user.role == 'vht':
                user.onboarding_completed = True
            user.save()
            
            profile, _ = UserProfile.objects.get_or_create(user=user)
            ps = ProfileSerializer(profile, data=data, partial=True)
            if ps.is_valid():
                ps.save()
                
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            
        return Response({
            "error": "Registration failed. Please check the details provided.",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VHTDashboardAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'vht':
            return Response({"error": "VHT access only"}, status=status.HTTP_403_FORBIDDEN)
        
        users = NutriUser.objects.filter(registered_by=request.user).order_by('-date_joined')
        from .services.agent_service import HealthAgentService
        agent_service = HealthAgentService()
        data = []
        
        for u in users:
            p = getattr(u, 'profile', None)
            assessment = None
            
            if p:
                assessment = agent_service.assess_individual(u)

            data.append({
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "onboarding_completed": u.onboarding_completed,
                "profile": ProfileSerializer(p).data if p else None,
                "screening": assessment,
                "date_joined": u.date_joined
            })
        
        return Response({
            "vht_name": request.user.username,
            "registered_count": len(data),
            "individuals": data
        })

class VHTRegisterIndividualAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'vht':
            return Response({"error": "VHT access only"}, status=status.HTTP_403_FORBIDDEN)
        
        full_name = request.data.get('full_name', 'Unnamed Individual')
        email = request.data.get('email')
        
        # If no email provided (for people without smart phones), generate one
        if not email:
            import time
            import uuid
            # Create a unique internal identifier
            name_slug = full_name.lower().replace(' ', '_')
            unique_id = str(uuid.uuid4())[:8]
            email = f"{name_slug}_{unique_id}@nutri.internal"
            
        if NutriUser.objects.filter(email=email).exists():
            return Response({"error": "User with this name/email already exists in system"}, status=status.HTTP_400_BAD_REQUEST)

        # Create basic account
        user = NutriUser.objects.create(
            email=email,
            username=email.split('@')[0],
            role='user',
            registered_by=request.user
        )
        # Use a random strong password for the internal account
        import secrets
        user.set_password(request.data.get('password', secrets.token_urlsafe(16)))
        user.save()

        # Fill profile data
        profile, _ = UserProfile.objects.get_or_create(user=user)
        ps = ProfileSerializer(profile, data=request.data, partial=True)
        if ps.is_valid():
            ps.save()
            user.onboarding_completed = True
            user.save()
            return Response({"message": "Individual registered successfully!", "id": user.id}, status=status.HTTP_201_CREATED)
        
        return Response(ps.errors, status=status.HTTP_400_BAD_REQUEST)

class OnboardingAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.onboarding_completed = True
            user.save()
            return Response(ProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MealPlanAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        food_items = list(FoodItem.objects.all())
        
        if not food_items:
            return Response({"error": "No food data available to generate meal plan"}, status=status.HTTP_404_NOT_FOUND)
            
        ai_service = AIService()
        profile_data = {
            "conditions": profile.medical_conditions,
            "goal": profile.goal
        }
        
        meal_plan = ai_service.generate_meal_plan(profile_data, food_items)
        if meal_plan:
            return Response(meal_plan)
        return Response({"error": "Failed to generate meal plan"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        try:
            profile = getattr(user, 'profile', None)
            
            profile_data = {
                "name": user.username,
                "age": profile.age if profile else 25,
                "gender": profile.gender if profile else 'male',
                "goal": profile.goal if profile else 'General Health',
                "conditions": profile.medical_conditions if profile else []
            }
            
            ai_service = AIService()
            reply = ai_service.chat_response(message, profile_data)
            
            return Response({"reply": reply})
        except Exception as e:
            import traceback
            print(f"Chat API Exception: {e}")
            print(traceback.format_exc())
            return Response({"error": "Failed to generate chat response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VisionAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_b64 = request.data.get('image')
        if not image_b64:
            return Response({"error": "Image data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Strip header if present (e.g., data:image/jpeg;base64,)
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]

        try:
            ai_service = AIService()
            result = ai_service.vision_analyze_food(image_b64)
            
            return Response(result)
        except Exception as e:
            import traceback
            print(f"Vision API Exception: {e}")
            print(traceback.format_exc())
            return Response({"error": "Failed to analyze image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
