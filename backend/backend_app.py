from flask import Flask, jsonify, request

app = Flask(__name__)

POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if 'title' and 'content' are provided
    if not data.get('title') or not data.get('content'):
        missing_fields = []
        if not data.get('title'):
            missing_fields.append('title')
        if not data.get('content'):
            missing_fields.append('content')

        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Generate a new unique ID (increment the max ID by 1)
    new_id = max(post["id"] for post in POSTS) + 1

    # Create the new post
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    # Add the new post to the POSTS list
    POSTS.append(new_post)

    # Return the newly created post with 201 Created status
    return jsonify(new_post), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
