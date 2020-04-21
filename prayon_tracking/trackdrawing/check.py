import requests
from .models import ExtractSAP

def languagetool_check(text):
    api_url = 'http://localhost:8081/v2/'
    lang = 'fr'

    params = {
        'language': lang,
        'text': text
    }

    session = requests.session()

    matches = session.get(api_url + 'check', params=params)

    return matches.json()

def insert_span(str, start, length, span_class):
    return '<SPAN class=\'' + span_class + '\'>' + str[start:start+length] + '</SPAN>'


def format_error(text):
    matches = languagetool_check(text)
    if matches['matches']:
        formatted_error=[]
        for error in matches['matches']:
            formatted_error.append(insert_span(text,error['offset'], error['length'], error['rule']['id']))

        offset = 0
        formatted_string = ''

        for i, error in enumerate(matches['matches']):
            formatted_string = formatted_string + text[offset:error['offset']]+formatted_error[i]
            offset = error['offset']+error['length']

        formatted_string=formatted_string+text[offset:]
    else:
        formatted_string = text

    return formatted_string
