# dashboard/sanitizer.py

def sanitize_post_data(post_data, platform):
    """
    Cleans and standardizes social media post data across platforms.
    """
    if platform == 'twitter':
        return {
            'id': post_data.get('id_str'),
            'text': post_data.get('text'),
            'likes': post_data.get('favorite_count'),
            'comments': post_data.get('reply_count', 0),  # reply_count requires elevated Twitter API
            'created_at': post_data.get('created_at'),
            'media_url': post_data.get('entities', {}).get('media', [{}])[0].get('media_url', '')
        }

    elif platform == 'facebook':
        return {
            'id': post_data.get('id'),
            'text': post_data.get('message', ''),
            'likes': post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
            'comments': post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
            'created_at': post_data.get('created_time'),
            'media_url': post_data.get('full_picture', '')
        }

    return {}
