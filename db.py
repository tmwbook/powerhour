from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    requests = db.relationship('PlaylistRequest', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.id}: {self.spotify_id}>'


class PlaylistRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    playlist_id = db.Column(db.Text, nullable=False)
    # This is server local time, logic will be done in timedeltas
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<PlaylistRequest {self.id}: {self.playlist_id} from {self.user}>'
