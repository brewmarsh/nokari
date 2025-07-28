from flask import request, jsonify
from .app import app, db
from .models import User, Resume, CoverLetter
from .serializers import UserSchema, ResumeSchema, CoverLetterSchema

@app.route('/users', methods=['POST'])
def create_user():
    user_schema = UserSchema()
    try:
        data = user_schema.load(request.json)
    except Exception as err:
        return jsonify(err.messages), 400

    user = User(**data)
    db.session.add(user)
    db.session.commit()

    return jsonify(user_schema.dump(user)), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))

@app.route('/resumes', methods=['POST'])
def create_resume():
    resume_schema = ResumeSchema()
    try:
        data = resume_schema.load(request.json)
    except Exception as err:
        return jsonify(err.messages), 400

    resume = Resume(**data)
    db.session.add(resume)
    db.session.commit()

    return jsonify(resume_schema.dump(resume)), 201

@app.route('/resumes/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    resume_schema = ResumeSchema()
    return jsonify(resume_schema.dump(resume))

@app.route('/cover-letters', methods=['POST'])
def create_cover_letter():
    cover_letter_schema = CoverLetterSchema()
    try:
        data = cover_letter_schema.load(request.json)
    except Exception as err:
        return jsonify(err.messages), 400

    cover_letter = CoverLetter(**data)
    db.session.add(cover_letter)
    db.session.commit()

    return jsonify(cover_letter_schema.dump(cover_letter)), 201

@app.route('/cover-letters/<int:cover_letter_id>', methods=['GET'])
def get_cover_letter(cover_letter_id):
    cover_letter = CoverLetter.query.get_or_404(cover_letter_id)
    cover_letter_schema = CoverLetterSchema()
    return jsonify(cover_letter_schema.dump(cover_letter))
