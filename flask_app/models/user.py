
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
import re, datetime
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
# The above is used when we do login registration, flask-bcrypt should already be in your env check the pipfile

# Remember 'fat models, skinny controllers' more logic should go in here rather than in your controller. Your controller should be able to just call a function from the model for what it needs, ideally.



class User:
    db = "recipes_schema" #which database are you using for this project
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.my_recipe_box = []
        
    # Create Users Models

    # class method to save our user to the database
    @classmethod
    def register_user(cls, user_data):
        if not cls.validate_user_registration(user_data):
            return False
        
        user_data = user_data.copy()  #immutable, so need to make a copy to add password

        user_data['password'] = bcrypt.generate_password_hash(user_data['password'])


        query = """
                INSERT INTO users(first_name, last_name, email, password) 
                VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        
        user_id = connectToMySQL(cls.db).query_db(query, user_data)

        session['user_id'] = user_id
        session['first_name'] = user_data["first_name"]
        session['logged_in'] = True

        return True

    # Read Users Models

    # @classmethod
    # def get_all(cls):
    #     query = "SELECT * FROM users;"
    #     # make sure to call the connectToMySQL function with the schema you are targeting.
    #     results = connectToMySQL(cls.db).query_db(query)
    #     # Create an empty list to append our instances of users
    #     all_users = []
    #     # Iterate over the db results and create instances of users with cls.
    #     for one_user in results:
    #         all_users.append(cls(one_user))
    #     return all_users


    # Read Users Models

    # the get_user_by_email method will be used when we need to retrieve just one specific row of the table
    @classmethod
    def get_user_by_email(cls, email):
        query = """
                SELECT * FROM users
                WHERE email = %(email)s;
        """
        data = {'email': email}
        result = connectToMySQL(cls.db).query_db(query, data)  # a list with one dictionary in it
        if len(result) < 1:     # no matching user
            return False
        one_user = cls(result[0])
        return one_user # returns user object

    # the get_user_by_id method will be used when we need to retrieve just one specific row of the table
    @classmethod
    def get_user_by_id(cls, id):
        query = """
                SELECT * FROM users
                WHERE id = %(id)s;
        """
        data = {'id': id}
        results = connectToMySQL(cls.db).query_db(query, data)  # a list with one dictionary in it
        one_user = cls(results[0])

        return one_user # returns user object

    # Update Users Models

    # @classmethod
    # def update_user(cls, data):   

    #     query = """
    #             UPDATE users
    #             SET first_name=%(first_name)s,
    #                 last_name=%(last_name)s,
    #                 email=%(email)s
    #             WHERE id=%(id)s;    
    #     """
    #     return connectToMySQL(cls.db).query_db(query, data)
    # Alternative solution:  in update.html, right after <h1> line put:  <input type="hidden" name="id" value={{one_user.id}}>
    # Then don't need to pass in id

    # Delete Users Models

    # @classmethod
    # def delete(cls, id):
    #     query = """
    #             DELETE from users
    #             WHERE id = %(id)s;
    #     """
    #     data = {'id': id}
    #     return connectToMySQL(cls.db).query_db(query, data)
    
    # Validation
    
    # determines if a string has at least one number in it
    @classmethod
    def string_contains_a_number(cls,str):
        for character in str:
            if character.isnumeric():
                return True
        return False    

    # determines if a string has at least one uppercase letter in it        
    @classmethod
    def string_contains_an_uppercase_letter(cls,str):
        for character in str:
            if character.isupper():
                return True 
        return False          

    # If needed, break this validation into two parts - validate_registration(user) and validate_login(user)
    @staticmethod
    def validate_user_registration(user):

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


        is_valid = True
        if len(user['first_name']) < 3 or user['first_name'].isspace() or not user['first_name'].isalpha():
            flash("First name must be at least 2 letters long.", "error")
            is_valid = False
        if len(user['last_name']) < 3 or user['last_name'].isspace()or not user['last_name'].isalpha():
            flash("Last name must be at least 2 letters long.", "error")
            is_valid = False
        if len(user['password']) < 8 or user['password'].isspace():
            flash("Password must be at least 8 characters long.", "error")
            is_valid = False
        elif user['password'] != user['confirm_password']:
            flash("Passwords do not match.", "error")
            is_valid = False
        if not User.string_contains_an_uppercase_letter(user['password']):
            flash("Password must contain at least one uppercase letter.", "error") 
            is_valid = False
        if not User.string_contains_a_number(user["password"]):
            flash("Password must contain at least one number.", "error") 
            is_valid = False                  
        if len(user['email']) == 0  or user['email'].isspace():
            flash("Email is required.", "error")
            is_valid = False       
        elif not EMAIL_REGEX.match(user['email']):
            flash("Invalid email format.", "error")
            is_valid = False
        if User.get_user_by_email(user['email']):
                flash(f"{user['email']} is already taken.")
                return False
        return is_valid
    
    
    
    # login and logout

    
    @classmethod
    def login_user(cls, data):
        email_to_check = data["email"]
        user_in_db = cls.get_user_by_email(email_to_check)

        if not user_in_db:
            flash(f"{email_to_check} is not registered.", "error")
            return False
        
        password_to_check = data["password"]
        if not bcrypt.check_password_hash(user_in_db.password, password_to_check):
            flash("Password does not match.", "error")
            return False
        
        session['user_id'] = user_in_db.id
        session['first_name'] = user_in_db.first_name
        session['logged_in'] = True

        return True
        






