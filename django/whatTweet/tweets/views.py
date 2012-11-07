#
# Autor: Rodrigo Ancavil del Pino.
# Email: rancavil@innovaser.cl
#        rancavil@gmail.com
#
# Aplicacion que permite consultar los 100 ultimos tweets de un usuario.
# Utiliza los servicios REST de la API de Twitter 1.1. Les recomiendo que
# revisen y entienda el uso de esta API (sus restricciones, etc.)
# 
# https://dev.twitter.com/docs/api/1.1
# 
# Para obtener las claves de acceso y token deben registrarse en el 
# sitio para desarrolladores de twitter.
#
# https://dev.twitter.com/
#
# Para obtener el consumerKey, consumerSecret, accessToken y accessTokenSecret
# deben regitrar la aplicacion de acuerdo a la info solicitada. 
#
# Deben asegurarse que cuenten con todas las librerias de python requeridas por 
# la aplicacion.
#
# oauth2 y httplib2.
# 
# Con $ pip install oauth2 (se instala httplib2)
#
# Descripcion:
#
# Basicamente lo que hace la aplicacion es desplegar la pagina index.html
# y atender los requerimientos GET para los parametros entregados. Las respuestas
# son JSON con la data para que sea desplegada como un grafico de google chart.
# 

from django.shortcuts         import render_to_response, get_object_or_404
from django.http              import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template          import RequestContext
from tweets.models            import Tweets

import datetime
import json

import oauth2 as oauth

consumerKey       = '' # Aca debes poner TU consumerKey entregado por twitter
consumerSecret    = '' # Aca debes poner TU consumerSecret entregado por twitter
accessToken       = '' # Aca debes poner TU accessToken entregado por twitter
accessTokenSecret = '' # Aca debes poner TU accessTokenSecret entregado por twitter

def index(request):
	username = None
	return render_to_response('tweets/index.html',{'title' : 'Que dije? (Beta)','username':username})

def topfive(request):
	username = None
	if 'username' in request.GET:
		username = request.GET['username']
		try:
			data     = _genera(username)
	
			tweet    = ''
			for d in data:
				created_at = d[0]
				num_tweets = d[1]
				tweet += '{"c":[{"v":"'+created_at+'","f":null},{"v":'+str(num_tweets)+',"f":null}]},'\
	
			tweet = tweet[0:len(tweet)-1]
		
			jsonData = '{"cols" : [' \
				'          {"id":"","label":"Fecha","type":"string"},'  \
				'          {"id":"","label":"Tweets","type":"number"}' \
				'         ],' \
        		'         "rows" : ['+tweet+']}'
			response = HttpResponse(jsonData)
			response['Content-Type'] = 'application/json'
			return response
		except:
			return HttpResponse('{"response":"error"}')
	else:
		return HttpResponse('{"response":"error"}')
	
def _invert(x,y):
	return y - x

def _genera(username):
	consumer = oauth.Consumer(consumerKey, consumerSecret)
	token    = oauth.Token(accessToken, accessTokenSecret)
	client   = oauth.Client(consumer,token)
	response = client.request('https://api.twitter.com/1.1/statuses/user_timeline.json?count=100&screen_name='+username)
	data = response[1]

	tweets = json.loads(data)
	fechas = []
	
	Tweets.objects.filter(username=username).delete()
	for t in tweets:
		created_at = t['created_at']
		dt = created_at.split(' ')
		fecha = dt[0]+' '+dt[1]+' '+dt[2]+' '+dt[5]
		fechahora = dt[0]+' '+dt[1]+' '+dt[2]+' '+dt[5]+' '+dt[3]
		f  = datetime.datetime.strptime(fecha,'%a %b %d %Y').strftime('%d-%m-%Y')
		fh = datetime.datetime.strptime(fechahora,'%a %b %d %Y %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
		fechas.append(f)

		tw = Tweets()
		tw.username = username
		tw.created_at = datetime.datetime.strptime(fh,'%d-%m-%Y %H:%M:%S')
		# En settings.py se cambio el parametrp USE_TZ de True a False
		# Para evitar el warning DateTimeField received a naive datetime
		# Reviar mas respecto a este tema.
		tw.date_text  = datetime.datetime.strptime(f ,'%d-%m-%Y').date()
		tw.text = t['text']
		tw.save()

	estadistica = _gen_estadisticas(fechas)
		
	est = sorted(estadistica,key=lambda c : c[1], cmp=_invert)

	return est[0:5]

def _gen_estadisticas(list_elem):
	stat  = {}
	lista = []
	for item in set(list_elem):
		stat[item] = list_elem.count(item)

	for f in stat:
		lista.append((f,stat[f]))

	return lista

def tweets(request):
	username  = None
	date_text = None

	if 'username' in request.GET and 'date_text' in request.GET:
		username  = request.GET['username']
		date_text = request.GET['date_text']

		tweets = Tweets.objects.filter(username = username).filter(date_text=datetime.datetime.strptime(date_text ,'%d-%m-%Y').date()).order_by('-created_at')
		tweet = ''
		for d in tweets:
			text = d.text
			hour = d.created_at
			tweet += '{"text":"'+text.replace('\n',' ').replace('"','')+'","hour":"'+hour.strftime('%H:%M:%S')+'"},'
		
		tweet = tweet[0:len(tweet)-1]

		tweet = tweet.encode('utf-8')
		c = json.JSONEncoder()
		s = c.encode('{"tweets" : ['+tweet+']}')
		jsonText = json.loads(s)
		
		response = HttpResponse(jsonText)
		response['Content-Type'] = 'application/json'
		return response
	else:
		return HttpResponse('{"response":"error"}')