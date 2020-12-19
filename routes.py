from flask import render_template, flash, redirect, url_for
from app import app, photos, db
from models import User, Tweet
from forms import RegisterForm, LoginForm, TweetForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return 'login failed'
        
        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('profile'))
        return 'login failed'
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/timeline')
def timeline():
    form = TweetForm()
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.date_created.desc()).all()
    current_time = datetime.now()
    return render_template('timeline.html', form=form, tweets=tweets, current_time=current_time)


@app.route('/post_tweet', methods=['POST'])
@login_required
def post_tweet():
    form = TweetForm()
    if form.validate():
        new_tweet = Tweet(user_id=current_user.id, text=form.text.data, date_created=datetime.now())
        db.session.add(new_tweet)
        db.session.commit()
        return redirect(url_for('timeline'))
    return 'new tweet failed'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # upload image
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)
        # add user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, username=form.username.data, password=hashed_password, image=image_url, join_date=datetime.now())
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))
    return render_template('register.html', form=form)