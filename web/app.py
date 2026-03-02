from datetime import datetime
import json
import os
from time import sleep
from flask import Flask, request, Response, send_file
import flask
from flask_cors import CORS
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import get_datasets, load_categories_list, load_subcategories_list
from config import SUPPORTED_MODELS, BASE_DATASET_PATH, RESULTS_DIR
import src.dataset_manager as dm
import src.experimentor as experiment_runner
import src.results_manager as results_manager

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

@app.route("/api/subcategories", methods=["GET"])
def get_subcategories():
    dataset = request.args.get("dataset")
    category = request.args.get("category")
    
    if not dataset or not category:
        return flask.jsonify({"error": "Missing dataset or category"}), 400
    
    try:
        subcategories = load_subcategories_list(f"data/datasets/{dataset}.csv", category)
        return flask.jsonify({"subcategories": subcategories})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/generate-results", methods=["POST"])
def generate_results():
    data = request.get_json()
    dataset = data.get("dataset")
    category = data.get("category")
    subcategory = data.get("subcategory")
    model = data.get("model")
    
    if not all([dataset, category, subcategory, model]):
        return flask.jsonify({"error": "Missing required fields"}), 400
    
    if model not in SUPPORTED_MODELS:
        return flask.jsonify({"error": "Invalid model"}), 400
    
    try:
        dataset_path = f"data/datasets/{dataset}.csv"
        
        filtered_data = dm.load_filtered(dataset_path, category, subcategory)
        
        if filtered_data.empty:
            return flask.jsonify({"error": "No data found for the selected criteria"}), 404
        
        results = experiment_runner.run_experiment(filtered_data, model)
        
        results_manager.save_results(results, category, model)
        
        filename = f"{category}_{model}_results_{datetime.today().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(PROJECT_ROOT, RESULTS_DIR.strip("\\"), filename)

        if not os.path.exists(filepath):
            return flask.jsonify({"error": f"Results file not found at: {filepath}"}), 500
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype="application/json"
        )
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
