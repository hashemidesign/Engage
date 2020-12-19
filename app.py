from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager


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

configure_uploads(app, photos)





@app.template_filter('time_since')
def time_since(delta):
    seconds = delta.total_seconds()
    
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return f'{int(days)}d'
    elif hours > 0:
        return f'{int(hours)}h'
    if minutes > 0:
        return f'{int(minutes)}m'
    else:
        return 'Just now'


from routes import *


manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
