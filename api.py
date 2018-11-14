# Heavily inspired by Pretty Printed. http://www.prettyprinted.com

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
db = SQLAlchemy(app)


# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(100))
    user_id = db.Column(db.Integer)


# middleware
def token_required(function_that_gets_decorated):
    @wraps(function_that_gets_decorated)
    def decorated(*args, **kwargs):
        token = None

        if 'access-token' in request.headers:
            token = request.headers['access-token']

        if not token:
            return jsonify({'message' : 'Token is missing.'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message' : 'Token is invalid.'}), 401

        return function_that_gets_decorated(current_user, *args, **kwargs)

    return decorated


# Users routes


# Start here by creating user.
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(name=data['name'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f'New user created: {new_user.name}.'})


# Log in with newly created user credentials as JSON and get a JWT token back.
@app.route('/users/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify. No authorization header provided.', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify. No user found.', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')}) # returns token

    return make_response(f'Could not verify, Wrong password for {user.name}', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


# See all current users.
@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users': output})


# See a specific user.
@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found.'})

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    return jsonify({'user': user_data})


# Edit a particular user.
@app.route('/users/<id>', methods=['PUT'])
@token_required
def promote_user(current_user, id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found with that id.'})

    db.session.commit()
    return jsonify({'message': f'User {user.name} has been modified.'})


# Delete a particular user.
@app.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'No user found.'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user.name} has been deleted.'})


# Posts routes


# Get all posts corresponding to current user
@app.route('/myposts', methods=['GET'])
@token_required
def get_all_myposts(current_user):
    posts = Post.query.filter_by(user_id=current_user.id).all()
    output = []

    for post in posts:
        post_data = {}
        post_data['id'] = post.id
        post_data['title'] = post.title
        post_data['content'] = post.content
        post_data['user_id'] = post.user_id
        output.append(post_data)

    return jsonify({'posts': output})


# Get all posts from all users.
@app.route('/allposts', methods=['GET'])
@token_required
def get_all_posts(current_user):
    posts = Post.query.all()
    output = []

    for post in posts:
        post_data = {}
        post_data['id'] = post.id
        post_data['title'] = post.title
        post_data['content'] = post.content
        post_data['user_id'] = post.user_id
        output.append(post_data)

    return jsonify({'posts': output})


# Get a specific post
@app.route('/myposts/<post_id>', methods=['GET'])
@token_required
def get_one_post(current_user, post_id):
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()

    if not post:
        return jsonify({'message': f'No post found. (Logged in as {current_user.name}).'})

    post_data = {}
    post_data['id'] = post.id
    post_data['text'] = post.text
    post_data['complete'] = post.complete
    return jsonify(post_data)


# Create a new post as a current user.
@app.route('/myposts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    new_post = Post(title=data['title'], content=data['content'], user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': "Post successfully created."})


# Update a post as a current user.
@app.route('/myposts/<id>', methods=['PUT'])
@token_required
def update_post(current_user, id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first()

    if not post:
        return jsonify({'message': 'No post found.'})

    post.complete = True
    db.session.commit()
    return jsonify({'message': 'Post has been updated.'})


# Delete a specific post that you are the owner of.
@app.route('/myposts/<id>', methods=['DELETE'])
@token_required
def delete_post(current_user, id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first()

    if not post:
        return jsonify({'message': 'No post found.'})

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted!'})


if __name__ == '__main__':
    # Create the database at startup.
    db.create_all()
    app.run(debug=True)
