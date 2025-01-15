from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import NotFound, BadRequest
from flask_limiter import Limiter

app = Flask(__name__, static_folder='static')

# Initialize Rate Limiting
limiter = Limiter(app)

# Sample data for blog posts
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."}
]

# Swagger UI configuration
SWAGGER_URL = "/api/docs"  # Swagger UI endpoint
API_URL = "/static/masterblog.json"  # Path to the Swagger JSON file in the static folder

# Initialize Swagger UI blueprint
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)

# Register Swagger UI blueprint
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Create a route for the list of posts
@app.route('/api/posts', methods=['GET'])
@limiter.limit("10 per minute")  # Example rate limit
def get_posts():
    sort_field = request.args.get('sort', default=None)
    sort_direction = request.args.get('direction', default='asc')

    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400
        if sort_direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

        POSTS.sort(key=lambda x: x[sort_field], reverse=(sort_direction == 'desc'))

    return jsonify(POSTS)

# Create a route to add a new post
@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Both 'title' and 'content' are required."}), 400

    new_post = {
        'id': len(POSTS) + 1,  # Simple ID generation based on the length of the current list
        'title': title,
        'content': content
    }
    POSTS.append(new_post)

    return jsonify(new_post), 201

# Create a route to delete a post by ID
@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = next((post for post in POSTS if post['id'] == id), None)

    if not post:
        raise NotFound(f"Post with id {id} not found.")

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."})

# Create a route to update a post by ID
@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    post = next((post for post in POSTS if post['id'] == id), None)

    if not post:
        raise NotFound(f"Post with id {id} not found.")

    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

    return jsonify(post)

# Create a route to search posts
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title', default=None)
    content = request.args.get('content', default=None)

    filtered_posts = POSTS

    if title:
        filtered_posts = [post for post in filtered_posts if title.lower() in post['title'].lower()]
    if content:
        filtered_posts = [post for post in filtered_posts if content.lower() in post['content'].lower()]

    return jsonify(filtered_posts)

# Error Handling: Handle 404 - Not Found errors
@app.errorhandler(NotFound)
def handle_not_found_error(error):
    return jsonify({"error": str(error)}), 404

# Error Handling: Handle 400 - Bad Request errors
@app.errorhandler(BadRequest)
def handle_bad_request_error(error):
    return jsonify({"error": str(error)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the app on port 5001
