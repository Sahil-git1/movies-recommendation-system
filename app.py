import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify, render_template

# Load the dataset
df_movies = pd.read_csv('movies.csv')

# Data preprocessing and preparation
df_movies = df_movies.drop(columns=['date_x', 'score', 'overview', 'crew', 'orig_title',
                                    'status', 'orig_lang', 'budget_x', 'revenue', 'country'])
df_movies = df_movies.dropna(subset=['genre', 'names'])
df_movies['genre'] = df_movies['genre'].str.lower()
df_movies['names'] = df_movies['names'].str.lower()

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df_movies['genre'])
cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

# Flask application setup
app = Flask(__name__)

# Recommendation function
def recommend_movies(movie_name, cosine_similarities, df_movies, num_recommendations=10):
    # Find the index of the movie that matches the movie_name
    idx = df_movies[df_movies['names'] == movie_name.lower()].index[0]
    
    # Get pairwise similarity scores with all movies
    sim_scores = list(enumerate(cosine_similarities[idx]))
    
    # Sort movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top similar movies
    sim_scores = sim_scores[1:num_recommendations+1]  # Exclude the movie itself
    
    # Get movie indices
    movie_indices = [i[0] for i in sim_scores]
    
    # Return top similar movie names
    return df_movies['names'].iloc[movie_indices].tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_name = request.form['movie']
    recommendations = recommend_movies(movie_name, cosine_similarities, df_movies)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
