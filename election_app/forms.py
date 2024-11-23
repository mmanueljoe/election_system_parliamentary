from django import forms
from .models import Candidate, PollingStation, Region, Party, Vote

class LoginForm(forms.Form):
    constituency_code = forms.CharField(max_length=100)

    def clean_constituency_code(self):
        code = self.cleaned_data.get('constituency_code')
        if not code:
            raise forms.ValidationError('Constituency code is required.')
        return code

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'picture', 'party']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Candidate name is required.')
        return name

    def clean_party(self):
        party = self.cleaned_data.get('party')
        if Candidate.objects.filter(party=party).exists():
            raise forms.ValidationError(f'The party "{party}" is already assigned to another candidate.')
        return party



class PollingStationForm(forms.ModelForm):
    class Meta:
        model = PollingStation
        fields = ['code', 'name', 'constituency', 'registered_voters', 'rejected_ballots', 'declared']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Polling Station Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'registered_voters': forms.NumberInput(attrs={'class': 'form-control'}),
            'rejected_ballots': forms.NumberInput(attrs={'class': 'form-control'}),
            'declared': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        instance = self.instance  # The current object being edited
        if PollingStation.objects.exclude(id=instance.id).filter(code=code).exists():
            raise forms.ValidationError(f"The polling station code '{code}' is already in use.")
        return code

    def clean_registered_voters(self):
        registered_voters = self.cleaned_data.get('registered_voters')
        if registered_voters is not None and registered_voters < 0:
            raise forms.ValidationError("Registered voters cannot be a negative number.")
        return registered_voters

    def clean_rejected_ballots(self):
        rejected_ballots = self.cleaned_data.get('rejected_ballots')
        if rejected_ballots is not None and rejected_ballots < 0:
            raise forms.ValidationError("Rejected ballots cannot be a negative number.")
        return rejected_ballots


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Region name is required.')
        return name


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'logo']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Party name is required.')
        return name

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            raise forms.ValidationError('Party logo is required.')
        return logo



class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['polling_station', 'candidate', 'votes']

    def clean_votes(self):
        votes = self.cleaned_data.get('votes')
        if votes < 0:
            raise forms.ValidationError('Votes cannot be negative.')
        return votes
    def clean(self):
        cleaned_data = super().clean()
        polling_station = cleaned_data.get('polling_station')
        votes = cleaned_data.get('votes')

        total_votes = sum(
            v.votes for v in Vote.objects.filter(polling_station=polling_station)
        ) + votes

        if total_votes > polling_station.registered_voters:
            raise forms.ValidationError(
                'Total votes exceed the number of registered voters for this polling station.'
            )
        return cleaned_data
