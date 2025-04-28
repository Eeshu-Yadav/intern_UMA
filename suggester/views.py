import os
from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
from .models import QueryLog

# Load environment variables
load_dotenv()

# Initialize Genai client
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
        
        try:
            # Generate content with Gemini 2.0 Flash
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Analyze this message: '{query}'. Respond ONLY with format: 'Tone: [one word] | Intent: [2-3 words]'"
            )
            
            analysis = response.text
            tone, intent = self.parse_response(analysis)
            
            # Action selection logic
            actions = []
            if "urgent" in tone.lower():
                actions = ACTION_MAPPING["urgent"]
            else:
                for key in ACTION_MAPPING:
                    if key in intent.lower():
                        actions = ACTION_MAPPING[key][:3]
                        break
                if not actions:
                    actions = ACTION_MAPPING["default"]
            
            # Database logging
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
            return Response({"error": f"Genai API Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def parse_response(self, text):
        try:
            parts = text.split("|")
            tone = parts[0].split(":")[1].strip()
            intent = parts[1].split(":")[1].strip()
            return tone, intent
        except:
            return "Neutral", "General Inquiry"