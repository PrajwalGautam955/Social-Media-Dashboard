# your_app/pipeline.py

from .models import Profile

def save_facebook_token(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        access_token = response.get('access_token')
        if access_token:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.facebook_token = access_token
            profile.save()
