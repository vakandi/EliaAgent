#!/bin/bash
set -e

VENV="$HOME/.venvs/tts"
MODEL="mlx-community/Kokoro-82M-bf16"

TEXT=""
TONE="default"
PLAY=true
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--emergency)
            TONE="emergency"
            shift
            ;;
        -x|--sexy)
            TONE="sexy"
            shift
            ;;
        -s|--serious)
            TONE="serious"
            shift
            ;;
        -h|--happy)
            TONE="happy"
            shift
            ;;
        -a|--angry)
            TONE="angry"
            shift
            ;;
        -d|--sad)
            TONE="sad"
            shift
            ;;
        -t|--tired)
            TONE="tired"
            shift
            ;;
        -y|--sassy)
            TONE="sassy"
            shift
            ;;
        -b|--boss)
            TONE="boss"
            shift
            ;;
        -w|--whisper)
            TONE="whisper"
            shift
            ;;
        --tone=*)
            TONE="${1#*=}"
            shift
            ;;
        --play)
            PLAY=true
            shift
            ;;
        --no-play)
            PLAY=false
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            TEXT="$*"
            break
            ;;
    esac
done

if [[ -z "$TEXT" ]]; then
    echo "Elia's Voice - Multi-tone TTS"
    echo ""
    echo "Usage: speak [OPTIONS] \"Your text here\""
    echo ""
    echo "Tones:"
    echo "  -e, --emergency  - Urgent, fast, higher pitch"
    echo "  -x, --sexy      - Slow, smooth, lower pitch (sultry)"
    echo "  -s, --serious   - Steady, neutral, professional"
    echo "  -h, --happy     - Fast, bright, enthusiastic"
    echo "  -a, --angry     - Fast, harsh, intense"
    echo "  -d, --sad       - Slow, low, melancholic"
    echo "  -t, --tired     - Slow, drowsy, lower pitch"
    echo "  -y, --sassy     - Medium speed, confident, playful"
    echo "  -b, --boss      - Authoritative, commanding"
    echo "  -w, --whisper   - Soft, quiet, intimate"
    echo ""
    echo "Options:"
    echo "  --play     - Play audio (default)"
    echo "  --no-play  - Don't play, only save"
    echo "  --debug    - Show TTS output"
    exit 1
fi

case $TONE in
    emergency)
        VOICE="ff_siwis"
        SPEED=1.5
        ;;
    sexy)
        VOICE="ff_siwis,am_adam:0.85"
        SPEED=0.8
        ;;
    serious)
        VOICE="ff_siwis"
        SPEED=0.95
        ;;
    happy)
        VOICE="ff_siwis"
        SPEED=1.3
        ;;
    angry)
        VOICE="ff_siwis"
        SPEED=1.4
        ;;
    sad)
        VOICE="ff_siwis,am_adam:0.9"
        SPEED=0.7
        ;;
    tired)
        VOICE="ff_siwis,am_adam:0.8"
        SPEED=0.65
        ;;
    sassy)
        VOICE="ff_siwis"
        SPEED=1.1
        ;;
    boss)
        VOICE="ff_siwis"
        SPEED=0.9
        ;;
    whisper)
        VOICE="ff_siwis,am_adam:0.9"
        SPEED=0.75
        ;;
    *)
        VOICE="ff_siwis"
        SPEED=1.0
        ;;
esac

source "$VENV/bin/activate"

CMD="python -m mlx_audio.tts.generate --model $MODEL --voice $VOICE --lang_code f --text \"$TEXT\" --speed $SPEED"

if $PLAY; then
    CMD="$CMD --play"
fi

if $DEBUG; then
    CMD="$CMD --verbose"
fi

eval $CMD
