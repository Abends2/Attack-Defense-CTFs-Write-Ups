import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    POSTGRES_CONNECT = os.environ.get('POSTGRES_CONNECT') or 'lol'
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
