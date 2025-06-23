from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/user/OneDrive/Documents/Pets4Pets/database.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    pets = db.relationship('Pet', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    pet_type = db.Column(db.String(100))
    age = db.Column(db.Integer)
    breed = db.Column(db.String(100))
    details = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followee_id', db.Integer, db.ForeignKey('user.id'))
)

User.following = db.relationship(
    'User', secondary=followers,
    primaryjoin=(followers.c.follower_id == User.id),
    secondaryjoin=(followers.c.followee_id == User.id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
)

class Twitter:
    def __init__(self):
        self.timestamp = 0

    def postTweet(self, userId, tweet):
        self.timestamp += 1
        new_post = Post(content=tweet, timestamp=self.timestamp, user_id=userId)
        db.session.add(new_post)
        db.session.commit()

    def getNewsFeed(self, userId):
        user = User.query.get(userId)
        if not user:
            return []
        followees = user.following.all() + [user]
        posts = Post.query.filter(Post.user_id.in_([u.id for u in followees])).order_by(Post.timestamp.desc()).limit(10).all()
        return [{'username': User.query.get(post.user_id).username, 'content': post.content} for post in posts]


    def follow(self, followerId, followeeId):
        follower = User.query.get(followerId)
        followee = User.query.get(followeeId)
        if followee not in follower.following:
            follower.following.append(followee)
            db.session.commit()

    def unfollow(self, followerId, followeeId):
        follower = User.query.get(followerId)
        followee = User.query.get(followeeId)
        if followee in follower.following:
            follower.following.remove(followee)
            db.session.commit()
        else:
            flash('Cannot unfollow as you are not following this user.', 'warning')

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word.lower():
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end_of_word = True

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return []
            node = node.children[ch]
        
        result = []
        self._dfs(node, prefix.lower(), result)
        return result

    def _dfs(self, node, prefix, result):
        if node.is_end_of_word:
            result.append(prefix)
        for ch in node.children:
            self._dfs(node.children[ch], prefix + ch, result)

trie = Trie()
twitter = Twitter()

@app.before_request
def check_session_user():
    if 'user_id' in session:
        if not User.query.get(session['user_id']):
            session.pop('user_id')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    feed = twitter.getNewsFeed(user_id)
    return render_template('home.html', feed=feed)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_age = int(request.form['pet_age'])
        pet_breed = request.form['pet_breed']
        pet_details = request.form['pet_details']

        if User.query.filter_by(username=username).first():
            return 'Username already exists!'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        new_pet = Pet(name=pet_name, pet_type=pet_type, age=pet_age, breed=pet_breed,
                      details=pet_details, user_id=new_user.id)
        db.session.add(new_pet)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/post', methods=['POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    twitter.postTweet(session['user_id'], content)
    return redirect(url_for('home'))

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix', '')
    suggestions = trie.starts_with(prefix)
    return jsonify(suggestions)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            return render_template('search.html', query=None, results=[])
        matching_pets = Pet.query.filter(Pet.pet_type.ilike(f'%{query}%')).all()
        results = []
        for pet in matching_pets:
            user = User.query.get(pet.user_id)
            is_following = False
            if 'user_id' in session:
                current_user = User.query.get(session['user_id'])
                is_following = user in current_user.following
            results.append({'pet_name': pet.name, 'breed': pet.breed, 'pet_type': pet.pet_type,
                            'owner_id': user.id, 'owner_name': user.username, 'is_following': is_following})
        return render_template('search.html', query=query, results=results)
    return render_template('search.html', query=None, results=[])

@app.route('/follow/<int:user_id>')
def follow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    twitter.follow(session['user_id'], user_id)
    flash('You are now following this user!', 'success')
    return redirect(url_for('search'))

@app.route('/unfollow/<int:user_id>')
def unfollow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    twitter.unfollow(session['user_id'], user_id)
    flash('Unfollowed successfully!', 'info')
    return redirect(url_for('search'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    followers = user.followers.all()
    following = user.following.all()
    return render_template('profile.html', user=user, followers=followers, following=following)

@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_age = int(request.form['pet_age'])
        pet_breed = request.form['pet_breed']
        pet_details = request.form['pet_details']
        
        new_pet = Pet(name=pet_name, pet_type=pet_type, age=pet_age, breed=pet_breed,
                      details=pet_details, user_id=session['user_id'])
        db.session.add(new_pet)
        db.session.commit()
        trie.insert(pet_type)
        flash('New pet added successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('add_pet.html')


@app.route('/api/feed')
def api_feed():
    if 'user_id' not in session:
        return jsonify({'feed': []})
    feed = twitter.getNewsFeed(session['user_id'])
    return jsonify({'feed': feed})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        pet_types = {pet.pet_type for pet in Pet.query.all()}
        for ptype in pet_types:
            trie.insert(ptype)
    app.run(debug=True)


