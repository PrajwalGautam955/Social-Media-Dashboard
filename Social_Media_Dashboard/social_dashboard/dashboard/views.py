from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User 
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
import requests

from .models import Profile, Post
from .sanitizer import sanitize_post_data


# Register View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})


# Dashboard View
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


# Profile View
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        twitter_key = request.POST.get('twitter_api_key')
        facebook_key = request.POST.get('facebook_api_key')

        if twitter_key:
            profile.twitter_api_key = twitter_key
        if facebook_key:
            profile.facebook_api_key = facebook_key

        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'dashboard/profile.html', {'profile': profile})


# Accounts View
@login_required
def accounts_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if request.POST.get('disconnect') == 'twitter':
            profile.twitter_api_key = ''
            messages.success(request, 'Twitter account disconnected.')
        elif request.POST.get('disconnect') == 'facebook':
            profile.facebook_api_key = ''
            messages.success(request, 'Facebook account disconnected.')
        else:
            twitter_key = request.POST.get('twitter_api_key')
            facebook_key = request.POST.get('facebook_api_key')

            if twitter_key:
                profile.twitter_api_key = twitter_key
                messages.success(request, 'Twitter account connected.')
            if facebook_key:
                profile.facebook_api_key = facebook_key
                messages.success(request, 'Facebook account connected.')

        profile.save()

    return render(request, 'dashboard/accounts.html', {'profile': profile})


# Posts View
@login_required
def posts_view(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        if content:
            Post.objects.create(user=request.user, content=content)
            messages.success(request, 'Post created successfully.')
            return redirect('post')
    posts = Post.objects.filter(user=request.user).order_by('-created_a
