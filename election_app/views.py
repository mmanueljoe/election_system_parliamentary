import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate, Vote, PollingStation, Constituency, Party,Region
from .forms import CandidateForm, PollingStationForm, VoteForm
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User

# from .forms import LoginForm  # Create a form for login if needed


@login_required
def landing_page(request):
    # Fetch the currently logged-in user's constituency from the session
    constituency_code = request.session.get('constituency_code')
    if not constituency_code:
        return redirect('login')

    # Get the constituency details
    constituency = get_object_or_404(Constituency, name=constituency_code)

    # Fetch polling stations and votes related to the constituency
    polling_stations = PollingStation.objects.filter(constituency=constituency)
    votes = Vote.objects.filter(polling_station__in=polling_stations)

    # Calculate statistics
    total_polling_stations = polling_stations.count()
    total_registered_voters = sum(ps.registered_voters for ps in polling_stations)
    total_votes_cast = sum(v.votes for v in votes)
    rejected_ballots = sum(ps.rejected_ballots for ps in polling_stations)

    # Handle percentage calculation
    voter_turnout_percentage = (
        (total_votes_cast / total_registered_voters) * 100 if total_registered_voters > 0 else 0
    )

    # Context for the template
    context = {
        'constituency': constituency,
        'total_polling_stations': total_polling_stations,
        'total_registered_voters': total_registered_voters,
        'total_votes_cast': total_votes_cast,
        'rejected_ballots': rejected_ballots,
        'voter_turnout_percentage': round(voter_turnout_percentage, 2),
    }

    return render(request, 'landing_page.html', context)


def login_view(request):
    if request.method == 'POST':
        constituency_code = request.POST.get('constituency_code')
        try:
            constituency = Constituency.objects.get(name=constituency_code)
            user, created = User.objects.get_or_create(username=constituency_code)
            login(request, user)
            request.session['constituency_code'] = constituency_code
            return redirect('dashboard')
        except Constituency.DoesNotExist:
            messages.error(request, "Invalid Constituency Code")
            return redirect('login')

    # Clear leftover messages when rendering the login page
    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, 'login.html')

def logout_view(request):
    # Log the user out and clear the session
    logout(request)
    
    # Redirect to login page after logout
    return redirect('login')

@login_required
def dashboard(request):
    constituency_code = request.session.get('constituency_code')
    if not constituency_code:
        return redirect('login')

    candidates = Candidate.objects.all()
    votes = Vote.objects.all()

    vote_data = []
    for candidate in candidates:
        candidate_votes = votes.filter(candidate=candidate)
        total_votes = sum(vote.votes for vote in candidate_votes)
        vote_data.append({
            'candidate_name': candidate.name,
            'party_name': candidate.party.name,
            'party_logo': candidate.party.logo.url if candidate.party.logo else None,
            'total_votes': total_votes
        })

    total_polling_stations = PollingStation.objects.count()
    total_registered_voters = sum(station.registered_voters for station in PollingStation.objects.all())
    total_rejected_ballots = sum(station.rejected_ballots for station in PollingStation.objects.all())
    total_votes_cast = sum(vote.votes for vote in votes)

    percentage = (total_votes_cast / total_registered_voters) * 100 if total_registered_voters else 0

    context = {
        'vote_data': json.dumps(vote_data),  # Convert vote data to JSON
        'total_polling_stations': total_polling_stations,
        'total_registered_voters': total_registered_voters,
        'total_rejected_ballots': total_rejected_ballots,
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
        form = CandidateForm()

    return render(request, 'add_candidate.html', {'form': form})

@login_required
def edit_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)  # Get the candidate object by ID
    if request.method == 'POST':
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect('candidate_list')  # Redirect after saving
    else:
        form = CandidateForm(instance=candidate)  # Prepopulate form with candidate data

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
@login_required
def add_polling_station(request):
    """
    Handles adding a new polling station.
    """
    if request.method == 'POST':
        form = PollingStationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new polling station to the database
            messages.success(request, "Polling station added successfully!")
            return redirect('polling_station_list')  # Redirect to the polling stations list page
        else:
            messages.error(request, "There was an error adding the polling station.")
    else:
        form = PollingStationForm()  # Display an empty form for GET requests

    return render(request, 'add_polling_station.html', {'form': form})


@login_required
def edit_polling_station(request, id):
    """
    Handles editing a polling station.
    """
    polling_station = get_object_or_404(PollingStation, id=id)  # Fetch the polling station by ID
    if request.method == 'POST':
        form = PollingStationForm(request.POST, instance=polling_station)  # Populate form with instance
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