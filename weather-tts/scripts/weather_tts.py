#!/usr/bin/env python3
"""
Weather TTS - Get weather and speak it aloud
Usage: python weather_tts.py <CITY> [--forecast N] [--say TEXT] [--lang en|zh]
"""

import subprocess
import sys
import os
import argparse
import json
import urllib.request

def get_weather(city, forecast_days=1):
    """Fetch weather from wttr.in"""
    try:
        url = f"https://wttr.in/{city}?format=j1&m"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        return {"error": str(e)}

def format_weather(data, forecast_days=1):
    """Format weather data for speech"""
    if "error" in data:
        return f"Sorry, I couldn't get weather for that location."

    current = data.get("current_condition", [{}])[0]
    temp = current.get("temp_C", "?")

    # Get today's weather
    weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
    humidity = current.get("humidity", "?")
    wind = current.get("windspeedKmph", "?")

    speech = f"Weather in your location: {weather_desc}, {temp} degrees Celsius, humidity {humidity} percent, wind {wind} kilometers per hour."

    # Add forecast if requested
    if forecast_days > 0:
        forecast = data.get("weather", [])[:forecast_days]
        for day in forecast:
            date = day.get("date", "")
            max_temp = day.get("tempMaxC", "?")
            min_temp = day.get("tempMinC", "?")
            desc = day.get("weatherDesc", [{}])[0].get("value", "Unknown")
            speech += f" On {date}, expect {desc}, temperatures from {min_temp} to {max_temp} degrees."

    return speech

def speak(text, lang="en"):
    """Use TTS to speak the text"""
    # Generate TTS via curl to ElevenLabs/OpenClaw TTS endpoint
    tts_url = "http://127.0.0.1:3499/tts"

    try:
        data = json.dumps({"text": text, "lang": lang}).encode('utf-8')
        req = urllib.request.Request(tts_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=10) as response:
            mp3_path = response.read().decode('utf-8').strip()

        # Play the audio
        subprocess.run(['afplay', mp3_path], check=True)
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        print(f"\n{text}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description='Weather TTS')
    parser.add_argument('city', nargs='?', default="Shenzhen", help='City name')
    parser.add_argument('--forecast', type=int, default=1, help='Number of forecast days')
    parser.add_argument('--say', type=str, default=None, help='Custom text to speak')
    parser.add_argument('--lang', type=str, default='en', help='Language: en or zh')

    args = parser.parse_args()

    if args.say:
        text = args.say
    else:
        data = get_weather(args.city, args.forecast)
        text = format_weather(data, args.forecast)

    print(f"\n{text}\n")
    speak(text, args.lang)

if __name__ == "__main__":
    main()
