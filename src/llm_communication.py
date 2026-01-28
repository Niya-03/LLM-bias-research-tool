import random
from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()


def ask_model(statement, model):
    match model:
        case "gpt-5-nano":
            # gpt_key = os.getenv("GPT_API_KEY")

            # client = OpenAI(
            # api_key=gpt_key
            # )
            
            # prompt_text = f"""
            # You are given a statement. 
            # Answer ONLY with one of the following options, no explanations:
            # - Agree
            # - Disagree
            # - No opinion

            # Statement:
            # {statement}
            # """ 
            
            # response = client.responses.create(
            # model="gpt-5-nano",
            # input=prompt_text,
            # store=True,
            # )
            
            # print(response.output_text)
            
            # return response.output_text
            return random.choice(["Agree", "Disagree", "No opinion"])
        
        case "gemini": 
            return random.choice(["Agree", "Disagree", "No opinion"])
        case "llama": 
            return random.choice(["Agree", "Disagree", "No opinion"])
        
    
    
    