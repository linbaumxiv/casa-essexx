"""
Signals for automated social media announcements.
Triggers Twitter/X updates when new Stores or Products are created.
"""

import tweepy
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Store, Product


def get_twitter_client():
    """Initializes and returns the Tweepy API client using settings credentials."""
    try:
        return tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    except Exception as e:
        print(f"Failed to initialize Twitter Client: {e}")
        return None


@receiver(post_save, sender=Store)
def tweet_new_store(sender, instance, created, **kwargs):
    """Announces a new Store on Twitter/X."""
    if created:
        # Check if we are in testing mode to avoid API errors during 'python manage.py test'
        if getattr(settings, 'TESTING', False):
            return

        client = get_twitter_client()
        if client:
            message = (
                f"🏪 New Store Alert! Check out '{instance.name}' on Casa Essexx. "
                f"\n\n{instance.description}"
            )
            try:
                client.create_tweet(text=message[:280])
            except Exception as e:
                print(f"Twitter Error (Store): {e}")


@receiver(post_save, sender=Product)
def tweet_new_product(sender, instance, created, **kwargs):
    """Announces a new Product arrival on Twitter/X."""
    if created:
        if getattr(settings, 'TESTING', False):
            return

        client = get_twitter_client()
        if client:
            message = (
                f"🛍️ New Arrival at {instance.store.name}!\n\n"
                f"Product: {instance.name}\n"
                f"Description: {instance.description}"
            )
            try:
                client.create_tweet(text=message[:280])
            except Exception as e:
                print(f"Twitter Error (Product): {e}")