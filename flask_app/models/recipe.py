
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_app.models import user
import re, datetime
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
# The above is used when we do login registration, flask-bcrypt should already be in your env check the pipfile

# Remember 'fat models, skinny controllers' more logic should go in here rather than in your controller. Your controller should be able to just call a function from the model for what it needs, ideally.

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Recipe:
    db = "recipes_schema" #which database are you using for this project
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_cooked = data['date_cooked']
        self.is_under_thirty_minutes = data['is_under_thirty_minutes']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']  
        self.chef = None
        
    # Create Recipes Models

    # class method to save our recipe to the database
    @classmethod
    def create_recipe(cls, recipe_data):
        if not cls.validate_recipe(recipe_data):
            return False
        
        recipe_data = recipe_data.copy()

        query = """
                INSERT INTO recipes (name, description, instructions, date_cooked, is_under_thirty_minutes, user_id) 
                VALUES (%(name)s, %(description)s, %(instructions)s, %(date_cooked)s, %(is_under_thirty_minutes)s, %(user_id)s);
        """

        recipe_id = connectToMySQL(cls.db).query_db(query, recipe_data)

        return recipe_id


    # Read Users Models

    @classmethod
    def get_all_recipes(cls):
        query = "SELECT * FROM recipes;"
        # make sure to call the connectToMySQL function with the schema you are targeting.
        results = connectToMySQL(cls.db).query_db(query)
        # Create an empty list to append our instances of recipes
        all_recipes = []
        # Iterate over the db results and create instances of users with cls.
        for one_recipe in results:
            all_recipes.append(cls(one_recipe))
        return all_recipes
    
    @classmethod
    def get_all_recipes_and_users(cls):
        query = """
                SELECT * FROM recipes
                LEFT JOIN users
                ON recipes.user_id = users.id;
                """
        results = connectToMySQL(cls.db).query_db(query)
        all_recipes_with_users = []
        for result in results:
            this_recipe = cls(result)
            this_recipe.chef = user.User({
                'id' : result['users.id'],
                'first_name' : result['first_name'],
                'last_name' : result['last_name'],
                'email' : result['email'],
                'password' : result['password'],
                'created_at' : result['users.created_at'],
                'updated_at' : result['users.updated_at']
            })
            all_recipes_with_users.append(this_recipe)
        return all_recipes_with_users


    # the get_user_by_email method will be used when we need to retrieve just one specific row of the table
    # @classmethod
    # def get_user_by_email(cls, email):
    #     query = """
    #             SELECT * FROM users
    #             WHERE email = %(email)s;
    #     """
    #     data = {'email': email}
    #     result = connectToMySQL(cls.db).query_db(query, data)  # a list with one dictionary in it
    #     if len(result) < 1:     # no matching user
    #         return False
    #     one_user = cls(result[0])
    #     return one_user # returns user object

    # the get_user_by_id method will be used when we need to retrieve just one specific row of the table
    @classmethod
    def get_recipe_by_id(cls, id):
        query = """
                SELECT * FROM recipes
                WHERE id = %(id)s;
        """
        data = {'id': id}
        results = connectToMySQL(cls.db).query_db(query, data)  # a list with one dictionary in it
        one_recipe = cls(results[0])

        return one_recipe # returns user object
    
    @classmethod
    def get_recipe_by_id_with_user(cls, id):
        query = """
                SELECT * FROM recipes
                LEFT JOIN users
                ON recipes.user_id = users.id
                WHERE recipes.id = %(id)s;
                """
        data = {'id': id}
        results = connectToMySQL(cls.db).query_db(query, data)  # a list with one dictionary in it
        one_recipe=results[0] # one dictionary

        return one_recipe # returns recipe dictionary


    # Update Recipes Models

    @classmethod
    def update_recipe(cls, data):  

        this_recipe = cls.get_recipe_by_id(data['id'])
        if session['user_id'] != this_recipe.user_id:
            return False

        is_valid = cls.validate_recipe(data)
        if not is_valid:
            return False
        
        query = """
                UPDATE recipes
                SET name = %(name)s,
                    description = %(description)s,
                    instructions = %(instructions)s,
                    date_cooked = %(date_cooked)s,
                    is_under_thirty_minutes = %(is_under_thirty_minutes)s
                WHERE id=%(id)s;    
        """
        connectToMySQL(cls.db).query_db(query, data)
        return True
    # Alternative solution:  in update.html, right after <h1> line put:  <input type="hidden" name="id" value={{one_user.id}}>
    # Then don't need to pass in id

    # Delete Users Models

    @classmethod
    def delete_recipe(cls, id):
        this_recipe = cls.get_recipe_by_id(id) 
        if session['user_id'] != this_recipe.user_id:   
            return False
        query = """
                DELETE FROM recipes
                WHERE id = %(id)s;
        """
        data = {'id': id}
        return connectToMySQL(cls.db).query_db(query, data)
    
    # Validation
    
    # determines if a string has at least one number in it
    # @classmethod
    # def string_contains_a_number(cls,str):
    #     for character in str:
    #         if character.isnumeric():
    #             return True
    #     return False    

    # determines if a string has at least one uppercase letter in it        
    # @classmethod
    # def string_contains_an_uppercase_letter(cls,str):
    #     for character in str:
    #         if character.isupper():
    #             return True 
    #     return False          

    # If needed, break this validation into two parts - validate_registration(user) and validate_login(user)
    @staticmethod
    def validate_recipe(recipe):
        is_valid = True
        if len(recipe['name']) < 3 or recipe['name'].isspace():
            flash("Recipe name must be at least 3 characters.", "error")
            is_valid = False
        if len(recipe['description']) < 3 or recipe['description'].isspace():
            flash("Description must be at least 3 characters long.", "error")
            is_valid = False
        if len(recipe['instructions']) < 3 or recipe['instructions'].isspace():
            flash("Instructions must be at least 3 characters long.", "error")
            is_valid = False
        if recipe['is_under_thirty_minutes'] != "1" and recipe['is_under_thirty_minutes'] != "2":
            flash("Indicate whether or not the recipe is under 30 minutes", "error") 
            is_valid = False 
        if len(recipe['date_cooked']) < 1:
            flash("Date cooked is required")
            is_valid = False 
        # Test and make sure this validation works                      
        return is_valid
    
    # @classmethod
    # def is_email_unique(cls, user_email):
    #     query = "SELECT email FROM users;"
    #     # make sure to call the connectToMySQL function with the schema you are targeting.
    #     results = connectToMySQL(cls.db).query_db(query)
    #     # Create an empty list to append our instances of emails
    #     all_emails = []
    #     # Iterate over the db results and create instances of  with cls.
    #     for one_email in results:
    #         all_emails.append(one_email['email'])
            
    #     for email in all_emails:
    #         if email.lower() == user_email.lower():
    #             flash(f"{user_email} is already taken.")
    #             return False
    #     return True  
    
    # login and logout

    # @classmethod
    # def do_passwords_match(cls, user_email, password_to_check):
    #     passwords_match = False
    #     one_user = cls.get_user_by_email(user_email)
    #     if bcrypt.check_password_hash(one_user.password, password_to_check):
    #         passwords_match = True
    #     return passwords_match
    
    # @classmethod
    # def login_user(cls, data):
    #     email_to_check = data["email"]
    #     user_in_db = cls.get_user_by_email(email_to_check)
    #     if not user_in_db:
    #         flash(f"{email_to_check} is not registered.", "error")
    #         return False
    #     password_to_check = data["password"]
    #     if not cls.do_passwords_match(email_to_check, password_to_check):
    #         flash("Password does not match.", "error")
    #         return False
    #     session['user_id'] = user_in_db.id
    #     session['first_name'] = user_in_db.first_name
    #     session['logged_in'] = True

    #     return True
        






