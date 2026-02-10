# 🌤️ Weather TTS Skill

Weather fetcher with Text-to-Speech voice output for OpenClaw. Uses wttr.in for weather data and speaks it aloud.

## Features

- 🌡️ **Current Weather** - Temperature, conditions, humidity, wind
- 📅 **Forecasts** - Multi-day weather predictions
- 🔊 **TTS Voice** - Speaks weather info in natural voice
- 🌍 **Global Coverage** - Cities worldwide
- 🇨🇳 **Chinese Support** - Works great for Chinese cities

## Quick Start

```bash
# Navigate to skill scripts
cd "/Users/Spike/Library/Application Support/OpenClaw/skills/weather-tts/scripts"

# Get current weather for a city
python3 weather_tts.py "Shenzhen"

# Get 3-day forecast
python3 weather_tts.py "Shenzhen" --forecast 3

# Custom message with voice
python3 weather_tts.py "London" --say "Don't forget your umbrella!"
```

## Examples

```bash
# Basic weather
python3 weather_tts.py "Beijing"

# Multi-day forecast
python3 weather_tts.py "Shanghai" --forecast 5

# Custom spoken message
python3 weather_tts.py "Tokyo" --say "It's going to rain today!"

# English output
python3 weather_tts.py "Paris" --lang en

# Chinese cities work great
python3 weather_tts.py "深圳"
python3 weather_tts.py "北京" --forecast 3
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--forecast N` | Show N day forecast | 1 |
| `--say TEXT` | Custom text to speak | Weather info |
| `--lang LANG` | Language: en or zh | Auto-detect |

## Output Example

```
深圳天气 ☀️
温度: 24°C
天气: 晴朗
湿度: 65%
风向: 东南风 3级

🌤️ 语音播报: 深圳今天天气晴朗，温度24度...

📅 未来3天预报:
明天: 晴朗 22-26°C
后天: 多云 20-24°C
```

## How It Works

1. Fetches weather data from **wttr.in** (free weather API)
2. Parses temperature, conditions, humidity, wind
3. Generates natural language summary
4. Uses OpenClaw TTS to speak the weather

## Supported Cities

Any city recognized by wttr.in:
- Chinese: 深圳, 北京, 上海, 成都, 杭州...
- Global: London, Tokyo, New York, Paris, Sydney...

## Browser Integration

The skill uses OpenClaw's TTS (Text-to-Speech) for voice output. Make sure TTS is configured in OpenClaw settings.

## Use Cases

- ☕ Morning weather briefing while having coffee
- 🚗 Weather check before commuting
- 🏃 Outdoor activity planning
- 🌧️ Reminder to bring umbrella

## License

MIT

## Contributing

Feel free to submit issues and pull requests!
