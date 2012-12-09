#!/usr/bin/env python

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

import tornado.ioloop
import tornado.web
import logging

import oauth2 as oauth

import os
import datetime
import json

from nosql.mongoTweets import TweetDBMongoDB
from tornado.options   import define, options

define("port",default=8089,type=int,help='Running in the port indicates')

consumerKey       = '' # Aca debes poner TU consumerKey entregado por twitter
consumerSecret    = '' # Aca debes poner TU consumerSecret entregado por twitter
accessToken       = '' # Aca debes poner TU accessToken entregado por twitter
accessTokenSecret = '' # Aca debes poner TU accessTokenSecret entregado por twitter

class MainPage(tornado.web.RequestHandler):
	def get(self):
		username = None
		logging.info('Starting the service')
		self.render('index.html',title='Que dije? (Beta)',username=username)

class TopFive(tornado.web.RequestHandler):
	def get(self):
		try:
			username = self.get_argument('username')
			data     = self._genera(username)
			tweet    = ''
			for d in data:
				created_at = d[0]
				num_tweets = d[1]
				tweet += '{"c":[{"v":"'+created_at+'","f":null},{"v":'+str(num_tweets)+',"f":null}]},'\
		
			tweet = tweet[0:len(tweet)-1]
			
			self.set_header('Content-Type','application/json')
			jsonData = '{"cols" : [' \
			   '          {"id":"","label":"Fecha","type":"string"},'  \
			   '          {"id":"","label":"Tweets","type":"number"}' \
			   '         ],' \
               '         "rows" : ['+tweet+']}'
			self.write(jsonData)
		except:
			self.write('{"response":"error"}')

	def _invert(self,x,y):
		return y - x

	def _genera(self, username):
		consumer = oauth.Consumer(consumerKey, consumerSecret)
		token    = oauth.Token(accessToken, accessTokenSecret)
		client   = oauth.Client(consumer,token)
		response = client.request('https://api.twitter.com/1.1/statuses/user_timeline.json?count=100&screen_name='+username)
		data = response[1]

		tweets = json.loads(data)
		fechas = []
		tw = TweetDBMongoDB()
		tw.deleteTweets({'user.screen_name':username})
		for t in tweets:
			created_at = t['created_at']
			dt = created_at.split(' ')
			fecha = dt[0]+' '+dt[1]+' '+dt[2]+' '+dt[5]
			f  = datetime.datetime.strptime(fecha,'%a %b %d %Y').strftime('%d-%m-%Y')
			fechas.append(f)
			oid = tw.insertTweet(t)

		tw.close()

		estadistica = self._gen_estadisticas(fechas)
		
		est = sorted(estadistica,key=lambda c : c[1], cmp=self._invert)

		return est[0:5]

	def _gen_estadisticas(self,list_elem):
		stat  = {}
		lista = []
		for item in set(list_elem):
			stat[item] = list_elem.count(item)

		for f in stat:
			lista.append((f,stat[f]))

		return lista

class Text(tornado.web.RequestHandler):
	def get(self):
		self.set_header('content-type', 'application/json; charset=UTF-8')
		username  = self.get_argument('username')
		date_text = self.get_argument('date_text')

		tw = TweetDBMongoDB()
		tweets = tw.getTweets({'user.screen_name':username})
		tweet = ''
		for t in tweets:
			text       = t['text']
			created_at = t['created_at']
			dt         = created_at.split(' ')
			fecha      = dt[0]+' '+dt[1]+' '+dt[2]+' '+dt[5]
			fechahora  = dt[0]+' '+dt[1]+' '+dt[2]+' '+dt[5]+' '+dt[3]
			f          = datetime.datetime.strptime(fecha,'%a %b %d %Y').strftime('%d-%m-%Y')
			if f == date_text:
				hour = datetime.datetime.strptime(fechahora,'%a %b %d %Y %H:%M:%S')
				tweet += '{"text":"'+text.replace('\n',' ').replace('"','')+'","hour":"'+hour.strftime('%H:%M:%S')+'"},'
		
		tweet = tweet[0:len(tweet)-1]

		tweet = tweet.encode('utf-8')
		c = json.JSONEncoder()
		s = c.encode('{"tweets" : ['+tweet+']}')
		jsonText = json.loads(s)

		tw.close()
		self.write(jsonText)

settings = {
	"static_path":os.path.join(os.getcwd(),'static'),
	"template_path":os.path.join(os.getcwd(),'templates')
}

app = tornado.web.Application([(r'/',MainPage),(r'/topfive',TopFive),(r'/tweets',Text),],**settings)

if __name__ == '__main__':
	tornado.options.parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()