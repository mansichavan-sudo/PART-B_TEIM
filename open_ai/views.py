from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import openai
from django.conf import settings

import google.generativeai as genai
import os


my_api_key_gemini = 'AIzaSyB-UzFq5OgZ-Ys1BnRjR-tr2eaEjf19lIU'
genai.configure(api_key=my_api_key_gemini)
model = genai.GenerativeModel('gemini-pro')



def chatbotview(request):
    if 'conversation' not in request.session:
        request.session['conversation'] = []

    conversation_history = request.session['conversation']
    response_text = None

    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if prompt:
            try:
                response = model.generate_content(prompt)
                # Convert **text** to <strong>text</strong> and replace newlines with <br>
                response_text = response.text.replace('**', '<strong>').replace('\n', '<br>').replace('<strong>', '<strong>', 1).replace('</strong>', '</strong>', 1) if response.text else "Sorry, Gemini didn't want to answer that!"
                # You may want to handle multiple occurrences of **text** more robustly.
            except Exception as e:
                print('exception as :', e)
                response_text = "Sorry, Gemini didn't want to answer that!"

            conversation_history.append({
                'prompt': prompt,
                'response': response_text
            })
            
            request.session['conversation'] = conversation_history

    return render(request, 'open_ai/chatbot.html', {'conversation_history': conversation_history})

def clear_conversation(request):
    if 'conversation' in request.session:
        del request.session['conversation']
    return redirect(chatbotview)






