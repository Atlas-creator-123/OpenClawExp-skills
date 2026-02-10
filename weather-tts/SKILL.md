---
name: weather-tts
description: Get weather and speak it aloud using TTS. Use when user asks about weather and wants voice output.
---

# Weather TTS Skill

## Usage

```bash
# Get current weather for a city
python scripts/weather_tts.py "Shenzhen"

# Get forecast
python scripts/weather_tts.py "Shenzhen" --forecast 3

# Custom message
python scripts/weather_tts.py "Shenzhen" --say "Don't forget your umbrella!"
```

## Scripts

### weather_tts.py

Fetches weather from wttr.in and speaks it using TTS.

**Options:**
- `--forecast N` - Show N day forecast (default: 1)
- `--say TEXT` - Custom text to speak (default: weather info)
- `--lang LANG` - Language: en or zh (default: auto-detect from text)

## Examples

```bash
python scripts/weather_tts.py "Shenzhen"
python scripts/weather_tts.py "London" --forecast 3 --say "It's going to rain!"
python scripts/weather_tts.py "Tokyo" --lang en
```
