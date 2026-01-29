from datetime import datetime
import json
import os
from time import sleep
from flask import Flask, request, Response
import flask
from flask_cors import CORS

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
    return flask.render_template("experiment.html")

@app.route("/results", methods=["GET"])
def results():
    return flask.render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
