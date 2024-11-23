import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate, Vote, PollingStation, Constituency, Party,Region,Candidate, Vote
from .forms import CandidateForm, PollingStationForm, VoteForm
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db import IntegrityError
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.contrib import messages

from django.urls import reverse
import json
from . import models  # Import your models from the app



@login_required
def landing_page(request):
    constituency_code = request.session.get('constituency_code')
    if not constituency_code:
        return redirect('login')

    constituency = get_object_or_404(Constituency, code=constituency_code)
    polling_stations = PollingStation.objects.filter(constituency=constituency)
    votes = Vote.objects.filter(polling_station__in=polling_stations)

    # Calculate statistics
    total_polling_stations = polling_stations.count()
    total_registered_voters = sum(ps.registered_voters for ps in polling_stations)
    total_votes_cast = sum(v.votes for v in votes)
    rejected_ballots = sum(ps.rejected_ballots for ps in polling_stations)
    overvotes = max(0, total_votes_cast - total_registered_voters)

    # Voter turnout percentage calculation
    voter_turnout_percentage = (total_votes_cast / total_registered_voters) * 100 if total_registered_voters else 0

    # Additional statistics (you can add more as needed)
    total_parties = len(set(candidate.party.name for candidate in Candidate.objects.all()))

    context = {
        'constituency': constituency,
        'total_polling_stations': total_polling_stations,
        'total_registered_voters': total_registered_voters,
        'total_votes_cast': total_votes_cast,
        'rejected_ballots': rejected_ballots,
        'overvotes': overvotes,
        'voter_turnout_percentage': round(voter_turnout_percentage, 2),
        'total_parties': total_parties,  # New stat for parties
    }
    return render(request, 'landing_page.html', context)


def login_view(request):
    if request.method == 'POST':
        constituency_code = request.POST.get('constituency_code')  # Use constituency code from form input
        try:
            # Validate constituency code
            constituency = Constituency.objects.get(code=constituency_code)  
            # Authenticate user using constituency code as the username
            user, created = User.objects.get_or_create(username=constituency_code)
            if created:
                user.set_unusable_password()  # Optional: Ensure user cannot log in with a password
                user.save()
            login(request, user)  # Log in the user
            request.session['constituency_code'] = constituency_code  # Store constituency code in session
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        except Constituency.DoesNotExist:
            messages.error(request, "Invalid Constituency Code")  # Display error if code is invalid
            return redirect('login')

    # Clear leftover messages when rendering the login page
    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, 'login.html')  # Render the login page



def logout_view(request):
    # Log the user out and clear the session
    logout(request)
    
    # Redirect to login page after logout
    return redirect('login')

@login_required
@login_required
def dashboard(request):
    constituency_code = request.session.get('constituency_code')  # Get constituency code from session
    if not constituency_code:
        return redirect('login')  # Redirect to login if no constituency code

    # Get the constituency using the code
    constituency = get_object_or_404(Constituency, code=constituency_code)  # Filter by code, not name

    # Filter candidates, polling stations, and votes within the constituency
    candidates = Candidate.objects.all()
    polling_stations = PollingStation.objects.filter(constituency=constituency)
    votes = Vote.objects.filter(polling_station__in=polling_stations)

    # Collect vote data for dashboard visualization
    vote_data = []
    for candidate in candidates:
        total_votes = votes.filter(candidate=candidate).aggregate(total=Sum('votes'))['total'] or 0
        vote_data.append({
            'candidate_name': candidate.name,
            'party_name': candidate.party.name,
            'party_logo': candidate.party.logo.url if candidate.party.logo else None,
            'total_votes': total_votes
        })

    # Calculate overall statistics
    total_polling_stations = polling_stations.count()
    total_registered_voters = sum(station.registered_voters for station in polling_stations)
    total_votes_cast = sum(vote['total_votes'] for vote in vote_data)
    total_rejected_ballots = sum(station.rejected_ballots for station in polling_stations)

    # Calculate overvotes
    total_overvotes = max(0, total_votes_cast - total_registered_voters)

    # Calculate voter turnout percentage
    percentage = (total_votes_cast / total_registered_voters) * 100 if total_registered_voters else 0

    context = {
        'vote_data': json.dumps(vote_data),  # Convert vote data to JSON
        'total_polling_stations': total_polling_stations,
        'total_registered_voters': total_registered_voters,
        'total_votes_cast': total_votes_cast,
        'total_rejected_ballots': total_rejected_ballots,
        'total_overvotes': total_overvotes,
        'percentage': round(percentage, 2)
    }
    return render(request, 'dashboard.html', context)



# Candidate logics
@login_required
def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidates.html', {'candidates': candidates})


@login_required
def add_candidate(request):
    """
    Handles adding a new candidate.
    """
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)  # Handles image upload
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added successfully!")
            return redirect('candidate_list')  # Redirect to candidate list after adding
        else:
            messages.error(request, "There was an error adding the candidate.")
    else:
        # Exclude parties already assigned to candidates
        assigned_parties = Candidate.objects.values_list('party', flat=True)
        form = CandidateForm()
        form.fields['party'].queryset = Party.objects.exclude(id__in=assigned_parties)

    return render(request, 'add_candidate.html', {'form': form})


@login_required
def edit_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)  # Get the candidate object by ID
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, f"Candidate '{candidate.name}' updated successfully!")
            return redirect('candidate_list')  # Redirect after saving
        else:
            messages.error(request, "There was an error updating the candidate.")
    else:
        form = CandidateForm(instance=candidate)
        # Exclude parties already assigned to other candidates
        assigned_parties = Candidate.objects.exclude(id=candidate.id).values_list('party', flat=True)
        form.fields['party'].queryset = Party.objects.exclude(id__in=assigned_parties)

    return render(request, 'edit_candidate.html', {'form': form, 'candidate': candidate})

@login_required
def delete_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, f'{candidate.name} has been deleted successfully!')
        return redirect('candidate_list')  # Redirect back to the candidate list after deletion

    return render(request, 'delete_candidate.html', {'candidate': candidate})  # Confirm before deletion


# polling stations logics
@login_required
def polling_station_list(request):
    polling_stations = PollingStation.objects.select_related('constituency').all()
    return render(request, 'polling_station_list.html', {'polling_stations': polling_stations})



@login_required
def add_polling_station(request):
    if request.method == 'POST':
        form = PollingStationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Polling station added successfully!")
                return redirect('polling_station_list')
            except IntegrityError:
                messages.error(request, "An error occurred while saving. Please check your inputs.")
        else:
            messages.error(request, "There was an error adding the polling station.")
    else:
        form = PollingStationForm()

    return render(request, 'add_polling_station.html', {'form': form})



@login_required
def edit_polling_station(request, id):
    """
    Handles editing a polling station.
    """
    polling_station = get_object_or_404(PollingStation, id=id)  # Fetch the polling station by ID
    if request.method == 'POST':
        form = PollingStationForm(request.POST, instance=polling_station)  # Pass instance to the form
        if form.is_valid():
            form.save()
            messages.success(request, f"Polling station '{polling_station.name}' updated successfully!")
            return redirect('polling_station_list')  # Redirect to polling station list
        else:
            messages.error(request, "There was an error updating the polling station.")
    else:
        form = PollingStationForm(instance=polling_station)  # Prepopulate form with polling station data

    return render(request, 'edit_polling_station.html', {'form': form, 'polling_station': polling_station})


@login_required
def delete_polling_station(request, id):
    """
    Handles deleting a polling station.
    """
    polling_station = get_object_or_404(PollingStation, id=id)  # Fetch the polling station by ID
    
    if request.method == 'POST':  # Confirm deletion on POST request
        polling_station.delete()
        messages.success(request, f"Polling station '{polling_station.name}' deleted successfully!")
        return redirect('polling_station_list')  # Redirect to polling station list after deletion

    # Render confirmation page for GET request
    return render(request, 'delete_polling_station.html', {'polling_station': polling_station})




# Constituency logics
@login_required
def constituency_list(request):
    constituencies = Constituency.objects.select_related('region').all()
    return render(request, 'constituency_list.html', {'constituencies': constituencies})

@login_required
def add_constituency(request):
    regions = Region.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        region_id = request.POST.get('region')
        if name and region_id:
            region = get_object_or_404(Region, id=region_id)
            Constituency.objects.create(name=name, region=region)
            messages.success(request, 'Constituency added successfully!')
            return redirect('constituency_list')
        else:
            messages.error(request, 'Please provide all required fields.')
    return render(request, 'add_constituency.html', {'regions': regions})

@login_required
def edit_constituency(request, id):
    regions = Region.objects.all()
    constituency = get_object_or_404(Constituency, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        region_id = request.POST.get('region')
        if name and region_id:
            region = get_object_or_404(Region, id=region_id)
            constituency.name = name
            constituency.region = region
            constituency.save()
            messages.success(request, 'Constituency updated successfully!')
            return redirect('constituency_list')
        else:
            messages.error(request, 'Please provide all required fields.')
    return render(request, 'edit_constituency.html', {'constituency': constituency, 'regions': regions})

@login_required
def delete_constituency(request, id):
    constituency = get_object_or_404(Constituency, id=id)
    if request.method == 'POST':
        constituency.delete()
        messages.success(request, 'Constituency deleted successfully!')
        return redirect('constituency_list')
    return render(request, 'delete_constituency.html', {'constituency': constituency})




# logic for region
@login_required
def region_list(request):
    regions = Region.objects.all()
    return render(request, 'region_list.html', {'regions': regions})

@login_required
def add_region(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Region.objects.create(name=name)
            messages.success(request, 'Region added successfully!')
            return redirect('region_list')
        else:
            messages.error(request, 'Region name cannot be empty.')
    return render(request, 'add_region.html')

@login_required
def edit_region(request, id):
    region = get_object_or_404(Region, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            region.name = name
            region.save()
            messages.success(request, 'Region updated successfully!')
            return redirect('region_list')
        else:
            messages.error(request, 'Region name cannot be empty.')
    return render(request, 'edit_region.html', {'region': region})

@login_required
def delete_region(request, id):
    region = get_object_or_404(Region, id=id)
    if request.method == 'POST':
        region.delete()
        messages.success(request, 'Region deleted successfully!')
        return redirect('region_list')
    return render(request, 'delete_region.html', {'region': region})


# votes logic
@login_required
def vote_list(request):
    votes = Vote.objects.select_related('polling_station', 'candidate')
    return render(request, 'votes.html', {'votes': votes})

@login_required
def add_vote(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vote added successfully.")
            return redirect('vote_list')
        else:
            # If form is invalid, show error messages
            messages.error(request, "Please ensure the vote count is a valid positive number.")
    else:
        form = VoteForm()
    
    return render(request, 'add_vote.html', {'form': form})

@login_required
def update_vote(request, id):
    vote = get_object_or_404(Vote, id=id)
    if request.method == 'POST':
        form = VoteForm(request.POST, instance=vote)
        if form.is_valid():
            form.save()
            messages.success(request, "Vote updated successfully.")
            return redirect('vote_list')
        else:
            # If form is invalid, show error messages
            messages.error(request, "Please ensure the vote count is a valid positive number.")
    else:
        form = VoteForm(instance=vote)
    
    return render(request, 'edit_vote.html', {'form': form})

@login_required
def delete_vote(request, id):
    vote = get_object_or_404(Vote, id=id)
    if request.method == 'POST':
        vote.delete()
        messages.success(request, "Vote deleted successfully.")
        return redirect('vote_list')
    return render(request, 'delete_vote.html', {'vote': vote})


# logic error election report
def election_report(request):
    polling_stations = PollingStation.objects.all()
    return render(request, 'election_report.html', {'polling_stations': polling_stations})




# vote management logic


@login_required
def manage_votes(request):

    constituency_code = request.session.get('constituency_code')
    if not constituency_code:
        return redirect('login')

    # Get the list of polling stations based on the constituency code
    polling_stations = PollingStation.objects.filter(constituency__code=constituency_code)
    
    # Get the polling station ID from the query parameter, handle invalid cases
    polling_station_id = request.GET.get('polling_station_id')
    polling_station = None
    
    if polling_station_id:
        try:
            polling_station = PollingStation.objects.get(id=polling_station_id)
        except PollingStation.DoesNotExist:
            messages.error(request, "Polling station not found.")
            return redirect(reverse('manage_votes'))  # Redirect without query parameter
    
    # If no polling station is selected, show a message and don't display candidate data
    if not polling_station:
        messages.info(request, "Please select a polling station to manage votes.")
    
    # Get the list of candidates and their votes for the selected polling station
    candidates = Candidate.objects.all()
    candidate_votes = {}
    
    if polling_station:
        # Prepopulate vote data by querying the Vote table
        votes = Vote.objects.filter(polling_station=polling_station)
        candidate_votes = {vote.candidate_id: vote.votes for vote in votes}
    
    print(json.dumps(candidate_votes, indent=4))  # Add this for debugging

    # Handle form submission for saving or clearing votes
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save':
            # Ensure votes are entered for at least one candidate
            if not any(request.POST.get(f'vote_{candidate.id}') for candidate in candidates):
                messages.error(request, "Please enter votes for at least one candidate.")
                return redirect(f'{reverse("manage_votes")}?polling_station_id={polling_station.id}')
            
            # Save or update votes
            for candidate in candidates:
                vote_count = request.POST.get(f'vote_{candidate.id}')
                if vote_count:
                    vote_count = int(vote_count)
                    if vote_count < 0:
                        messages.error(request, "Vote count cannot be negative.")
                        return redirect(f'{reverse("manage_votes")}?polling_station_id={polling_station.id}')
                    if vote_count > polling_station.registered_voters:
                        messages.error(request, f"Vote count for {candidate.name} exceeds registered voters.")
                        return redirect(f'{reverse("manage_votes")}?polling_station_id={polling_station.id}')
                    
                    # Update or create the vote record
                    vote, created = Vote.objects.update_or_create(
                        polling_station=polling_station,
                        candidate=candidate,
                        defaults={'votes': vote_count}
                    )

            # Save rejected ballots
            rejected_ballots = request.POST.get('rejected_ballots')
            if rejected_ballots is not None:
                polling_station.rejected_ballots = int(rejected_ballots)
                polling_station.save()

            messages.success(request, "Votes successfully saved.")
            return redirect(f'{reverse("manage_votes")}?polling_station_id={polling_station.id}')
        elif action == 'clear':
            # Clear votes for the selected polling station
            for candidate in candidates:
                Vote.objects.filter(polling_station=polling_station, candidate=candidate).delete()
            messages.success(request, "Votes cleared successfully.")
            return redirect(f'{reverse("manage_votes")}?polling_station_id={polling_station.id}')
    
    return render(request, 'manage_votes.html', {
        'polling_stations': polling_stations, 
        'polling_station': polling_station, 
        'candidates': candidates,
        'candidate_votes': candidate_votes,  # Pass pre-populated vote data
    })



@login_required
def election_report(request):
    constituency_code = request.session.get('constituency_code')
    if not constituency_code:
        return redirect('login')

    # Fetch polling stations for the constituency
    polling_stations = PollingStation.objects.filter(constituency__code=constituency_code)

    report_data = []
    for station in polling_stations:
        # Get all votes for the polling station
        votes = Vote.objects.filter(polling_station=station)
        total_votes = sum(vote.votes for vote in votes)
        parties = {}

        # Collect party-wise vote data
        for vote in votes:
            party_name = vote.candidate.party.name
            parties[party_name] = parties.get(party_name, 0) + vote.votes

        # Calculate voter turnout
        voter_turnout = (total_votes / station.registered_voters) * 100 if station.registered_voters > 0 else 0

        # Append row data to the report
        report_data.append({
            'code': station.code,
            'name': station.name,
            'registered_voters': station.registered_voters,
            'parties': parties,
            'over_votes': station.over_votes,
            'rejected_ballots': station.rejected_ballots,
            'total_votes': total_votes,
            'voter_turnout': f"{voter_turnout:.2f}%"
        })

    return render(request, 'election_report.html', {'report_data': report_data})
