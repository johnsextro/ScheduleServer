import logging
import webapp2
import json
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import team
import time
from season_service import Season
from team import Team
from available_season import AvailableSeasons
from individual_game import IndividualGame

class Load(webapp2.RequestHandler):
	schoolNames = ["ICOM", "2Rivers", "A.S.H.", "AS", "ASH", "All Saints", "Assumption", "Borromeo", "HS", "HT", "Holy Rosary", "Holy Spirit", "Holy Trinity", "ICD", "ICOM", "IHM", "J and A", "JA", "JandA", "LWCS", "Living Word", "S.H. Troy", "SC", "SESR", "SESR Carrie Mejia", "SH T", "SH Troy", "SJ", "SJ Cott", "Sacred Heart Troy", "St Cletus", "St Joe", "St Joe Cottleville", "St Josephville", "St Patrick", "St Paul", "St Peter", "St Peters", "St Theodore", "St. Cletus", "St. Ignatius", "St. Joe", "St. Joe Cottleville", "St. Joe Cott", "St. Joe Josephsville", "St. Patrick", "St. Paul", "St. Peter", "St. Rose", "St. Sabina", "St. Theo", "St. Theodore", "St.Joe Cottleville", "St.Patrick", "Sts J and A", "Sts JandA", "Sts. J and A", "Sts. J andA", "Sts. JandA", "St Joseph", "St. Joseph"]
	
	def get(self):
		start_time = time.time()
		url = "http://slcycstcharlesdistrict.sportssignup.com/site/ClientSite/team_and_division_data"
		form_fields = {"season_id": "season_id=1519074"}
		form_data = urllib.urlencode(form_fields)
		result = urlfetch.fetch(url=url,
    		payload=form_data,
    		method=urlfetch.POST,
    		headers={'Content-Type': 'application/x-www-form-urlencoded'})
		logging.info(json.dumps(result.content))

	def get_team_ids(self, seasonId):
		teams = []
		urlString = "http://www.cycstcharles.com/schedule.php?month=999&year=999&pfv=n&location=-1&leagueid=1&season=%d&conference=-1&division=-1&team=-1" % seasonId
		url = urlfetch.fetch(url=urlString, deadline=99)
		if url.status_code == 200:
			tree = etree.HTML(url.content)
			elements = tree.xpath('//td[@class="smalltext"][7]/select[@class="smalltext"]//option')
			for team_name in elements:
				attribs = team_name.attrib
				value = attribs["value"]
				teams.append([team_name.text.strip(),value[value.find("&team=")+6:]])
		return teams

	def save_team_games(self, games, team_id, coach, season, grade):
		t = team.Team(key_name=str(team_id))
		t.teamId = str(team_id)
		for val in self.schoolNames:
			if coach.find(val) > -1:
				t.school = val
				coach = coach[len(val)+1:]
				coach = coach.strip()
				t.coach = coach
				logging.info("School = %s, Coach = %s" % (t.school, t.coach))
				t.season = season
				t.grade = grade
				t.year = 2015
				t.schedule = self.jsonify_games(games, team_id)
				if t.school is not None and t.grade is not None:
					t.put()
				break

	def jsonify_games(self, games, team_id):
		gamelist = []
		for rowindex in range(len(games)):
			if len(games[rowindex])>3 and games[rowindex][1].text is not None and games[rowindex][2].text is not None:
				try:
					game = '{"game_date": "%s", "time": "%s", "home": "%s", "away": "%s", "location": "%s", "id": "%s", "score": "%s"}' % (games[rowindex][self.GAME_DATE].text, games[rowindex][self.GAME_TIME].text, games[rowindex][self.HOME_TEAM].text, games[rowindex][self.AWAY_TEAM].text, games[rowindex][self.LOCATION][0].text, games[rowindex][self.GAME_ID].text, games[rowindex][self.SCORE].text)
					gamelist.append(game)
					ig = IndividualGame(teamId=str(team_id), 
									gameId=games[rowindex][self.GAME_ID].text,
									game=game)
					ig.put()
				except IndexError, e:
					logging.debug("jsonify_games encountered an error, skipping and continuing")
					continue
		return '{"games": [%s]}' % ", ".join(gamelist)

app = webapp2.WSGIApplication([('/crontask/loadgames', Load)],debug=True)

if __name__ == '__main__':
	run_wsgi_app(application)