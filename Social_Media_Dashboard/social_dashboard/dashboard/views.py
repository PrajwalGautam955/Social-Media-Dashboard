

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth import login
from .models import Profile
from django.contrib.auth import logout
import requests
from .sanitizer import sanitize_post_data
from django.http import JsonResponse
from .models import Post


# Profile View
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        facebook_key = request.POST.get('facebook_api_key')
        # Instagram API key is removed — using login instead

        if facebook_key is not None:
            profile.facebook_api_key = facebook_key

        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES.get('profile_picture')

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'dashboard/profile.html', {'profile': profile})

# @login_required
# def posts_view(request):
#     if request.method == 'POST':
#         content = request.POST.get('post_content')
#         if content:
#             Post.objects.create(user=request.user, content=content)
#             messages.success(request, 'Post created successfully.')
#             return redirect('dashboard')
#     posts = Post.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'dashboard/post.html', {'posts': posts})

# @login_required
# def view_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     return render(request, 'dashboard/view_post.html', {'post': post})




# Register View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Optional: log the user in after registration
            messages.success(request, 'Account created successfully.')
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})

#dashboard
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

# Profile View
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        facebook_key = request.POST.get('EAAZAggnshCJ8BPKmZBNUmt7ZBha0khFTvkc7d8m3y9q1wEjoQE12doG9pbTrVOph9go43XYfjyCq4XsLs0fGJVEDUGCx67wGPWL7Yu5nfDLXS9CduMuv5DJA9mfamUFMpsJV1ZCKFZB3G43YXEpmBCxZBMOjCJ7KhEcvat6ZAjXK0GJcvAsUlCgvWFdGvNCSztCeRMZBgwjmcuEQpbQZC5WcmqvSooDrv64kYqbYP')
        # Instagram API key is removed — using login instead

        if facebook_key is not None:
            profile.facebook_api_key = facebook_key

        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES.get('profile_picture')

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'dashboard/profile.html', {'profile': profile})



#Create Post view
def create_post_view(request):
    return render(request, 'dashboard/Create_post.html')

def create_post_view(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        uploaded_file = request.FILES.get('media_file')

        if uploaded_file:
            fs = FileSystemStorage()
            file_path = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(file_path)
            # Save content + file_url to DB (if using a model)

        # Handle saving logic or redirect
    return render(request, 'dashboard/Create_post.html')



# View Post
def view_post(request):
    return render(request, 'dashboard/view_post.html')

# Accounts View

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile

@login_required
def accounts_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        disconnect_account = request.POST.get('disconnect')
        instagram_key = request.POST.get('instagram_api_key')
        facebook_key = request.POST.get('facebook_api_key')

        # Handle disconnections
        if disconnect_account == 'instagram':
            profile.instagram_api_key = ''
            messages.success(request, 'Instagram account disconnected.')
        elif disconnect_account == 'facebook':
            profile.facebook_api_key = ''
            messages.success(request, 'Facebook account disconnected.')

        # Handle new connections
        if instagram_key:
            profile.instagram_api_key = instagram_key
            messages.success(request, 'Instagram account connected.')

        if facebook_key:
            profile.facebook_api_key = facebook_key
            messages.success(request, 'Facebook account connected.')

        profile.save()

    return render(request, 'dashboard/accounts.html', {'profile': profile})



# @login_required
# def accounts_view(request):
#     profile, _ = Profile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         if request.POST.get('disconnect') == 'twitter':
#             profile.twitter_api_key = ''
#             messages.success(request, 'Twitter account disconnected.')
#         elif request.POST.get('disconnect') == 'facebook':
#             profile.facebook_api_key = ''
#             messages.success(request, 'Facebook account disconnected.')
#         else:
#             twitter_key = request.POST.get('twitter_api_key')
#             facebook_key = request.POST.get('facebook_api_key')

#             if twitter_key:
#                 profile.twitter_api_key = twitter_key
#                 messages.success(request, 'Twitter account connected.')
#             if facebook_key:
#                 profile.facebook_api_key = facebook_key
#                 messages.success(request, 'Facebook account connected.')

#         profile.save()

#     return render(request, 'dashboard/accounts.html', {'profile': profile})


# Posts View
@login_required
def posts_view(request):
    if request.method == 'POST':
        post_content = request.POST.get('post_content')
        if post_content:
            print("New post to share:", post_content)  # Future: send to API
            messages.success(request, 'Post created (mock).')
    return render(request, 'dashboard/post.html')




#  APi - Integrations

@login_required
def fetch_social_posts(request):
    profile = Profile.objects.get(user=request.user)
    all_posts = []

    # Twitter API Call (mocked for now)
    if profile.twitter_api_key:
        try:
            twitter_response = requests.get(
                "https://api.twitter.com/1.1/statuses/user_timeline.json?count=5",
                headers={"Authorization": f"Bearer {profile.twitter_api_key}"}
            )
            if twitter_response.status_code == 200:
                twitter_data = twitter_response.json()
                for post in twitter_data:
                    cleaned = sanitize_post_data(post, 'twitter')
                    cleaned['platform'] = 'Twitter'
                    all_posts.append(cleaned)
            else:
                print("Twitter error:", twitter_response.text)
        except Exception as e:
            print("Twitter exception:", e)

    # Facebook API Call (mocked for now)
    if profile.facebook_api_key:
        try:
            fb_response = requests.get(
                f"https://graph.facebook.com/v12.0/me/posts?fields=message,created_time,full_picture,comments.summary(true),likes.summary(true)&access_token={profile.facebook_api_key}"
            )
            if fb_response.status_code == 200:
                fb_data = fb_response.json().get('data', [])
                for post in fb_data:
                    cleaned = sanitize_post_data(post, 'facebook')
                    cleaned['platform'] = 'Facebook'
                    all_posts.append(cleaned)
            else:
                print("Facebook error:", fb_response.text)
        except Exception as e:
            print("Facebook exception:", e)

    return JsonResponse({'posts': all_posts})
