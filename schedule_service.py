from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service
from team import Team
import logging

package = 'SaintsSchedule'

# Create the request string containing the user's name
class ScheduleRequest(messages.Message):
    team_id = messages.StringField(1, required=True)

# Create the response string
class ScheduleResponse(messages.Message):
    schedule = messages.StringField(1, required=True)

# Create the RPC service to exchange messages
class ScheduleService(remote.Service):

    @remote.method(ScheduleRequest, ScheduleResponse)
    def schedule(self, request):
		t = Team()
		games = t.getGames(request.team_id)
		return ScheduleResponse(schedule=games)

# Map the RPC service and path (/schedule)
app = service.service_mappings([('/schedule.*', ScheduleService)])