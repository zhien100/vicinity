
from random import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import csv
import os
import requests
import random
from dotenv import load_dotenv, find_dotenv
from geopy import distance


hospital_list = []
clinic_list = []

# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#              tracker: Tracker,
#              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")
        
#         return []

class ActionSetSearchHospital(Action):
    def name(self) -> Text:
        return "action_set_search_hospital"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #  hospital = True
        return[
            SlotSet("set_clinic", False),
            SlotSet("set_hospital",True)
        ]

class ActionSetSearchClinic(Action):
    def name(self) -> Text:
        return "action_set_search_clinic"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # hospital = False
        return[
            SlotSet("set_hospital",False),
            SlotSet("set_clinic", True)
        ]

class ActionFetchHospitals(Action):
    def name(self) -> Text:
        return "action_fetch_hospitals"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Fetching hospitals...")
        
        print("Fetching hospitals")
        if len(hospital_list) == 0:
            with open('hospital.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    hospital_list.append(row)
        
        dispatcher.utter_message(text="Hospitals fetched")
        return []

class ActionFetchClinics(Action):
    def name(self) -> Text:
        return "action_fetch_clinics"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Fetching clinics...")
        
        if len(clinic_list) == 0:
            with open('clinic.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    clinic_list.append(row)

        dispatcher.utter_message(text="Clinics fetched")
        return []

class ActionCalculateHospitalDistance(Action):
    def name(self) -> Text:
        return "action_calculate_hospital_distance"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        address = tracker.get_slot("address")
        print("*****************")
        print(address)
        
        load_dotenv(find_dotenv())
        api_key = os.environ.get("GOOGLE_API_KEY")

        parameters = {"address": address, "key":api_key}
        URL = "https://maps.googleapis.com/maps/api/geocode/json"


        r = requests.get(url = URL, params = parameters)

        data = r.json()

        print(data)
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        lat_long = (latitude, longitude)

        closest_hospitals = []

        for hospital in hospital_list:
            dist = distance.distance(lat_long, (hospital["LATITUDE"], hospital["LONGITUDE"]))
            for i in range(5):
                if len(closest_hospitals) < i:
                    break

                if len(closest_hospitals) == i:
                    hospital["DISTANCE"] = dist
                    closest_hospitals.append(hospital)
                    break

                elif dist < closest_hospitals[i]["DISTANCE"]:
                    hospital["DISTANCE"] = dist
                    closest_hospitals.insert(i ,hospital)
                    break

        closest_hospitals = closest_hospitals[:5]

        text = "Here are the closest hospitals we've found: \n"
        for i in range(5):
            text += f"No: {i+1}. \n"
            text += f"Name: {closest_hospitals[i]['HOSPITAL NAME']}\n"
            text += f"Address: {closest_hospitals[i]['HOSPITAL ADDRESS']}\n"
            text += f"Email: {closest_hospitals[i]['E-MAIL ADDRESS']}\n"
            text += f"Telephone: {closest_hospitals[i]['TELEPHONE NO.']}\n"
            text += "\n\n"
        
        dispatcher.utter_message(text=text)

        return []

class ActionCalculateClinicDistance(Action):
    def name(self) -> Text:
        return "action_calculate_clinic_distance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        address = tracker.get_slot("address")
        
        load_dotenv(find_dotenv())
        api_key = os.environ.get("GOOGLE_API_KEY")

        parameters = {"address": address, "key":api_key}
        URL = "https://maps.googleapis.com/maps/api/geocode/json"
        r = requests.get(url = URL, params = parameters)

        data = r.json()
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        lat_long = (latitude, longitude)

        closest_clinics = []
        for clinic in clinic_list:
            dist = distance.distance(lat_long, (clinic["LATITUDE"], clinic["LONGITUDE"])).km
            for i in range(5):
                if len(closest_clinics) < i:
                    break

                if len(closest_clinics) == i:
                    clinic["DISTANCE"] = dist
                    closest_clinics.append(clinic)
                    break

                elif dist < closest_clinics[i]["DISTANCE"]:
                    clinic["DISTANCE"] = dist
                    closest_clinics.insert(i ,clinic)
                    break

        closest_clinics = closest_clinics[:5]
        
        text = "Here are the closest clinics we've found: \n"
        for i in range(5):
            text += f"No: {i+1}. \n"
            text += f"Name: {closest_clinics[i]['CLINIC NAME']}\n"
            text += f"Address: {closest_clinics[i]['CLINIC ADDRESS']}\n"
            text += f"Email: {closest_clinics[i]['E-MAIL ADDRESS']}\n"
            text += f"Telephone: {closest_clinics[i]['TELEPHONE NO.']}\n"
            text += "\n\n"
        
        dispatcher.utter_message(text=text)

        return []