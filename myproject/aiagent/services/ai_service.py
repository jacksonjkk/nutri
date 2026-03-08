import os
import json
from groq import Groq
from django.conf import settings
from dotenv import load_dotenv

# load_dotenv() - Removed from here, moved to AIService.__init__ for precision

class AIService:
    def __init__(self):
        # Use absolute path for .env to ensure it loads in background tasks
        env_path = os.path.join(settings.BASE_DIR, '.env')
        load_dotenv(env_path)
        
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            self.model_name = 'llama-3.3-70b-versatile'
            self.vision_model = 'meta-llama/llama-4-maverick-17b-128e-instruct'
        else:
            self.client = None
            print(f"⚠️ GROQ_API_KEY not found at {env_path}")

    def generate_behavioral_insight(self, profile_data, analytics_data):
        """
        Calls Groq to interpret processed data and return structured insights.
        """
        if not self.client:
            return self._offline_fallback()

        prompt = f"""
        Role: Senior Clinical Nutritionist & Behavioral Coach.
        System Context: interpret mathematical analytics for a health platform in Uganda.
        
        Input Data (JSON):
        {{
            "profile": {{
                "goal": "{profile_data.get('goal')}",
                "conditions": {json.dumps(profile_data.get('conditions', []))}
            }},
            "analytics": {{
                "avg_calories": {analytics_data.get('avg_calories', 0)},
                "weekend_spike": {analytics_data.get('weekend_spike', False)},
                "sleep_avg": {analytics_data.get('avg_sleep', 0)},
                "consistency": {analytics_data.get('consistency_score', 0)},
                "trend": "{analytics_data.get('calorie_trend', 'stable')}"
            }}
        }}

        Task: Provide a structured analysis.
        Output MUST be valid JSON with the following keys:
        - summary: 1-sentence overview.
        - behavioral_insight: Deep dive into the "Why" behind the data.
        - risk_level: "Low", "Medium", or "High".
        - recommendations: List of 3 actionable items.
        - motivation: A brief encouraging message.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"AI Service Error: {e}")
            return self._offline_fallback()

    def generate_meal_plan(self, profile_data, food_items_list):
        """
        Generates a structured meal plan that matches the frontend MealPlan interface.
        """
        if not self.client:
            return None

        # Provide IDs so the frontend can map them back to its metadata
        food_info = ", ".join([f"{f.name} (id: {f.id or f.name.lower()})" for f in food_items_list])
        
        prompt = f"""
        Role: Nutrition Planner for Uganda.
        Goal: {profile_data.get('goal', 'maintenance')}.
        Conditions: {json.dumps(profile_data.get('conditions', []))}.
        Available Foods: {food_info}.

        Task: Create a 1-day balanced Ugandan meal plan.
        Output MUST be a valid JSON object matching this EXACT structure:
        {{
            "meals": [
                {{
                    "type": "breakfast",
                    "items": [{{ "foodId": "id_from_list", "portion": "e.g. 2 fingers" }}],
                    "notes": "Healthy tip"
                }},
                {{
                    "type": "lunch",
                    "items": [{{ "foodId": "id_from_list", "portion": "e.g. 1 medium plate" }}],
                    "notes": "Cultural tip"
                }},
                {{
                    "type": "dinner",
                    "items": [{{ "foodId": "id_from_list", "portion": "e.g. 2 pieces" }}],
                    "notes": "Light meal tip"
                }}
            ],
            "totalNutrients": {{
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            }}
        }}

        CRITICAL: 
        1. Use ONLY the IDs provided in the Available Foods list for "foodId".
        2. Use REALISTIC Ugandan portion units: 'fingers' (for matooke/bananas), 'pieces' (for meat/tubers), 'plates', 'bowls', or 'tablespoons'. DO NOT use 'cups' for solid local foods.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise meal planning expert. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Meal Plan Error: {e}")
            return None

    def generate_hybrid_insight(self, profile_data, ml_results):
        """
        Takes raw results from the local ML Brain and uses Groq to find the best way to explain them.
        """
        if not self.client:
            return self._offline_fallback()

        import traceback
        try:
            # Use separate variable for clean prompt building
            ml_data_json = json.dumps(ml_results, indent=2)
            profile_data_json = json.dumps(profile_data, indent=2)
            
            prompt = f"""
            Role: Ugandan Health Communicator.
            Context: Our local ML Model (The Brain) has analyzed the user data and produced these results:
            {ml_data_json}

            User Profile: {profile_data_json}

            Task: Translate these technical ML results into a friendly, culturally relevant message.
            - CRITICAL: Tailor advice to their goal: "{profile_data.get('goal', 'General Health')}".
            - If the goal is "Gain Weight", focus on healthy calorie density (e.g., groundnuts, avocados, oils).
            - If the goal is "Lose Weight", focus on volume and fiber.
            - The summary should be empowering.
            - The behavioral_insight should explain WHAT the results mean for their specific goal.
            - Include 3 specific Ugandan food recommendations.
            
            Output MUST be valid JSON with keys: summary, behavioral_insight, risk_level, recommendations, motivation.
            """

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a friendly health coach. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"❌ Hybrid AI Error: {str(e)}")
            print(traceback.format_exc())
            return self._offline_fallback()

    def chat_response(self, user_message, profile_data):
        """
        Provides direct conversation with the user.
        """
        if not self.client:
            return "I am currently offline. Please check back later."

        prompt = f"""
        Role: Nutri Agent (Ugandan Nutrition Assistant).
        User Goal: {profile_data.get('goal', 'General Health')}.
        User Profile: {json.dumps(profile_data)}.
        
        Task: Provide conversational health advice.
        Special Instruction: 
        - If the user mentions a budget (e.g., "I have 5000 UGX"), look at their health goals and suggest a specific shopping list of local foods that fits that price.
        - Be an *Agent*, not just a search engine. Suggest specific quantities if possible.
        - Use Ugandan context always.
        - If weight progress is mentioned, suggest adjustments.

        Profile: {json.dumps(profile_data)}
        User Query: {user_message}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful Ugandan nutrition assistant. Speak English, but you can use some common Luganda or Swahili words if appropriate."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Chat Error: {e}")
            return "I am sorry, I am having trouble thinking right now."

    def vision_analyze_food(self, image_b64):
        """
        Analyzes an image (base64) to identify foods and estimate nutrition.
        """
        if not self.client:
            return {"error": "AI client not initialized"}

        prompt = """
        Analyze this food image in the context of Ugandan cuisine.
        1. Identify the primary food items (e.g., Matooke, Gnuts, Beef, Posho, Cabbage).
        2. Estimate the calories, protein, carbs, and fats.
        3. Provide a brief health tip based on the meal composition.
        
        Output MUST be MUST be JSON with:
        {
            "identified_foods": ["item1", "item2"],
            "estimates": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0},
            "insight": "Cultural/Health tip"
        }
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt + "\nRespond with JSON only."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                            }
                        ]
                    }
                ],
                model=self.vision_model
            )
            content = chat_completion.choices[0].message.content
            # Try to find JSON in the response if the model included extra text
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            return json.loads(content)
        except Exception as e:
            import traceback
            print(f"Vision AI Error: {e}")
            print(traceback.format_exc())
            return {"error": str(e)}

    def generate_morning_briefing(self, profile_data, recent_logs_data):
        """
        Generates a proactive "Morning Briefing" mission for the user.
        """
        if not self.client:
            return None

        prompt = f"""
        Role: Proactive Health Coach (Uganda context).
        User Goal: {profile_data.get('goal', 'General Health')}.
        Health Conditions: {json.dumps(profile_data.get('conditions', []))}.
        Recent Performance (Last 3 days): {json.dumps(recent_logs_data)}.

        Task: Generate a "Mission for the Day".
        - Autonomous Logic: If weight progress has stalled (based on logs), suggest a shift (e.g., "I've noticed your weight is plateauing, let's swap Posho for Matooke today").
        - Nudge: Be specific about Ugandan food.
        - Tone: Conversational Agent (less "app", more "helper").

        Output MUST be JSON with:
        {{
            "summary": "Short Mission Title",
            "message": "Direct message explaining the 'why' (e.g., 'Your carbs are 20% higher than target...')",
            "recommendation": "Specific food action",
            "autonomous_adjustment": "Did you adjust the plan based on progress? (Yes/No)",
            "motivation": "Short punchy line"
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an autonomous health agent. You analyze data and adjust goals proactively. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Morning Briefing Error: {e}")
            return None

    def check_food_risk_ai(self, food_name, profile_data):
        """
        Uses AI reasoning to check if a food is risky for a specific health profile.
        NO hardcoding. Real clinical reasoning.
        """
        if not self.client:
            return None

        prompt = f"""
        Analyze if this food is risky for the user.
        Food: {food_name}
        User Goal: {profile_data.get('goal')}
        User Conditions: {json.dumps(profile_data.get('conditions', []))}

        Task: Determine if there is a clinical reason to avoid this food.
        Return JSON:
        {{
            "is_risky": true/false,
            "reason": "Clear explanation of the nutrient impact (e.g., glycemic index, sodium, etc.)",
            "severity": "Low/Medium/High"
        }}
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a clinical nutritionist. Analyze risk based on nutrients. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"AI Risk Check Error: {e}")
            return None

    def _offline_fallback(self):
        return {
            "summary": "NutriAgent is in Local-Only Mode.",
            "behavioral_insight": "AI Reasoning is currently offline. We are using local metrics to monitor your health. Your patterns appear stable.",
            "risk_level": "Low",
            "recommendations": ["Focus on local seasonal vegetables", "Keep a consistent meal schedule", "Drink 2-3 liters of water daily"],
            "motivation": "Consistency is the key to lasting health. You're doing great!"
        }
