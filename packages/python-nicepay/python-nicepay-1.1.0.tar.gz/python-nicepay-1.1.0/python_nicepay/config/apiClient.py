import json

import requests
import urllib.parse
import webbrowser


class apiClient:

    @staticmethod
    def send(host, header, request, endpoint):
        response = requests.post(url=host + endpoint, headers=header, json=request)
        return response.json()

    @staticmethod
    def sendDelete(host, header, request, endpoint):
        response = requests.delete(url=host + endpoint, headers=header, json=request)
        return response.json()

    @staticmethod
    def get(host, request, endpoint):
        data = urllib.parse.urlencode(request)
        webbrowser.open(f"{host}{endpoint}?{data}")

    @staticmethod
    def sendUrl(host, request, endpoint):
        response = requests.post(url=host + endpoint, data=request)
        return apiClient.safe_json(response)

    @staticmethod
    def redirect(host, tXid, endpoint):
        url = f"{host}{endpoint}?tXid={tXid}"
        webbrowser.open(url)
        return url

    def safe_json(response):
        try:
            # normal case: already valid JSON
            return response.json()
        except ValueError:
            text = response.text.strip()
            # try to strip until first {
            if "{" in text:
                try:
                    json_str = text[text.index("{") :]
                    return json.loads(json_str)
                except Exception:
                    pass
            # fallback: return raw text
            return {"raw": text}