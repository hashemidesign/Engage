from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileAllowed, FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'afsfvskjdfnskjdvhhskhdksndv'
app.config['UPLOADED_PHOTOS_DEST'] = 'images'

login_manager = LoginManager(app)
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


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


@app.route('/login', methods=['POST'])
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



@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/timeline')
def timeline():
    return render_template('timeline.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # upload image
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)
        # add user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, username=form.username.data, password=hashed_password, image=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))
    return render_template('register.html', form=form)


if __name__ == "__main__":
    manager.run()
