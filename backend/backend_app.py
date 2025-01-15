from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Flask Tutorial", "content": "Learn Flask by building a blog."},
    {"id": 4, "title": "Blogging 101", "content": "Everything you need to know about blogging."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Get query parameters for sorting
    sort_by = request.args.get('sort', '')
    direction = request.args.get('direction', '')

    # Validate 'sort' and 'direction' parameters
    if sort_by and sort_by not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400

    if direction and direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

    # If sorting parameters are provided, apply sorting
    if sort_by:
        POSTS.sort(key=lambda post: post[sort_by].lower(), reverse=(direction == 'desc'))

    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Ensure title and content are provided
    if not data.get('title') or not data.get('content'):
        missing_fields = []
        if not data.get('title'):
            missing_fields.append('title')
        if not data.get('content'):
            missing_fields.append('content')

        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Generate a new unique ID (increment the max ID by 1)
    new_id = max(post["id"] for post in POSTS) + 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post by id
    post = next((post for post in POSTS if post["id"] == id), None)

    if post:
        POSTS.remove(post)
        return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200
    else:
        return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post by id
    post = next((post for post in POSTS if post["id"] == id), None)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Get the updated title and content from the request body
    data = request.get_json()

    # Update the fields if they are provided
    if "title" in data:
        post["title"] = data["title"]
    if "content" in data:
        post["content"] = data["content"]

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts based on title and content queries
    filtered_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower()) or (content_query in post["content"].lower())
    ]

    return jsonify(filtered_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
