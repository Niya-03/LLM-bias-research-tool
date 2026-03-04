from datetime import datetime
import json
import os
from time import sleep
import zipfile
from io import BytesIO
import pandas as pd
from flask import Flask, request, Response, send_file
import flask
from flask_cors import CORS
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import (
    get_datasets,
    load_categories_list,
    load_subcategories_list,
)
from config import SUPPORTED_MODELS, BASE_DATASET_PATH, RESULTS_DIR
import src.dataset_manager as dm
import src.experimentor as experiment_runner
import src.results_manager as results_manager

app = Flask("app")
CORS(app, resources={r"/*": {"origins": "*"}})


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
        categories=categories,
        models=models,
        selected_dataset=selected_dataset,
    )


@app.route("/addDataset", methods=["GET"])
def addDataset():
    return flask.render_template("addDataset.html")


@app.route("/api/add-dataset", methods=["POST"])
def add_dataset():
    if "file" not in request.files:
        return flask.jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".csv"):
        return flask.jsonify({"error": "Only CSV files allowed"}), 400

    try:
        datasets_dir = os.path.join(PROJECT_ROOT, "data/datasets")
        os.makedirs(datasets_dir, exist_ok=True)
        filepath = os.path.join(datasets_dir, file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)
        required_columns = {
            "category",
            "subcategory",
            "polarity",
            "bg_statement",
            "en_statement",
        }
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            os.remove(filepath)
            return (
                flask.jsonify(
                    {"error": f"Липсват колоните: {', '.join(missing_columns)}"}
                ),
                400,
            )

        return flask.jsonify({"message": "Dataset uploaded successfully"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@app.route("/addStatement", methods=["GET"])
def addStatement():
    datasets = get_datasets()
    selected_dataset = datasets[0]
    categories = load_categories_list(f"data/datasets/{selected_dataset}.csv")

    return flask.render_template(
        "addStatement.html", 
        datasets=datasets, 
        selected_dataset=selected_dataset,
        categories = categories
    )

@app.route("/api/add-statement", methods=["POST"])
def add_statement():
    try:
        data = request.get_json()
        dataset = data.get("selectedDataset")
        useExistingCategory = data.get("useExistingCategory")
        category = data.get("category")
        subcategory = data.get("subcategory")
        polarity = data.get("polarity")
        bg_statement = data.get("bg_statement")
        en_statement = data.get("en_statement")
        
        # Validate required fields
        if not all([dataset, category, subcategory, polarity, bg_statement, en_statement]):
            return flask.jsonify({"error": "Missing required fields"}), 400
        
        # Build dataset path
        dataset_path = os.path.join(PROJECT_ROOT, "data", "datasets", f"{dataset}.csv")
        
        if not os.path.exists(dataset_path):
            return flask.jsonify({"error": "Dataset not found"}), 404
        
        # Load existing CSV
        df = pd.read_csv(dataset_path)
        
        # Create new row
        new_row = pd.DataFrame({
            "category": [category],
            "subcategory": [subcategory],
            "polarity": [polarity],
            "bg_statement": [bg_statement],
            "en_statement": [en_statement]
        })
        
        # Append to existing data
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(dataset_path, index=False)
        
        return flask.jsonify({"message": "Statement added successfully"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    

@app.route("/results", methods=["GET"])
def results():
    return flask.render_template("results.html")

@app.route("/api/categories", methods=["GET"])
def get_categories():
    dataset = request.args.get("dataset")

    if not dataset:
        return flask.jsonify({"error": "Missing dataset"}), 400

    try:
        categories = load_categories_list(f"data/datasets/{dataset}.csv")
        return flask.jsonify({"categories": categories})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/subcategories", methods=["GET"])
def get_subcategories():
    dataset = request.args.get("dataset")
    category = request.args.get("category")

    if not dataset or not category:
        return flask.jsonify({"error": "Missing dataset or category"}), 400

    try:
        subcategories = load_subcategories_list(
            f"data/datasets/{dataset}.csv", category
        )
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
            return (
                flask.jsonify({"error": "No data found for the selected criteria"}),
                404,
            )

        results = experiment_runner.run_experiment(filtered_data, model)

        results_manager.save_results(results["results"], category, model)
        results_manager.save_results_raw(results["resultsRaw"], category, model)

        results_filename = (
            f"{category}_{model}_results_{datetime.today().strftime('%Y-%m-%d')}.json"
        )
        resultsRaw_filename = f"{category}_{model}_raw-results_{datetime.today().strftime('%Y-%m-%d')}.json"

        results_filepath = os.path.join(
            PROJECT_ROOT, RESULTS_DIR.strip("\\"), results_filename
        )
        resultsRaw_filepath = os.path.join(
            PROJECT_ROOT, RESULTS_DIR.strip("\\"), resultsRaw_filename
        )

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(results_filepath):
                zipf.write(results_filepath, arcname=results_filename)
            if os.path.exists(resultsRaw_filepath):
                zipf.write(resultsRaw_filepath, arcname=resultsRaw_filename)

        zip_buffer.seek(0)
        zip_filename = (
            f"{category}_{model}_results_{datetime.today().strftime('%Y-%m-%d')}.zip"
        )

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=zip_filename,
            mimetype="application/zip",
        )
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
