from django import forms
from .models import Candidate, PollingStation, Region, Party, Vote

class LoginForm(forms.Form):
    constituency_code = forms.CharField(max_length=100)

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'picture', 'party']

class PollingStationForm(forms.ModelForm):
    class Meta:
        model = PollingStation
        fields = ['name', 'constituency', 'registered_voters', 'rejected_ballots', 'declared']

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'logo']


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['polling_station', 'candidate', 'votes']

    def clean_votes(self):
        votes = self.cleaned_data.get('votes')
        if votes < 0:
            raise forms.ValidationError('Votes cannot be negative.')
        return votes