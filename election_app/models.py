from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Constituency(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class Party(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='party_logos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    party = models.OneToOneField(Party, on_delete=models.CASCADE)  # Ensures one candidate per party
    picture = models.ImageField(upload_to='candidate_pictures/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PollingStation(models.Model):
    name = models.CharField(max_length=100)  # name for polling stations
    code = models.CharField(max_length=50, unique=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    registered_voters = models.IntegerField()
    rejected_ballots = models.IntegerField(default=0)
    total_votes_cast = models.IntegerField(default=0, editable=False)
    over_votes = models.IntegerField(default=0, editable=False)
    declared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_over_votes(self):
        total_votes = sum(vote.votes for vote in self.vote_set.all())
        self.total_votes_cast = total_votes
        self.over_votes = max(0, total_votes - self.registered_voters)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.code})"

class Vote(models.Model):
    polling_station = models.ForeignKey(PollingStation, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    votes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Changed from `polling_station.name` to `polling_station.code`
        return f"Votes for {self.candidate.name} at {self.polling_station.code}"
    

