---
sidebar_position: 2
sidebar_label: "4.2 Whisper"
title: "Chapter 4.2: Speech Understanding with OpenAI Whisper"
description: "Learn to integrate speech recognition for natural robot interaction using Whisper"
keywords: [whisper, speech recognition, asr, openai, voice commands, robotics]
---

# Speech Understanding with OpenAI Whisper

In this chapter, you will learn how to integrate OpenAI's Whisper for robust speech recognition, enabling natural voice-based robot interaction.

## What is Whisper?

**Whisper** is OpenAI's automatic speech recognition (ASR) model:

- **Multilingual**: 99+ languages supported
- **Robust**: Handles noise, accents, technical terms
- **Versatile**: Transcription, translation, language detection
- **Open source**: Available for local deployment

### Model Sizes

| Model | Parameters | VRAM | Speed | Quality |
|-------|------------|------|-------|---------|
| tiny | 39M | ~1GB | Fastest | Basic |
| base | 74M | ~1GB | Fast | Good |
| small | 244M | ~2GB | Moderate | Better |
| medium | 769M | ~5GB | Slow | Great |
| large | 1550M | ~10GB | Slowest | Best |
| turbo | 809M | ~6GB | Fast | Great |

## Installation

### Python Package

```bash
# Install Whisper
pip install openai-whisper

# Install with CUDA support
pip install openai-whisper torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install ffmpeg (required for audio processing)
# Ubuntu
sudo apt install ffmpeg
# Windows (using chocolatey)
choco install ffmpeg
```

### Verify Installation

```python
import whisper

# List available models
print(whisper.available_models())

# Load a model
model = whisper.load_model("base")
print(f"Model loaded: {model}")
```

## Basic Transcription

### Simple Usage

```python
import whisper

# Load model (downloads on first use)
model = whisper.load_model("turbo")

# Transcribe audio file
result = model.transcribe("audio.mp3")

# Print full transcription
print(result["text"])

# Access detailed information
print(f"Language: {result['language']}")
print(f"Segments: {len(result['segments'])}")
```

### Segment Information

```python
result = model.transcribe("speech.wav")

for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

Output:
```
[0.00s - 3.20s] Hello, I need you to pick up the red cup.
[3.20s - 6.50s] Place it on the table next to the laptop.
[6.50s - 8.80s] Then come back here.
```

## Word-Level Timestamps

### Enabling Word Timestamps

```python
result = model.transcribe(
    "audio.mp3",
    word_timestamps=True
)

for segment in result["segments"]:
    print(f"\nSegment: {segment['text']}")
    if "words" in segment:
        for word in segment["words"]:
            print(f"  '{word['word']}': {word['start']:.2f}s - {word['end']:.2f}s")
```

Output:
```
Segment:  Pick up the red cup.
  'Pick': 0.00s - 0.30s
  'up': 0.30s - 0.45s
  'the': 0.45s - 0.55s
  'red': 0.55s - 0.75s
  'cup': 0.75s - 1.10s
```

## Language Detection and Translation

### Automatic Language Detection

```python
# Load audio and detect language
audio = whisper.load_audio("foreign_speech.mp3")
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

# Detect language
_, probs = model.detect_language(mel)
detected_language = max(probs, key=probs.get)
print(f"Detected language: {detected_language} ({probs[detected_language]:.2%})")
```

### Translation to English

```python
# Transcribe and translate to English
result = model.transcribe(
    "german_speech.mp3",
    task="translate"  # Translates to English
)

print(f"Original language: {result['language']}")
print(f"English translation: {result['text']}")
```

## Real-Time Streaming

### Microphone Input

```python
import sounddevice as sd
import numpy as np
import whisper

model = whisper.load_model("base")

def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone."""
    print("Recording...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    print("Recording complete.")
    return audio.flatten()

def transcribe_realtime():
    """Record and transcribe in a loop."""
    while True:
        audio = record_audio(duration=5)

        # Transcribe
        result = model.transcribe(audio)
        text = result["text"].strip()

        if text:
            print(f"Heard: {text}")

            # Check for stop command
            if "stop listening" in text.lower():
                break

if __name__ == "__main__":
    transcribe_realtime()
```

### Voice Activity Detection (VAD)

```python
import webrtcvad
import numpy as np

class VoiceActivityDetector:
    def __init__(self, sample_rate=16000, aggressiveness=3):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration_ms = 30
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

    def is_speech(self, audio_frame):
        """Check if audio frame contains speech."""
        # Convert to 16-bit PCM
        audio_int16 = (audio_frame * 32767).astype(np.int16)
        return self.vad.is_speech(audio_int16.tobytes(), self.sample_rate)

    def get_speech_segments(self, audio):
        """Extract speech segments from audio."""
        segments = []
        speech_start = None

        for i in range(0, len(audio) - self.frame_size, self.frame_size):
            frame = audio[i:i + self.frame_size]
            is_speech = self.is_speech(frame)

            if is_speech and speech_start is None:
                speech_start = i
            elif not is_speech and speech_start is not None:
                segments.append((speech_start, i))
                speech_start = None

        return segments
```

## ROS 2 Integration

### Whisper ASR Node

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from audio_msgs.msg import Audio  # Custom message
import whisper
import numpy as np

class WhisperNode(Node):
    def __init__(self):
        super().__init__('whisper_asr')

        # Load Whisper model
        model_name = self.declare_parameter('model', 'base').value
        self.model = whisper.load_model(model_name)
        self.get_logger().info(f'Loaded Whisper model: {model_name}')

        # Subscribers and publishers
        self.audio_sub = self.create_subscription(
            Audio,
            '/audio/input',
            self.audio_callback,
            10
        )

        self.text_pub = self.create_publisher(
            String,
            '/speech/text',
            10
        )

        # Audio buffer
        self.audio_buffer = []
        self.buffer_duration = 5.0  # seconds
        self.sample_rate = 16000

    def audio_callback(self, msg):
        # Accumulate audio
        audio_data = np.frombuffer(msg.data, dtype=np.float32)
        self.audio_buffer.extend(audio_data)

        # Check if buffer is full
        buffer_samples = int(self.buffer_duration * self.sample_rate)
        if len(self.audio_buffer) >= buffer_samples:
            self.process_audio()

    def process_audio(self):
        # Convert buffer to numpy array
        audio = np.array(self.audio_buffer, dtype=np.float32)
        self.audio_buffer = []

        # Transcribe
        result = self.model.transcribe(audio)
        text = result["text"].strip()

        if text:
            # Publish transcription
            msg = String()
            msg.data = text
            self.text_pub.publish(msg)
            self.get_logger().info(f'Transcribed: {text}')

def main():
    rclpy.init()
    node = WhisperNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Command Parser

```python
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import re

class CommandParser(Node):
    def __init__(self):
        super().__init__('command_parser')

        self.text_sub = self.create_subscription(
            String,
            '/speech/text',
            self.text_callback,
            10
        )

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Command patterns
        self.patterns = {
            r"move forward": self.move_forward,
            r"move backward|go back": self.move_backward,
            r"turn left": self.turn_left,
            r"turn right": self.turn_right,
            r"stop": self.stop,
            r"pick up (.+)": self.pick_up,
        }

    def text_callback(self, msg):
        text = msg.data.lower()
        self.get_logger().info(f'Processing: {text}')

        for pattern, handler in self.patterns.items():
            match = re.search(pattern, text)
            if match:
                handler(match)
                return

        self.get_logger().warn(f'Unknown command: {text}')

    def move_forward(self, match):
        twist = Twist()
        twist.linear.x = 0.5
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Moving forward')

    def move_backward(self, match):
        twist = Twist()
        twist.linear.x = -0.5
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Moving backward')

    def turn_left(self, match):
        twist = Twist()
        twist.angular.z = 0.5
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Turning left')

    def turn_right(self, match):
        twist = Twist()
        twist.angular.z = -0.5
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Turning right')

    def stop(self, match):
        twist = Twist()  # All zeros
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Stopping')

    def pick_up(self, match):
        object_name = match.group(1)
        self.get_logger().info(f'Pick up command: {object_name}')
        # Trigger manipulation action...
```

## Performance Optimization

### Faster Whisper

Use `faster-whisper` for 4x speedup:

```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel

# Load model with CTranslate2
model = WhisperModel("base", device="cuda", compute_type="float16")

# Transcribe
segments, info = model.transcribe("audio.mp3")

print(f"Detected language: {info.language}")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

### GPU Optimization

```python
import torch
import whisper

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")

# Load on GPU
model = whisper.load_model("base", device="cuda")

# Transcribe with FP16 (faster on GPU)
result = model.transcribe("audio.mp3", fp16=True)
```

### Batch Processing

```python
from pathlib import Path

def batch_transcribe(audio_dir, model_name="base"):
    """Transcribe all audio files in directory."""
    model = whisper.load_model(model_name)

    audio_files = list(Path(audio_dir).glob("*.mp3")) + \
                  list(Path(audio_dir).glob("*.wav"))

    results = {}
    for audio_file in audio_files:
        result = model.transcribe(str(audio_file))
        results[audio_file.name] = result["text"]
        print(f"Processed: {audio_file.name}")

    return results
```

## Handling Robot Commands

### Intent Classification

```python
from dataclasses import dataclass
from typing import Optional, List
import re

@dataclass
class RobotCommand:
    intent: str
    action: Optional[str] = None
    object: Optional[str] = None
    location: Optional[str] = None
    parameters: dict = None

class IntentClassifier:
    """Classify robot commands from transcribed speech."""

    def __init__(self):
        self.intents = {
            "navigation": [
                r"go to (.+)",
                r"move to (.+)",
                r"navigate to (.+)",
                r"come here",
                r"follow me",
            ],
            "manipulation": [
                r"pick up (.+)",
                r"grab (.+)",
                r"put (.+) on (.+)",
                r"place (.+) in (.+)",
                r"give me (.+)",
                r"hand me (.+)",
            ],
            "information": [
                r"what do you see",
                r"where is (.+)",
                r"find (.+)",
                r"look for (.+)",
            ],
            "control": [
                r"stop",
                r"pause",
                r"continue",
                r"faster",
                r"slower",
            ],
        }

    def classify(self, text: str) -> RobotCommand:
        text = text.lower().strip()

        for intent, patterns in self.intents.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return self._build_command(intent, pattern, match, text)

        return RobotCommand(intent="unknown")

    def _build_command(self, intent, pattern, match, text):
        cmd = RobotCommand(intent=intent)

        groups = match.groups()
        if intent == "manipulation":
            if groups:
                cmd.object = groups[0]
                if len(groups) > 1:
                    cmd.location = groups[1]

        elif intent == "navigation":
            if groups:
                cmd.location = groups[0]

        elif intent == "information":
            if groups:
                cmd.object = groups[0]

        return cmd

# Usage
classifier = IntentClassifier()

commands = [
    "Pick up the red cup",
    "Go to the kitchen",
    "What do you see?",
    "Stop",
]

for text in commands:
    cmd = classifier.classify(text)
    print(f"'{text}' -> Intent: {cmd.intent}, Object: {cmd.object}, Location: {cmd.location}")
```

---

## Exercise: Build a Voice-Controlled Robot

Create a complete voice command system for a robot.

### Requirements

1. Set up Whisper with ROS 2
2. Implement continuous listening
3. Parse these commands:
   - "Move forward/backward"
   - "Turn left/right"
   - "Pick up [object]"
   - "Go to [location]"
   - "Stop"
4. Publish appropriate ROS 2 messages

### Expected Outcome

- Robot responds to voice commands
- Commands are parsed and executed
- System handles noise and unclear speech
- Graceful handling of unknown commands

### Testing

```bash
# Start the system
ros2 launch voice_control voice_control.launch.py

# Test with audio file
ros2 run voice_control test_command --audio command.wav
```

---

## Summary

OpenAI Whisper enables robust speech recognition for robotics:

- **Easy integration**: Simple Python API
- **Multiple models**: Size/speed trade-offs
- **Multilingual**: Support for 99+ languages
- **Word timestamps**: Precise timing information

Key integration points:
- Real-time microphone input
- ROS 2 audio topics
- Intent classification for commands
- Performance optimization with faster-whisper

In the next chapter, you will learn about vision-language models for scene understanding.

**Next:** [Vision-Language Models](./3-vision-language.md)
