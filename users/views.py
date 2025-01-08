from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages
from users.models import Profile
from projectb15.models import Event
from users.models import Upload
from datetime import datetime, timedelta

@login_required
def account_creation(request):
    """Redirect user to update profile if fields are missing."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    # If fields are missing, redirect to update_user_fields
    if not profile.nickname or not request.user.email:
        return redirect('update_user_fields')

    # Otherwise, redirect to home
    return redirect('home')

@login_required
def user_profile(request):
    """Display user profile information."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'nickname': profile.nickname,
        'user_type': "Admin" if profile.is_pm_admin else "User",
    }
    return render(request, 'user_profile.html', context)

@login_required
def file_list(request):
    """Display a list of uploaded files."""
    files = Upload.objects.all()
    return render(request, 'file_list.html', {'files': files})

@login_required
def update_user_fields(request):
    """Page for updating user profile fields."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    user = request.user
    if request.method == "POST":
        # Fetch data from form submission
        new_email = request.POST.get('email')
        new_nickname = request.POST.get('nickname')

        # Update fields only if they are not blank
        if new_email:
            request.user.email = new_email
            request.user.save()
        if new_nickname:
            profile.nickname = new_nickname
            profile.save()
            request.user.profile.nickname = new_nickname
            request.user.profile.save()
            request.user.username = new_nickname
            request.user.save()
        if 'delete_account' in request.POST:
            Event.objects.filter(owner=user).delete()
            if hasattr(user, 'profile'):
                user.profile.delete()
            user.delete()
            messages.success(request, "Your account had been deleted.")
            return redirect('home')
        # Success message and redirect
        messages.success(request, "Your profile has been updated!")
        return redirect('home')  # Redirect to the home page

    context = {
        'email': request.user.email,
        'nickname': profile.nickname,
    }
    return render(request, 'update_user_fields.html', context)

@login_required
def delete_user(request):
    """Delete user, their profile, related events, and log them out."""
    user = request.user
    
    # Delete all events owned by the user
    Event.objects.filter(owner=user).delete()
    
    # Delete the user's profile
    if hasattr(user, 'profile'):
        user.profile.delete()
    
    # Delete the user account
    user.delete()
    
    
  
    # Log out the user
    logout(request)
    messages.info(request, 'Your account has been deleted.')
    return redirect('home')

@login_required
def home(request):
    """Home view displaying user profile and events for the week."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Query events this week
    events_this_week = Event.objects.filter(
        owner=request.user,
        date__range=[start_of_week.date(), end_of_week.date()]  # Match date within the week
    )

    context = {
        'events_this_week': events_this_week,
        'user_profile': request.user.profile,
    }
    return render(request, 'index.html', context)