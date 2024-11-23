from django import template
from election_app.models import Vote

register = template.Library()

@register.filter
def get_vote(polling_station, candidate_id):
    """
    A custom filter to get the vote count for a specific candidate at a polling station.
    """
    try:
        # Fetch the vote for the specific candidate in the specific polling station
        vote = Vote.objects.get(polling_station=polling_station, candidate_id=candidate_id)
        return vote.votes
    except Vote.DoesNotExist:
        return 0  # Return 0 if no vote is found for the candidate at the polling station
