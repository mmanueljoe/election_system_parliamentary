from django.contrib import admin
from .models import Region, Constituency, Party, Candidate, PollingStation, Vote

admin.site.register(Region)
admin.site.register(Constituency)
admin.site.register(Party)
admin.site.register(Candidate)
admin.site.register(PollingStation)
admin.site.register(Vote)
