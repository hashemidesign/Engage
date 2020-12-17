from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileAllowed, FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime


app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'afsfvskjdfnskjdvhhskhdksndv'
app.config['UPLOADED_PHOTOS_DEST'] = 'images'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

configure_uploads(app, photos)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(50))
    image = db.Column(db.String(100))
    join_date = db.Column(db.DateTime)
    tweets = db.relationship('Tweet', backref='user', lazy='dynamic')


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(140))
    date_created = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired('A full name is required'), Length(max=100, message='Your name can\'t be more than 100 characters')])
    username = StringField('Username', validators=[InputRequired('A username is required'), Length(max=30, message='Your username can\'t be more than 30 characters')])
    password = PasswordField("Password", validators=[InputRequired('A password is required')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Only images are accepted')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('A username is required')])
    password = PasswordField("Password", validators=[InputRequired('A password is required')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class TweetForm(FlaskForm):
    text = TextAreaField('Message', validators=[InputRequired('Message is required')])


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


@app.template_filter('time_since')
def time_since(delta):
    seconds = delta.total_seconds()
    
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return f'{days}d'
    elif hours > 0:
        return f'{hours}h'
    if minutes > 0:
        return f'{minutes}m'
    else:
        return 'Just now'


if __name__ == "__main__":
    manager.run()
