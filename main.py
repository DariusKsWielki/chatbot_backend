from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

# Słownik do przechowywania stanu rozmowy dla każdego użytkownika (identyfikowanego unikalnym ID)
conversation_states = {}

OPENAI_API_KEY = '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'

def call_chat_gpt(prompt, user_id):
    restaurant_info = {
        'pizza_hut': {
            'name': 'Pizza Hut',
            'menu': 'Pizza Margherita, Pizza Pepperoni, Pizza Veggie',
            'opening_hours': '10:00 - 22:00'
        },
    }
    # Sprawdź, czy to początek rozmowy z danym użytkownikiem
    if user_id not in conversation_states:
        # Ustaw początkowy stan rozmowy i przygotuj initial_prompt
        conversation_states[user_id] = {'initial_prompt_sent': True}
        prompt = f"Hej ChatGPT, teraz jesteś chatbotem do zamawiania pizzy w lokalu {restaurant_info['pizza_hut']['name']} z menu {restaurant_info['pizza_hut']['menu']}. Będziesz rozmawiać z klientami. Zacznij rozmowę od 'Dzień dobry, w czym mogę pomóc?'"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    data = {
        'model': 'gpt-3.5-turbo',  # Wskazanie modelu
        'prompt': prompt,
        'temperature': 0.7,
        'max_tokens': 100
    }
    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    response_json = response.json()
    return response_json['choices'][0]['text']

# Zmodyfikowana funkcja, aby przyjmować obiekt request jako argument
@app.route('/', methods=['POST'])
def handle_request(request):
    req = request.get_json(silent=True, force=True)
    query_text = req.get('queryResult').get('queryText')

    # Otrzymaj session ID z żądania; jeśli nie ma, wygeneruj nowe
    session_id = req.get('session')
    if not session_id:
        # Generowanie nowego unikalnego ID sesji, jeśli nie dostarczono
        session_id = str(uuid.uuid4())

    # Użyj session_id jako user_id do śledzenia stanu konwersacji
    chat_gpt_response = call_chat_gpt(query_text, session_id)
    response_text = chat_gpt_response

    return jsonify({
        'fulfillmentText': response_text,
        'session_id': session_id  # Zwróć aktualne session_id jako część odpowiedzi
    })

if __name__ == '__main__':
    app.run(debug=True)
