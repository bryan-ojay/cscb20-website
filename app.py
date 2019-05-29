from flask import Flask, session, redirect, url_for, escape, request, render_template
import sqlite3
app=Flask(__name__)
app.secret_key=b'a8c6e4'

@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # sql connect
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        # get sql data where username and password match input
        results = db.execute(
        "select * from users where username=? and password=?",
        (request.form['username'], request.form['password'])).fetchall()
        db.close()
        # check results
        if len(results) == 0: # incorrect username/password
            return render_template('login.html', title='Login',
            msg="Incorrect username or password.")
        else:
            session['username']=results[0][0]
            session['usertype']=results[0][2]
            return redirect(url_for('home'))

    elif 'username' in session:
        return redirect(url_for('home'))

    else:
        return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # sql connect
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        # check if a user already has this name
        results = db.execute(
        "SELECT * from USERS WHERE username=?",
        (request.form['username'],)).fetchall()

        # if a user already has this name, tell the user to try again
        if len(results) != 0:
            db.close()
            return render_template('register.html', title='Register', invalid=True)

        # else add the user to the list of users
        else:
            db.execute(
                """INSERT INTO users
                (username, password, type)
                VALUES (?, ?, ?)""",
                (request.form['username'], request.form['password'], request.form['usertype'])
            )
            # insert new greades row if new user is a student
            if request.form['usertype'] == 'Student':
                db.execute(
                    """INSERT INTO grades
                    (username, a1, a2, a3, q1, q2, q3, q4, midterm, final)
                    VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)""",
                    (request.form['username'],)
                )
            conn.commit()
            db.close()

            msg = "Registration successful."
            return render_template('result.html', result="Success", msg=msg)

    elif 'username' in session:
        return redirect(url_for('home'))

    else:
        return render_template('register.html', title='Register', invalid=False)


@app.route('/grades', methods=['GET', 'POST'])
def grades():
    # Do not respond if not logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # student asking for remark
    elif request.method == 'POST':
        # update remark requests
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        db.execute(
            """INSERT INTO remarks
            (username, assessment, request)
            VALUES (?, ?, ?)""",
            (session['username'], request.form['assessment'], request.form['request'])
        )
        conn.commit()
        db.close()
        msg = "Remark request sent."
        return render_template('result.html', result="Success", msg=msg)
       

    # load student specific grades
    elif session['usertype'] == 'Student':
        conn = sqlite3.connect('assignment3.db')
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute("SELECT * from GRADES WHERE username='{}'".format(session['username']))

        rows = cur.fetchall()
        return render_template('student_grades.html', title='Grades', rows = rows)

        
    # load all student grades
    elif session['usertype'] == 'Instructor':
        conn = sqlite3.connect('assignment3.db')
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute("SELECT * from GRADES order by username")

        rows = cur.fetchall()
        return render_template('instructor_grades.html', title='Grades', rows = rows)


@app.route('/syllabus')
def syllabus():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('syllabus.html', title='Syllabus')


@app.route('/remarks')
def remarks():
    if 'username' not in session:
        return redirect(url_for('login'))

    elif session['usertype'] == 'Student':
        return render_template('base.html', title='Not Found',
            content="You submit a remark request when you view your grades.")

    elif session['usertype'] == 'Instructor':
        conn = sqlite3.connect('assignment3.db')
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute("SELECT * from remarks order by id DESC")

        rows = cur.fetchall()
        return render_template('remarks.html', title='Remarks', rows = rows)


@app.route('/assignments')
def assignments():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('assignments.html', title='Assignments')


@app.route('/lectures')
def lectures():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('lectures.html', title='Lectures')


@app.route('/announcements')
def announcements():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('announcements.html', title='Announcements')


@app.route('/tutorials')
@app.route('/labs')
def tutorials():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('tutorials.html', title='Tutorials')


@app.route('/quizzes')
def quizzes():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('quizzes.html', title='Quizzes')


@app.route('/tests')
def tests():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('tests.html', title='Tests')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    # student inputting feedback to instructor
    elif request.method == 'POST':
        instructor = request.form['instructor']
        teach = request.form['teach']
        teachimp = request.form['teachimp']
        lab = request.form['lab']
        labimp = request.form['labimp']

        with sqlite3.connect("assignment3.db") as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO feedback (directed_to, teach,teachimp,lab,labimp)
                VALUES (?,?,?,?,?)""", (instructor, teach, teachimp, lab, labimp))

            con.commit()
            msg = "Record successfully added."

            return render_template("result.html", msg = msg, result = "Success")
            con.close()

    elif session['usertype'] == 'Student':
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        # get sql data where username and password match input
        results = db.execute(
        "select username from users where type = 'Instructor'").fetchall()
        db.close()
        return render_template('feedback.html', title='Feedback', rows=results)

    elif session['usertype'] == 'Instructor':
        conn = sqlite3.connect('assignment3.db')
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute("SELECT * from feedback WHERE directed_to='{}'".format(session['username']))

        rows = cur.fetchall()
        return render_template('instructor_feedback.html', title='Feedback', rows = rows)


@app.route('/editmark', methods=['GET', 'POST'])
def editmark():
    if 'username' not in session:
        return redirect(url_for('login'))

    elif session['usertype'] != 'Instructor':
        return render_template('base.html', title='Not Found',
                        content="The page you requested is not available.")
    
    elif request.method == 'POST':
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        # get sql data where username and password match input
        results = db.execute(
            """UPDATE grades SET {} = ?
            where username = ?""".format(request.form['assessment']), 
            (request.form['mark'], request.form['student']))
        conn.commit()
        db.close()
        return render_template('result.html', title="Success", msg="Mark edited.")

    else:
        # sql connect
        conn = sqlite3.connect('assignment3.db')
        db = conn.cursor()
        # get sql data where username and password match input
        results = db.execute(
        """select username from users 
           where type='Student'
           order by username""").fetchall()
        db.close()
        return render_template('editmark.html', title='Edit Marks', students=results)


@app.route('/team')
def team():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('team.html', title='Team')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('usertype', None)
    return render_template('base.html', title='Logout',
                           content='You have been logged out.')


@app.route('/<page>')
def not_found(page):
    return render_template('base.html', title='Not Found',
                           content="The page you requested is not available.")


if __name__=="__main__":
    app.run(debug=True, port=5000)
