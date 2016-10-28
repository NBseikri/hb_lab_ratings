from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import correlation
from model import User, Movie, Rating


def make_score_corr_dictionary(movie_title, user_id):
    m = Movie.query.filter_by(title=movie_title).one()
    u = User.query.get(user_id)

    # This is all ratings from our user
    ratings = u.ratings

    # All of the other users ratings object who have rated toy story
    other_ratings = Rating.query.filter_by(movie_id=m.movie_id).all()

    # THis is a list of other users who have rated Toy Story
    other_users = [r.user for r in other_ratings]



    score_corr = {}

    u_movie_ids = [rating.movie_id for rating in u.ratings]

    for u_movie in u_movie_ids:
        u_score = Rating.query.filter_by(user_id=u.user_id, movie_id=u_movie).one().score
        
        for o_user in other_users:
            try:
                o_score = Rating.query.filter_by(user_id=o_user.user_id, movie_id=u_movie).one().score
            except NoResultFound:
                o_score = None

            if o_score:
                paired_ratings = score_corr.get(o_user.user_id, [])
                paired_ratings.append((u_score, o_score))
                score_corr[o_user.user_id] = paired_ratings

    return score_corr

def calculate_max_pearson_score(score_corr):

    pearson_scores = {}
    for user_id, all_paired_ratings in score_corr.iteritems():
        pearson_score = correlation.pearson(all_paired_ratings)
        pearson_scores[pearson_score] = user_id

    max_pearson_score = max(pearson_scores.keys())

    return max_pearson_score, pearson_scores[max_pearson_score]



def calculate_prediction(max_pearson_score, max_similarity_user_id, movie_id):

    score = Rating.query.filter_by(user_id=max_similarity_user_id, movie_id=movie_id).one().score
    predicted_score = max_pearson_score * score

    return predicted_score


# score_corr = make_score_corr_dictionary('Toy Story', 945)
# max_pearson_score, max_similarity_user_id = calculate_max_pearson_score(score_corr)
# print max_pearson_score

# predicted_score = calculate_prediction(max_pearson_score, max_similarity_user_id, 945)
# print predicted_score

