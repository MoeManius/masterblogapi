from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
