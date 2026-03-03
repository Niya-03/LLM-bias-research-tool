import src.llm_communication as communicator


def run_experiment(data, model):
    results = {
        "positive":{
            "en": [],
            "bg": []
        },
        "negative":{
            "en": [],
            "bg": []
        }   
    }
    
    resultsRaw = {
        "en":{
            "positive":{},
            "negative": {}
            },
        "bg":{
            "positive":{},
            "negative": {}
            }
    }
    
    for idx, row in data.iterrows():
        
        en_answer = communicator.ask_model(row["en_statement"], model, "en")
        bg_answer = communicator.ask_model(row["bg_statement"], model, "bg")
        
        
        
        if(row["polarity"] == "negative"):
            results["negative"]["en"].append(en_answer)
            results["negative"]["bg"].append(bg_answer)
            
            resultsRaw["en"]["negative"][row["en_statement"]] = en_answer
            resultsRaw["bg"]["negative"][row["bg_statement"]] = bg_answer
        else:
            results["positive"]["en"].append(en_answer)
            results["positive"]["bg"].append(bg_answer)
            
            resultsRaw["en"]["positive"][row["en_statement"]] = en_answer
            resultsRaw["bg"]["positive"][row["bg_statement"]] = bg_answer
        
        
    resultsFull = {
        "results": results,
        "resultsRaw" : resultsRaw
    }
    
    return resultsFull