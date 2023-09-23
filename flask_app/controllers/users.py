from flask_app import app
from flask import render_template, redirect, request, session, url_for, flash
from flask_app.models import user, recipe # import entire file, rather than class, to avoid circular imports
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
# As you add model files add them the the import above
# This file is the second stop in Flask's thought process, here it looks for a route that matches the request

# Create Users Controller

@app.route('/users/register', methods=["POST"])
def create_user():
    if request.form["which_form"] == "register":
        if not user.User.register_user(request.form):
            return render_template("login_and_registration.html", first_name=request.form["first_name"], last_name=request.form["last_name"], registration_email=request.form["email"] )

    return redirect("/recipes") 

# Can also combine GET and POST under one name (for rendering template vs getting form information) for example:
# @app.route('/books/create', methods=['POST', 'GET'])
# def create_book():
# if 'user_id' not in session: return redirect('/')
# if request.method == 'GET':
#   return render_template('create_book.html')
# if request.method == 'POST':
#   if book.Book.create_book(request.form):
#       return redirect('/users/main')
#   return redirect('/books/create')

# Read Users Controller

@app.route('/')
def index():
    return render_template("login_and_registration.html")

# @app.route('/users/dashboard')
# def show_dashboard():
#     if "logged_in" in session:
#         if session['logged_in']:
#             return render_template("all_recipes_dashboard.html", user=user.User.get_user_by_id(session['user_id']))
#     else:
#         return redirect("/users/logout")


# @app.route('/users/show/<int:user_id>')
# def show_one_user(user_id): 
#     one_user = user.User.get_user_by_id(user_id)
#     return render_template("read_one.html", one_user=one_user)

# @app.route('/users/show_form')
# def show_create_user_form():
#     return render_template("create.html")

# @app.route('/users/<int:id>/edit')
# def show_update_user_form(id):
#     one_user = user.User.get_user_by_id(id)
#     return render_template("update.html", one_user=one_user )  


# preface route names with the file you are in e.g., @app.rout('/users/create) because you may have several controllers # and you want to have a way to make a distinction

# BE CAREFUL not to overwrite imported models in line 3 by using the model name as a variable name in your methods

# Update Users Controller

# @app.route('/users/<int:id>/update_user', methods=['POST'])
# def update_user(id):

#     data = {
#         "id" : id,
#         "first_name": request.form["first_name"],
#         "last_name": request.form["last_name"],
#         "email": request.form["email"]
#     }
#     user.User.update_user(data)
    
#     # return redirect('/users/show/{{id}}')
#     return redirect(url_for('show_one_user', user_id=id))  #obtained from https://code-maven.com/slides/python/flask-internal-redirect-parameters


# Delete Users Controller

# @app.route('/users/delete/<int:id>')
# def delete(id):
#     user.User.delete(id)
#     return redirect('/users')

# Login and Logout

@app.route('/users/logout')
def logout():
    #session.pop("user_id")
    session.clear()  
    return redirect("/")

@app.route('/users/login', methods=['POST'])
def login():

    if not user.User.login_user(request.form):
        return render_template("login_and_registration.html", login_email=request.form["email"])
    return redirect('/recipes')
    
# Notes:
# 1 - Use meaningful names
# 2 - Do not overwrite function names
# 3 - No matchy, no worky
# 4 - Use consistent naming conventions 
# 5 - Keep it clean
# 6 - Test every little line before progressing
# 7 - READ ERROR MESSAGES!!!!!!
# 8 - Error messages are found in the browser and terminal




# How to use path variables:
# @app.route('/<int:id>')                                   The variable must be in the path within angle brackets
# def index(id):                                            It must also be passed into the function as an argument/parameter
#     user_info = user.User.get_user_by_id(id)              The it will be able to be used within the function for that route
#     return render_template('index.html', user_info)

# Converter -	Description
# string -	Accepts any text without a slash (the default).
# int -	Accepts integers.
# float -	Like int but for floating point values.
# path 	-Like string but accepts slashes.

# Render template is a function that takes in a template name in the form of a string, then any number of named arguments containing data to pass to that template where it will be integrated via the use of jinja
# Redirect redirects from one route to another, this should always be done following a form submission. Don't render on a form submission.