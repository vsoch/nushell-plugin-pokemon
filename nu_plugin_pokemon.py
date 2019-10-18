#!/usr/bin/env python3
import json
import logging
import fileinput
import sys

from pokemon.master import (
    get_pokemon,
    catch_em_all
)
from pokemon.skills import (
    get_ascii, 
    get_avatar
)

logging.basicConfig(filename="/tmp/nu_plugin_pokemon.log",
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(name)s - %(levelname)s - %(message)s')

def print_good_response(response):
    '''a good response confirms to jsonprc 2.0, we include a method "response" and
       params, which should be a dict with key "Ok" and value as the json config,
       (config) an empty list (begin_filter or end_filter) or a list of dict
       responses (filter).
    '''
    json_response = {
        "jsonrpc": "2.0",
        "method": "response",
        "params": {"Ok": response}
    }
    logging.info("Printing response %s" % response)
    print(json.dumps(json_response))
    sys.stdout.flush()


def get_length(string_value):
    string_len = len(string_value["item"]["Primitive"]["String"])
    int_item = {"Primitive": {"Int": string_len}}
    int_value = string_value
    int_value["item"] = int_item
    return int_value


def list_pokemon(do_sort=False):
    '''print list of all names of pokemon in database

       Parameters
       ==========
       do_sort: return list of sorted pokemon (ABC)
    '''
    names = catch_em_all(return_names=True)
 
    if do_sort:
        names.sort()
    for name in names:
        try:
            print(name)
        except:
            pass

def catch_pokemon():
    '''use the get_pokemon function to catch a random pokemon, return it
       (along with stats!) as a single string
    '''
    catch = get_pokemon()   
    for pokemon_id, meta in catch.items():
        response = meta['ascii']
        response = "%s\n%s %s" %(response, meta["name"], meta['link'])
        print(response)


def get_usage():
    return '''Catch an asciinema pokemon on demand.\n
  --avatar AVATAR    generate a pokemon avatar for some unique id.
  --pokemon POKEMON  generate ascii for a particular pokemon (by name)
  --catch            catch a random pokemon!
  --list             list pokemon available
  --list-sorted      list pokemon available (sorted)
  --help             show this usage
'''

def get_config():
    '''return the configuration object
    '''
    return {
      "name": "pokemon",
      "usage": get_usage(),
      "positional": [],
      "rest_positional": None,
      "named": {
          "avatar": {"Optional": "String"},
          "pokemon": {"Optional": "String"},
          "catch": "Switch",
          "help": "Switch",
          "list": "Switch",
          "list-sorted": "Switch",
          "help": "Switch"
      },
      "is_filter": False
    }



def parse_params(input_params):
    '''parse the parameters into an easier to parse object. An example looks 
       like the following (I'm not sure why an empty list is passed as a second
       entry)

	[{'args': {'positional': None,
	   'named': {'switch': {'tag': {'anchor': None,
	      'span': {'start': 58, 'end': 64}},
	     'item': {'Primitive': {'Boolean': True}}},
	    'mandatory': {'tag': {'anchor': None, 'span': {'start': 20, 'end': 32}},
	     'item': {'Primitive': {'String': 'MANDATORYARG'}}},
	    'optional': {'tag': {'anchor': None, 'span': {'start': 44, 'end': 55}},
	     'item': {'Primitive': {'String': 'OPTIONALARG'}}}}},
	  'name_tag': {'anchor': None, 'span': {'start': 0, 'end': 7}}},
	 []]
    '''
    # Just grab the args dictionary
    input_params = input_params[0]
    positional = input_params['args'].get('positional', [])
    named = input_params['args'].get('named', {})

    # We will return lookup dictionary of params
    params = {}

    # Keep a simple dictionary with values we know types for
    for name, values in named.items():

        # is it a String? Boolean?
        value_type = list(values['item']['Primitive'].keys())[0]

        if value_type == "String":
            params[name] = values['item']['Primitive']['String']

        elif value_type == "Boolean":
            params[name] = values['item']['Primitive']['Boolean']

        # If you use other types, add them here

        else:
            logging.info("Invalid paramater type %s:%s" %(name, values))

    return params        



def getTag():
    '''for local testing without Nu, we provide a function to return
       a dummy tag
    '''
    return {"anchor":None, "span":{"end":0,"start":0}}


for line in fileinput.input():

    x = json.loads(line)
    method = x.get("method")

    # Keep log of requests from nu
    logging.info("REQUEST %s" % line)
    logging.info("METHOD %s" % method)

    # Case 1: Nu is asking for the config to discover the plugin
    if method == "config":
        plugin_config = get_config()
        logging.info("plugin-config: %s" % json.dumps(plugin_config))
        print_good_response(plugin_config)
        break

    # Case 3: A filter must return the item filtered with a tag
    elif method == "sink":

        # Parse the parameters into a simpler format, example for each type
        # {'switch': True, 'mandatory': 'MANDATORYARG', 'optional': 'OPTIONALARG'}
        params = parse_params(x['params'])
        logging.info("PARAMS %s" % params)

        if params.get('catch', False):
            logging.info("We want to catch a random pokemon!")
            catch_pokemon()

        elif params.get('list', False):
            logging.info("We want to list Pokemon names.")
            list_pokemon()

        elif params.get('list-sorted', False):
            logging.info("We want to list sorted Pokemon names.")
            list_pokemon(do_sort=True)

        elif params.get('avatar', '') != '':
            logging.info("We want a pokemon avatar!")
            catch = get_avatar(params['avatar'])

        elif params.get('pokemon', '') != '':
            get_ascii(name=params['pokemon'])

        elif params.get('help', False):
            print(get_usage())

        else:
            print(get_usage())

        break

    else:
        break
