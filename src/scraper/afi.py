from bs4 import BeautifulSoup
import showtimes
import datetime
import re
import requests


MONDAY = 0
SUNDAY = 6
SATURDAY = 5


def scrape(site_url="https://afisilver.afi.com/films/calendar.aspx"):
    """
    """
    # scrape from site
    page = requests.get(site_url)
    soup = BeautifulSoup(page.content, "html.parser")

    # collection will start on the upcoming sunday and end 1 week later
    today = datetime.date.today()
    if today.weekday == SUNDAY:
        next_sun = today
    else:
        next_sun = today + datetime.timedelta(6-today.weekday())

    # parse out the content for the specified days
    shows = parse(soup, next_sun)

    return shows


def parse(soup, start_date):
    """
    """
    # get a list of the days in order (including days from last and next month)
    days = soup.find_all('td', class_="day")
    dates = [int(x.contents[0]) for x in days]

    month_start_idx = dates.index(1)
    next_sun_idx = dates[month_start_idx:].index(start_date.day)+month_start_idx
    next_sat_idx = next_sun_idx + 6

    shows = []
    # for each day next week
    for i in range(next_sun_idx, next_sat_idx+1):
        day = list(days[i].children)[0]
        movies = str(list(days[i].children)[1]) # 0 index has day of month, 1 index has content        
        split_movies = re.findall(r"Movies/Details.*?\">(.*?)</a><br/>(.*?)<br/>", movies)
        # for each movie in the day
        for movie in split_movies:
            
            try:
                j = re.findall(r"([^a-z()]{3,})(\(.+?\))?", movie[0])[0] # ("MOVIE NAME", "(YYYY)")
                year = re.sub("[^0-9]", "", j[1])  
            except IndexError: # TODO what causes this?
                print("ERROR: ", movie)
                continue

            movie_name = j[0]
            movie_times = movie[1]

            # format times
            times = re.findall(r"(?:\d)?\d:\d\d(?: a\.m\.)?", movie_times)
            times = [x.replace(".", "") for x in times]
            times = [x + " pm" if "am" not in x else x for x in times]

            shows.append(showtimes.Showtimes(movie_name.strip(), day, times, "AFI Silver", year))
    
    return shows


