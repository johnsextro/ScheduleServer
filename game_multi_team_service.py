from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service
from team import Team
import logging
import json

package = 'SaintsSchedule'

class Games(messages.Message):
	game_date = messages.StringField(1, required=True)
	time = messages.StringField(2, required=True)
	home = messages.StringField(3, required=True)
	away = messages.StringField(4, required=True)
	location = messages.StringField(5, required=True)
	game_id = messages.StringField(6, required=True)
	score = messages.StringField(7)


class GamesMultiTeamRequest(messages.Message):
    team_ids = messages.StringField(1, required=True)

# Create the response string
class GamesMultiTeamResponse(messages.Message):
    games = messages.MessageField(Games, 1, repeated=True)

# Create the RPC service to exchange messages
class GamesMultiTeamService(remote.Service):

    @remote.method(GamesMultiTeamRequest, GamesMultiTeamResponse)
    def games(self, request):
		t = Team()
		responseArray = []
		schedule = t.getGamesMultiTeams(request.team_ids)
		gamesArray = eval(schedule)
		for game in gamesArray:
			logging.info(game)
			responseGame = Games(game_date=game['game_date'][5:], time=game['time'], home=game['home'], away=game['away'], location=game['location'], game_id=game['id'], score=game['score'])
			responseArray.append(responseGame)
		return GamesMultiTeamResponse(games=responseArray)

# Map the RPC service and path (/schedule)
app = service.service_mappings([('/multigames.*', GamesMultiTeamService)])