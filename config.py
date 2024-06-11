import os 

class Config:
    
    SECRET_KEY = os.urandom(24)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'todo_app'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
   
    GOOGLE_CLIENT_ID = '31694232043-8esavc73ivqhipmu8skief95cvfdd6e9.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'

    """ MAIL_USERNAME = 'edcorgris@gmail.com'  # Agrega tu email
    MAIL_PASSWORD = 'your_email_password'  # Agrega la contraseña de tu email """