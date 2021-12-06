import shutil
from pathlib import Path
from urllib.parse import urljoin

import requests

path = 'downloads'
base_url = 'https://pokeapi.co/api/v2/'


if Path.exists(Path(path)):
    shutil.rmtree(path)
Path.mkdir(Path(path))


def pokemons(url: str, qty: int):
    return requests.get(urljoin(url, f'pokemon/?limit={qty}')).json()['results']


def get_sprite_url(url, sprite='front_default'):
    response = requests.get(url)
    return response.json()['sprites'][sprite]


def download_pokemon(name: str, url: str, type_='png'):
    response = requests.get(url)
    fname = f'{path}/{name}.{type_}'
    with open(fname, 'wb') as f:
        f.write(response.content)
    return fname


def run():
    for pokemon in pokemons(base_url, qty=100):
        name = pokemon['name']
        pokemon_url = pokemon['url']
        sprite_url = get_sprite_url(pokemon_url)
        download_pokemon(name, sprite_url)


run()
