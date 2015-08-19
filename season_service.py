from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service
from team import Team
from google.appengine.api import memcache
import logging

package = 'SaintsSchedule'

class Season(messages.Message):
	season = messages.StringField(1, required=True)

class SeasonRequest(messages.Message):
    seasonRequest = messages.StringField(1, required=False)

# Create the response string
class SeasonResponse(messages.Message):
    seasons = messages.MessageField(Season, 1, repeated=True)

# Create the RPC service to exchange messages
class SeasonService(remote.Service):

    @remote.method(SeasonRequest, SeasonResponse)
    def season(self, request):
		theCache = memcache.get('seasons')
		if theCache is None:
			t = Team()
			seasons = []
			for team in t.getSeasons():
				season = Season(season=team.season)
				if season not in seasons:
					seasons.append(season)
			if not memcache.add('seasons', seasons):
				logging.error('memcache failed to set')
			return SeasonResponse(seasons=seasons)
		else:
			return SeasonResponse(seasons=theCache)

# Map the RPC service and path (/schedule)
app = service.service_mappings([('/season.*', SeasonService)])