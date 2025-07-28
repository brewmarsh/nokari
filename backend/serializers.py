from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)
    default_resume_id = fields.Int()
    default_cover_letter_id = fields.Int()

class ResumeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    file = fields.Str(required=True)
    user_id = fields.Int(required=True)

class CoverLetterSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    file = fields.Str(required=True)
    user_id = fields.Int(required=True)
