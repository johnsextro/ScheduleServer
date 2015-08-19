from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service
from google.appengine.api import memcache
from team import Team
import logging

package = 'SaintsSchedule'

class School(messages.Message):
	school = messages.StringField(1, required=True)

class SchoolRequest(messages.Message):
    season = messages.StringField(1, required=False)

# Create the response string
class SchoolResponse(messages.Message):
	schools = messages.MessageField(School, 1, repeated=True)

# Create the RPC service to exchange messages
class SchoolService(remote.Service):

 	@remote.method(SchoolRequest, SchoolResponse)
 	def school(self, request):
		cacheKey = request.season
		if cacheKey is None:
			cacheKey = 'AllSchools'
		theCache = memcache.get(cacheKey)
		if theCache is None:
			t = Team()
			schools = []
			for team in t.getSchools(request.season):
				school = School(school=team.school)
				if school not in schools:
					schools.append(school)
			if not memcache.add(cacheKey, schools):
				logging.error('Unable to set cache')
			return SchoolResponse(schools=schools)
		else:
			return SchoolResponse(schools=theCache)

# Map the RPC service and path (/schedule)
app = service.service_mappings([('/school.*', SchoolService)])