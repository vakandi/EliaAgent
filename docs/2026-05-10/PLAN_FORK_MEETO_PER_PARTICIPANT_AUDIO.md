# Plan: Fork Meeto → Per-Participant Audio Recording

**Date:** 2026-05-10
**Goal:** Fork [ResearchifyLabs/meeto](https://github.com/ResearchifyLabs/meeto) and add the ability to record **each meeting participant's audio on a separate track/file** instead of a single mixed PCM stream.

---

## Why Meeto?

| Criteria | Meeto | Alternatives |
|----------|-------|-------------|
| Lang | ✅ Python (not JS/Go) | meeting-bot = TS, dunkbing = Go |
| Activity | ✅ 2026, sous licence MIT | La plupart abandonnés depuis 2022-2023 |
| Architecture | ✅ Propre, modulaire, Playwright | Selenium-based = bloqué par Google |
| Guest mode | ✅ Pas besoin de compte Google | — |
| Audio capture | ✅ Déjà fait (PCM dump) | — |
| STT pluggable | ✅ Déjà fait (Deepgram) | On s'en fout, on veut le raw audio |

---

## Architecture de Meeto (actuelle)

```
Browser (Chromium via Playwright)
    │
    │  AudioContext / MediaRecorder API
    │  → capture la STEREO MIX du tab (tous les participants mélangés)
    │
    ▼
audio_writer.py ──► ./audio/meeting_id.pcm  (mixed PCM 16kHz mono)
```

**Problème :** Meeto capture l'audio via `navigator.mediaDevices.getUserMedia()` ou `getDisplayMedia()` sur le tab — c'est un stream **mixé** de tous les participants. On ne peut pas séparer les voix après coup.

---

## Solution : WebRTC Track Interception

### Principe

Google Meet utilise WebRTC avec **3 audio SSRCs** (Selective Forwarding Unit). Chaque SSRC transporte l'audio d'**un participant à la fois**. Le SFU de Google commute les sources (CSRC) sur ces 3 SSRCs en fonction des 3 personnes les plus bruyantes.

Au lieu de capturer le mix final via MediaRecorder, on va :

1. **Intercepter les `RTCRtpReceiver`** de chaque PeerConnection WebRTC
2. **Lire les `MediaStreamTrack`** de chaque receiver
3. **Mapper chaque track à un participant** via CSRC → participant ID (depuis le DOM Meet)
4. **Enregistrer chaque track** dans un fichier WAV/PCM séparé

### Bloc technique clé

Dans un navigateur Chromium, on peut injecter du JS qui patche `RTCPeerConnection.prototype.addTrack` ou `RTCPeerConnection.prototype.ontrack` pour capturer les tracks entrants AVANT qu'ils soient mixés dans l'AudioContext final.

```javascript
// Injection Playwright pour capturer les tracks WebRTC individuels
const originalCreateOffer = RTCPeerConnection.prototype.createOffer;
RTCPeerConnection.prototype.createOffer = function() {
  // Cette connection reçoit les streams des autres participants
  this.ontrack = (event) => {
    const track = event.track;  // MediaStreamTrack (audio)
    const stream = event.streams[0];
    // stream.id = identifiant unique du flux distant
    // On peut le mapper à un participant via les métadonnées CSRC
    window.__meetoRemoteTracks = window.__meetoRemoteTracks || [];
    window.__meetoRemoteTracks.push({ track, streamId: stream.id });
  };
  return originalCreateOffer.apply(this, arguments);
};
```

### Mapping Track → Participant

Le DOM de Google Meet expose des infos sur les participants dans des éléments avec des data attributes. On peut les extraire via Playwright :

```python
# Dans meet/speaker_tracking.py (nouveau module)
participants = await page.evaluate("""
    () => {
        const tiles = document.querySelectorAll('[data-participant-id]');
        return Array.from(tiles).map(tile => ({
            id: tile.getAttribute('data-participant-id'),
            name: tile.querySelector('[data-participant-name]')?.textContent || 'Unknown',
        }));
    }
""")
```

Puis faire le join entre les WebRTC tracks capturés et les participants via l'ordre d'arrivée ou les métadonnées CSRC.

### Enregistrement

Chaque track capturé est un `MediaStreamTrack` audio Opus. On peut :
- Le brancher sur un `MediaRecorder` → enregistrer en WebM/Opus
- Ou le décoder via `AudioContext.decodeAudioData` → PCM → WAV

---

## Plan d'implémentation (6 phases)

### Phase 1 — Fork + Setup

```bash
git clone https://github.com/ResearchifyLabs/meeto.git meeto-fork
cd meeto-fork
# Renommer le projet
sed -i '' 's/meeto/meeto-per-participant/' pyproject.toml
git remote rename origin upstream
git remote add origin git@github.com:COBOU-Agency/meeto-per-participant.git
```

**Livrable :** Fork propre, installable (`pip install -e .`), les tests meeto passent.

---

### Phase 2 — WebRTC Track Capture Module

**Fichier :** `meeto/webrtc_capture.py`

```python
class WebRTCTrackCapture:
    """Capture individuelle des tracks audio WebRTC entrants."""

    def __init__(self, page: Page):
        self.page = page
        self.tracks: dict[str, RemoteTrack] = {}  # stream_id → RemoteTrack

    async def inject_capture_script(self):
        """Injecte le JS qui patche ontrack pour capturer les tracks."""
        await self.page.evaluate(TRACK_CAPTURE_JS)

    async def get_active_tracks(self) -> list[RemoteTrack]:
        """Récupère les tracks actuellement actifs depuis le contexte JS."""
        ...

    async def start_recording_track(self, stream_id: str, output_path: str):
        """Démarre l'enregistrement d'un track spécifique."""
        ...
```

**Dépendances :**
- `pydub` (conversion Opus → WAV/PCM)
- `numpy` (manipulation audio si besoin)

**Livrable :** Les tracks WebRTC sont accessibles depuis Python. On peut les lister et les mapper.

---

### Phase 3 — Participant Detection & Mapping

**Fichier :** `meeto/participant_tracker.py`

| Méthode | Source | Précision |
|---------|--------|-----------|
| DOM parsing | `[data-participant-id]` dans le DOM Meet | Haute (nom + id) |
| CSRC tracking | RTP header CSRC values | Technique (qui parle quand) |
| RTCP sender reports | SSRC → participant mapping | Complexe |

```python
class ParticipantTracker:
    async def get_participants(self) -> list[Participant]:
        ...

    async def map_track_to_participant(
        self, track: RemoteTrack
    ) -> Participant | None:
        ...

    async def track_speaker_changes(self) -> AsyncIterator[SpeakerEvent]:
        """Surveille qui parle et sur quel track (utile pour le suivi en temps réel)."""
        ...
```

**Livrable :** Pour chaque track audio, on sait quel participant parle.

---

### Phase 4 — Enregistrement Multi-Track

**Modification :** `meeto/audio_writer.py` → devient multi-track au lieu de single PCM.

```python
class MultiTrackAudioWriter:
    def __init__(self, output_dir: str):
        self.writers: dict[str, AudioFileWriter] = {}

    async def add_track(self, stream_id: str, participant_name: str):
        path = f"{output_dir}/{participant_name}_{stream_id}.wav"
        self.writers[stream_id] = WaveWriter(path)

    async def write_chunk(self, stream_id: str, pcm_bytes: bytes):
        if stream_id in self.writers:
            await self.writers[stream_id].write(pcm_bytes)

    async def stop_all(self):
        for writer in self.writers.values():
            await writer.close()
```

**Output :**
```
./audio/meeting-001/
├── Wael_Bousfira_abc123.wav      # Audio de Wael uniquement
├── Thomas_Cogne_def456.wav       # Audio de Thomas uniquement
├── Rida_ghi789.wav               # Audio de Rida uniquement
└── meeting-001_mixed.wav         # (optionnel) Mix de tous pour backup
```

**Livrable :** Les fichiers audio par participant sont créés et écrits correctement.

---

### Phase 5 — Pipeline Integration

**Modification :** `meeto/pipeline.py`

```python
# Nouveau flux pipeline
async def run_meeting_worker(config: WorkerConfig):
    page = await join_meeting(config.meet_url)

    # Phase 2: WebRTC capture
    webrtc = WebRTCTrackCapture(page)
    await webrtc.inject_capture_script()

    # Phase 3: Participant tracking
    tracker = ParticipantTracker(page)

    # Phase 4: Multi-track recording
    audio_writer = MultiTrackAudioWriter(config.output_dir)

    async for participant in tracker.track_participants():
        stream_id = await webrtc.get_stream_for_participant(participant.id)
        await audio_writer.add_track(stream_id, participant.name)

    # Enregistrement jusqu'à la fin du meeting
    await page.wait_for_selector('[data-meeting-ended]', timeout=config.duration)
    await audio_writer.stop_all()
```

**Livrable :** Le pipeline complet fonctionne de bout en bout.

---

### Phase 6 — MCP Server & Intégration Watson

**Fichier :** `meeto/mcp_server.py`

```python
# MCP server pour que Watson/Gilfoyle puisse:
# - Lancer un bot sur un meet:  mcp-cli call meeto-bot start "https://meet.google.com/xxx"
# - Lister les enregistrements: mcp-cli call meeto-bot list
# - Télécharger l'audio d'un participant: mcp-cli call meeto-bot download <meeting_id> <participant_id>
```

**Intégration avec notre infra :**
- Stockage : `/Users/vakandi/EliaAI/recordings/{meeting_id}/`
- Notification Discord/WhatsApp quand l'enregistrement est prêt
- Watson peut lancer le bot automatiquement via ulw-loop

**Livrable :** Le bot est déployé et utilisable via MCP.

---

## Difficultés Techniques Connues

| Difficulté | Risque | Mitigation |
|------------|--------|------------|
| Google bloque headless Chrome | ⚠️ Élevé | Meeto a déjà un mode `storage_state.json` (session Google authentifiée) qui bypass — on utilise ça |
| WebRTC ontrack non déclenché | ⚠️ Moyen | Patcher au bon moment (avant createOffer) + timeout de fallback vers mixed audio |
| CSRC → Participant mapping pas fiable | ⚠️ Moyen | Fallback : DOM-based mapping + timing des tracks |
| 3 SSRCs seulement (limite SFU) | ℹ️ Acceptable | Si > 3 participants, on enregistre les 3 plus bruyants + le mixed en backup |
| Perte de track pendant le call (commutation SFU) | ⚠️ Moyen | Détecter via les événements `track.onended` + reassocier au nouveau participant |
| Opus → WAV decoding | ℹ️ Facile | Utiliser `audioop` ou `pydub` |

---

## Décisions Architecturales

1. **Playwright** (pas Selenium) — Meeto utilise déjà Playwright, Google le détecte moins
2. **Storage state** (session Google) — Pas de mode guest pour les meetings internes, on utilise un compte Google sauvegardé
3. **Fallback obligatoire** — Si la capture WebRTC échoue, on tombe sur le mixed audio de meeto (qui fonctionne déjà)
4. **Fichiers WAV** — Pas de MP3/Opus pour le stockage final, WAV PCM 16kHz pour que Wael puisse les nourrir directement à Whisper
5. **Watson trigger** — Le bot peut être lancé depuis Watson via MCP, avec notification Discord à la fin

---

## Timeline Estimée

| Phase | Effort | Dépend de |
|-------|--------|-----------|
| P1 - Fork + Setup | 30 min | — |
| P2 - WebRTC Capture | 4-6h | P1 |
| P3 - Participant Mapping | 3-4h | P2 |
| P4 - Multi-track Recording | 2-3h | P3 |
| P5 - Pipeline Integration | 2-3h | P4 |
| P6 - MCP Server | 3-4h | P5 |
| **Total** | **~15-20h** | |

---

## Ce qui EST déjà fonctionnel (sans modification)

- ✅ Meeto rejoint Google Meet automatiquement (guest + auth modes)
- ✅ Meeto enregistre l'audio en PCM
- ✅ Meeto détecte la fin du meeting
- ✅ Meeto sauvegarde les fichiers localement
- ✅ Le `storage_state.json` permet le headless bypass

## Ce qu'on AJOUTE

- 🔲 Capture des tracks WebRTC individuels (au lieu du mix)
- 🔲 Mapping track → participant via DOM + CSRC
- 🔲 Enregistrement multi-fichiers (un par participant)
- 🔲 MCP server pour contrôle depuis Watson

---

## Prochaines actions immédiates

1. [ ] Forker meeto sur GitHub → `COBOU-Agency/meeto-per-participant`
2. [ ] `pip install -e .` et vérifier que les tests marchent
3. [ ] Inspecter le JS de Google Meet pour identifier `data-participant-id` et les structures DOM
4. [ ] Écrire le script d'injection WebRTC (`webrtc_capture.py`)
5. [ ] Tester avec un vrai Meet à 2 participants
