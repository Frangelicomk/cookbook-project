import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
# from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'assets')

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'PUsG,-0id*1DKs(LXS}yp8PVTf`jzc'

mongo = PyMongo(app)

messages = [{'title': 'Message One',
             'description': 'Message One Content'},
            {'title': 'Message Two',
             'description': 'Message Two Content'}
            ]


# @app.route("/")
def index():
    """
    Formats index.html, take recipes from database and
    puts them on index.html

    """
    recipes = mongo.db.recipes.find()
    return render_template("index.html", recipes=recipes)


@app.route("/about")
def about():
    """
    Formats the structure of about.html

    """
    return render_template("about.html", page_title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registration auth, checks if user already exists in database.
    This function was coppied from Code Institute Mini Project

    """
    if not session.get("user"):
        if request.method == "POST":
            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                flash("Username already exists")
                return redirect(url_for("register"))
            register_user = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(
                    request.form.get("password"))}
            mongo.db.users.insert_one(register_user)

            # put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
            return redirect(url_for("favorites", username=session["user"]))

        return render_template("register.html")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This function check whether the user has logged in or if the username
    and password are matching the database of a registered user
    This function was coppied from Code Institute Mini Project

    """
    if not session.get("user"):
        if request.method == "POST":
            # check if username exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                # ensure hashed password matches user input
                if check_password_hash(
                        existing_user["password"],
                        request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "favorites", username=session["user"]))
                else:
                    # invalid password match
                    flash("Incorrect Username and/or Password")
                    return redirect(url_for("login"))

            else:
                # username doesn't exist
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        return render_template("login.html")
    return redirect(url_for("index"))


@app.route("/favorites<username>", methods=["GET", "POST"])
def favorites(username):
    """
    Favorites html only appears if user is logged in

    """
    if session.get("user"):
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        return render_template("favorites.html", username=username)
    return render_template(
        "login.html")


@app.route("/logout")
def logout():
    """
    Log out button only appears if user is logged in

    """
    if session.get("user"):
        flash("You have been logged out")
        session.pop("user")
        return redirect(url_for("login"))


@app.route('/add_recipe', methods=('GET', 'POST'))
def add_recipe():
    """
    add_recipe only appears if user is logged in

    """
    if session.get("user"):
        if request.method == 'POST':
            cousine_name = request.form.get('cousine_name')
            recipe_name = request.form.get('recipe_name')
            description = request.form.get('description')
            ingredients = request.form.get('ingredients')
            cover = request.form.get("cover")

            if not cousine_name:
                flash('Cousine Name is required!')
            elif not recipe_name:
                flash('Recipe Name is required!')
            elif not description:
                flash('Description is required!')
            elif not ingredients:
                flash('Ingredients is required!')
            elif not cover:
                flash('Cover is required!')
            else:
                document = {
                    'cousine_name': cousine_name,
                    'recipe_name': recipe_name, 'description': description,
                    'cover': cover, 'ingredients': ingredients}
                messages.append(document)
                mongo.db.recipes.insert_one(document)

        return render_template('add_recipe.html', username=session["user"])
    return render_template(
        "login.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
