import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def search_place(query):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    results = response.json()

    if results["status"] == "OK" and results["results"]:
        place = results["results"][0]  # Pega o primeiro resultado
        return place["place_id"], place["name"], place["formatted_address"]
    else:
        print("Place not found.")
        return None, None, None

def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=rating,reviews&key={GOOGLE_API_KEY}"
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
    unique_reviews = {}

    for review in reviews:
        text = review["text"]
        if text not in unique_reviews:
            unique_reviews[text] = review.get("rating", 0)

    positive_reviews = [text for text, rating in unique_reviews.items() if rating >= 4]
    negative_reviews = [text for text, rating in unique_reviews.items() if rating < 4]

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
    place_id, place_name, address = search_place(query)

    if place_id:
        # Criar link do Google Maps
        maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

        print(f"\nFound place: {place_name}\nAddress: {address}\nLink: {maps_link}\n")

        rating, reviews = get_place_details(place_id)

        if reviews:
            summary = summarize_reviews(reviews)
            print(f"Place Rating: {rating}\nSummary:\n{summary}")
        else:
            print("No reviews found for this place.")
    else:
        print("Place ID retrieval failed.")

if __name__ == "__main__":
    main()
