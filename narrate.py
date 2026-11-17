#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf
import spacy
from kokoro import KPipeline
import subprocess

def synthesize_text_file(input_path: Path, output_path: Path, voice: str = 'af_heart', speed: float = 1.0):
    text = input_path.read_text(encoding='utf-8').strip()
    if not text:
        print("Error: Input file is empty.")
        return

    # Load spacy sentencizer to break text into natural spoken phrases
    nlp = spacy.load('xx_ent_wiki_sm')
    nlp.add_pipe('sentencizer')
    doc = nlp(text)
    sentences = [s.text.strip() for s in doc.sents if s.text.strip()]

    print(f"Loaded '{input_path.name}' ({len(text):,} chars, {len(sentences)} sentences).")
    print(f"Synthesizing with voice '{voice}' at {speed}x speed...")

    lang_code = voice[0]  # 'a' for American, 'b' for British
    pipeline = KPipeline(lang_code=lang_code)

    audio_segments = []
    for i, sent in enumerate(sentences, 1):
        print(f"[{i}/{len(sentences)}] {sent[:60]}...")
        for _, _, audio in pipeline(sent, voice=voice, speed=speed, split_pattern=r'\n\n'):
            audio_segments.append(audio)

    if not audio_segments:
        print("No audio generated.")
        return

    raw_audio = np.concatenate(audio_segments)
    temp_wav = output_path.with_suffix('.tmp.wav')
    sf.write(temp_wav, raw_audio, 24000)

    # If the user specified .m4a or .mp3, compress with ffmpeg; otherwise leave as .wav
    if output_path.suffix.lower() in ['.m4a', '.m4b']:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(temp_wav),
            '-c:a', 'aac', '-b:a', '64k', str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        temp_wav.unlink()
    elif output_path.suffix.lower() == '.mp3':
        subprocess.run([
            'ffmpeg', '-y', '-i', str(temp_wav),
            '-c:a', 'libmp3lame', '-q:a', '2', str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        temp_wav.unlink()
    else:
        temp_wav.rename(output_path)

    print(f"✅ Finished: {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a Markdown or text document into spoken audio.")
    parser.add_argument("input_file", type=Path, help="Path to .txt or .md document")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output audio file path (.m4a, .mp3, or .wav)")
    parser.add_argument("-v", "--voice", default="af_heart", help="Kokoro voice (default: af_heart)")
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="Speech rate multiplier (default: 1.0)")

    args = parser.parse_args()
    output = args.output or args.input_file.with_suffix('.m4a')
    synthesize_text_file(args.input_file, output, voice=args.voice, speed=args.speed)