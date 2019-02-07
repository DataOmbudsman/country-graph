import json
import requests

from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Dict, Iterable, Set

VALID_CONTINENTS = ['Africa', 'Asia', 'Europe', 'North_America', 'Oceania', 'South_America']
INVALID_CONTINENT = 'Antarctica'
CONTINENTS = VALID_CONTINENTS + [INVALID_CONTINENT]


def get_continents_of_countries(countries_to_find: Iterable[str]):
    countries_by_continents = extract_countries_by_continents()
    country_to_continent = get_continents_per_countries(countries_to_find, countries_by_continents)
    country_to_continent = hack(country_to_continent)
    return country_to_continent


def extract_countries_by_continents():
    source = download_source()
    continent_tables = find_continent_tables(source)
    countries_by_continent = extract_country_names_from_table(continent_tables)
    return countries_by_continent


def download_source():
    url = 'https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_by_continent'
    source = requests.get(url).text
    return source


def find_continent_tables(source):
    continent_start = '<h2><span class="mw-headline" id="{}">'
    continent_start_indices = [source.find(continent_start.format(continent))
                               for continent in CONTINENTS]

    valid_continent_chunks = [source[continent_start_indices[i] : continent_start_indices[i+1]]
                              for i, continent in enumerate(VALID_CONTINENTS)]

    valid_continent_tables = [BeautifulSoup(chunk, 'lxml').find('table')
                              for chunk in valid_continent_chunks]

    return valid_continent_tables


def extract_country_names_from_table(continent_tables):
    country_names_of_continent = defaultdict(lambda: [])

    for continent, continent_table in zip(CONTINENTS, continent_tables):
        for row in continent_table.find_all('tr'):
            try:
                country_name = row.find('td').text
                country_name = clean_country_cell(country_name)
                if not country_name.startswith('AA') and not country_name.startswith('ZZ'):
                    country_names_of_continent[continent].append(country_name)
            except:
                pass

    return country_names_of_continent


def clean_country_cell(txt):
    return txt.replace('\xa0', ' ').strip()


def get_continents_per_countries(countries_to_find, continent_to_countries):
    continents_per_countries = dict()
    for country_to_find in countries_to_find:
        continents_per_countries[country_to_find] = find_continents_of_country(
            country_to_find, continent_to_countries)

    return continents_per_countries


def find_continents_of_country(country_to_find: str, countries_by_continents):
    continents = set()

    for continent, country_names in countries_by_continents.items():
        for country_name in country_names:
            if country_to_find in country_name:
                continents.add(continent)

    return continents


def hack(country_to_continent):
    """
    Override Wikipedia for the purpose of the visalization.
    """
    hacks = {
        'Denmark': {'Europe'},
        'East Timor': {'Asia'},
        'France': {'Europe', 'North_America', 'South_America'},
        'Guinea': {'Africa'},
        'Indonesia': {'Asia'},
        'Netherlands': {'Europe', 'North_America'},
        'Spain': {'Europe', 'Africa'},
        'United Kingdom': {'Europe', 'Asia'},
    }
    country_to_continent.update(hacks)
    return country_to_continent
