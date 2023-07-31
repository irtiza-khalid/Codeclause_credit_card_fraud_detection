from flask import Flask,request,render_template,redirect,url_for
import pickle
import requests
import pandas as pd
from patsy import dmatrices
import requests
from bs4 import BeautifulSoup
movies = pickle.load(open(r'model\movie_list.pkl', 'rb'))

similarity = pickle.load(open(r'model\similarity.pkl', 'rb'))

import requests

def fetch_poster(movie_id):
    api_key = "2a460e8a8a39dd93492e922ae36358e1"  # Replace this with your actual API key from themoviedb.org
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return None
    else:
        return None


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies_poster = []
    recommended_movies_name = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]].title)

    return recommended_movies_name, recommended_movies_poster

application = Flask(__name__)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/contact')
def contact():
    return render_template('contact.html')

@application.route('/recommendation',methods=['GET','POST'])
def recommendation():
    movie_list = movies['title'].values
    status = False
    if request.method == "POST":
        try:
            if request.form:
                movies_name = request.form['movies']
                recommended_movies_name, recommended_movies_poster = recommend(movies_name)
                status = True

                # Combine the two lists before passing to the template
                movies_and_posters = zip(recommended_movies_name, recommended_movies_poster)
                return render_template("prediction.html", movies_and_posters=movies_and_posters, movie_list=movie_list, status=status)

        except Exception as e:
            error = {'error': e}
            return render_template('prediction.html', error=error, movie_list=movie_list, status=status)

    else:
        return render_template('prediction.html', movie_list=movie_list, status=status)
if __name__ == '__main__':
    application.run(debug=True)
