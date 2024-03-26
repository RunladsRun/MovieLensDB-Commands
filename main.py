# File: main.py
#
# Provides 5 commends to retrieve stats from MovieLens database
#
#   Project #02
#   Name: Scott Hong
#   NetID: shong85
#   UIN: 679056829
#

import sqlite3
import objecttier

##################################################################  
# 
# commendOne:
#
# Inputs a movie name and outputs the movie’s ID, title, 
# and year of release. 
#
def commendOne(dbConn):
  title = input("\nEnter movie name (wildcards _ and % supported): ")
  movieList = objecttier.get_movies(dbConn, title)
  print("\n# of movies found:", len(movieList))

  if len(movieList) > 100:
    print("There are too many movies to display, please narrow your search and try again...")
    return

  print()
  for i in movieList:
    print(i.Movie_ID, ":", i.Title, f"({i.Release_Year})")


##################################################################  
# 
# commendTwo:
#
# Inputs a movie id and outputs detailed movie information about
# this movie --- tagline, budget, revenue, genres, etc.
#   
def commendTwo(dbConn):
  id = input("\nEnter movie id: ")

  details = objecttier.get_movie_details(dbConn, id)

  if details is None:
    print("\nNo such movie...")
    return

  print()
  print(details.Movie_ID, ":", details.Title)
  print("  Release date:", details.Release_Date)
  print("  Runtime:", details.Runtime, "(mins)")
  print("  Orig language:", details.Original_Language)
  print("  Budget: $"+ f"{details.Budget:,}", "(USD)")
  print("  Revenue: $"+ f"{details.Revenue:,}", "(USD)")
  print("  Num reviews:", details.Num_Reviews)
  print("  Avg rating:", f"{details.Avg_Rating:.2f}", "(0..10)")
  
  str = ""
  for i in details.Genres:
    str += i+", "
  print("  Genres:", str)
  
  str = ""
  for j in details.Production_Companies:
    str += j+", "
  print("  Production companies:", str)

  print("  Tagline:", details.Tagline)


##################################################################  
# 
# commendThree:
#
# Output the top N movies based on their average rating and 
# with a minimum number of reviews.
#
def commendThree(dbConn):
  
  n = input("\nN? ")
  if int(n) < 1:
    print("Please enter a positive value for N...")
    return
  
  min = input("min number of reviews? ")
  if int(min) < 1:
    print("Please enter a positive value for min number of reviews...")
    return

  list = objecttier.get_top_N_movies(dbConn, int(n), int(min))
  print()
  for i in list:
    print(i.Movie_ID, ":", i.Title, f"({i.Release_Year}),", "avg rating =", f"{i.Avg_Rating:.2f}", f"({i.Num_Reviews} reviews)")

##################################################################  
# 
# commendFour:
#
# Inserts a new review into the database. The program inputs 
# a movie id and a rating (0..10), and then inserts the review 
# after validating the input
#
def commendFour(dbConn):
  rating = input("\nEnter rating (0..10): ")
  if int(rating) > 10 or int(rating) < 0:
    print("Invalid rating...")
    return
  id = input("Enter movie id: ")

  result = objecttier.add_review(dbConn, id, int(rating))

  if result:
    print("\nReview successfully inserted")
  else:
    print("\nNo such movie...")

##################################################################  
# 
# commendFive:
#
# Sets the tagline for a given movie, either by inserting 
# (if not already there) or updating (if already there)
#
def commendFive(dbConn):
  tagline = input("\nTagline? ")
  id = input("movie id? ")

  result = objecttier.set_tagline(dbConn, id, tagline)

  if result:
    print("\nTagline successfully set")
  else:
    print("\nNo such movie...")



##################################################################  
# 
# main
#
dbConn = sqlite3.connect('MovieLens.db')

print("** Welcome to the MovieLens app **\n")
print("General stats:")
print("  # of movies:", f"{objecttier.num_movies(dbConn):,}")
print("  # of reviews:", f"{objecttier.num_reviews(dbConn):,}")

commend = ""
while commend != "x":
  commend = input("\nPlease enter a command (1-5, x to exit): ")
  if commend == "1":
    commendOne(dbConn)
  elif commend == "2":
    commendTwo(dbConn)
  elif commend == "3":
    commendThree(dbConn)
  elif commend == "4":
    commendFour(dbConn)
  elif commend == "5":
    commendFive(dbConn)
  elif commend != "x":
    print("Invalid commend.")

dbConn.close()