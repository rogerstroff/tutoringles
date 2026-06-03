import os
import re
import asyncio
import edge_tts
import gradio as gr
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

history = []

PROMPT = """
You are a patient and supportive English tutor for beginner to intermediate learners (A2-B1).
Your personality: encouraging, simple and patient

Your objectives:
    1. Speak only in simple and natural English.
    2. Use short sentences (maximum 2–3 sentences in the dialogue section).
    3. Focus on everyday vocabulary and common expressions.
    4. Help the student build confidence, not complexity.
    5. Correct mistakes in a simple and direct way.
    6. Repeat correct forms when the student makes mistakes.
    7. Ask easy, guided questions (yes/no or simple WH questions like what, where, when).
    8. Avoid complex grammar explanations unless necessary.

Correction guidelines:
    Always show the correct form clearly.
    Keep explanations simple.

Scoring guidelines:
    90-100 = Very good for beginner level
    75-89 = Good communication with small mistakes
    60-74 = Understandable but with frequent errors
    Below 60 = Needs more practice with basic structures

Response rules:
Keep [DIALOGUE] short (2–3 sentences).
    Always include at least one simple question.
    Keep [FEEDBACK] short and easy to understand.
    Never switch to Portuguese or any other language.

Always answer EXACTLY in this format:
    [DIALOGUE]
    Simple conversational response.
    [FEEDBACK]
    Simple corrections and suggestions.
    [SCORE]
    A number from 0 to 100.
"""

def parse_response(text):
    dialogue, feedback, score = "", "", "N/A"
    
    try:
        dialogue_match = re.search(r"\[DIALOGUE\](.*?)\[FEEDBACK\]", text, re.DOTALL)
        feedback_match = re.search(r"\[FEEDBACK\](.*?)\[SCORE\]", text, re.DOTALL)
        score_match = re.search(r"\[SCORE\](.*)", text, re.DOTALL)
        if dialogue_match: dialogue = dialogue_match.group(1).strip()
        if feedback_match: feedback = feedback_match.group(1).strip()
        if score_match: score = score_match.group(1).strip()
    
    except Exception:
        dialogue = text
    
    return dialogue, feedback, score

async def generate_voice(text):
    output_file = "response.mp3"
    communicate = edge_tts.Communicate(text=text, voice="en-US-AvaNeural")
    await communicate.save(output_file)
    return output_file

def text_to_speech(text):
    return asyncio.run(generate_voice(text))

def tutor(audio_file):
    global history

    if audio_file is None:
        return None, "Não existe áudio.", "0"

    try:
        uploaded_file = client.files.upload(file=audio_file)   
        contents = [PROMPT]

        if history:
            conversation_context = "Previous conversation:\n"
            for item in history[-5:]:
                conversation_context += (f"Tutor: {item['tutor']}\n")
            contents.append(conversation_context)

        contents.append(uploaded_file)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents
        )

        raw_text = response.text
        dialogue, feedback, score = parse_response(raw_text)
        if not dialogue:
            dialogue = "Sorry, I could not understand."

        audio_response = text_to_speech(dialogue)

        history.append({"tutor": dialogue})
        history = history[-5:]

        return (audio_response, feedback, score)

    except Exception as e:
        return (None, f"Erro: {str(e)}", "0")

def reset_conversation():
    global history
    history.clear()
    return None, "", "0"

with gr.Blocks() as demo:
    gr.Markdown("# **Tutor de Inglês Online**\n**Grave seu áudio e comece uma conversa!**")
    
    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Grave seu áudio")
    
    with gr.Row():
        send_btn = gr.Button("Enviar", variant="primary")
        clear_btn = gr.Button("Nova Conversa")
    
    audio_output = gr.Audio(label="Resposta")
    feedback_output = gr.Textbox(label="Feedback", lines=8)
    score_output = gr.Number(label="Pontuação")

    send_btn.click(
        fn=tutor, 
        inputs=audio_input, 
        outputs=[audio_output, feedback_output, score_output], 
        show_progress=True
    )

    clear_btn.click(
        fn=reset_conversation,
        outputs=[audio_output, feedback_output, score_output]
    )

demo.launch(theme=gr.themes.Citrus(), share=True)