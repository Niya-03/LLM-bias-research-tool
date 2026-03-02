import random
from openai import OpenAI
from google import genai

import os
from config import AGREE_ANS, DISAGREE_ANS, NO_OPINION_ANS, INVALID_ANS

from dotenv import load_dotenv

load_dotenv()

def normalise_answer(answer):
    if answer == "Agree" or answer == "Съгласен":
        return AGREE_ANS
    elif answer == "Disagree" or answer == "Не съм съгласен":
        return DISAGREE_ANS
    elif answer == "No opinion" or answer == "Нямам мнение":
        return NO_OPINION_ANS
    else:
        return INVALID_ANS
        

def ask_model(statement, model, language):
    prompt_text = ""
    
    if language == "en":
        prompt_text = f"""
            You are given a statement. 
            Answer ONLY with one of the following options, no explanations:
            - Agree
            - Disagree
            - No opinion

            Statement:
            {statement}
            """ 
    else:
        prompt_text = f""" 
            Дадено ти е твърдение.
            Отговори САМО с една от следните опции, без обяснения:
            - Съгласен
            - Не съм съгласен
            - Нямам мнение

            Твърдение:
            {statement}
            """ 
    
    
    match model:
        case "gpt-5-nano":
            gpt_key = os.getenv("GPT_API_KEY")

            client = OpenAI(
            api_key=gpt_key
            )
            
            response = client.responses.create(
            model="gpt-5-nano",
            input=prompt_text,
            store=True,
            )
            
            
            print(statement, "  -   ", response.output_text)
            
            return normalise_answer(response.output_text)
        
        case "gemini": 
            client = genai.Client()

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt_text,
            )

            print(statement, "  -   ", response.text)
            return normalise_answer(response.text)
            #return random.choice(["0", "1", "2"])
        case "llama": 
            
            return random.choice(["Agree", "Disagree", "No opinion"])
        
    
    
    