from src.scraper.afi import *
from bs4 import BeautifulSoup

import datetime
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../src/')


def test_release_year():
    """THE HOWLING (1981)"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 1)
    shows = parse(soup, start_date)

    howling = shows[4]

    assert howling.movie_name == "THE HOWLING"
    assert howling.year == "1981"


def test_no_showtimes():
    """Check back daily for showtimes"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 12)
    shows = parse(soup, start_date)

    movie = shows[4]

    assert movie.movie_name == "BELFAST"
    assert len(movie.times) == 0
    

def test_one_showtime():
    """4:45 pm"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 1)
    shows = parse(soup, start_date)

    howling = shows[4]

    assert howling.movie_name == "THE HOWLING"
    assert len(howling.times) == 1
    assert howling.times[0] == "4:45 pm"    


def test_multi_showtimes():
    """1:55, 4:20, 9:10"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 6)
    shows = parse(soup, start_date)

    movie = shows[0]

    assert movie.movie_name == "SPENCER"
    assert len(movie.times) == 5
    assert movie.times[0] == "11:00 am"
    assert movie.times[4] == "9:00 pm"


def test_non_english():
    """PLÁCIDO (1961)"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 14)
    shows = parse(soup, start_date)

    movie = shows[2]

    assert movie.movie_name == "PLÁCIDO"


def test_text_after_year():
    """POSSESSION (1981) - Director's Cut"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 6)
    shows = parse(soup, start_date)

    movie = shows[2]

    assert movie.movie_name == "POSSESSION"
    assert movie.year == "1981"


def test_text_before_year():
    """THE FRENCH DISPATCH Advance Screenings"""
    """No examples in afi-nov-21"""
    assert True # TODO


def test_text_in_year():
    """DRACULA (1931 Spanish language version)"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 2)
    shows = parse(soup, start_date)

    movie = shows[4]

    assert movie.movie_name == "DRACULA"
    assert movie.year == "1931"


def test_opened_captioned():
    """1:55, 4:20, (6:45 Open captioned show), 9:10"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 1)
    shows = parse(soup, start_date)

    movie = shows[0]

    assert movie.movie_name == "THE FRENCH DISPATCH"
    assert len(movie.times) == 4
    assert movie.times == ["1:55 pm", "4:20 pm", "6:45 pm", "9:10 pm"]


def test_non_movie():
    """Edward Everett Horton comedy shorts program feat. live accompaniment by Ben Model; intro by Steve Massa"""
    with open("./tests/data/afi-nov-21.html", "r") as webpage: 
        data = webpage.read().encode("utf-8")

    soup = BeautifulSoup(data, "html.parser")
    start_date = datetime.date(2021, 11, 20)
    shows = parse(soup, start_date)

    movie = shows[2]

    assert len([x for x in shows if x.day == "20"]) == 3
    assert movie.movie_name == "SO THIS IS PARIS"
