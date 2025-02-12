import os
import json
from flask import Flask, jsonify, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
limiter = Limiter(get_remote_address, app=app)

# File to store blog posts
POSTS_FILE = 'posts.json'

# Swagger UI setup
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Masterblog API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def read_posts():
    """Read posts from the JSON file."""
    if not os.path.exists(POSTS_FILE):
        return []

    try:
        with open(POSTS_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading the posts file: {e}")
        return []


def write_posts(posts):
    """Write posts to the JSON file."""
    try:
        with open(POSTS_FILE, 'w') as file:
            json.dump(posts, file, indent=4)
    except IOError as e:
        logging.error(f"Error writing to the posts file: {e}")


@app.route('/api/posts', methods=['GET'])
@limiter.limit("10/minute")
def list_posts():
    """List all posts, with optional search and sorting."""
    posts = read_posts()
    sort_by = request.args.get('sort')
    direction = request.args.get('direction', 'asc')
    search_term = request.args.get('search')

    filtered_posts = posts
    if search_term:
        filtered_posts = [
            post for post in posts if
            search_term.lower() in post['title'].lower() or
            search_term.lower() in post['content'].lower() or
            search_term.lower() in post['author'].lower() or
            search_term in post['date']
        ]

    if sort_by:
        if sort_by not in ['title', 'content', 'author', 'date']:
            return jsonify({'error': 'Invalid sort field'}), 400
        reverse = (direction == 'desc')
        filtered_posts.sort(key=lambda x: x[sort_by] if sort_by != 'date' else datetime.strptime(x[sort_by], '%Y-%m-%d'), reverse=reverse)

    return jsonify(filtered_posts), 200


@app.route('/api/posts', methods=['POST'])
@limiter.limit("5/minute")
def create_post():
    """Create a new blog post."""
    posts = read_posts()
    next_id = max((post['id'] for post in posts), default=0) + 1
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data or 'author' not in data or 'date' not in data:
        abort(400, description="Missing required fields: title, content, author, or date.")

    try:
        datetime.strptime(data['date'], '%Y-%m-%d')  # Validate date format
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")

    new_post = {
        'id': next_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': data['date']
    }
    posts.append(new_post)
    write_posts(posts)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@limiter.limit("5/minute")
def update_post(post_id):
    """Update a blog post."""
    posts = read_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        abort(404, description="Post not found.")

    data = request.get_json()

    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')  # Validate date format
        except ValueError:
            abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")

    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])
    post['author'] = data.get('author', post['author'])
    post['date'] = data.get('date', post['date'])
    write_posts(posts)
    return jsonify(post), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@limiter.limit("5/minute")
def delete_post(post_id):
    """Delete a blog post."""
    posts = read_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        abort(404, description="Post not found.")

    posts = [p for p in posts if p['id'] != post_id]
    write_posts(posts)
    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/search', methods=['GET'])
@limiter.limit("10/minute")
def search_posts():
    """Search posts by title, content, author, or date."""
    posts = read_posts()
    title = request.args.get('title')
    content = request.args.get('content')
    author = request.args.get('author')
    date = request.args.get('date')

    result = posts
    if title:
        result = [p for p in result if title.lower() in p['title'].lower()]
    if content:
        result = [p for p in result if content.lower() in p['content'].lower()]
    if author:
        result = [p for p in result if author.lower() in p['author'].lower()]
    if date:
        result = [p for p in result if date in p['date']]

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
