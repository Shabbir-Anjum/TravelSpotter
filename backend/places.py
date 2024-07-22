from opencage.geocoder import OpenCageGeocode
import requests
from dotenv import load_dotenv
import os

class Places:
    def __init__(self):
        load_dotenv()
        self.geocoding_api_key = os.getenv("GEOCODING_API_KEY")
        self.rapid_api_key = os.getenv("RAPID_API_KEY")
        self.rapid_api_host = os.getenv("RAPID_API_HOST")

    def get_latitude_longitude(self, address):
        """
        Get latitude and longitude coordinates for a given address.
        """ 
        query = address
        geocoder = OpenCageGeocode(self.geocoding_api_key)

        results = geocoder.geocode(query)
        
        res = ""
        res += str(results[0]['geometry']['lat'])
        res += ","
        res += str(results[0]['geometry']['lng'])
       
        return res
        
        
    def get_nearby_places(self, lat_lng, place_type, radius=10000):
        """
        Get nearby places based on latitude, longitude, and radius.
        """
        
        url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

        querystring = {"location":lat_lng,"type":place_type,"radius":radius,"language":"en"}

        headers = {
            "x-rapidapi-key": self.rapid_api_key,
            "x-rapidapi-host": self.rapid_api_host
        }

        response = requests.get(url, headers=headers, params=querystring)

        return response
        
        