#!/usr/bin/python3
from functools import lru_cache

import requests
from requests.exceptions import ConnectionError


class YandexException(Exception):
    """Common API wrapper exception."""
    pass


class YandexTranslate:
    """YandexTranslate API wrapper."""

    URL = 'https://translate.yandex.net/api/v1.5/tr.json/'

    def __init__(self, api_key):
        """Use an API key provided by Yandex.
        To obtain a key, visit https://translate.yandex.com/developers
        """
        self.api_key = api_key
        self._session = requests.Session()

    def _get_api_response(self, endpoint, payload):
        """Common request method for API communication."""
        try:
            response = self._session.get(self.URL + endpoint, params=payload)
            if response.status_code != 200:
                raise YandexException(response.json())
            return response.json()
        except ConnectionError:
            raise YandexException('API unavailable')

    @property
    @lru_cache(maxsize=1)
    def supported_languages(self):
        """Return a list of currently supported languages.
        All languages are represented using ISO 639-1 language codes.
        """
        payload = {
            'ui': 'en',
            'key': self.api_key
        }
        return self._get_api_response('getLangs', payload).get('langs')

    def _get_translate_direction(self, source, target):
        """Raise an exception if either source or target language are not 
        currently supported by the Yandex Translate API.
        """
        if target not in self.supported_languages:
            raise YandexException('target language \'{}\' not supported'.format(target))
        if source is None:
            return target
        if source not in self.supported_languages:
            raise YandexException('source language \'{}\' not supported'.format(source))
        return '{}-{}'.format(source, target)

    def translate(self, text, target='en', source=None):
        """Return JSON response containing a list of translated text.

        Text will translate to English by default. Translations may not be
        fully accurate if source is not specified, as API will detect source
        language.

        Only use ISO 639-1 language codes with this method.
        """
        translate_direction = self._get_translate_direction(source, target)
        payload = {
            'text': text,
            'format': 'plain',
            'lang': translate_direction,
            'key': self.api_key
        }
        return self._get_api_response('translate', payload)

    def detect_language(self, text):
        """Return JSON response containing detected language of text.
        Languages are represented using ISO 639-1 language codes.
        """
        payload = {
            'text': text,
            'format': 'plain',
            'key': self.api_key
        }
        return self._get_api_response('detect', payload)


if __name__ == '__main__':
    y = YandexTranslate('trnsl.1.1.20170926T212748Z.c9c27fd0296048d9.99429f12be71a862b1767c0039cd8bb7beafc29f')
    print(y.detect_language('A po jakiemu to?'))
