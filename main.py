import json
import requests
import speech_recognition as sr
import pyttsx3
import re
import threading
import time

API_KEY = "toLx1kZK8ag7"
PROJECT_TOKEN = "tMOVOooQOTti"
RUN_TOKEN = "tR09UzFt5sPz"


class Data1:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data',
                                params=self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    def get_total_deaths(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Deaths:":
                return content['value']

    def get_country_data(self, country):
        data = self.data['country']

        for content in data:
            if content['name'].lower() == country.lower():
                return content
        return "0"

    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries

    def update_data(self):
        response = requests.post(f'https://parsehub.com/api/v2/projects/{PROJECT_TOKEN}/run',
                                params=self.params)
        old_data = self.data

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print('Data updated.')
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()

# data2 = Data2(API_KEY1, PROJECT_TOKEN1)


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()


def main():
    print("program started")
    data1 = Data1(API_KEY, PROJECT_TOKEN)
    end = "stop"
    country_list = set(data1.get_list_of_countries())

    country_patterns = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data1.get_country_data(country)['totalCases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data1.get_country_data(country)['totalDeaths'],
        re.compile("cases [\w\s]+"): lambda country: data1.get_country_data(country)['totalCases'],
        re.compile("deaths [\w\s]+"): lambda country: data1.get_country_data(country)['totalDeaths'],
    }

    total_patterns = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data1.get_total_cases,
        re.compile("total cases [\w\s]+"): data1.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data1.get_total_deaths,
        re.compile("total deaths [\w\s]+"): data1.get_total_deaths,
    }
    update_cmd = "update"

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in country_patterns.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in total_patterns.items():
            if pattern.match(text):
                result = func()
                break

        if text == update_cmd:
            result = "Data is being updated. This may take some while."
            data1.update_data()

        if result:
            print(result)
            speak(result)

        if text.find(end) != -1:
            print("Exiting...")
            break


main()
