from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import tweepy
from .models import Store, Product

def get_twitter_client():
    return tweepy.Client(
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
    )

@receiver(post_save, sender=Store)
def tweet_new_store(sender, instance, created, **kwargs):
    if created:  #tweet when the store is first created
        client = get_twitter_client()
        message = f"🏪 New Store Alert! Check out '{instance.name}' on Casa Essexx. \n\n{instance.description}"
        try:
            client.create_tweet(text=message[:280]) # Twitter limit check
        except Exception as e:
            print(f"Twitter Error: {e}")

@receiver(post_save, sender=Product)
def tweet_new_product(sender, instance, created, **kwargs):
    if created: #tweet when a product is added
        client = get_twitter_client()
        message = f"🛍️ New Arrival at {instance.store.name}!\n\nProduct: {instance.name}\nDescription: {instance.description}"
        try:
            client.create_tweet(text=message[:280])
        except Exception as e:
            print(f"Twitter Error: {e}")