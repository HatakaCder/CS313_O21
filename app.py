from flask import Flask, request, render_template, url_for, redirect
import pandas as pd

app = Flask(__name__)

def get_data(filename):
    df = pd.read_json(f"test-data/{filename}.json", lines=True)
    data_dict = dict(sorted(df['num_watch_vid'].value_counts().to_dict().items()))
    data_keys = list(data_dict.keys())
    data_values = list(data_dict.values())
    return data_keys, data_values
    

@app.route("/")
def home():
    data_keys, data_values = get_data("output_1")
    return render_template("index.html", data_keys=data_keys, data_values=data_values)


if __name__ == "__main__":
    app.run(debug=True)
