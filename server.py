from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt  
import re	
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe' 

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
ALPHA_ONLY = re.compile(r'^[a-zA-Z]+$')

@app.route('/')
def root():
    return redirect('/users')

@app.route('/users')
def users():
    mysql = connectToMySQL('Users_Flask')	        # call the function, passing in the name of our db
    users = mysql.query_db('SELECT * FROM users;')  # call the query_db function, pass in the query as a string
    return render_template("users.html",users = users)

@app.route('/users/new')
def new_users():
    return render_template('new-user.html')
@app.route('/users/new/email-realtime', methods = ["POST"])
def email_realtime():
    found = False
    mysql = connectToMySQL('Users_Flask') 
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = { 'em': request.form['email'] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    return render_template('partials/email.html',found = found)

@app.route('/users/new/validate', methods = ["POST"])
def validate_new_user():
    #Check to see if it is in a valid email format
    if not EMAIL_REGEX.match(request.form['email']):  
        flash("Please enter a valid email address.","email")
    if not ALPHA_ONLY.match(request.form['first-name']):
        flash("Please enter a valid first name.", "first-name" )
    if not ALPHA_ONLY.match(request.form['last-name']):
        flash("Please enter a valid last name.", "last-name" )
    if '_flashes' in session.keys():
        return redirect("/users/new")
    else:
        #Check to see if the email is avaiable
        query = "SELECT * FROM users WHERE email = %(em)s"
        data = {'em': request.form['email']}
        mysql = connectToMySQL('Users_Flask')
        user = mysql.query_db(query,data)

        if len(user) >= 1:
            flash("Email already in use, please try another.",'email')
            return redirect("/users/new")
        #If email not in use then add it to the database
        else:
            query = "INSERT INTO users (first_name,last_name,email,created_at,updated_at) VALUES (%(fn)s,%(ln)s,%(em)s,NOW(),NOW());"
            data = {'fn': request.form['first-name'],
                    'ln': request.form['last-name'],
                    'em': request.form['email']}

            mysql = connectToMySQL('Users_Flask')
            id = mysql.query_db(query,data)
            return redirect(f"/users/{id}")

@app.route('/users/<id>')
def view_user(id):
    mysql = connectToMySQL("Users_Flask")
    query = "SELECT * FROM users WHERE id = %(id)s;"
    data = { "id" : id }
    user = mysql.query_db(query,data)

    return render_template('view-user.html',user = user[0])

@app.route('/users/<id>/edit')
def edit_user(id):
    mysql = connectToMySQL("Users_Flask")
    query = "SELECT * FROM users WHERE id = %(id)s;"
    data = { "id" : id }
    user = mysql.query_db(query,data)
    return render_template('edit-user.html',user = user[0])

@app.route('/users/<id>/edit/validate',methods = ["POST"])
def validate_edit_user(id):
    #Check to see if it is in a valid email format
    if not EMAIL_REGEX.match(request.form['email']):  
        flash("Please enter a valid email address.","email")
    if not ALPHA_ONLY.match(request.form['first-name']):
        flash("Please a valid first name.", "first-name" )
    if not ALPHA_ONLY.match(request.form['last-name']):
        flash("Please a valid last name.", "last-name" )
    if '_flashes' in session.keys():
        return redirect(f"/users/{id}/edit")
    else:
        #Check to see if the email is avaiable
        query = "SELECT * FROM users WHERE email = %(em)s AND id != %(id)s"
        data = {'em': request.form['email'],'id':id}
        mysql = connectToMySQL('Users_Flask')
        user = mysql.query_db(query,data)

        if len(user) >= 1:
            flash("Email already in use, please try another.",'email')
            return redirect(f"/users/{id}/edit")
        #If email not in use then add it to the database
        else:
            query = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(em)s, updated_at = NOW() WHERE id = %(id)s ;"
            data = {'fn': request.form['first-name'],
                    'ln': request.form['last-name'],
                    'em': request.form['email'],
                    'id': id}

            mysql = connectToMySQL('Users_Flask')
            mysql.query_db(query,data)
            return redirect(f"/users/{id}")

@app.route('/users/<id>/delete')
def delete_user(id):
    query = "DELETE FROM users WHERE id = %(id)s"
    data = {'id':id}
    mysql = connectToMySQL('Users_Flask')
    mysql.query_db(query,data)
    return redirect('/users')

if __name__ == "__main__":
    app.run(port=5005,debug=True) 
