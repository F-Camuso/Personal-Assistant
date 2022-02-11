
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = "https://accounts.spotify.com/api/token"

DEVICE_API = 'https://api.spotify.com/v1/me/player/devices'
MY_PLAYLISTS = 'https://api.spotify.com/v1/me/playlists'
PLAY = 'https://api.spotify.com/v1/me/player/play'
NEXT = 'https://api.spotify.com/v1/me/player/next'
VOLUME = 'https://api.spotify.com/v1/me/player/volume'
USER_INFO = 'https://api.spotify.com/v1/me'
CREATE_PLAYLIST = 'https://api.spotify.com/v1/users/'    
CURRENT_TRACK = 'https://api.spotify.com/v1/me/player/currently-playing'

# for local testing use localhost 
REDIRECT_URI = 'https://js-server-f-camuso.cloud.okteto.net/'
# REDIRECT_URI = 'http://localhost:3000/'

# preciso armazenar os códigos em um BD usando alguma criptografia e trazer pra ca
# problema 401 toda vez que eu reseto
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''   

def refresh_token():
    payload = {"grant_type": "refresh_token",
              "refresh_token": REFRESH_TOKEN}
    print(json.dumps(payload))
    rCode = requests.post(TOKEN, headers={
                        "Authorization": f"Basic {os.getenv('IDSECRET')}",
                        "Content-type": "application/x-www-form-urlencoded"
                    },
                    data = payload)
    ACCESS_TOKEN = rCode.json()['access_token'] 
    return 

def get_devices():
    resDevice = requests.get(DEVICE_API,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Bearer {}".format(ACCESS_TOKEN)
                        })
                        
    return resDevice

def get_playlists():
    resMyPlaylist = requests.get(MY_PLAYLISTS,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {}".format(ACCESS_TOKEN)
                    })

    return resMyPlaylist 

class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender = tracker.sender_id
        url = REDIRECT_URI+'sender/'+sender
        x = requests.get(url)
        print("get Sender_id response: ", x.status_code)
        dispatcher.utter_message(text=f"e ae, qual a boa?")
        
        
        return []

class ActionAccessSpotify(Action):

    def name(self) -> Text:
        return "action_access_spotify"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        url = 'https://accounts.spotify.com/authorize?client_id='
        url += os.getenv('ID')
        url += '&response_type=code'
        url += '&redirect_uri='+ REDIRECT_URI + 'code'
        url += '&scope=user-read-private%20user-read-email%20user-modify-playback-state%20user-read-playback-position%20user-library-read%20streaming%20user-read-playback-state%20user-read-recently-played%20playlist-read-private%20playlist-modify-private'
        # url += '&show_dialog=true'
        dispatcher.utter_message(text="Clique no link para acessar sua conta")
        dispatcher.utter_message(response="utter_link", link_name = "spotify", link = url)

        return []

class ActionConnected(Action):

    def name(self) -> Text:
        return "action_connect_spotify"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        code = tracker.latest_message['entities'][0]['value'] 
    
        payload = {"grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI+"code"}
        rCode = requests.post(TOKEN, headers={
                                "Authorization": f"Basic {os.getenv('IDSECRET')}",
                                "Content-type": "application/x-www-form-urlencoded"
                            },
                            data = payload)
        # [FIX] The dispatcher is not working zzz
        print("get Code response: ", rCode.status_code)        
        if(rCode.status_code == 200):
            dispatcher.utter_message(text=f"Você foi conectado no spotify :D")

        global ACCESS_TOKEN
        global REFRESH_TOKEN
        ACCESS_TOKEN = rCode.json()['access_token']
        REFRESH_TOKEN = rCode.json()['refresh_token']

        return []
        
class ActionExecuteFunction(Action):

    def name(self) -> Text:
        return "action_execute_function"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        global ACCESS_TOKEN
      
        #Daqui pra baixo é temporário, só pra testar mesmo
      
        function_slot = tracker.get_slot("function_slot")
        object_slot = tracker.get_slot("object_slot")

        # execute_something(function_slot,object_slot)
        if(function_slot == 'show'):
                
            if(object_slot == 'devices'):
                devices = get_devices()
                if(devices.status_code == 200):
                    r = devices.json()
                    # print(devices)
                    dispatcher.utter_message(text=f"Estes são os dispositivos conectados atualmente:")
                    for results in r["devices"]:
                        dispatcher.utter_message(text=f"device = {results['name']}")    
                
                if(get_devices().status_code == 401):
                    print('entrei no refresh')
                    ACCESS_TOKEN = refresh_token()
            
            if(object_slot == 'playlists'):
                playlists = get_playlists()
                if(playlists.status_code == 200):
                    p = playlists.json()
                    playlist_string = ""
                    dispatcher.utter_message(text=f"Estas são suas playlists:")
                    for results in p["items"]:
                        playlist_string += results['name'] + "\n"
                    dispatcher.utter_message(text=f"{playlist_string}")    
                if(playlists.status_code == 401):
                    print('entrei no refresh')
                    ACCESS_TOKEN = refresh_token()

        return []    



def get_currentTrack():
    currentTrack = requests.get(CURRENT_TRACK,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(ACCESS_TOKEN)
                })  
    return currentTrack.json()

class ActionGetCurrentTrack(Action):

    def name(self) -> Text:
        return "action_get_current_track"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        dispatcher.utter_message(text=f"{get_currentTrack()['item']['name'] }") 

        return []

# def activate_player(text):
#     jsonTrack = get_currentTrack()
#     if(text == 'play'):
#         print('oi')
#     if(text == 'pause'):

#     return []
# class ActionActivatePlayer(Action):
    
#     def name(self) -> Text:
#         return "action_access_player"
    
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:

#         function_slot = tracker.getSlot["function_slot"]
#         activate_player(function_slot)
#         return [SlotSet["function_slot", None]]