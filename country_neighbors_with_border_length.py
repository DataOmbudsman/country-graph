import json
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

NeighborBorder = Dict[str, int]

### FETCH FROM WIKIPEDIA

def fetch_data_rows_from_wikipedia():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_land_borders'
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')

    country_table = soup.find('table', {'class': 'wikitable sortable'})
    rows = country_table.find_next('tbody', recursive=False).findChildren('tr', recursive=False)
    return rows[2:]


### COUNTRY LIST

def contains_sovereign_country(row) -> bool:
    country_cell = row.find_next('td')
    indicators_of_partial_sovereignity = country_cell.find_all('i')
    return len(indicators_of_partial_sovereignity) == 0

def _remove_text_in_parentheses(country_name):
    return re.sub(r'\(.*?\)', '', country_name).strip()

def _hack_country_name(country_name):
    """
    For purposes of this list, Aruba, Curaçao, Sint Maarten and the Netherlands
    are considered constituent parts of one sovereign state.
    """
    if country_name == 'Netherlands, Kingdom of the':
        return 'Netherlands'
    return country_name

def get_country_name(row) -> str:
    country_cell = row.find_next('td')
    first_link = country_cell.find_next('a')
    country_name = first_link.text

    country_name = _remove_text_in_parentheses(country_name)
    country_name = _hack_country_name(country_name)
    return country_name

def get_country_list(rows_of_countries):
    return set([
        get_country_name(row) for row in rows_of_countries
        if contains_sovereign_country(row)
    ])


### NEIGHBOR LIST WITH BORDERS

def _is_sovereign_neighbor(neighbor) -> bool:
    return neighbor in countries

def _get_neighbors(neighbor_container) -> List[str]:
    neighbor_links = neighbor_container.find_all('a')
    neighbors = [neighbor_link.text for neighbor_link in neighbor_links
                 if _is_sovereign_neighbor(neighbor_link.text)]
    return neighbors

def _get_chunk_of_neighbor(neighbor, chunks) -> str:
    for chunk in chunks:
        if chunk.startswith(neighbor):
            return chunk
        possible_country = re.search(r'\((.*?)\)', chunk)
        if possible_country and possible_country.group(1) == neighbor:
            return chunk
    print('Something unexpected happened')

def _get_border_from_chunk(chunk: str) -> float:
    has_border_data = ':' in chunk
    if has_border_data:
        border = chunk.split(' ')[-1].replace(',', '')
        return float(border)
    return -1

def _get_border_from_container(neighbor, neighbor_container) -> float:
    chunks = neighbor_container.text.split('\xa0')
    chunk_of_neighbor = _get_chunk_of_neighbor(neighbor, chunks)
    border = _get_border_from_chunk(chunk_of_neighbor)
    return border

def _get_neighbors_with_borders(neighbors, neighbor_container):
    neighbors_with_borders = [(neighbor, _get_border_from_container(neighbor, neighbor_container))
                              for neighbor in neighbors]
    neighbors_with_borders = {neighbor: border for (neighbor, border) in neighbors_with_borders
                              if border != -1}
    return neighbors_with_borders

def extract_neighbor_border_pairs(neighbor_container) -> NeighborBorder:
    neighbors = _get_neighbors(neighbor_container)
    neighbors_with_borders = _get_neighbors_with_borders(neighbors, neighbor_container)
    return neighbors_with_borders

def get_neighbors_with_border_length(row) -> NeighborBorder:
    neighbor_containers = row.find_all('div', {'class': 'mw-collapsible-content'})
    if neighbor_containers:
        neighbor_container = neighbor_containers[-1]
        neighbor_border_pairs = extract_neighbor_border_pairs(neighbor_container)
        return neighbor_border_pairs
    return {}

def get_neighbors_of_countries(rows_of_countries, countries):
    neighbors_of_countries = {}

    for row in rows_of_countries:
        country = get_country_name(row)
        if country in countries:
            neighbors = get_neighbors_with_border_length(row)
            neighbors_of_countries[country] = neighbors

    return neighbors_of_countries


### CLEANUP NEIGHBOR DATA

def consolidate(neighbors_of_countries):
    """
    Fix the the imperfections in the data:
    1. country is not in the neighbors of its neighbor
    2. border length is not the same viewed from the two sides
    """
    for country, neighbors in neighbors_of_countries.items():
        for neighbor, border1 in neighbors.items():

            if country not in neighbors_of_countries[neighbor]:
                neighbors_of_countries[neighbor][country] = border1

            border2 = neighbors_of_countries[neighbor][country]
            if border1 != border2:
                border_consolidated = max(border1, border2)
                neighbors_of_countries[country][neighbor] = border_consolidated
                neighbors_of_countries[neighbor][country] = border_consolidated


### SAVE DATA IN SEVERAL FORMATS

def assemble_node_list(neighbors_of_countries):
    countries = neighbors_of_countries.keys()
    return [{'name': country, 'neighbor_count': len(neighbors_of_countries[country])}
            for country in countries]

def assemble_link_list(neighbors_of_countries):
    link_list = []
    for country, neighbors in neighbors_of_countries.items():
        for neighbor, border in neighbors.items():
            country_pairs_sorted = sorted([country, neighbor])
            link = {'source': country_pairs_sorted[0],
                    'target': country_pairs_sorted[1],
                    'border': border}

            if link not in link_list:
                link_list.append(link)

    return link_list

def save_data_as_nodes_and_links(neighbors_of_countries):
    data = {}
    data['nodes'] = assemble_node_list(neighbors_of_countries)
    data['links'] = assemble_link_list(neighbors_of_countries)

    with open('nodes_and_links.json', 'w') as f:
        json.dump(data, f)

def save_countries_and_neighbors(neighbors_of_countries):
    with open('neighbors_of_countries.json', 'w') as f:
        json.dump(neighbors_of_countries, f)


### MAIN

rows_of_countries = fetch_data_rows_from_wikipedia()
countries = get_country_list(rows_of_countries)
neighbors_of_countries = get_neighbors_of_countries(rows_of_countries, countries)
consolidate(neighbors_of_countries)
save_countries_and_neighbors(neighbors_of_countries)
save_data_as_nodes_and_links(neighbors_of_countries)
