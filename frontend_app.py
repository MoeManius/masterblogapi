import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

BACKEND_API_URL = 'http://localhost:5002/api/posts'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Fetch blog posts from the backend API."""
    response = requests.get(BACKEND_API_URL)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch posts"}), response.status_code

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new blog post by sending data to the backend API."""
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data or 'author' not in data or 'date' not in data:
        return jsonify({"error": "Missing required fields: title, content, author, or date."}), 400

    response = requests.post(BACKEND_API_URL, json=data)

    if response.status_code == 201:
        return jsonify(response.json()), 201
    else:
        return jsonify({"error": "Failed to create post"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=5000)
