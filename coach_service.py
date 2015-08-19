from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service
from google.appengine.api import memcache
from team import Team
import logging

package = 'SaintsSchedule'

class Coach(messages.Message):

	team_id = messages.StringField(1, required=True)
	name = messages.StringField(2, required=True)
	school = messages.StringField(3)
	grade = messages.StringField(4)

class Coaches(messages.Message):
	coaches = messages.MessageField(Coach, 1, repeated=True)

# Create the request string containing the user's name
class CoachRequest(messages.Message):
	school = messages.StringField(1, required=False)
	season = messages.StringField(2, required=False)

# Create the RPC service to exchange messages
class CoachService(remote.Service):

	@remote.method(CoachRequest, Coaches)
	def coach(self, request):
		cacheKey = 'AllCoaches'
		if (request.school is not None) and (request.season is None):
			cacheKey = request.school
		else:
			cacheKey = request.season + request.school
		theCache = memcache.get(cacheKey)
		if theCache is None:
			t = Team()
			coaches = []
			for team in t.getCoaches(request.school, request.season):
				coach = Coach(team_id=team.teamId, name=team.coach, school=team.school, grade=team.grade)
				coaches.append(coach)
			if not memcache.add(cacheKey, coaches):
				logging.error('Unable to set cache')
			return Coaches(coaches=coaches)
		else:
			return Coaches(coaches=theCache)

# Map the RPC service and path (/schedule)
app = service.service_mappings([('/coach.*', CoachService)])