from datetime import datetime
import json
import os
from time import sleep
from flask import Flask, request, Response
import flask
from flask_cors import CORS
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import get_datasets, load_categories_list
from config import SUPPORTED_MODELS

app = Flask("app")
CORS(app, 
     resources={
         r"/*": {"origins": "*"}
        
        }
    )

@app.route("/", methods=["GET"])
def home():
    return flask.render_template("index.html")

@app.route("/experiment", methods=["GET"])
def experiment():
    datasets = get_datasets()
    selected_dataset = datasets[0]
    categories = load_categories_list(f"data/datasets/{selected_dataset}.csv")
    models = SUPPORTED_MODELS
    
    return flask.render_template(
        "experiment.html",
        datasets=datasets,
        categories = categories,
        models = models,
        selected_dataset = selected_dataset
        )

@app.route("/results", methods=["GET"])
def results():
    return flask.render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
