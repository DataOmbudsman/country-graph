# Country Contiguity Graph

An [interactive visualization][graph] that shows how the countries of the world are connected to each other via land borders.

[graph]: https://dataombudsman.github.io/country-graph/

## Data

There are two data files to be found in `data`, both scraped from Wikipedia ([List of countries and territories by land borders][data1], [List of sovereign states and dependent territories by continent][data2]) with Python scripts stored in `scripts`.

- `data/neighbors_of_countries.json` contains the list of neighbors for each country. Neighbor information contains the name of the neighbor and the length of the common land border (in km) in the form of `"Finland": {"Norway": 736, "Sweden": 614, Russia": 1340}`.
- `data/nodes_and_links.json` is a processed form of the previous file, directly feeding the graph.  
Under key `nodes`, a list of country information is provided. Country information is in the form of `{"name": "Hungary", "neighbor_count": 7, "continents": ["Europe"]}`.  
Under key `links`, a list of border information is provided. Border information is in the form of `{"source": "Albania", "target": "Greece", "border": 282}`.

[data1]: https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_land_borders
[data2]: https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_by_continent
