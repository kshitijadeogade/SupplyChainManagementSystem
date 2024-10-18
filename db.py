from flask_mysqldb import MySQL
from flask import Flask
from config import Config

def init_db(app: Flask):
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB
    mysql = MySQL(app)
    return mysql
