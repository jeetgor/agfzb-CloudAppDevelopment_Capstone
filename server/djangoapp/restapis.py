import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        api_key = kwargs.get("api_key", None)
        if api_key:
            # Basic authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


#  Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"],
                state=dealer_doc['state']
            )
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, **kwargs):
    """ Get Reviews"""
    results = []
    json_result = get_request(url)
    if json_result:
        reviews = json_result["entries"]

        for review in reviews:
            dealer_review = DealerReview(id=review["id"],
                                        name=review["name"],
                                        dealership=review["dealership"],
                                        review=review["review"],
                                        purchase=review["purchase"],
                                        purchase_date=review["purchase_date"],
                                        car_make=review["car_make"],
                                        car_model=review["car_model"],
                                        car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review.get("review", "")))
            results.append(dealer_review)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    # Natural language understanding url
    NLU_API_KEY = "NDMLH1CZRVTiQ7zLrWbuonhYiLEyfZhiZF7AbfKubWeR"

    # Call get_request with a URL parameter
    json_result = get_request("https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/817c5ca5-adff-4b02-a2fe-8810bae23791/v1/analyze", 
                                api_key=NLU_API_KEY, 
                                text=text, 
                                version="2021-08-01",
                                features= {
                                    "sentiment": {},
                                },
                                return_analyzed_text=True)
    if json_result and "sentiment" in json_result:
        sentiment = json_result["sentiment"]["document"]["label"]
        return sentiment