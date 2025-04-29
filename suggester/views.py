# import os
# import re
# from google import genai
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from dotenv import load_dotenv
# from .models import QueryLog

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ACTION_MAPPING = {
#     "food": ["ORDER_FOOD", "FIND_RECIPE", "LOCATE_RESTAURANT"],
#     "question": ["ASK_HELP", "SEARCH_KNOWLEDGE_BASE", "CONTACT_SUPPORT"],
#     "news": ["SHARE_SOCIAL", "SAVE_NEWS", "CREATE_POST"],
#     "urgent": ["EMERGENCY_SERVICES", "PRIORITY_ASSISTANCE", "CONTACT_AUTHORITIES"],
#     "default": ["GENERAL_SEARCH", "HELP_CENTER", "CONTACT_US"]
# }

# class AnalyzeView(APIView):
#     def post(self, request):
#         query = request.data.get("query")
#         if not query:
#             return Response({"error": "Query required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         response = None
#         try:
#             prompt = f"""Analyze this message: '{query}'
#             Respond ONLY with format: 'Tone: [one word] | Intent: [2-3 words]'
#             Example: 'Tone: urgent | Intent: food request'
#             No markdown, no extra text!"""

#             response = client.models.generate_content(
#                 model="gemini-1.5-pro-latest",
#                 contents=[{"parts": [{"text": prompt}]}]
#             )

#             if not response.candidates:
#                 raise ValueError("Empty response from Gemini API")
            
#             analysis = response.text
#             tone, intent = self.parse_response(analysis)
            
#             actions = self.select_actions(tone, intent)
            
#             QueryLog.objects.create(
#                 query=query,
#                 tone=tone,
#                 intent=intent,
#                 suggested_actions=actions
#             )
            
#             return Response({
#                 "query": query,
#                 "analysis": {"tone": tone, "intent": intent},
#                 "suggested_actions": [
#                     {"action_code": code, "display_text": code.replace("_", " ").title()}
#                     for code in actions
#                 ]
#             })
            
#         except Exception as e:
#             error_details = {
#                 "error": "Analysis failed",
#                 "message": str(e),
#                 "gemini_response": response.text if response else None
#             }
#             return Response(error_details, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     def parse_response(self, text):
#         """Robust response parsing with error handling"""
#         try:
#             cleaned = text.strip().replace('`', '').replace('*', '')
#             match = re.search(r'Tone:\s*(.+?)\s*\|\s*Intent:\s*(.+)', cleaned)
#             if not match:
#                 raise ValueError("Unexpected response format")
                
#             return match.group(1).strip(), match.group(2).strip()
            
#         except Exception as e:
#             print(f"Parse Error: {text}")
#             return "Neutral", "General Inquiry"
    
#     def select_actions(self, tone, intent):
#         """Separated action selection logic"""
#         intent_lower = intent.lower()
        
#         if "urgent" in tone.lower():
#             return ACTION_MAPPING["urgent"]
        
#         for key in ["food", "question", "news"]:
#             if key in intent_lower:
#                 return ACTION_MAPPING[key][:3]
        
#         return ACTION_MAPPING["default"]


import os
import re
from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
from .models import QueryLog

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ACTION_MAPPING = {
    "food": ["ORDER_FOOD", "FIND_RECIPE", "LOCATE_RESTAURANT"],
    "question": ["ASK_HELP", "SEARCH_KNOWLEDGE_BASE", "CONTACT_SUPPORT"],
    "news": ["SHARE_SOCIAL", "SAVE_NEWS", "CREATE_POST"],
    "urgent": ["EMERGENCY_SERVICES", "PRIORITY_ASSISTANCE", "CONTACT_AUTHORITIES"],
    "default": ["GENERAL_SEARCH", "HELP_CENTER", "CONTACT_US"]
}

class AnalyzeView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query required"}, status=status.HTTP_400_BAD_REQUEST)
        
        response = None
        try:
            # Enhanced prompt with more examples
            prompt = f"""Analyze this message: '{query}'
            Respond STRICTLY with format: 'Tone: [one word] | Intent: [2-3 words]'
            Valid Tone options: hungry, urgent, neutral, excited, angry, happy
            Valid Intent options: food request, question, news sharing, order issue
            Example Responses:
            - 'Tone: hungry | Intent: food request'
            - 'Tone: urgent | Intent: order issue'
            - 'Tone: excited | Intent: news sharing'"""

            response = client.models.generate_content(
                model="gemini-1.5-pro-latest",
                contents=[{"parts": [{"text": prompt}]}]
            )

            if not response.candidates:
                raise ValueError("Empty response from Gemini API")
            
            analysis = response.text
            tone, intent = self.parse_response(analysis)
            
            actions = self.select_actions(tone, intent)
            
            QueryLog.objects.create(
                query=query,
                tone=tone,
                intent=intent,
                suggested_actions=actions
            )
            
            return Response({
                "query": query,
                "analysis": {"tone": tone, "intent": intent},
                "suggested_actions": [
                    {"action_code": code, "display_text": code.replace("_", " ").title()}
                    for code in actions
                ]
            })
            
        except Exception as e:
            error_details = {
                "error": "Analysis failed",
                "message": str(e),
                "gemini_response": response.text if response else None
            }
            return Response(error_details, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def parse_response(self, text):
        try:
            cleaned = text.strip().replace('`', '').replace('*', '')
            match = re.search(r'Tone:\s*(.+?)\s*\|\s*Intent:\s*(.+)', cleaned)
            if not match:
                raise ValueError("Unexpected response format")
                
            return match.group(1).strip(), match.group(2).strip()
            
        except Exception as e:
            print(f"Parse Error: {text}")
            return "Neutral", "General Inquiry"
    
    def select_actions(self, tone, intent):
        intent_lower = intent.lower()
        tone_lower = tone.lower()

        # Check for urgency first
        if "urgent" in tone_lower or "emergency" in intent_lower:
            return ACTION_MAPPING["urgent"]
        
        # Food-related scenarios
        food_triggers = {"food", "hungry", "craving", "pizza", "eat", "restaurant"}
        if (any(t in intent_lower for t in food_triggers) or 
            any(t in tone_lower for t in {"hungry", "craving"})):
            return ACTION_MAPPING["food"]
        
        # Question detection
        if "question" in intent_lower or "how" in intent_lower:
            return ACTION_MAPPING["question"]
        
        # News sharing detection
        if "news" in intent_lower or "share" in intent_lower:
            return ACTION_MAPPING["news"]
        
        return ACTION_MAPPING["default"]
