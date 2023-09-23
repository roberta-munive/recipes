from flask_app import app
from flask import render_template, redirect, request, session, url_for, flash
from flask_app.models import user, recipe # import entire file, rather than class, to avoid circular imports
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
# As you add model files add them the the import above
# This file is the second stop in Flask's thought process, here it looks for a route that matches the request

# Create Recipes Controller

@app.route('/recipes/create_recipe', methods=["POST"])
def add_recipe():
    if "user_id" not in session:
        return redirect("/")
    if request.form["which_form"] == "create_recipe":
        one_recipe = recipe.Recipe.create_recipe(request.form)
        if not one_recipe:
            return render_template("add_recipe.html", name=request.form["name"], description=request.form["description"], instructions=request.form["instructions"] )
        # add all recipes and return in redirect

    return redirect("/recipes/get_all")

# Read Recipes Controller


@app.route('/recipes')
def show_dashboard():
    if "logged_in" in session:
        if session['logged_in']:
            return render_template("all_recipes_dashboard.html", user=user.User.get_user_by_id(session['user_id']), all_recipes=recipe.Recipe.get_all_recipes_and_users())
    return redirect("/users/logout")

@app.route('/recipes/new')
def show_create_recipe_form():
    if "user_id" not in session:
        return redirect("/")
    return render_template("add_recipe.html")

@app.route('/recipes/get_all')
def get_all_recipes_with_users():
    all_recipes=recipe.Recipe.get_all_recipes_and_users()
    return render_template("all_recipes_dashboard.html", all_recipes=all_recipes) 

@app.route('/recipes/<int:recipe_id>')
def show_one_recipe(recipe_id): 
    if "logged_in" in session:
        if session['logged_in']:
            one_recipe = recipe.Recipe.get_recipe_by_id_with_user(recipe_id)
            return render_template("view_recipe.html", one_recipe=one_recipe)
    return redirect("/users/logout")

# Update Recipes Controller

@app.route('/recipes/edit/<int:recipe_id>')
def show_update_recipe_form(recipe_id):
    if "logged_in" in session:
        if session['logged_in']:
            one_recipe = recipe.Recipe.get_recipe_by_id(recipe_id)
            return render_template("edit_recipe.html", one_recipe=one_recipe )  
    return redirect("/users/logout")    

@app.route('/recipes/update/<int:recipe_id>', methods=['POST'])
def update_recipe(recipe_id):

    if "user_id" not in session:
        return redirect("/")
    
    if request.form["which_form"] == "edit_recipe":
        one_recipe = recipe.Recipe.update_recipe(request.form)
        if not one_recipe:
            path = f"/recipes/edit/{recipe_id}"
            return redirect(path)
    return redirect('/recipes/get_all')

# Delete Users Controller

@app.route('/recipes/delete/<int:id>')
def delete_recipe(id):
    if "user_id" not in session:
        return redirect("/")
    recipe.Recipe.delete_recipe(id)
    return redirect('/recipes/get_all')