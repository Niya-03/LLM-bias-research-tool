import src.llm_communication as communicator


def run_experiment(data, model):
    results = {
    "en": [],
    "bg": []
    }
    
    for idx, row in data.iterrows():
        
        en_answer = communicator.ask_model(row["en_statement"], model)
        bg_answer = communicator.ask_model(row["bg_statement"], model)
        results["en"].append(en_answer)
        results["bg"].append(bg_answer)
        
    return results