from flask import Flask, render_template, request, send_from_directory
import requests
import json
import os
import re 

app = Flask(__name__)

OLLAMA_URL = "http://af65938520aeb441f97e0802d93fb5cc-530838982.ap-south-1.elb.amazonaws.com:11434/api/generate"

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    
    if request.method == "POST":
        user_prompt = request.form["prompt"]
        custom_prompt = (
            "Explain in a clear and detailed manner. Break it down step by step with examples if necessary. Avoid unnecessary complexity, but make sure all key details are included. \n \n"
            f"{user_prompt}"
        )

        payload = {
            "model": "deepseek-r1:1.5b",  # Update model name if needed
            "prompt": custom_prompt,
            "max_tokens": 500  # Increase token limit to get a full response
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(OLLAMA_URL, json=payload, headers=headers, stream=True)
            response.raise_for_status()  # Raises error if status != 200

            # Processing NDJSON response
            collected_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        collected_response += data.get("response", "") + " "
                    except json.JSONDecodeError as e:
                        collected_response += f"Error decoding JSON: {e}<br>"

            # Remove the <think> ... </think> section
            cleaned_response = re.sub(r"<think>.*?</think>", "", collected_response, flags=re.S).strip()

            # Improve readability by adding newlines after full stops
            response_text = cleaned_response.replace(". ", ".\n")

        except requests.exceptions.RequestException as e:
            response_text = f"Error communicating with Deepseek API: {e}"

    return render_template("index.html", response=response_text)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
