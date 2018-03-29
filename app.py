"""
This script runs the newproj application using a development server.
"""

from os import environ
from newproj import app 


if __name__ == '__main__':
    #HOST = environ.get('SERVER_HOST', 'localhost')
    HOST='0.0.0.0'
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.secret_key = 'mysecret'
    app.run(HOST,PORT)
