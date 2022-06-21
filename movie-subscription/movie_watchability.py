import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import socket

format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=format_str)

def get_price(service_html, price_classname):
	"""
	Searches and parses the HTML for a service and returns the price to watch the movie

	Args:
		service_html (bs4.BeautifulSoup): HTML for the individual service
		price_classname (str): the HTML class that contains the pricing information 

	Returns:
		price (str): the price to watch the movie
	"""
	price = service_html.find('div', class_=price_classname).text
	price = price.replace('HD', '')
	return price.strip()

def add_movie_to_output(movietitle, movieurl, watchoptions, stream_services, rent_services, buy_services):
	"""
	Adds the different options to watch the movie to the output JSON object

	Args:
		movietitle (str): the title of the movie
		movieurl (str): the JustWatch URL for the movie
		watchoptions (dict): contains all of the movies and their available streaming services
		stream_services (list): the services where the movie can be streamed
		rent_services (list): the services where the movie can be rented
		buy_services (list): the services where the movie can be purchased

	Returns:
		Adds the movie services data to the JSON output object
	"""
	return watchoptions['Movies'].append(
		{'Movie Title': movietitle,
		'Movie URL': movieurl,
		'Watch Options': {'Stream': stream_services,
							'Rent': rent_services,
							'Buy': buy_services
						}
		})


def get_services_to(watchtype, soup):
	"""
	Searches the HTML and returns a list of all the services and prices for a particular watch type (stream, rent, buy)

	Args:
		watchtype (str): may be one of three options (stream, rent, buy)
		soup (bs4.BeautifulSoup): the HTML for the entire webpage for the movie

	Returns:
		watchtype_services (list): all the services and their prices for the movie and a watch type
	"""
	watchtype_services = []
	watchtype_section = soup.find_all('div', class_=f'price-comparison__grid__row price-comparison__grid__row--{watchtype} price-comparison__grid__row--block')

	for section in watchtype_section:
		logging.debug(section.prettify())
		services = section.find_all('div', class_='price-comparison__grid__row__element')
		for service in services:
			logging.debug(service.prettify())
			if service.img:
				logging.debug(service.img['title'])
				logging.debug(get_price(service,'price-comparison__grid__row__price'))
				watchtype_services.append( f"{service.img['title'].strip()} | {get_price(service,'price-comparison__grid__row__price')}" )
	return list(set(watchtype_services))

def main():
	# import the data
	movie_requests = pd.read_excel('movie_requests.xlsx')

	# intialize the output JSON object
	now = datetime.now()
	dt_string = now.strftime("%m-%d-%Y")
	watchoptions = {'Metadata': dt_string,
			'Movies': []}

	# loop through all of the movies
	for i in range( len(movie_requests) ):
		movieurl = movie_requests['JustWatch URL'][i]
		logging.debug(movieurl)
		movietitle = movie_requests['Movie Name'][i]
		logging.debug(movietitle)

		page = requests.get(movieurl)
		soup = BeautifulSoup(page.content, 'html.parser')
		logging.debug(soup)

		stream_services = get_services_to('stream', soup)
		logging.debug(stream_services)

		rent_services = get_services_to('rent', soup)
		logging.debug(rent_services)

		buy_services = get_services_to('buy', soup)
		logging.debug(buy_services)

		add_movie_to_output(movietitle, movieurl,watchoptions, stream_services, rent_services, buy_services)
		logging.debug(json.dumps(watchoptions, indent=2))

	logging.info(json.dumps(watchoptions, indent=2))

	with open(f"./movie-watchoptions/{dt_string}.json", "w") as out:
		out.write(json.dumps(watchoptions, indent=2))

if __name__ == '__main__':
	main()