# -*- coding: utf-8 -*-

import re
import sys
import os
import urllib
import urllib2
import requests
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import base64
import time
import random
import inputstreamhelper

mode = None

__addon_id__= 'plugin.video.hbogohu'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id = 'plugin.video.hbogohu')

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
MUA = 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; Nexus 5X Build/OPP3.170518.006)'

LIST_CONTAINER_CONTENT_TYPE_MOVIE = 1
LIST_CONTAINER_CONTENT_TYPE_SERIES = 2
LIST_CONTAINER_CONTENT_TYPE_SERIES_EPISODE = 3

NON_AUTHENTICATED_OP_ID = '00000000-0000-0000-0000-000000000000'

se = __settings__.getSetting('se')
language = __settings__.getSetting('language')

params = None
url = None
name = None

if language == '0':
	lang = 'Hungarian'
	Code = 'HUN'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.Hungarian.Forced.srt')
elif language == '1':
	lang = 'Hungarian'
	Code = 'HUN'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.Hungarian.Forced.srt')
elif language == '2':
	lang = 'English'
	Code = 'ENG'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.English.Forced.srt')


md = xbmc.translatePath(__Addon.getAddonInfo('path') + '/resources/media/')
search_string = urllib.unquote_plus(__settings__.getSetting('lastsearch'))

operator = __settings__.getSetting('operator')

op_ids = [
	NON_AUTHENTICATED_OP_ID, # Anonymous NoAuthenticated
	'15276cb7-7f53-432a-8ed5-a32038614bbf', # HBO GO webes
	'48f48c5b-e9e4-4fca-833b-2fa26fb1ad22', # UPC Direct
	'b7728684-13d5-46d9-a9a4-97d676cdaeec', # DIGI
	'04459649-8a90-46f1-9390-0cd5b1958a5d', # Magyar Telekom Nyrt.
	'e71fabae-66b6-4972-9823-8743f8fcf06f', # Telenor MyTV
	'1ca45800-464a-4e9c-8f15-8d822ad7d8a1', # UPC Magyarország
	'f2230905-8e25-4245-80f9-fccf67a24005', # INVITEL
	'383cd446-06fb-4a59-8d39-200a3e9bcf6f', # Celldömölki Kábeltelevízió Kft.
	'fe106c75-293b-42e6-b211-c7446835b548', # Eurocable – Hello Digital
	'42677aa5-7576-4dc7-9004-347b279e4e5d', # HFC-Network Kft.
	'3a3cce31-fb19-470a-9bb5-6947c4ac9996', # HIR-SAT 2000 Kft.
	'c6441ec8-e30f-44b6-837a-beb2eb971395', # Jurop Telekom
	'd91341c2-3542-40d4-adab-40b644798327', # Kabelszat 2002
	'18fb0ff5-9cfa-4042-be00-638c5d34e553', # Klapka Lakásszövetkezet
	'97cddb59-79e3-4090-be03-89a6ae06f5ec', # Lát-Sat Kft.
	'c48c350f-a9db-4eb6-97a6-9b659e2db47f', # MinDig TV Extra
	'7982d5c7-63df-431d-806e-54f98fdfa36a', # PARISAT
	'18f536a3-ecac-42f1-91f1-2bbc3e6cfe81', # PR-TELECOM
	'adb99277-3899-439e-8bdf-c749c90493cd', # TARR Kft
	'5729f013-f01d-4cc3-b048-fe5c91c64296', # Vác Városi Kábeltelevízió Kft.
	'b4f422f7-5424-4116-b72d-7cede85ead4e', # Vidanet Zrt.
	'6a52efe0-54c4-4197-8c55-86ee7a63cd04', # HBO Development Hungary
	'f320aa2c-e40e-49c2-8cdd-1ebef2ac6f26', # HBO GO Vip/Club Hungary
]
op_id = op_ids[int(operator)];

individualization = ''
goToken = ''
customerId = ''
GOcustomerId = ''
sessionId = NON_AUTHENTICATED_OP_ID
FavoritesGroupId = ''

loggedin_headers = {
	'User-Agent': UA,
	'Accept': '*/*',
	'Accept-Language': 'en-US,en;q=0.5',
	'Referer': 'https://www.hbogo.hu/',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Origin': 'https://www.hbogo.hu',
	'X-Requested-With': 'XMLHttpRequest',
	'GO-Language': 'HUN',
	'GO-requiredPlatform': 'CHBR',
	'GO-Token': '',
	'GO-SessionId': '',
	'GO-swVersion': '4.8.0',
	'GO-CustomerId': '',
	'Connection': 'keep-alive',
	'Accept-Encoding': ''
}

# individualization es customerId eltarolasa
def storeIndiv(indiv, custid):
	global individualization
	global customerId

	individualization = __settings__.getSetting('individualization')
	if individualization == '':
		__settings__.setSetting('individualization', indiv)
		individualization = indiv

	customerId = __settings__.getSetting('customerId')
	if customerId == '':
		__settings__.setSetting('customerId', custid)
		customerId = custid

# FavoritesGroupId eltarolasa
def storeFavgroup(favgroupid):
	global FavoritesGroupId

	FavoritesGroupId = __settings__.getSetting('FavoritesGroupId')
	if FavoritesGroupId == '':
		__settings__.setSetting('FavoritesGroupId', favgroupid)
		FavoritesGroupId = favgroupid

# eszkoz regisztracioja
def SILENTREGISTER():
	global goToken
	global individualization
	global customerId
	global sessionId

	req = urllib2.Request('https://hu.hbogo.eu/services/settings/silentregister.aspx', None, loggedin_headers)

	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	if jsonrsp['Data']['ErrorMessage']:
		xbmcgui.Dialog().ok('Error', jsonrsp['Data']['ErrorMessage'])

	indiv = jsonrsp['Data']['Customer']['CurrentDevice']['Individualization']
	custid = jsonrsp['Data']['Customer']['CurrentDevice']['Id'];
	storeIndiv(indiv, custid)

	sessionId= jsonrsp['Data']['SessionId']
	return jsonrsp

# lejatszasi lista id lekerdezes
def GETFAVORITEGROUP():
	global FavoritesGroupId

	req = urllib2.Request('https://huapi.hbogo.eu/v7/Settings/json/HUN/COMP', None, loggedin_headers)

	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	favgroupId = jsonrsp['FavoritesGroupId']
	storeFavgroup(favgroupId)

# belepes
def LOGIN():
	global sessionId
	global goToken
	global customerId
	global GOcustomerId
	global individualization
	global loggedin_headers
	global FavoritesGroupId

	operator = __settings__.getSetting('operator')
	username = __settings__.getSetting('username')
	password = __settings__.getSetting('password')
	customerId = __settings__.getSetting('customerId')
	individualization = __settings__.getSetting('individualization')
	FavoritesGroupId = __settings__.getSetting('FavoritesGroupId')

	if (individualization == '' or customerId == ''):
		jsonrsp = SILENTREGISTER()

	if (FavoritesGroupId == ''):
		GETFAVORITEGROUP()

	if (username == '' or password == ''):
		xbmcgui.Dialog().ok('Hiba', 'Kérlek add meg a beállításoknál a belépési adatokat!')
		xbmcaddon.Addon(id = 'plugin.video.hbogohu').openSettings('Accunt')
		xbmc.executebuiltin('Container.Refresh')
		LOGIN()

	headers = {
		'Origin': 'https://gateway.hbogo.eu',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'hu,en-US;q=0.9,en;q=0.8',
		'User-Agent': UA,
		'GO-Token': '',
		'Accept': 'application/json',
		'GO-SessionId': '',
		'Referer': 'https://gateway.hbogo.eu/signin/form',
		'Connection': 'keep-alive',
		'GO-CustomerId': NON_AUTHENTICATED_OP_ID,
		'Content-Type': 'application/json',
	}

    # todo: a gatewayes hivasok helyett lehet vissza lehet alni a bulgar verziora, de jelenleg igy tuti mukodik
    # a linkek a weboldalrol lettek kiszedve
	if operator == '1':
		url = 'https://api.ugw.hbogo.eu/v3.0/Authentication/HUN/JSON/HUN/COMP'
	else:
		url = 'https://hugwapi.hbogo.eu/v2.1/Authentication/json/HUN/COMP'

	data_obj = {
		'Action': 'L',
		'AppLanguage': None,
		'ActivationCode': None,
		'AllowedContents': [],
		'AudioLanguage': None,
		'AutoPlayNext': False,
		'BirthYear': 1,
		'CurrentDevice': {
			'AppLanguage':'',
			'AutoPlayNext': False,
			'Brand': 'Chromium',
			'CreatedDate': '',
			'DeletedDate': '',
			'Id': NON_AUTHENTICATED_OP_ID,
			'Individualization': individualization,
			'IsDeleted': False,
			'LastUsed': '',
			'Modell': '62',
			'Name': '',
			'OSName': 'Ubuntu',
			'OSVersion': 'undefined',
			'Platform': 'COMP',
			'SWVersion': '2.4.2.4025.240',
			'SubtitleSize': ''
		},
		'CustomerCode': '',
		'DebugMode': False,
		'DefaultSubtitleLanguage': None,
		'EmailAddress': username,
		'FirstName': '',
		'Gender': 0,
		'Id': NON_AUTHENTICATED_OP_ID,
		'IsAnonymus': True,
		'IsPromo': False,
		'Language': 'HUN',
		'LastName': '',
		'Nick': '',
		'NotificationChanges': 0,
		'OperatorId': op_id,
		'OperatorName': '',
		'OperatorToken': '',
		'ParentalControl': {
			'Active': False,
			'Password': '',
			'Rating': 0,
			'ReferenceId': NON_AUTHENTICATED_OP_ID
		},
		'Password': password,
		'PromoCode': '',
		'ReferenceId': NON_AUTHENTICATED_OP_ID,
		'SecondaryEmailAddress': '',
		'SecondarySpecificData': None,
		'ServiceCode': '',
		'SubscribeForNewsletter': False,
		'SubscState': None,
		'SubtitleSize': '',
		'TVPinCode': '',
		'ZipCode': ''
	}

	data = json.dumps(data_obj)
	r = requests.post(url, headers = headers, data = data)

	jsonrspl = json.loads(r.text)

	try:
		if jsonrspl['ErrorMessage']:
			xbmcgui.Dialog().ok('Login Hiba!', jsonrspl['ErrorMessage'])
	except:
		pass

	customerId = jsonrspl['Customer']['CurrentDevice']['Id']
	individualization = jsonrspl['Customer']['CurrentDevice']['Individualization']

	sessionId = jsonrspl['SessionId']
	if sessionId == NON_AUTHENTICATED_OP_ID:
		xbmcgui.Dialog().ok('Login Hiba!', 'Ellenőrizd a belépési adatokat!')
		xbmcaddon.Addon(id = 'plugin.video.hbogohu').openSettings('Accunt')
		xbmc.executebuiltin('Action(Back)')
	else:
		goToken = jsonrspl['Token']
		GOcustomerId = jsonrspl['Customer']['Id']

		loggedin_headers['GO-SessionId'] = str(sessionId)
		loggedin_headers['GO-Token'] = str(goToken)
		loggedin_headers['GO-CustomerId'] = str(GOcustomerId)

# kategoria
def CATEGORIES():
	global FavoritesGroupId

	addDir('Keresés...', 'search', '', 4,'')

	if (FavoritesGroupId == ''):
		GETFAVORITEGROUP()

	if (FavoritesGroupId != ''):
		addDir('Lejátszási listád', 'https://huapi.hbogo.eu/v7/CustomerGroup/json/HUN/COMP/' + FavoritesGroupId + '/-/-/-/1000/-/-/false', '', 1, md + 'FavoritesFolder.png')

	req = urllib2.Request('https://huapi.hbogo.eu/v5/Groups/json/HUN/COMP', None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Hiba', jsonrsp['ErrorMessage'])
	except:
		pass

	for cat in range(0, len(jsonrsp['Items'])):
		addDir(jsonrsp['Items'][cat]['Name'].encode('utf-8', 'ignore'), jsonrsp['Items'][cat]['ObjectUrl'].replace('/0/{sort}/{pageIndex}/{pageSize}/0/0', '/0/0/1/1024/0/0'), '', 1, md + 'DefaultFolder.png')

def list_add_movie_link(item):
	# if it's a movie    # addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
	plot = item['Abstract'].encode('utf-8', 'ignore')

	if 'AvailabilityTo' in item:
		if item['AvailabilityTo'] is not None:

			plot = plot + ' A film megtekinthető: ' + item['AvailabilityTo'].encode('utf-8', 'ignore')

	object_url = item['ObjectUrl']
	age_rating = item['AgeRating']
	imdb = item['ImdbRate']
	background_url = item['BackgroundUrl']
	cast = [item['Cast'].split(', ')][0]
	director = item['Director']
	writer = item['Writer']
	duration = item['Duration']
	genre = item['Genre']
	name = item['Name'].encode('utf-8', 'ignore')
	original_name = item['OriginalName']
	production_year = item['ProductionYear']

	addLink(object_url, plot, age_rating, imdb, background_url, cast, director, writer, duration, genre, name, original_name, production_year, 5)
	#xbmc.log('GO: FILMI: DUMP: ' + item['ObjectUrl'], xbmc.LOGNOTICE)

def list_add_series_episode(item):
	# If it's a series episode    # addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
	plot = item['Abstract'].encode('utf-8', 'ignore')
	if item['AvailabilityTo'] is not None:
		plot = plot + ' Az epizód megtekinthető: ' + item['AvailabilityTo'].encode('utf-8', 'ignore')

	object_url = item['ObjectUrl']
	age_rating = item['AgeRating']
	imdb = item['ImdbRate']
	background_url = item['BackgroundUrl']
	cast = [item['Cast'].split(', ')][0]
	director = item['Director']
	writer = item['Writer']
	duration = item['Duration']
	genre = item['Genre']
	name = item['SeriesName'].encode('utf-8', 'ignore') + ' - ' + str(item['SeasonIndex']) + '. ÉVAD ' + str(item['Index']) + '. RÉSZ'
	original_name = item['OriginalName']
	production_year = item['ProductionYear']

	addLink(object_url, plot, age_rating, imdb, background_url, cast, director, writer, duration, genre, name, original_name, production_year, 5)

def list_add_series(item):
	# If it's a series
	name = item['Name'].encode('utf-8', 'ignore')
	object_url = item['ObjectUrl']
	abstract = item['Abstract'].encode('utf-8', 'ignore')
	mode = 2
	background_url = item['BackgroundUrl']
	addDir(name, object_url, abstract, mode, background_url)

def list_add_subcategory(item):
	addDir(item['Name'].encode('utf-8', 'ignore'), item['ObjectUrl'], '', 1, md + 'DefaultFolder.png')

# lista
def LIST(url):
	global sessionId
	global loggedin_headers

	if sessionId == NON_AUTHENTICATED_OP_ID:
		LOGIN()

	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Hiba', jsonrsp['ErrorMessage'])
	except:
		pass
	# If there is a subcategory / genres
	if len(jsonrsp['Container']) > 1:
		for Container in range(0, len(jsonrsp['Container'])):
			item = jsonrsp['Container'][Container]
			list_add_subcategory(item)
	else:
		items = jsonrsp['Container'][0]['Contents']['Items']

		for titles in range(0, len(items)):
			item = items[titles]
			content_type = item['ContentType']

			if content_type == LIST_CONTAINER_CONTENT_TYPE_MOVIE: #1 = MOVIE/EXTRAS, 2 = SERIES(serial), 3 = SERIES(episode)
				list_add_movie_link(item)

			elif content_type == LIST_CONTAINER_CONTENT_TYPE_SERIES_EPISODE:
				list_add_series_episode(item)

			else:
				list_add_series(item)


def season_add_season(item):
	addDir(item['Name'].encode('utf-8', 'ignore'), item['ObjectUrl'], item['Abstract'].encode('utf-8', 'ignore'), 3, item['BackgroundUrl'])

# evadok
def SEASON(url):
	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Hiba', jsonrsp['ErrorMessage'])
	except:
		pass

	items = jsonrsp['Parent']['ChildContents']['Items']
	for season in range(0, len(items)):
		item = items[season];
		season_add_season(item)

def episode_add_episode(item):
	# addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
	plot = item['Abstract'].encode('utf-8', 'ignore')
	if 'AvailabilityTo' in item:
		if item['AvailabilityTo'] is not None:
			plot = plot + ' Az epizód megtekinthető: ' + item['AvailabilityTo'].encode('utf-8', 'ignore')

	object_url = item['ObjectUrl']
	age_rating = item['AgeRating']
	imdb = item['ImdbRate']
	background_url = item['BackgroundUrl']
	cast = [item['Cast'].split(', ')][0]
	director = item['Director']
	writer = item['Writer']
	duration = item['Duration']
	genre = item['Genre']
	name = item['SeriesName'].encode('utf-8', 'ignore') + ' - ' + str(item['SeasonIndex']) + '. ÉVAD ' + item['Name'].encode('utf-8', 'ignore')
	original_name = item['OriginalName']
	production_year = item['ProductionYear']

	addLink(object_url, plot, age_rating, imdb, background_url, cast, director, writer, duration, genre, name, original_name, production_year, 5)

# epizodok
def EPISODE(url):
	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Hiba', jsonrsp['ErrorMessage'])
	except:
		pass

	items = jsonrsp['ChildContents']['Items']
	for episode in range(0, len(items)):
		item = items[episode]
		episode_add_episode(item)

# lejatszas
def PLAY(url):
	global goToken
	global individualization
	global customerId
	global GOcustomerId
	global sessionId
	global loggedin_headers

	if sessionId == NON_AUTHENTICATED_OP_ID:
		LOGIN()

	if se == 'true':
		try:
			#http://huapi.hbogo.eu/player50.svc/Content/json/HUN/COMP/
			#http://huapi.hbogo.eu/player50.svc/Content/json/HUN/APPLE/
			#http://huapi.hbogo.eu/player50.svc/Content/json/HUN/SONY/
			req = urllib2.Request('http://huapi.hbogo.eu/v5/Content/json/HUN/MOBI/' + cid, None, loggedin_headers)
			req.add_header('User-Agent', MUA)
			opener = urllib2.build_opener()
			f = opener.open(req)
			jsonrsps = json.loads(f.read())

			try:
				if jsonrsps['Subtitles'][0]['Code'] == Code:
					slink = jsonrsps['Subtitles'][0]['Url']
				elif jsonrsps['Subtitles'][1]['Code'] == Code:
					slink = jsonrsps['Subtitles'][1]['Url']
				req = urllib2.Request(slink, None, loggedin_headers)
				response = urllib2.urlopen(req)
				data = response.read()
				response.close()

				subs = re.compile('<p[^>]+begin="([^"]+)\D(\d+)"[^>]+end="([^"]+)\D(\d+)"[^>]*>([\w\W]+?)</p>').findall(data)
				row = 0
				buffer = ''
				for sub in subs:
					row = row + 1
					buffer += str(row) + '\n'
					buffer += '%s,%03d' % (sub[0], int(sub[1])) + ' --> ' + '%s,%03d' % (sub[2], int(sub[3])) + '\n'
					buffer += urllib.unquote_plus(sub[4]).replace('<br/>', '\n').replace('<br />', '\n').replace('\r\n', '').replace('&lt;', '<').replace('&gt;', '>').replace('\n    ','').strip()
					buffer += '\n\n'
					sub = 'true'
					with open(srtsubs_path, "w") as subfile:
						subfile.write(buffer)

				if sub != 'true':
					raise Exception()

			except:
				sub = 'false'
		except:
			sub = 'false'


	purchase_payload = '<Purchase xmlns="go:v5:interop"><AllowHighResolution>true</AllowHighResolution><ContentId>'+ cid + '</ContentId><CustomerId>' + GOcustomerId + '</CustomerId><Individualization>' + individualization + '</Individualization><OperatorId>' + op_id + '</OperatorId><ClientInfo></ClientInfo><IsFree>false</IsFree><UseInteractivity>false</UseInteractivity></Purchase>'

	purchase_headers = {
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding': '',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'GO-CustomerId': str(GOcustomerId),
		'GO-requiredPlatform': 'CHBR',
		'GO-SessionId': str(sessionId),
		'GO-swVersion': '4.7.4',
		'GO-Token': str(goToken),
		'Host': 'huapi.hbogo.eu',
		'Referer': 'https://hbogo.hu/',
		'Origin': 'https://www.hbogo.hu',
		'User-Agent': UA
		}

	req = urllib2.Request('https://huapi.hbogo.eu/v5/Purchase/Json/HUN/COMP', purchase_payload, purchase_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrspp = json.loads(f.read())

	try:
		if jsonrspp['ErrorMessage']:
			xbmcgui.Dialog().ok('Hiba', jsonrspp['ErrorMessage'])
	except:
		pass

	MediaUrl = jsonrspp['Purchase']['MediaUrl'] + '/Manifest'
	PlayerSessionId = jsonrspp['Purchase']['PlayerSessionId']
	x_dt_auth_token = jsonrspp['Purchase']['AuthToken']

	dt_custom_data = base64.b64encode(json.dumps({
		'userId': GOcustomerId,
		'sessionId': PlayerSessionId,
		'merchant': 'hboeurope',
	}))


	li = xbmcgui.ListItem(iconImage = thumbnail, thumbnailImage = thumbnail, path = MediaUrl)
	if (se == 'true' and sub == 'true'):
		li.setSubtitles([srtsubs_path])
	license_server = 'https://lic.drmtoday.com/license-proxy-widevine/cenc/'
	license_headers = urllib.urlencode({
		'dt-custom-data': dt_custom_data,
		'x-dt-auth-token': x_dt_auth_token,
		'Origin': 'https://www.hbogo.hu',
		'Content-Type': ''
		})
	license_key = license_server + '|' + license_headers + '|R{SSM}|JBlicense'

	protocol = 'ism'
	drm = 'com.widevine.alpha'
	is_helper = inputstreamhelper.Helper(protocol, drm = drm)
	is_helper.check_inputstream()
	li.setProperty('inputstreamaddon', 'inputstream.adaptive')
	li.setProperty('inputstream.adaptive.manifest_type', protocol)
	li.setProperty('inputstream.adaptive.license_type', drm)
	li.setProperty('inputstream.adaptive.license_data', 'ZmtqM2xqYVNkZmFsa3Izag==')
	li.setProperty('inputstream.adaptive.license_key', license_key)

	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

	#Задаване на външни субтитри, ако е избран този режим
	#if (se == 'true' and sub == 'true'):
	#	while not xbmc.Player().isPlaying():
	#		xbmc.sleep(42)
	#		xbmc.Player().setSubtitles(srtsubs_path)

SEARCH_CONTENT_TYPE_MOVIE = 1
SEARCH_CONTENT_TYPE_MOVIE_ALT = 7
SEARCH_CONTENT_TYPE_SERIES = 2
SEARCH_CONTENT_TYPE_SERIES_EPISODE = 3

def search_add_movie(item):
	object_url = item['ObjectUrl']
	plot = item['Abstract'].encode('utf-8', 'ignore')
	age_rating = item['AgeRating']
	imdb = item['ImdbRate']
	background_url = item['BackgroundUrl']
	cast = [item['Cast'].split(', ')][0]
	director = item['Director']
	writer = item['Writer']
	duration = item['Duration']
	genre = item['Genre']
	name = item['Name'].encode('utf-8', 'ignore')
	original_name = item['OriginalName']
	production_year = item['ProductionYear']

	addLink(object_url, plot, age_rating, imdb, background_url, cast, director, writer, duration, genre, name, original_name, production_year, 5)

def search_add_series_episode(item):
	object_url = item['ObjectUrl']
	plot = item['Abstract'].encode('utf-8', 'ignore')
	age_rating = item['AgeRating']
	imdb = item['ImdbRate']
	background_url = item['BackgroundUrl']
	cast = [item['Cast'].split(', ')][0]
	director = item['Director']
	writer = item['Writer']
	duration = item['Duration']
	genre = item['Genre']
	name = item['SeriesName'].encode('utf-8', 'ignore') + ' ' + item['Name'].encode('utf-8', 'ignore')
	original_name = item['OriginalName']
	production_year = item['ProductionYear']

	addLink(object_url, plot, age_rating, imdb, background_url, cast, director, writer, duration, genre, name, original_name, production_year, 5)

def search_add_series(item):
	name = item['Name'].encode('utf-8', 'ignore')
	object_url = item['ObjectUrl']
	plot = item['Abstract'].encode('utf-8', 'ignore')
	background_url = item['BackgroundUrl']
	addDir(name, object_url, plot, 2, background_url)

def SEARCH():
	keyb = xbmc.Keyboard(search_string, 'Filmek, sorozatok keresése...')
	keyb.doModal()
	searchText = ''
	if (keyb.isConfirmed()):
		searchText = urllib.quote_plus(keyb.getText())
		if searchText == '':
			addDir('Nincs találat', '', '', '', md + 'DefaultFolderBack.png')
		else:
			__settings__.setSetting('lastsearch', searchText)

			req = urllib2.Request('https://huapi.hbogo.eu/v5/Search/Json/HUN/COMP/' + searchText.decode('utf-8', 'ignore').encode('utf-8', 'ignore') + '/0', None, loggedin_headers)
			opener = urllib2.build_opener()
			f = opener.open(req)
			jsonrsp = json.loads(f.read())

			try:
				if jsonrsp['ErrorMessage']:
					xbmcgui.Dialog().ok('Hiba', jsonrsp['ErrorMessage'])
			except:
				pass

			br = 0
			items = jsonrsp['Container'][0]['Contents']['Items']
			for index in range(0, len(items)):
				item = items[index]
				if (item['ContentType'] == SEARCH_CONTENT_TYPE_MOVIE or item['ContentType'] == SEARCH_CONTENT_TYPE_MOVIE_ALT): #1,7 = MOVIE/EXTRAS, 2 = SERIES(serial), 3 = SERIES(episode)
					#Ако е филм    # addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
					search_add_movie(item)
				elif item['ContentType'] == SEARCH_CONTENT_TYPE_SERIES_EPISODE:
					#Ако е Epizód на сериал    # addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
					search_add_series_episode(item)
				else:
					search_add_series(item)
					#Ако е сериал
				br = br + 1
			if br == 0:
				addDir('Nincs találat', '', '', '', md + 'DefaultFolderBack.png')

def addLink(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode):
	cid = ou.rsplit('/', 2)[1]

	u = sys.argv[0] + '?' + urllib.urlencode({
		'url': url,
		'mode': str(mode),
		'name:': name,
		'cid': cid,
		'thumbnail': bu
	})

	liz = xbmcgui.ListItem(name, iconImage = bu, thumbnailImage = bu)
	liz.setArt({ 'thumb': bu, 'poster': bu, 'banner' : bu, 'fanart': bu })
	liz.setInfo( type = 'Video', infoLabels = {
		'plot': plot,
		'mpaa': str(ar) + '+',
		'rating': imdb,
		'cast': cast,
		'director': director,
		'writer': writer,
		'duration': duration,
		'genre': genre,
		'title': name,
		'originaltitle': on,
		'year': py
	})
	liz.addStreamInfo('video', { 'width': 1280, 'height': 720 })
	liz.addStreamInfo('video', { 'aspect': 1.78, 'codec': 'h264' })
	liz.addStreamInfo('audio', { 'codec': 'aac', 'channels': 2 })
	liz.setProperty('IsPlayable' , 'true')
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = False)
	return ok


def addDir(name, url, plot, mode, iconimage):
	u = sys.argv[0] + '?' + urllib.urlencode({
		'url': url,
		'mode': str(mode),
		'name': name
	})

	liz = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png', thumbnailImage = iconimage)
	liz.setInfo( type = 'Video', infoLabels = { 'Title': name, 'Plot': plot } )

	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)

	return ok

def get_params():
	param = []
	paramstring = sys.argv[2]

	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')

		if (params[len(params)-1] == '/'):
			params = params[0:len(params)-2]

		pairsofparams = cleanedparams.split('&')
		param = {}

		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')

			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]

	return param

MODE_LIST = 1
MODE_SEASON = 2
MODE_EPISODE = 3
MODE_SEARCH = 4
MODE_PLAY = 5
MODE_SILENT_REGISTER = 6
MODE_LOGIN = 7

def main():
	global params
	global url
	global name
	global thumbnail
	global mode
	global cid

	params = get_params()

	try:
		url = urllib.unquote_plus(params['url'])
	except:
		pass

	try:
		name = urllib.unquote_plus(params['name'])
	except:
		pass

	try:
		thumbnail = str(params['thumbnail'])
	except:
		pass

	try:
		mode = int(params['mode'])
	except:
		pass

	try:
		cid = str(params['cid'])
	except:
		pass



	if mode == None or url == None or len(url) < 1:
		CATEGORIES()

	elif mode == MODE_LIST:
		LIST(url)

	elif mode == MODE_SEASON:
		SEASON(url)

	elif mode == MODE_EPISODE:
		EPISODE(url)

	elif mode == MODE_SEARCH:
		SEARCH()

	elif mode == MODE_PLAY:
		PLAY(url)

	elif mode == MODE_SILENT_REGISTER:
		SILENTREGISTER()

	elif mode == MODE_LOGIN:
		LOGIN()


	xbmcplugin.endOfDirectory(int(sys.argv[1]))

if __name__ == '__main__':
	main()

# vim: sw=2:ts=2:noexpandtab
