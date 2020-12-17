from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileAllowed, FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'afsfvskjdfnskjdvhhskhdksndv'
app.config['UPLOADED_PHOTOS_DEST'] = 'images'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
configure_uploads(app, photos)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(50))
    image = db.Column(db.String(100))


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired('A full name is required'), Length(max=100, message='Your name can\'t be more than 100 characters')])
    username = StringField('Username', validators=[InputRequired('A username is required'), Length(max=30, message='Your username can\'t be more than 30 characters')])
    password = PasswordField("Password", validators=[InputRequired('A password is required')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Only images are accepted')])
    submit = SubmitField('Register')


@app.route('/')
def index():
    return render_template('index.html')


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
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)

        return f'<h1>name: {form.name.data}, username: {form.username.data}, password: {form.password.data}, image_url: {image_url}'
    return render_template('register.html', form=form)


if __name__ == "__main__":
    manager.run()
