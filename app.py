# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('login.html')

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/create')
def create():
    conn = get_connection() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT ken_code,ken_name FROM todoufuken')
    todoufuken_list = cur.fetchall()
    print(todoufuken_list)
    sql = 'SELECT shikaku_code,shikaku_name FROM shikaku'
    cur.execute(sql)
    shikaku_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('create.html',todoufuken_list=todoufuken_list,shikaku_list=shikaku_list)

@app.route('/detail')
def detail():
	return render_template('detail.html')

@app.route('/useredit')
def useredit():
	return render_template('useredit.html')

@app.route('/userlist')
def userlist():
	return render_template('userlist.html')
def get_connection(): 
    DB_USER = 'postgres'
    DB_PASS = 'Ab1234'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'postgres'
    return psycopg2.connect(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

@app.post('/regist')
def regist():
    form = request.form
    print(form['first-name'],form[''])
    reg = "INSERT  INTO  users (user_id, name, mail, password) values('1',form['first-name'],form['email],form['password'] )"
    cur.execute(reg)
    regist_list = cur.fetchall()
    cur.close()
    conn.close()


if __name__ == '__main__':
	app.run()