from google.appengine.ext import db
import logging
import string

package = 'SaintsSchedule'

class AvailableSeasons(db.Model):
	season = db.IntegerProperty()

	def getSeasons(self):
		availableSeasons = AvailableSeasons()
		q = db.Query(AvailableSeasons)
		q = AvailableSeasons.all()
		if q.count() == 0:
			availableSeasons.season = 47
			availableSeasons.put()
			q = AvailableSeasons.all()
		return q.run()