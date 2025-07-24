from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User 
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import requests

from .models import Profile, Post
from .sanitizer import sanitize_post_data

# ✅ Facebook Token Check
def check_facebook_connection(access_token):
    url = 'https://graph.facebook.com/v18.0/me'
    params = {
        'fields': 'id,name',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    return response.status_code == 200

# ✅ Instagram Token Check (Dummy — adjust with real check)
def check_instagram_connection(access_token):
    url = 'https://graph.instagram.com/me'
    params = {
        'fields': 'id,username',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    return response.status_code == 200

# ✅ Register View
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

# ✅ Dashboard View
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

# ✅ Profile View
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        facebook_key = request.POST.get('facebook_api_key')
        instagram_key = request.POST.get('instagram_api_key')
        if facebook_key:
            profile.facebook_api_key = facebook_key
        if instagram_key:
            profile.instagram_api_key = instagram_key

        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'dashboard/profile.html', {'profile': profile})

# ✅ Create Post View
@login_required
def create_post_view(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        uploaded_file = request.FILES.get('media_file')

        if uploaded_file:
            fs = FileSystemStorage()
            file_path = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(file_path)
            # Save logic goes here (optional)

        if content:
            Post.objects.create(user=request.user, content=content)
            messages.success(request, 'Post created successfully.')
            return redirect('dashboard')

    return render(request, 'dashboard/Create_post.html')

# ✅ View Post
@login_required
# View Post
def view_post(request):
    return render(request, 'dashboard/view_post.html')

# ✅ Accounts View (connect/disconnect Facebook/Instagram)
@login_required
def accounts_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if request.POST.get('disconnect') == 'instagram':
            profile.instagram_api_key = ''
            messages.success(request, 'Instagram account disconnected.')

        elif request.POST.get('disconnect') == 'facebook':
            profile.facebook_api_key = ''
            messages.success(request, 'Facebook account disconnected.')

        else:
            instagram_key = request.POST.get('instagram_api_key')
            facebook_key = request.POST.get('facebook_api_key')

            if instagram_key:
                if check_instagram_connection(instagram_key):
                    profile.instagram_api_key = instagram_key
                    messages.success(request, 'Instagram account connected successfully!')
                else:
                    messages.error(request, 'Invalid Instagram API key.')

            if facebook_key:
                if check_facebook_connection(facebook_key):
                    profile.facebook_api_key = facebook_key
                    messages.success(request, 'Facebook account connected successfully!')
                else:
                    messages.error(request, 'Invalid Facebook API key.')

        profile.save()
        return redirect('accounts')

    return render(request, 'dashboard/accounts.html', {'profile': profile})

# ✅ Posts View
@login_required
def posts_view(request):
    if request.method == 'POST':
        post_content = request.POST.get('post_content')
        if post_content:
            Post.objects.create(user=request.user, content=post_content)
            messages.success(request, 'Post created successfully.')
            return redirect('posts')
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/post.html', {'posts': posts})


# Handle and Store the Access Token
@login_required

def facebook_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('dashboard')

    fb_app_id = '1794963388041375'
    fb_app_secret = '57b70aada8a31a23320bd22f0bda3152T'
    redirect_uri = 'https://yourdomain.com/facebook/callback/'

    # Exchange code for access token
    token_url = (
        f'https://graph.facebook.com/v19.0/oauth/access_token?client_id={fb_app_id}'
        f'&redirect_uri={redirect_uri}&client_secret={fb_app_secret}&code={code}'
    )

    response = requests.get(token_url)
    data = response.json()
    access_token = data.get('EAAZAggnshCJ8BPLoNE6zRx6uUJ6RvHI6zwTFcW0Q058EAF6575XhJT27BUMDVKuHzIk6lw04FL7zntp8gtyg2tYGgUUxODNNSKK2KBfVJKhdGZAh0eVDO1xvRVj3YJBkKGXfQRgFcyo4Y7UhIwXXtuGyOm4kEduMZCv4E8IqrG14tymZCxr1aGFiDvXAMHRywZBO1ZCmGtpZCtYAm0dcWCCrZCwe7gOjoZCoatEbl')

    if access_token:
        profile = request.user.profile
        profile.facebook_access_token = access_token
        profile.save()

    return redirect('dashboard')





# ✅ Fetch Social Posts (Instagram + Facebook API)
@login_required
def fetch_social_posts(request):
    profile = Profile.objects.get(user=request.user)
    all_posts = []

    # Instagram Posts
    if profile.instagram_api_key:
        try:
            ig_response = requests.get(
                f"https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,timestamp,username&access_token={profile.instagram_api_key}"
            )
            if ig_response.status_code == 200:
                ig_data = ig_response.json().get('data', [])
                for post in ig_data:
                    cleaned = sanitize_post_data(post, 'instagram')
                    cleaned['platform'] = 'Instagram'
                    all_posts.append(cleaned)
            else:
                print("Instagram error:", ig_response.text)
        except Exception as e:
            print("Instagram exception:", e)

    # Facebook Posts
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
