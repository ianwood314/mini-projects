import json
import csv
import pandas as pd
import requests
from datetime import datetime
import os.path
from os import path
import logging
import socket

'''
Website for Cyrptocurrency Abbreviations:
	https://abbreviations.yourdictionary.com/articles/major-cryptocurrency-abbreviations.html
'''

format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=format_str)

def get_crypto_ids():
	"""
	Returns a list of all the cryptocurrency abbrevations from the text file containing the cryptocurrencies of interest
	"""
	with open('crypto_ids.txt') as f:
		crypto_ids = f.readlines()
		crypto_ids = [cid.rstrip() for cid in crypto_ids]
	logging.debug(crypto_ids)

	return crypto_ids

def get_price_data(cyrpto_abbrev):
	"""
	Makes a request to the Binance API and returns the current exchange price 
	of the requested cryptocurrency

	Args:
		cyrpto_abbrev (str): abbreviation for the requested cryptocurrency

	Returns:
		price_data (JSON): Contains the abbreviation of the cryptocurrency in the 'symbol' key
			and contains the current exchange price in the 'price' key
	"""
	cyrpto_url = f'https://api.binance.com/api/v3/ticker/price?symbol={cyrpto_abbrev}' # Binance API URL
	price_data = requests.get(cyrpto_url)
	return price_data.json()

def write_price_data(price_data):
	"""
	Writes the price of the cryptocurrency at the current date and time to the CSV file
	for the cryptocurrency. If the cryptocurrency does not have a CSV file, one will be
	created for it

	Args:
		price_data (JSON): Contains the abbreviation of the cryptocurrency in the 'symbol' key
			and contains the current exchange price in the 'price' key
	"""
	cyrpto_abbrev = price_data['symbol']
	price = price_data['price']

	add_headers = not path.exists(f'./price-data/{cyrpto_abbrev}_price_data.csv')
	logging.debug(add_headers)

	with open(f'./price-data/{cyrpto_abbrev}_price_data.csv', 'a') as out:
			writer = csv.writer(out)
			if add_headers:
				writer.writerow(['Date', 'Time', 'Price (USD)'])
			writer.writerow([date(), time(), price])

def date():
	return datetime.now().strftime('%m/%d/%Y')

def time():
	return datetime.now().strftime('%H:%M:%S')

def main():

	crypto_ids = get_crypto_ids()

	for cid in crypto_ids:
		price_data = get_price_data(cid)
		logging.info(json.dumps(price_data, indent=2))
		write_price_data(price_data)

if __name__ == '__main__':
	main()
