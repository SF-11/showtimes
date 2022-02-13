import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from dataclasses import dataclass

import scraper.afi
import requests
import json
import shutil
import os
from os.path import exists
import re


config = {}

@dataclass
class Showtimes:
    """
    """
    def __init__(self, movie_name, day, times, theater, year):
        super().__init__()
        self.movie_name = movie_name
        self.day = day
        self.times = times
        self.theater = theater
        self.year = year


def tmdb_query(movies: Showtimes):
    """
    """
    movie_list = []

    for m in movies:
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=" \
            + config["API_KEY"] + "&query=" + m.movie_name + "&year=" + m.year)
        
        movie_info = response.text
        parsed = json.loads(movie_info)

        try:
            search_result = parsed["results"][0]
            movie_list.append((m, search_result))
        except IndexError as ex:
            # TODO log and report errors via email
            continue

    return movie_list


def download_poster(poster_path):
    try:
        poster_url = "https://image.tmdb.org/t/p/original" + poster_path
    except TypeError:
        return
    
    # request to get poster image
    r = requests.get(poster_url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        
        # download poster image
        if not exists("temp"): os.makedirs("temp") # TODO delete dir after run
        with open("temp" + poster_path, "wb+") as f:
            shutil.copyfileobj(r.raw, f)

        return "temp" + poster_path

    else:
        return "" # FIXME


def format_results(movies):
    """
    :param movies: tuple of (Showtime object, TMDB search result)
    """
    msg = MIMEMultipart('mixed')
    msg["Subject"] = "Your Weekly Movie Report"
    msg["From"] = "Showtimes"
    msg["To"] = config["TO_EMAIL"]

    # iterate movies
    days_html = ""
    movie_cells_html = ""
    col = 0 # FIXME
    curr_day = movies[0][0].day
    for m in movies:
        # limit number of poster in a row to 5 
        if col % 4 == 0:
            movie_cells_html += "</tr><tr>"
        col += 1

        # unpack results
        showtime, search_result = m

        # Make a new section for each day of showtimes
        if curr_day != showtime.day:
            with open("templates/day.html", "r") as f:
                day = f.read()
                day = day.format(date=curr_day, movies=movie_cells_html)
                days_html += day
            movie_cells_html = ""
            curr_day = showtime.day

        # download poster image
        downloaded = download_poster(search_result["poster_path"])
        poster_path = downloaded if downloaded else ""

        # create cell for movie
        with open("templates/movie_cell.html", "r") as f:
            cell = f.read()
            cell = cell.format(poster=poster_path.split("/")[-1], movie_name=search_result["title"], theater=showtime.theater, times=showtime.times)
            movie_cells_html += cell   

        # embed poster image - skip if path not found
        if poster_path == "":
            continue
        with open(poster_path, "rb") as f:
            msg_image = MIMEImage(f.read())
        msg_image.add_header("Content-ID", '<{}>'.format(poster_path.split("/")[-1]))
        msg.attach(msg_image)

    # get last day of movies
    with open("templates/day.html", "r") as f:
        day = f.read()
        day = day.format(date=curr_day, movies=movie_cells_html)
        days_html += day

    # build html string
    # open base html template
    with open("templates/email.html", "r") as f:
        base_html = f.read()
    base_html = base_html.format(days=days_html)
    
    full_text = MIMEText(base_html, "html")
    msg.attach(full_text)

    return msg


def load_config():
    """
    """        
    with open("st.cfg", "r") as fd:
        
        for line in fd:
            if not re.match("[^\s]*? = [^\s]*?", line):
                continue

            split_line = line.split(" = ")
            config[split_line[0]] = split_line[1].strip()


def send_email(msg):
    """
    """
    server = smtplib.SMTP(config["SMTP_SERVER"])
    server.starttls()
    server.login(config["BOT_EMAIL"], config["BOT_PW"])
    server.send_message(msg)
    server.quit()


if __name__=="__main__":
    load_config()
    
    # scrape theaters
    afi_movies = scraper.afi.scrape()
    # regal_movies = scraper.regal.scrape()

    search_results = tmdb_query(afi_movies)

    # format results
    message = format_results(search_results)

    # send an email
    send_email(message)

    shutil.rmtree("temp")
