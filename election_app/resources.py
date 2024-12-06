from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import PollingStation, Constituency

class PollingStationResource(resources.ModelResource):
    constituency = fields.Field(
        column_name='Constituency',
        attribute='constituency',
        widget=ForeignKeyWidget(Constituency, 'name')
    )

    class Meta:
        model = PollingStation
        fields = ('id', 'name', 'code', 'constituency', 'registered_voters', 'rejected_ballots', 'declared')
        export_order = ('id', 'name', 'code', 'constituency', 'registered_voters', 'rejected_ballots', 'declared')

        # Exclude fields automatically handled by the system
        exclude = ('total_votes_cast', 'over_votes', 'created_at', 'updated_at')
