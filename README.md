# Tutor de Inglês LLM
Aluno: Roger Stroff Leites
Tópicos Especiais em Computação.
Python 3.10+

O sistema funciona como um tutor de inglês por voz. Usuário fala via microfone e recebe:
-Resposta em áudio gerada por IA
-Feedback textual com correções gramaticais e sugestões
-Pontuação de desempenho

Bibliotecas utilizadas:
Gradio
Google Gemini API (multimodal)
edge-tts (síntese de voz)
python-dotenv

---

Instalação:
```bash
git clone https://github.com/rogerstroff/tutoringles.git
cd tutoringles
python -m venv venv
venv\Scripts\activate
pip install -r reqs.txt
python tutoringles.py
