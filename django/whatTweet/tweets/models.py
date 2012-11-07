from django.db import models

# Entidad para almacenar los tweets.
class Tweets(models.Model):
	username   = models.CharField(max_length=120)
	created_at = models.DateTimeField()
	date_text  = models.DateField()
	text       = models.TextField()

	def __unicode__(self):
		return self.username
