from flask import jsonify, make_response
from app.models import UserAdmin, Register
from app.apis.users import UserOperation
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from datetime import datetime
from app.database import db_session

USER_ADMIN_REGISTRATION_SCHEMA = {
    'token': fields.Str(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'password': fields.Str(),

}


class UserRegister(MethodResource, Resource, UserOperation):
    """Provides api for register a new Admin Users"""

    @doc(description='This endpoint provide registering option for admin users.', tags=['User Registration'])
    @use_kwargs(USER_ADMIN_REGISTRATION_SCHEMA)
    def post(self, **kwargs):
        token = kwargs.get("token")
        password = kwargs.get("password")
        registration_record = Register.query.filter_by(token=token).first()

        if not registration_record:
            return make_response(jsonify(message='The invitation did not found. Please contact site admin.'), 400)

        if registration_record.token_expiration_date < datetime.now():
            return make_response(jsonify(message='The invitation token has expired.'), 400)
        # This key is no longer required.
        del kwargs['token']

        if not password:
            return make_response(jsonify("Registration request requires 'password'."), 400)

        kwargs['email'] = registration_record.email
        kwargs['password'] = generate_password_hash(password)

        if not self.validate_password(password=password):
            return make_response(jsonify(message="The password does not comply with the password policy."), 400)

        # Create a new Admin user
        db_session.add(UserAdmin(**kwargs))
        # delete invitation
        db_session.delete(registration_record)
        db_session.commit()

        return jsonify(message="User registered successfully ")