# File: objecttier.py
#
# objecttier
#
# Builds Movie-related objects from data retrieved through
# the data tier.
#
#   Project #02
#   Name: Scott Hong
#   NetID: shong85
#   UIN: 679056829
#
import datatier


##################################################################
#
# Movie:
#
# Constructor(...)
# Properties:
#   Movie_ID: int
#   Title: string
#   Release_Year: string
#
class Movie:

  def __init__(self, id, title, year):
    self._Movie_ID = id
    self._Title = title
    self._Release_Year = year

  @property
  def Movie_ID(self):
    return self._Movie_ID

  @property
  def Title(self):
    return self._Title

  @property
  def Release_Year(self):
    return self._Release_Year


##################################################################
#
# MovieRating:
#
# Constructor(...)
# Properties:
#   Movie_ID: int
#   Title: string
#   Release_Year: string
#   Num_Reviews: int
#   Avg_Rating: float
#
class MovieRating(Movie):

  def __init__(self, id, title, year, review, rating):
    Movie.__init__(self, id, title, year)
    self._Num_Reviews = review
    self._Avg_Rating = rating

  @property
  def Num_Reviews(self):
    return self._Num_Reviews

  @property
  def Avg_Rating(self):
    return self._Avg_Rating


##################################################################
#
# MovieDetails:
#
# Constructor(...)
# Properties:
#   Movie_ID: int
#   Title: string
#   Release_Date: string, date only (no time)
#   Runtime: int (minutes)
#   Original_Language: string
#   Budget: int (USD)
#   Revenue: int (USD)
#   Num_Reviews: int
#   Avg_Rating: float
#   Tagline: string
#   Genres: list of string
#   Production_Companies: list of string
#
class MovieDetails(MovieRating):

  def __init__(self, list):
    MovieRating.__init__(self, list[0], list[1], list[2], list[3], list[4])
    self._Release_Date = list[5]
    self._Runtime = list[6]
    self._Original_Language = list[7]
    self._Budget = list[8]
    self._Revenue = list[9]
    self._Tagline = list[10]
    self._Genres = list[11]
    self._Production_Companies = list[12]

  @property
  def Release_Date(self):
    return self._Release_Date

  @property
  def Runtime(self):
    return self._Runtime

  @property
  def Original_Language(self):
    return self._Original_Language

  @property
  def Budget(self):
    return self._Budget

  @property
  def Revenue(self):
    return self._Revenue

  @property
  def Tagline(self):
    return self._Tagline

  @property
  def Genres(self):
    return self._Genres

  @property
  def Production_Companies(self):
    return self._Production_Companies


##################################################################
#
# num_movies:
#
# Returns: # of movies in the database; if an error returns -1
#
def num_movies(dbConn):
  total = datatier.select_one_row(dbConn, "Select count(*) From Movies;", None)
  if total is None:
    return -1
  return total[0]


##################################################################
#
# num_reviews:
#
# Returns: # of reviews in the database; if an error returns -1
#
def num_reviews(dbConn):
  total = datatier.select_one_row(dbConn, "Select count(*) From Ratings;", None)
  if total is None:
    return -1
  return total[0]


##################################################################
#
# get_movies:
#
# gets and returns all movies whose name are "like"
# the pattern. Patterns are based on SQL, which allow
# the _ and % wildcards. Pass "%" to get all stations.
#
# Returns: list of movies in ascending order by movie id;
#          an empty list means the query did not retrieve
#          any data (or an internal error occurred, in
#          which case an error msg is already output).
#
def get_movies(dbConn, pattern):
  sql = """ Select Movie_ID, title, strftime('%Y', Release_Date) from Movies where title like ? order by Movie_ID; """
  rows = datatier.select_n_rows(dbConn, sql, [pattern])
    
  list = []

  if rows is None:
    return list

  for row in rows:
    movie = Movie(row[0], row[1], row[2])
    list.append(movie)

  return list


##################################################################
#
# get_movie_details:
#
# gets and returns details about the given movie; you pass
# the movie id, function returns a MovieDetails object. Returns
# None if no movie was found with this id.
#
# Returns: if the search was successful, a MovieDetails obj
#          is returned. If the search did not find a matching
#          movie, None is returned; note that None is also
#          returned if an internal error occurred (in which
#          case an error msg is already output).
#
def get_movie_details(dbConn, movie_id):
  sql = """ select movies.Movie_ID, title, strftime('%Y', Release_Date), count(rating), avg(coalesce(rating,0)), Date(Release_Date), runtime, Original_Language, Budget, Revenue, coalesce(tagline,"") from movies left join movie_taglines on movies.Movie_ID = movie_taglines.Movie_ID left join ratings on movies.Movie_ID = ratings.Movie_ID where movies.Movie_ID = ? group by movies.Movie_ID; """

  tuple = datatier.select_one_row(dbConn, sql, [movie_id])
  
  if tuple is None or len(tuple) == 0:
    return None

  dataList = list(tuple)

  companySql = """ select company_Name from Movie_production_companies join companies on Movie_production_companies.company_ID = companies.company_ID where Movie_production_companies.Movie_ID = ? order by company_Name; """

  companyList = datatier.select_n_rows(dbConn, companySql, [movie_id])

  for i, j in enumerate(companyList):
    companyList[i] = j[0]

  genreSql = """ select genre_name from Movie_genres join genres on Movie_genres.genre_ID = genres.genre_ID where Movie_genres.Movie_ID = ? order by genre_name; """
  genreList = datatier.select_n_rows(dbConn, genreSql, [movie_id])

  for i, j in enumerate(genreList):
    genreList[i] = j[0]

  dataList.append(genreList)
  dataList.append(companyList)

  return MovieDetails(dataList)
  
##################################################################
#
# get_top_N_movies:
#
# gets and returns the top N movies based on their average
# rating, where each movie has at least the specified # of
# reviews. Example: pass (10, 100) to get the top 10 movies
# with at least 100 reviews.
#
# Returns: returns a list of 0 or more MovieRating objects;
#          the list could be empty if the min # of reviews
#          is too high. An empty list is also returned if
#          an internal error occurs (in which case an error
#          msg is already output).
#
def get_top_N_movies(dbConn, N, min_num_reviews):
  sql = """ select movies.Movie_ID, title, strftime('%Y', Release_Date), 
  count(rating) as total, avg(coalesce(rating,0)) as average from movies 
  left join ratings on movies.Movie_ID = ratings.Movie_ID 
  group by ratings.Movie_ID having total >= ? order by average desc limit ?  """

  rows = datatier.select_n_rows(dbConn, sql, [min_num_reviews, N])

  list = []

  if rows is None:
    return list

  for row in rows:
    movieRating = MovieRating(row[0], row[1], row[2], row[3], row[4])
    list.append(movieRating)

  return list


##################################################################
#
# add_review:
#
# Inserts the given review --- a rating value 0..10 --- into
# the database for the given movie. It is considered an error
# if the movie does not exist (see below), and the review is
# not inserted.
#
# Returns: 1 if the review was successfully added, returns
#          0 if not (e.g. if the movie does not exist, or if
#          an internal error occurred).
#
def add_review(dbConn, movie_id, rating):

  movie = datatier.select_one_row(dbConn, "select Movie_ID from movies where Movie_ID = ?;", [movie_id])

  if movie is None or len(movie) == 0:
    return 0
  
  sql = """ INSERT INTO Ratings(Movie_ID, Rating) values (?, ?); """

  result = datatier.perform_action(dbConn, sql, [movie_id, rating])

  if result == -1:
    return 0
  else:
    return 1
    


##################################################################
#
# set_tagline:
#
# Sets the tagline --- summary --- for the given movie. If
# the movie already has a tagline, it will be replaced by
# this new value. Passing a tagline of "" effectively
# deletes the existing tagline. It is considered an error
# if the movie does not exist (see below), and the tagline
# is not set.
#
# Returns: 1 if the tagline was successfully set, returns
#          0 if not (e.g. if the movie does not exist, or if
#          an internal error occurred).
#
def set_tagline(dbConn, movie_id, tagline):
  movie = datatier.select_one_row(dbConn, "select Movie_ID from movies where Movie_ID = ?;", [movie_id])

  if movie is None or len(movie) == 0:
    return 0

  movieTagline = datatier.select_one_row(dbConn, "select Movie_ID from movie_taglines where Movie_ID = ?;", [movie_id])

  if len(movieTagline) == 0:
    result = datatier.perform_action(dbConn, "INSERT INTO movie_taglines(Movie_ID, tagline) values (?, ?);", [movie_id, tagline])
  else:
    result = datatier.perform_action(dbConn, "Update movie_taglines set tagline = ? where movie_ID = ?; ", [tagline, movie_id])

  if result == -1:
    return 0
  else:
    return 1
  
