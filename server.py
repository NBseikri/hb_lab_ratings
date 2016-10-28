"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import similarities


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
    """Showing the user profile """

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
    """Shows movie details page """

    movie = Movie.query.get(movie_id)
    user_rating = Rating.query.filter_by(user_id=945, movie_id=movie_id).first()

    if user_rating == None:
        score_corr = similarities.make_score_corr_dictionary(movie.title, movie_id)
        max_pearson_score, max_similarity_user_id = similarities.calculate_max_pearson_score(score_corr)
        print max_pearson_score

        predicted_score = similarities.calculate_prediction(max_pearson_score, max_similarity_user_id, movie_id)
        print predicted_score

    return render_template('movie.html', movie=movie, user_rating=user_rating, predicted_score=predicted_score)


@app.route('/add_rating', methods=['POST'])
def add_or_update_rating():
    """Add or update the users rating."""

    user_id = session.get('user_id')
    movie_id = request.form.get('movie_id')
    movie = Movie.query.get(movie_id)
    score = request.form.get('rating')


    db_rating = db.session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id)

    try: 
        rating_exists = db_rating.one()
    except NoResultFound:

        print "No instance of rating found in db for this user."        
        rating_exists = None 

    except MultipleResultsFound:
        print "Multiple rating instances found in db for this user."
        rating_exists = db_rating.first()


    if rating_exists:
        db_rating.update({'score': score})
        db.session.commit()
        flash("Your rating has been updated to " + score + ".")
    else:
        rating = Rating(user_id=user_id,
                    movie_id=movie_id,
                    score=score)
        db.session.add(rating)
        db.session.commit()
        flash("Your rating for " + rating.movie.title + "has been added.")
    
    return redirect('/movie/{}'.format(movie_id))



@app.route("/register", methods=['GET'])
def get_registration_form():
    """Displays registration form"""

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

        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/')

@app.route('/login', methods=['GET'])
def show_login_form():

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def login_process():

    email = request.form.get('email')
    password = request.form.get('password')

    user_query = db.session.query(User).filter_by(email=email)
    try:
        user = user_query.one()
    except NoResultFound:
        print "No user instance found for this email in db."
        user = None
    except MultipleResultsFound:
        print "Multiple user instances found for this email in db."
        user = user_query.first()

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

