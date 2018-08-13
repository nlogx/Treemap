"""
=== Module Description ===
This module contains a new class, PopulationTree, which is used to model
population data drawn from the World Bank API.
"""
import json
import urllib.request as request

from tree_data import AbstractTree


# Constants for the World Bank API urls.
WORLD_BANK_BASE = 'http://api.worldbank.org/countries'
WORLD_BANK_POPULATIONS = (
    WORLD_BANK_BASE +
    '/all/indicators/SP.POP.TOTL?format=json&date=2014:2014&per_page=270'
)
WORLD_BANK_REGIONS = (
    WORLD_BANK_BASE + '?format=json&date=2014:2014&per_page=310'
)


class PopulationTree(AbstractTree):
    """A tree representation of country population data.

    This tree always has three levels:
      - The root represents the entire world.
      - Each node in the second level is a region (defined by the World Bank).
      - Each node in the third level is a country.

    The data_size attribute corresponds to the 2014 population of the country,
    as reported by the World Bank.

    See https://datahelpdesk.worldbank.org/ for details about this API.
    """
    def __init__(self, world, root=None, subtrees=None, data_size=0):
        """Initialize a new PopulationTree.

        If <world> is True, then this tree is the root of the population tree,
        and it should load data from the World Bank API.

        If <world> is False, pass the other arguments directly to the superclass
        constructor.

        @type self: PopulationTree
        @type world: bool
        @type root: object
        @type subtrees: list[PopulationTree] | None
        @type data_size: int
        """
        if world:
            region_trees = _load_data()
            AbstractTree.__init__(self, 'World', region_trees)
        else:
            if subtrees is None:
                subtrees = []
            AbstractTree.__init__(self, root, subtrees, data_size)

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the world to a country.

        @type self: AbstractTree
        @rtype: str
        """
        return ' -> '


def _load_data():
    """Create a list of trees corresponding to different world regions.

    Each tree consists of a root node -- the region -- attached to one or
    more leaves -- the countries in that region.

    @rtype: list[PopulationTree]
    """
    # Get data from World Bank API.
    country_populations = _get_population_data()
    regions = _get_region_data()

    trees = []  # [RegionsTrees (with countries)]
    for region in regions:
        countries = []  # [CountriesTrees (with population)]
        for country in regions[region]:
            population = 0
            if country in country_populations:
                population = country_populations[country]
            countries.append(PopulationTree(False, country, None, population))
        trees.append(PopulationTree(False, region, countries))
    return trees


def _get_population_data():
    """Return country population data from the World Bank.

    The return value is a dictionary, where the keys are country names,
    and the values are the corresponding populations of those countries.

    Ignore all countries that do not have any population data,
    or population data that cannot be read as an int.

    @rtype: dict[str, int]
    """

    _, population_data = _get_json_data(WORLD_BANK_POPULATIONS)
    population_data = population_data[47:]

    countries = {}

    for country in population_data:
        if country['value'] is not None:
            pop, name = country['value'], country['country']['value']
            countries[name] = int(pop)
    return countries


def _get_region_data():
    """Return country region data from the World Bank.

    The return value is a dictionary, where the keys are region names,
    and the values a list of country names contained in that region.

    Ignore all regions that do not contain any countries.

    @rtype: dict[str, list[str]]
    """
    # ignore the first component of the returned JSON, which is metadata.
    _, country_data = _get_json_data(WORLD_BANK_REGIONS)

    regions = {}

    for country in country_data:
        if country['region']['value'] != 'Aggregates':
            name, region = country['name'], country['region']['value']
            if region in regions:
                regions[region].append(name)
            else:
                regions[region] = [name]
    return regions


def _get_json_data(url):
    """Return a dictionary representing the JSON response from the given url.

    @type url: str
    @rtype: Dict
    """
    response = request.urlopen(url)
    return json.loads(response.read().decode())


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config='pylintrc.txt')
