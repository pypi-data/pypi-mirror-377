# Pixtools

A collection of multimedia utilities for AI-powered applications.

## Features

- **Text-to-Speech**: Convert text to audio using OpenAI's TTS API
- **Voice Recording**: Record and transcribe audio using OpenAI's Whisper API
- **Audio Playback**: Play audio files with simple controls
- **OpenAI Client**: Streamlined interface for OpenAI API interactions
- **File Caching**: Efficient caching system for API responses and generated content
- **Image Generation**: Generate images using OpenAI's DALL-E API

## Installation

```bash
pip install pixtools
```

## Requirements

- Python 3.10 or higher
- OpenAI API key

## Quick Start

```python
from pixtools import TextToSpeech, VoiceToText, ImageGen, OpenAIClient

# Initialize OpenAI client
client = OpenAIClient(api_key="your-api-key")

# Text-to-speech
tts = TextToSpeech(client)
tts.speak("Hello, world!")

# Voice recording and transcription
voice = VoiceToText(client)
text = voice.record_and_transcribe()

# Image generation
image_gen = ImageGen(client)
image_gen.generate("A beautiful sunset", "sunset.png")
```

## License

MIT License