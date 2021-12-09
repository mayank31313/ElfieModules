import requests


class StdErrHandler:
    host="http://localhost:8978"
    @staticmethod
    def getErrorDetails(error_message):
        response = requests.post(f"{StdErrHandler.host}/parseException", json={
            "exceptionBody": error_message
        })
        data = response.json()
        if data['status'] == "OK":
            return data['response']
        return None

    @staticmethod
    def getRecommendations(error_message, question='How can we solve this error ?'):
        response = requests.post(f"{StdErrHandler.host}/recommend", json={
            'error': error_message,
            'question': question
        })

        return response.json()