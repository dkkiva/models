import requests

# pull in links
# grab csv columns of urls

r = requests.get('https://www.facebook.com/thebigyellowhousesiemreap')

if r.status_code == 404:
	print(r.status_code)
else:
	print('fhdsjk')

