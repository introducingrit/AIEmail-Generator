import os
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Put your API key directly here inside quotes
groq_client = Groq(api_key="YOUR_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_email():
    data = request.json or {}
    recipient = data.get("recipient", "Colleague")
    purpose = data.get("purpose", "")
    tone = data.get("tone", "Professional")
    key_points = data.get("key_points", "")

    if not purpose:
        return jsonify({"error": "Email purpose is required."}), 400

    prompt = f"""
    You are an expert executive communication assistant. Generate a professional email based on:
    - Recipient: {recipient}
    - Purpose/Context: {purpose}
    - Desired Tone: {tone}
    - Key Points to Include: {key_points}

    Format your output EXACTLY as follows:
    SUBJECT: <Insert concise, compelling email subject line>
    BODY:
    <Insert complete email body including standard greeting and professional sign-off>
    """

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional email writing assistant."},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7,
        )
        
        response_text = chat_completion.choices[0].message.content

        subject = ""
        body = ""
        if "SUBJECT:" in response_text and "BODY:" in response_text:
            parts = response_text.split("BODY:")
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
        else:
            subject = "Professional Communication"
            body = response_text.strip()

        return jsonify({"subject": subject, "body": body})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)