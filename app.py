import shutil
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from urllib.parse import urljoin

import requests

path = 'downloads'
base_url = 'https://pokeapi.co/api/v2/'


if Path.exists(Path(path)):
    shutil.rmtree(path)
Path.mkdir(Path(path))


def get_pokemons_url(url: str, qty: int):
    return requests.get(urljoin(url, f'pokemon/?limit={qty}')).json()['results']


def get_sprite_url(url, sprite='front_default'):
    response = requests.get(url['url'])
    return url['name'], response.json()['sprites'][sprite]


def download_sprite(args, type_='png'):
    name, url = args
    response = requests.get(url)
    fname = f'{path}/{name}.{type_}'
    with open(fname, 'wb') as f:
        f.write(response.content)
    return fname


def pipeline(*funcs):
    def inner(arg):
        state = arg
        for func in funcs:
            state = func(state)

    return inner


target = pipeline(get_sprite_url, download_sprite)


event = Event()
queue = Queue()


def run():
    pokemons = get_pokemons_url(base_url, qty=100)
    [queue.put(pokemon) for pokemon in pokemons]
    event.set()
    queue.put('Kill')


class Worker(Thread):
    def __init__(self, target, queue: Queue, *, name='Worker'):
        super().__init__()
        self._target = target
        self.queue = queue
        self.name = name
        self._stopped = False
        print(self.name, 'started')

    def run(self):
        event.wait()
        while not self.queue.empty():
            pokemon = self.queue.get()
            print(self.name, pokemon)
            if pokemon == 'Kill':
                self.queue.put('Kill')
                self._stopped = True
                break
            self._target(pokemon)


def get_pool(n_th: int):
    return [Worker(target=target, queue=queue, name=f'Worker {n}') for n in range(n_th)]


print(queue.queue)
print('start')
ths = get_pool(25)
[th.start() for th in ths]
run()
