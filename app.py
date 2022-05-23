# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
import re
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'kensyu'
app.permanent_session_lifetime = timedelta(minutes=3)


def get_connection():
    DB_USER = 'postgres'
    DB_PASS = 'Ab1234'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'postgres'
    db = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    return psycopg2.connect(db)


@app.get('/')
def index():
    return render_template('login.html')


@app.post('/login')
def login():
    """
    ログイン確認
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # メールアドレスとパスワード
            form = request.form
            sql = """
            SELECT
                mail
                ,password
                ,lock_flag
            FROM
                users
            WHERE
                mail = %s
            """
            data = [
                form['email-address']
            ]
            cur.execute(sql, data)
            login_data = cur.fetchone()
            print(login_data)
            # 未入力の場合,登録されていないデータを入力された場合の処理
            is_invalid = False
            if form['email-address'] == "":
                is_invalid = True
                flash('メールアドレスを入力してください', 'ng_email')
            if form['password'] == "":
                is_invalid = True
                flash('パスワードを入力してください', 'ng_password')
            if login_data is None:
                is_invalid = True
                flash('登録されているメールアドレスを入力してください', 'ng_email')
            else:
                if login_data['lock_flag'] == '2' or login_data['lock_flag'] == '3':
                    is_invalid = True
                    flash('アカウントがロックされました', 'ng_password')
                if not check_password_hash(
                    login_data['password'],
                    form['password']
                ):
                    is_invalid = True
                    if login_data['lock_flag'] != '3':
                        login_data['lock_flag'] = str(
                            int(login_data['lock_flag']) + 1)
                        sql = """
                        UPDATE
                            users
                        SET
                            lock_flag = %s
                        WHERE
                            mail = %s
                        """
                        data = [
                            login_data['lock_flag'],
                            form['email-address']
                        ]
                        cur.execute(sql, data)
                    flash('正しいパスワードを入力してください', 'ng_password')
            if is_invalid:

                return redirect('/')
            # ssesionに情報を格納する
            session['email'] = form['email-address']
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.get('/dashboard')
def dashboard():
    # セッション
    if 'email' not in session:
        return redirect('/')
    return render_template('dashboard.html')


@app.get('/create')
def create():
    """
    作成画面
    """
    if 'email' not in session:
        return redirect('/')
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql = """
            SELECT
                ken_code
                ,ken_name
            FROM
                todoufuken
            """
            cur.execute(sql)
            todoufuken_list = cur.fetchall()
            print(todoufuken_list)
            sql = """
            SELECT
                shikaku_code
                ,shikaku_name
            FROM
                shikaku
            """
            cur.execute(sql)
            shikaku_list = cur.fetchall()
    return render_template(
        'create.html',
        todoufuken_list=todoufuken_list,
        shikaku_list=shikaku_list
    )


@app.route('/delete/<user_id>')
def delete(user_id):
    """
    ユーザー削除
    """
    if 'email' not in session:
        return redirect('/')
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql = """
            UPDATE
                users
            SET
                status = '9'
            WHERE
                user_id = %s
            """
            cur.execute(sql, [user_id])
            conn.commit()
    return redirect('/userlist')


@app.get('/detail/<user_id>')
def detail(user_id):
    """
    ユーザー詳細
    """
    if 'email' not in session:
        return redirect('/')
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # user,user_info,todoufukenテーブル
            sql = """
            SELECT
                u.user_id
                ,u.name
                ,u.mail
                ,u.password
                ,ui.jyusyo
                ,ui.tel
                ,ui.gender
                ,ui.yubin
                ,t.ken_name
            FROM
                users AS u
                JOIN user_info AS ui
                    ON u.user_id = ui.user_id
                JOIN todoufuken AS t
                    ON ui.ken_code = t.ken_code
            WHERE u.user_id = %s
            """
            cur.execute(sql, [user_id])
            user = cur.fetchone()
            print(user)
            print(user_id)
            if user['gender'] == '0':
                user['gender'] = '男性'
            else:
                user['gender'] = '女性'

            sql = """
            SELECT
                u.user_id
                ,s.shikaku_name
                ,s.shikaku_code
            FROM
                user_shikaku AS u
                JOIN shikaku AS s
                    ON u.shikaku_code = s.shikaku_code
            WHERE u.user_id = %s
            """
            cur.execute(sql, [user_id])
            shikaku_list = cur.fetchall()
            shikaku_name = ""
            for shikaku in shikaku_list:
                shikaku_name += f" {shikaku['shikaku_name']}"

    # データベースからユーザーID
    return render_template(
        'detail.html',
        user=user,
        shikaku_name=shikaku_name
    )


@app.get('/useredit/<user_id>')
def useredit(user_id):
    """
    ユーザー編集
    """
    if 'email' not in session:
        return redirect('/')
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # user,user_info,todoufukenテーブル
            sql = """
            SELECT
                u.user_id
                ,u.name
                ,u.mail
                ,u.password
                ,ui.jyusyo
                ,ui.tel
                ,ui.gender
                ,ui.yubin
                ,t.ken_name
            FROM
                users AS u
                JOIN user_info AS ui
                    ON u.user_id = ui.user_id
                JOIN todoufuken AS t
                    ON ui.ken_code = t.ken_code
            WHERE u.user_id = %s
            """
            cur.execute(sql, [user_id])
            user = cur.fetchone()
            print(user)
            if user['gender'] == '0':
                user['gender'] = '男性'
            else:
                user['gender'] = '女性'
            # shikaku_code_list
            # [for shikaku_code in detail_list['shikaku_code']]
            sql = """
            SELECT
                shikaku_code
            FROM
                user_shikaku
            WHERE
                user_id = %s
            """
            cur.execute(sql, [user_id])
            shikaku_data = cur.fetchall()

            shikaku_code_list = []
            for shikaku_code_number in shikaku_data:
                shikaku_code_list.append(shikaku_code_number['shikaku_code'])
            print(shikaku_code_list)
            sql = """
            SELECT
                shikaku_code
                ,shikaku_name
            FROM
                shikaku
            """
            cur.execute(sql)
            shikaku_list = cur.fetchall()

            sql = """
            SELECT
                ken_name
                ,ken_code
            FROM
                todoufuken
            """
            cur.execute(sql)
            todoufuken_list = cur.fetchall()

    return render_template(
        'useredit.html',
        user=user,
        shikaku_list=shikaku_list,
        shikaku_code_list=shikaku_code_list,
        todoufuken_list=todoufuken_list
    )


@app.post('/update/<user_id>')
def update(user_id):
    """
    アップデート
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            shikaku_list = request.form.getlist("shikaku")
            form = request.form
            # バリデーション
            name = r'^.{1,100}$'
            password = r'^([a-zA-Z0-9]{1,200})$'
            mail = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
            post = r'^\d{3}-\d{4}$'
            sql = """
            SELECT
                mail
                ,password
            FROM
                users
            WHERE
                mail = %s
            """
            data = [
                form['email-address']
            ]
            cur.execute(sql, data)
            user_data = cur.fetchone()
            is_invalid = False
            if re.match(name, form['first-name']) is None:
                is_invalid = True
                flash('名前を入力してください', 'ng_name')
            if 'gender' not in form:
                is_invalid = True
                flash('性別を選択してください', 'ng_gender')
            if re.match(password, form['password']) is None:
                is_invalid = True
                flash('パスワードを入力してください', 'ng_password')
            if re.match(mail, form['email-address']) is None:
                is_invalid = True
                flash('メールアドレスを入力してください', 'ng_email')
            if user_data is not None:
                is_invalid = True
                flash('このメールアドレスは登録されています', 'ng_email')
            if re.match(post, form['post-code']) is None:
                is_invalid = True
                flash('郵便番号を入力してください', 'ng_post')
            if re.match(name, form['address']) is None:
                is_invalid = True
                flash('住所を入力してください', 'ng_address')
            if form['pref_name'] == "0":
                is_invalid = True
                flash('都道府県を選択してください', 'ng_todoufuken')
            if is_invalid:

                return redirect(f'/useredit/{user_id}')
            # 名前,メール,パスワード
            sql = """
            UPDATE
                users
            SET
                name = %s
                ,mail = %s
                ,password = %s
            WHERE
                user_id = %s
            """
            data = [
                form['first-name'],
                form['email-address'],
                generate_password_hash(form['password']),
                user_id
            ]
            cur.execute(sql, data)
            # 住所,郵便番号,性別,都道府県
            sql = """
            UPDATE
                user_info
            SET
                jyusyo = %s
                ,gender = %s
                ,yubin = %s
                ,ken_code = %s
            WHERE
               user_id = %s
            """
            data = [
                form['address'],
                form['gender'],
                form['post-code'],
                form['pref_name'],
                user_id
            ]
            print(form['pref_name'])
            cur.execute(sql, data)

            sql = """
            DELETE
            FROM
                user_shikaku
            WHERE
                user_id = %s
            """
            cur.execute(sql, [user_id])

            sql = """
            INSERT
            INTO
                user_shikaku (
                user_id,
                shikaku_code
            )
            VALUES (
                %s
                ,%s
            )
            """
            for i in range(len(shikaku_list)):
                cur.execute(sql, [user_id, shikaku_list[i]])
            conn.commit()

    return redirect('/userlist')


@app.get('/userlist')
def userlist():
    """
    ユーザー一覧
    """
    if 'email' not in session:
        return redirect('/')
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql = """
            SELECT
                u.user_id
                , u.name
            FROM
                users AS u
            WHERE
                u.status = '0'
            """
            cur.execute(sql)
            user_list = cur.fetchall()

            sql = """
            SELECT
                us.user_id
                , s.shikaku_code
                , s.shikaku_name
            FROM
                user_shikaku AS us
            JOIN shikaku AS s
                ON us.shikaku_code = s.shikaku_code
            """
            cur.execute(sql)
            shikaku_list = cur.fetchall()
            shikaku_user_dict = {}
            for shikaku in shikaku_list:
                if shikaku['user_id'] in shikaku_user_dict:
                    shikaku_user_dict[shikaku['user_id']
                                      ] += f" {shikaku['shikaku_name']}"
                else:
                    shikaku_user_dict[shikaku['user_id']
                                      ] = shikaku['shikaku_name']

    return render_template(
        'userlist.html',
        user_list=user_list,
        shikaku_user_dict=shikaku_user_dict
    )


@app.post('/regist')
def regist():
    """
    登録処理
    """
    with get_connection() as conn:
        with conn.cursor() as cur:

            shikaku_list = request.form.getlist("shikaku")
            print(shikaku_list)
            # shikaku_list = ['1','2']
            form = request.form
            sql = """
            SELECT
                mail
                ,password
            FROM
                users
            WHERE
                mail = %s
            """
            data = [
                form['email-address']
            ]
            cur.execute(sql, data)
            user_data = cur.fetchone()
            print(user_data)
            # バリデーション varcharの値
            # 名前,100文字以下
            # アドレス@マークの前に文字列とドメインが必須,
            # パスワード,半角英数字の100文字以下
            # 郵便番号 3-4文字以下
            # 住所 100文字以下
            name = r'^.{1,100}$'
            password = r'^([a-zA-Z0-9]{1,200})$'
            mail = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
            post = r'^\d{3}-\d{4}$'
            is_invalid = False
            # flaskのシークレットキーを追加
            # 未入力や値が間違ってた場合に訂正文を表示
            if re.match(name, form['first-name']) is None:
                is_invalid = True
                flash('名前を入力してください', 'ng_name')
            if 'gender' not in form:
                is_invalid = True
                flash('性別を選択してください', 'ng_gender')
            if re.match(password, form['password']) is None:
                is_invalid = True
                flash('パスワードを入力してください', 'ng_password')
            if re.match(mail, form['email-address']) is None:
                is_invalid = True
                flash('メールアドレスを入力してください', 'ng_email')
            if user_data is not None:
                is_invalid = True
                flash('このメールアドレスは登録されています', 'ng_email')
            if re.match(post, form['post-code']) is None:
                is_invalid = True
                flash('郵便番号を入力してください', 'ng_post')
            if re.match(name, form['address']) is None:
                is_invalid = True
                flash('住所を入力してください', 'ng_address')
            if form['pref_name'] == "0":
                is_invalid = True
                flash('都道府県を選択してください', 'ng_todoufuken')
            if is_invalid:

                return redirect('/create')

            print(form)
            sql = "SELECT nextval('seq_user')"
            cur.execute(sql)
            user_id = cur.fetchone()[0]
            print(user_id)
            # user_id ='1'
            sql = """
            INSERT
            INTO users (
                user_id,
                name,
                mail,
                password,
                lock_flag,
                status
            )
            values (
                %s
                ,%s
                ,%s
                ,%s
                ,'0'
                ,'0'
            )
            """

            data = [
                user_id,
                form['first-name'],
                form['email-address'],
                generate_password_hash(form['password'])
            ]
            cur.execute(sql, data)
            sql = """
            INSERT
            INTO user_shikaku(
                user_id
                ,shikaku_code
            )
            values (
                %s
                ,%s
            )
            """
            for i in range(len(shikaku_list)):
                print(shikaku_list[i])
                cur.execute(sql, [user_id, shikaku_list[i]])
            sql = """
            INSERT
            INTO user_info(
                user_id
                , gender
                , yubin
                , ken_code
                , jyusyo
                , status
                )
            values (
                %s
                ,%s
                ,%s
                ,%s
                ,%s
                ,'0'
            )
            """

            cur.execute(
                sql, [
                    user_id,
                    form['gender'],
                    form['post-code'],
                    form['pref_name'],
                    form['address']
                ])
            conn.commit()
    return redirect("/userlist")


if __name__ == '__main__':
    app.run(debug=True)
