"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/user/<user_id>')
def show_user_profile(user_id):

    user = User.query.get(user_id)

    # To create exclusive access to user profile without displaying id in browser 
    # user = User.query.get(session['user_id'])


    return render_template('user.html', user=user)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movie/<movie_id>')
def show_movie(movie_id):

    movie = Movie.query.get(movie_id)

    # To create exclusive access to user profile without displaying id in browser 
    # user = User.query.get(session['user_id'])


    return render_template('movie.html', movie=movie)


@app.route("/register", methods=['GET'])
def get_registration_form():


    return render_template("register_form.html")


@app.route("/register", methods=['POST'])
def registration_process():

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    emails = db.session.query(User.email).all()    

    if email in emails:
        return redirect('/login')

    else:
        user = User(email=email,
                    password=password,
                    age=age,
                    zipcode=zipcode,
                    )

        # We need to add to the session or it won't ever be stored
        db.session.add(user)
        # Once we're done, we should commit our work
        db.session.commit()

        return redirect('/')

@app.route('/login', methods=['GET'])
def show_login_form():

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def login_process():

    email = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter_by(email=email).first()

    if user:
        if user.password == password:
            flash("You've successfully logged in.")
            session['user_id'] = user.user_id
            return redirect('/user/{}'.format(user.user_id))
        else:
            flash("I'm sorry that password is incorrect. Please try again.")
            return redirect('/login')

    else:
        flash("""I'm sorry that email is not in our system. Please try again
                or go to our registration page to create a new account.""")
        return redirect('/login')


@app.route('/logout')
def logout_process():

    session['user_id'] = None
    flash("You've successfully logged out!")
    return redirect('/')





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000)
