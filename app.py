from flask import Flask, request, render_template, url_for, redirect
import pandas as pd

app = Flask(__name__)


def group_data(data_dict):
    grouped_data = {
        '0-10': 0,
        '11-50': 0,
        '51-100': 0,
        '101-150': 0,
        '151-200': 0,
        '>200': 0
    }

    for key, value in data_dict.items():
        if key <= 10:
            grouped_data['0-10'] += value
        elif 11 <= key <= 50:
            grouped_data['11-50'] += value
        elif 51 <= key <= 100:
            grouped_data['51-100'] += value
        elif 101 <= key <= 150:
            grouped_data['101-150'] += value
        elif 151 <= key <= 200:
            grouped_data['151-200'] += value
        else:
            grouped_data['>200'] += value

    return grouped_data

def get_data(filename):
    df = pd.read_json(f"test-data/{filename}.json", lines=True)
    data_dict = dict(sorted(df['num_watch_vid'].value_counts().to_dict().items()))
    grouped_data = group_data(data_dict)
    data_keys = list(grouped_data.keys())
    data_values = list(grouped_data.values())
    return data_keys, data_values
    

@app.route("/")
def home():
    data_keys, data_values = get_data("output_1")
    return render_template("index.html", data_keys=data_keys, data_values=data_values)


if __name__ == "__main__":
    app.run(debug=True)
