import os
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import QueryLog

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ACTION_MAPPING = {
    "Order Food": ["ORDER_FOOD", "FIND_RECIPE"],
    "Ask Question": ["ASK_HELP", "SEARCH_KNOWLEDGE_BASE"],
    "Share News": ["SHARE_SOCIAL", "SAVE_NEWS"],
    "Urgent Help": ["CONTACT_SUPPORT", "EMERGENCY_SERVICES"],
    "Default": ["GENERAL_SEARCH"]
}

class AnalyzeView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Analyze: '{query}'. Respond with 'Tone: [one word] | Intent: [2-3 words]'"
                }]
            )
            
            analysis = response.choices[0].message.content
            tone, intent = self.parse_response(analysis)
            
            actions = []
            for key in ACTION_MAPPING:
                if key.lower() in intent.lower():
                    actions = ACTION_MAPPING[key][:3]
                    break
            if not actions:
                actions = ACTION_MAPPING["Default"]
            
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
                    {"action_code": code, "display_text": code.replace("_", " ")}
                    for code in actions
                ]
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def parse_response(self, text):
        parts = text.split("|")
        tone = parts[0].split(":")[1].strip()
        intent = parts[1].split(":")[1].strip()
        return tone, intent