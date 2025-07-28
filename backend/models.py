from .app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)
    default_resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=True)
    default_cover_letter_id = db.Column(db.Integer, db.ForeignKey('cover_letter.id'), nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('resumes', lazy=True))

    def __repr__(self):
        return f'<Resume {self.name}>'

class CoverLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('cover_letters', lazy=True))

    def __repr__(self):
        return f'<CoverLetter {self.name}>'
