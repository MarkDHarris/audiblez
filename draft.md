# Architectural Decision Record: Local TTS Pipeline

We have evaluated the Kokoro-82M model running locally on Apple Silicon. 
The pipeline produces high-fidelity 24 kHz speech using native CPU execution, 
achieving approximately 8 to 10 times real-time generation speed.
