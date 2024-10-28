import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_place_id(query):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
    }
    data = {
        "textQuery": query,
    }
    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()

    if "places" in response_json and response_json["places"]:
        place = response_json["places"][0]
        return place["id"], place["displayName"]["text"], place["formattedAddress"]
    else:
        print("Place not found.")
        return None, None, None

def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    place_data = response.json()

    if "result" in place_data:
        result = place_data["result"]
        rating = result.get("rating", "N/A")
        reviews = result.get("reviews", [])
        return rating, reviews
    else:
        print("Details not found for the specified place ID.")
        return None, None

def summarize_reviews(reviews):
    positive_reviews = [review["text"] for review in reviews if review.get("rating", 0) >= 4]
    negative_reviews = [review["text"] for review in reviews if review.get("rating", 0) < 4]

    chat_prompt = (
        f"Please summarize the reviews of a place with the following details:\n"
        f"Positive reviews: {positive_reviews}\n"
        f"Negative reviews: {negative_reviews}\n\n"
        "Summarize the best and worst aspects based on these reviews."
    )

    response = model.generate_content(chat_prompt)

    return response.text

def main():
    query = input("Enter the place you want to search for: ")
    place_id, place_name, address = get_place_id(query)

    if place_id:
        print(f"\nFound place: {place_name}\nAddress: {address}\n")

        rating, reviews = get_place_details(place_id)

        if reviews:
            summary = summarize_reviews(reviews)
            print(f"\nPlace Rating: {rating}\nSummary:\n{summary}")
        else:
            print("No reviews found for this place.")
    else:
        print("Place ID retrieval failed.")

if __name__ == "__main__":
    main()
