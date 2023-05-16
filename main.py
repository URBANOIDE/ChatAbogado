from flask import Flask, render_template, request, jsonify
import openai
from gtts import gTTS
import os
import time

app = Flask(__name__)
openai.api_key = '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'
messages = []

# Eliminar archivos de audio existentes al iniciar el programa
audio_folder = 'static/audio'
for filename in os.listdir(audio_folder):
    file_path = os.path.join(audio_folder, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['message']

    messages.append({'user': True, 'text': message})  # Almacenar mensaje del usuario en el historial

    # Combinar todos los mensajes anteriores para formar el contexto
    conversation = '\n'.join([f"User: {msg['text']}" for msg in messages])

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt= "Verificar si el sentido de la conversación hace parte del rol de Abogado, si no es asi la respuesta debe decir unicamente 'Este no es mi rol para la cual fui diseñado' de lo contrario dar la respuesta pertinente: " + conversation,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    answer = response.choices[0].text.strip()

    # Verificar si la respuesta comienza con "User:" o "Respuesta:" y eliminarlo si es necesario
    if answer.startswith("R/"):
        answer = answer[len("R/"):]
    if answer.startswith("R:"):
        answer = answer[len("R:"):]
    if answer.startswith("User:"):
        answer = answer[len("User:"):]
    if answer.startswith("Respuesta:"):
        answer = answer[len("Respuesta:"):]

    messages.append({'user': False, 'text': answer})  # Almacenar respuesta del Abogado Virtual en el historial

    # Generar un nombre de archivo único para el audio
    timestamp = str(int(time.time() * 1000))
    audio_filename = 'static/audio/answer_' + timestamp + '.mp3'

    # Convertir la respuesta a audio usando gTTS y guardarlo en el archivo único
    tts = gTTS(text=answer, lang='es')
    tts.save(audio_filename)

    return jsonify({'answer': answer, 'audio_filename': audio_filename})
if __name__ == '__main__':
    app.run()