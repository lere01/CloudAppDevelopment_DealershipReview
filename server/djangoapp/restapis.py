import requests
import json
import logging
# import related models here
from .models import CarDealer, DealerReview
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
        json_data = list(filter(
            lambda x: x['doc']['id'] == kwargs['dealerId'],
            json_data
        ))

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
    # - Call get_request() with specified arguments
    dealer = get_request(url, dealerId=dealerId)

    # - Parse JSON results into a DealerView object list
    if dealer:
        detail = dealer[0]['doc']
        review = detail["review"]
        sentiment = analyze_review_sentiments(review)

        review_obj = DealerReview(
            car_make=detail['car_make'], car_model=detail['car_model'], car_year=detail['car_year'], 
            dealership=detail['dealership'], id=detail['id'], sentiment=sentiment, reviewer=detail['name'],
            purchase=detail['purchase'], purchase_date=detail['purchase_date'], review=review
        )
        return review_obj


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    # - Call get_request() with specified arguments

    url = "https://us-south.functions.appdomain.cloud/api/v1/web/9cab6064-8f89-48a0-9509-f27bfdab97e9/api/sentiment"
    result = get_request(url, text=text)
    
    # - Get the returned sentiment label such as Positive or Negative
    if result:
        sentiment = result["keywords"][0]["sentiment"]["label"]
        return sentiment
