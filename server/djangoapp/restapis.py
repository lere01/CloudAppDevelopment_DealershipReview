import requests
import json
import logging
from .models import CarDealer, DealerReview
from .helpers import fa_lookup
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):

    logger.info("GET from {} ".format(url))
    try:
        if kwargs.get('api_key'):
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', kwargs['api_key']))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)

    except:
        # If any error occurs
        logger.error("Network exception occurred")

    json_data = json.loads(response.text)

    if kwargs.get('dealerId'):
        new_data = list(filter(
            lambda x: x['doc']['dealership'] == kwargs['dealerId'],
            json_data
        ))
        return new_data

    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    logger.info("POST to {}".format(url))

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"},
                                 params=kwargs, json=payload
                                 )
    except:
        logger.error("Network exception occurred")

    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    dealers = get_request(url)

    if dealers:
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"], state=dealer['state'])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealerId):
    reviews = []
    dealer_reviews = get_request(url, dealerId=dealerId)

    # - Parse JSON results into a DealerView object list
    if dealer_reviews:
        for review in dealer_reviews:
            detail = review['doc']
            review = detail["review"]
            sentiment, emotion, emotion_color = analyze_review_sentiments(review)
            print(detail)

            review_obj = DealerReview(
                car_make=detail['car_make'], car_model=detail['car_model'], car_year=detail['car_year'],
                dealership=detail['dealership'], sentiment=sentiment, reviewer=detail['name'],
                purchase=detail['purchase'], purchase_date=detail['purchase_date'], review=review, 
                emotion=emotion, emotion_color=emotion_color
            )
            reviews.append(review_obj)
        
        return reviews


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/9cab6064-8f89-48a0-9509-f27bfdab97e9/api/sentiment"
    result = get_request(url, text=text)

    # - Get the returned sentiment label such as Positive or Negative
    if result:
        keywords = result["keywords"][0]
        try: 
            emotions = keywords['emotion']
            emotion = fa_lookup[max(emotions, key=emotion.get)].split(':')[0]
            emotion_color = fa_lookup[max(emotions, key=emotion.get)].split(':')[1]
            sentiment = keywords['sentiment']
        except:
            sentiment = "neutral"
            emotion = fa_lookup["indifference"].split(':')[0]
            emotion_color = fa_lookup["indifference"].split(':')[1]
        
        return (sentiment, emotion, emotion_color)
