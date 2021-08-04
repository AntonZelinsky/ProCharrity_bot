import datetime

from sqlalchemy.exc import SQLAlchemyError

from app.database import db_session
from app.models import AdminUser
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from marshmallow import fields, Schema
from app.logger import app_logger as logger


class LoginSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class Login(MethodResource, Resource):
    """
    Authorization of existing users by username and password.
    After authorization, the auth user receives a JWT token.
    This access token should be passed to the header.
    """

    @doc(description='This endpoint provides jwt token for authorized users',
         tags=['User Login'],
         params={
             'email': {
                 'description': 'The registered user\' email address.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'password': {
                 'description': 'User\'s password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             }
         },
         responses={200: {'description': "access_token:'' refresh_token: ''"},
                    403: {'description': "Запрос не может быть пустым.'., "
                                         "Неверный почтовый адрес или пароль., "
                                         "Необходимо указать <email> и <password>."},

                    }
         )
    @use_kwargs(LoginSchema)
    def post(self, **kwargs):
        if not kwargs:
            logger.info('Received an empty request.')
            return make_response(jsonify(message="Запрос не может быть пустым."), 403)

        email = kwargs.get("email").lower()
        password = kwargs.get("password")

        if not email or not password:
            logger.info('The request did not contain a username or password.')
            return make_response(jsonify(message="Необходимо указать <email> и <password>."), 403)

        user = AdminUser.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            logger.info(f'Passed incorrect email or password. Email: {email}.')
            return make_response(jsonify(message="Неверный почтовый адрес или пароль."), 403)

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        user = AdminUser.query.get(user.id)
        user.last_logon = datetime.datetime.now()
        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.exception(str(ex))
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        logger.info(f'The User {email} successfully logged in . Token has been generated.')
        return make_response(jsonify(access_token=access_token,
                                     refresh_token=refresh_token), 200)
