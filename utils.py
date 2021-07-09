import codecs
import json
import os


class Config:

    def __init__(self, bot, test_mode=False):
        self._bot = bot
        self._data = None
        self._test_mode = test_mode
        self.load()

    def load(self):
        if not os.path.isfile('config.json'):
            raise Exception('The config wasn\'t found!')
        with codecs.open('config.json', 'r', 'utf-8-sig') as f:
            self._data = json.load(f)

    def save(self):
        if not os.path.isfile('config.json'):
            raise Exception('The config wasn\'t found!')
        with open('config.json', 'w') as f:
            json.dump(self._data, f, indent=2)

    def get(self, path):
        path = path.lower().replace('{mode}', 'production' if not self._test_mode else 'staging')
        paths = path.split('.') if path != '' else []
        current = self._data
        for p in paths:
            try:
                current = current[p]
            except KeyError:
                raise NotFound('The config value wasn\'t found.')
        return current

    def set(self, path, value):
        path = path.lower().replace('{mode}', 'production' if not self._test_mode else 'staging')
        paths = path.split('.')
        current_value = value
        for i in range(len(paths)):
            current = self.get('.'.join(paths[:len(paths) - (i + 1)]))
            current[paths[len(paths) - (i + 1)]] = current_value
            current_value = current
        self._data = current_value
        self.save()


class NotFound(Exception):
    pass

#Coded by Focus™#0001
#don't forget to give me credits
