#!/usr/bin/env python3
"""
Elia's Voice - Multi-tone TTS using Kokoro
Usage: speak [OPTIONS] "Your text here"
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

VENV = Path.home() / ".venvs" / "tts"
MODEL = "mlx-community/Kokoro-82M-bf16"

TONES = {
    "default": {"voice": "ff_siwis", "speed": 1.0},
    "emergency": {"voice": "ff_siwis", "speed": 1.2},
    "sexy": {"voice": "ff_siwis", "speed": 0.8},
    "serious": {"voice": "ff_siwis", "speed": 0.95},
    "joyful": {"voice": "ff_siwis", "speed": 1.15},
    "angry": {"voice": "ff_siwis", "speed": 1.2},
    "sad": {"voice": "ff_siwis", "speed": 0.75},
    "tired": {"voice": "ff_siwis", "speed": 0.7},
    "sassy": {"voice": "ff_siwis", "speed": 1.1},
    "boss": {"voice": "ff_siwis", "speed": 0.9},
    "whisper": {"voice": "ff_siwis", "speed": 0.75},
}


def split_text_into_chunks(text, max_length=400):
    """Split text into chunks that won't exceed the token limit."""
    sentences = (
        text.replace(". ", ".|").replace("! ", "!|").replace("? ", "?|").split("|")
    )
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_length + len(sentence) > max_length:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0

        current_chunk.append(sentence)
        current_length += len(sentence) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text]


def find_wav_file(directory):
    """Find the actual wav file in the output directory."""
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".wav"):
                return os.path.join(root, f)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Elia's Voice - Multi-tone TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tones:
  -e, --emergency  Urgent, fast
  -x, --sexy       Slow, smooth (sultry)
  -s, --serious    Steady, neutral
  -j, --joyful     Fast, bright
  -a, --angry      Fast, harsh
  -d, --sad        Slow, melancholic
  -t, --tired      Slow, drowsy
  -y, --sassy      Confident, playful
  -b, --boss       Authoritative
  -w, --whisper    Soft, intimate

Examples:
  speak "Bonjour!"
  speak -e "C'est urgent!"
  speak -x "Tu me manques..."
  speak --name="mon-message" --autoplay "Mon message personnalisé"
        """,
    )

    parser.add_argument("text", nargs="*", help="Text to speak")
    parser.add_argument("-e", "--emergency", action="store_true", help="Urgent tone")
    parser.add_argument("-x", "--sexy", action="store_true", help="Sexy/sultry tone")
    parser.add_argument(
        "-s", "--serious", action="store_true", help="Serious/professional tone"
    )
    parser.add_argument("-j", "--joyful", action="store_true", help="Happy/joyful tone")
    parser.add_argument("-a", "--angry", action="store_true", help="Angry/intense tone")
    parser.add_argument("-d", "--sad", action="store_true", help="Sad/melancholic tone")
    parser.add_argument("-t", "--tired", action="store_true", help="Tired/drowsy tone")
    parser.add_argument("-y", "--sassy", action="store_true", help="Sassy/playful tone")
    parser.add_argument(
        "-b", "--boss", action="store_true", help="Boss/authoritative tone"
    )
    parser.add_argument(
        "-w", "--whisper", action="store_true", help="Whisper/soft tone"
    )
    parser.add_argument(
        "--tone", choices=list(TONES.keys()), default="default", help="Tone preset"
    )
    parser.add_argument(
        "--play", action="store_true", default=False, help="Play audio after generation"
    )
    parser.add_argument(
        "--autoplay",
        action="store_true",
        default=False,
        help="Autoplay audio after generation",
    )
    parser.add_argument(
        "--no-play",
        dest="play",
        action="store_false",
        help="Don't play, only save (default)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Custom name for output file (without extension)",
    )
    parser.add_argument("--debug", action="store_true", help="Show TTS output")

    args = parser.parse_args()

    if args.text:
        text = " ".join(args.text)
    else:
        print("Error: No text provided")
        print('Usage: speak "Your text here"')
        sys.exit(1)

    tone_keys = [
        "emergency",
        "sexy",
        "serious",
        "joyful",
        "angry",
        "sad",
        "tired",
        "sassy",
        "boss",
        "whisper",
    ]
    tone = "default"
    for key in tone_keys:
        if getattr(args, key.replace("-", "_")):
            tone = key
            break

    settings = TONES[tone]
    voice = settings["voice"]
    speed = settings["speed"]

    if args.name:
        output_name = args.name
    else:
        output_name = "elia_output"

    output_dir = Path(__file__).parent
    final_output = output_dir / f"{output_name}.wav"

    chunks = split_text_into_chunks(text)

    if len(chunks) == 1:
        # Single chunk - generate directly
        chunk_dir = output_dir / "temp_output"
        if chunk_dir.exists():
            import shutil

            shutil.rmtree(chunk_dir, ignore_errors=True)
        chunk_dir.mkdir(exist_ok=True)

        cmd = [
            str(VENV / "bin" / "python"),
            "-m",
            "mlx_audio.tts.generate",
            "--model",
            MODEL,
            "--voice",
            voice,
            "--lang_code",
            "f",
            "--text",
            text,
            "--speed",
            str(speed),
            "--output",
            str(chunk_dir),
        ]

        if args.debug:
            cmd.append("--verbose")

        env = {"PATH": f"{VENV}/bin:{subprocess.getoutput('echo $PATH')}"}
        subprocess.run(cmd, env=env)

        wav_file = find_wav_file(str(chunk_dir))
        if wav_file and os.path.exists(wav_file):
            import shutil

            if final_output.exists():
                final_output.unlink()
            shutil.move(wav_file, str(final_output))
            shutil.rmtree(chunk_dir, ignore_errors=True)
            print(f"✅ Audio saved as: {final_output}")
        else:
            print(f"❌ Error: Could not find generated audio file")
            sys.exit(1)
    else:
        # Multiple chunks
        temp_wavs = []

        for i, chunk in enumerate(chunks):
            chunk_dir = output_dir / f"chunk_{i}"
            if chunk_dir.exists():
                import shutil

                shutil.rmtree(chunk_dir, ignore_errors=True)
            chunk_dir.mkdir(exist_ok=True)

            cmd = [
                str(VENV / "bin" / "python"),
                "-m",
                "mlx_audio.tts.generate",
                "--model",
                MODEL,
                "--voice",
                voice,
                "--lang_code",
                "f",
                "--text",
                chunk,
                "--speed",
                str(speed),
                "--output",
                str(chunk_dir),
            ]

            if args.debug:
                cmd.append("--verbose")

            env = {"PATH": f"{VENV}/bin:{subprocess.getoutput('echo $PATH')}"}
            subprocess.run(cmd, env=env)

            wav_file = find_wav_file(str(chunk_dir))
            if wav_file:
                temp_wavs.append(wav_file)
            else:
                print(f"⚠️ Warning: Could not find audio for chunk {i}")

        if not temp_wavs:
            print(f"❌ Error: No audio files generated")
            sys.exit(1)

        # Concatenate
        concat_list = output_dir / "concat_list.txt"
        with open(concat_list, "w") as f:
            for tw in temp_wavs:
                f.write(f"file '{tw}'\n")

        concat_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(final_output),
        ]
        subprocess.run(concat_cmd)

        # Cleanup
        import shutil

        for i in range(len(chunks)):
            chunk_dir = output_dir / f"chunk_{i}"
            if chunk_dir.exists():
                shutil.rmtree(chunk_dir, ignore_errors=True)
        concat_list.unlink()
        print(f"✅ Audio saved as: {final_output}")

    if args.play or args.autoplay:
        print(f"🔊 Playing audio...")
        subprocess.Popen(
            ["open", str(final_output)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"▶️ Opened with default player!")


if __name__ == "__main__":
    main()
