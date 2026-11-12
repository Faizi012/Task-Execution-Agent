
import requests

url = "http://localhost:11434/v1/chat/completions"

payload = {
    "model": "qwen2.5:3b",
    "messages": [
        {
            "role": "user",
            "content": "Say only: Qwen is working!"
        }
    ],
    "stream": False
}

try:
    response = requests.post(
        url,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    print("SUCCESS!")
    print(result["choices"][0]["message"]["content"])

except requests.exceptions.RequestException as e:
    print("CONNECTION FAILED:", e)
