from google.appengine.ext import db
import logging
import string

package = 'SaintsSchedule'

class IndividualGame(db.Model):
	teamId = db.StringProperty()
	gameId = db.StringProperty()
	game = db.StringProperty()

	def getGames(self, teamId):
		game = IndividualGame()
		q = db.Query(IndividualGame)
		q = IndividualGame.all()
		q.filter("teamId =", str(teamId))
		return q.run()