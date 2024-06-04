from flask import Flask, request, render_template, url_for, redirect, jsonify
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from pymongo import MongoClient

# Global parameters
cloud_data = pd.DataFrame()

# App init
app = Flask(__name__)

# Function to get data from MongoDB
def get_data_mongo():
    df = pd.DataFrame()
    # Chuỗi kết nối (Connection String) đến cluster của MongoDB
    connect = [
        "nothing",
        "mongodb+srv://21520553:Pass4trial@cluster1.qdcmgu5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1",
        "mongodb+srv://21520553:Pass4trial@cluster2.kv5qtl9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2",
        "mongodb+srv://21520553:Pass4trial@cluster3.qh1bqlz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster3"
    ]

    for i in range(3, 4):
        mg_cluster = MongoClient(connect[i])
        db = mg_cluster[f'database{i}']
        collection = db[f'dataframe{i}']

        sub_doc_1 = collection.find().limit(600000)
        sub_doc_2 = collection.find().skip(600000)
        sub_df_1 = pd.DataFrame(list(sub_doc_1))
        sub_df_2 = pd.DataFrame(list(sub_doc_2))
        df = pd.concat([df, sub_df_1, sub_df_2], ignore_index=True)

    # Drop column '_id' that occurs due to MongoDB
    df.drop(columns=['_id'], inplace=True, errors='ignore')
    return df


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


def extract_views_count(df):
    data_dict = dict(sorted(df['num_watch_vid'].value_counts().to_dict().items()))
    grouped_data = group_data(data_dict)
    data_keys = list(grouped_data.keys())
    data_values = list(grouped_data.values())
    return data_keys, data_values


@app.route("/")
def home():
    data_keys, data_values = extract_views_count(cloud_data)
    return render_template("index.html", data_keys=data_keys, data_values=data_values)


@app.route('/cluster')
def cluster():
    np.random.seed(10)
    X = np.random.randn(100, 2)
    # Khởi tạo mô hình K-Means với 4 cụm
    kmeans = KMeans(n_clusters=3)
    # Huấn luyện mô hình trên dữ liệu
    kmeans.fit(X)
    labels = kmeans.labels_
    # Tạo danh sách các cụm
    clusters = [[] for _ in range(3)]
    for point, label in zip(X, labels):
        clusters[label].append({'x': point[0], 'y': point[1]})

    # Truyền dữ liệu cụm vào template
    return render_template('cluster.html', clusters=clusters)


@app.route('/send-category', methods=['POST'])
def send_category():
    selected_category = str(request.json.get('selectedCategory'))
    print(selected_category)
    filtered_df = pd.DataFrame()
    if selected_category == '>200':
        filtered_df = cloud_data[cloud_data['num_watch_vid'] > 200]
    else:
        # Tách giá trị tối thiểu và tối đa từ biến str
        minmax = selected_category.split('-')
        min_value = int(minmax[0])
        max_value = int(minmax[1])
        # Lọc DataFrame với điều kiện
        filtered_df = cloud_data[(cloud_data['num_watch_vid'] >= min_value) & (cloud_data['num_watch_vid'] <= max_value)]
    filtered_df = filtered_df.loc[:, ['id', 'name', 'gender', 'num_watch_vid']]
    filtered_data = filtered_df.to_dict('records')
    return jsonify(filtered_data)


if __name__ == "__main__":
    cloud_data = pd.read_json('test-data/output_1.json', lines=True) #get_data_mongo()
    app.run(debug=True)
