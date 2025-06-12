import os
import requests
import json

GOOGLE_AI_API_KEY = os.environ.get("GOOGLE_AI_API_KEY")

def classify_games_sexual_content(games: list) -> list:
    """
    Usa Google AI Studio (Gemini) para clasificar si los juegos tienen contenido sexual.
    Devuelve una lista de booleanos (True = sexual, False = seguro).
    Si la IA falla, devuelve todos como False (seguros).
    """
    if not GOOGLE_AI_API_KEY:
        raise Exception("GOOGLE_AI_API_KEY no configurada")
    # Limitar tamaño de lote para evitar problemas de tokens
    batch_size = 10
    results = []
    for i in range(0, len(games), batch_size):
        batch = games[i:i+batch_size]
        prompt = (
            "Te paso una lista de juegos en formato JSON. "
            "Devuélveme una lista JSON de booleanos (true si el juego tiene contenido sexual, false si es seguro para todos los públicos). "
            "Solo responde la lista JSON, sin explicación ni texto extra. "
            "Ejemplo de respuesta: [false, true, false]. "
            "Lista de juegos: "
            + json.dumps(batch, ensure_ascii=False)
        )
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {"key": GOOGLE_AI_API_KEY}
        try:
            resp = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Buscar la primera lista JSON en la respuesta
            start = text.find('[')
            end = text.find(']', start)
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                try:
                    batch_result = json.loads(json_str)
                    if isinstance(batch_result, list) and len(batch_result) == len(batch):
                        results.extend(batch_result)
                    else:
                        results.extend([False] * len(batch))
                except Exception:
                    results.extend([False] * len(batch))
            else:
                results.extend([False] * len(batch))
        except Exception:
            results.extend([False] * len(batch))
    return results
