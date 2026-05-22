"""Windows loopback audio phase bridge for Shion's felt body shader.

Serves a small JSON endpoint consumed by outputs/shader_depth_sample.html.
The bridge listens to the default WASAPI loopback device and converts desktop
audio into a soft phase/envelope/onset signal.
"""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import numpy as np
import pyaudiowpatch as pyaudio


class AudioPhaseState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.state: dict[str, Any] = {
            "enabled": False,
            "source": "wasapi_loopback",
            "device": None,
            "sample_rate": 0,
            "phase": 0.0,
            "envelope": 0.0,
            "onset": 0.0,
            "confidence": 0.0,
            "bass": 0.0,
            "brightness": 0.0,
            "timestamp": time.time(),
            "error": None,
        }

    def update(self, **values: Any) -> None:
        with self.lock:
            self.state.update(values)
            self.state["timestamp"] = time.time()

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return dict(self.state)


def wrap_phase(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def find_loopback_device(pa: pyaudio.PyAudio) -> dict[str, Any]:
    try:
        return pa.get_default_wasapi_loopback()
    except Exception:
        pass

    for index in range(pa.get_device_count()):
        device = pa.get_device_info_by_index(index)
        if device.get("isLoopbackDevice"):
            return device
    raise RuntimeError("WASAPI loopback device not found")


def capture_loopback_audio(state: AudioPhaseState, stop_event: threading.Event) -> None:
    pa = pyaudio.PyAudio()
    stream = None
    phase = 0.0
    envelope = 0.0
    onset = 0.0
    confidence = 0.0
    last_envelope = 0.0
    last_time = time.time()

    try:
        device = find_loopback_device(pa)
        sample_rate = int(device["defaultSampleRate"])
        channels = int(device["maxInputChannels"] or 2)
        chunk = 1024
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=int(device["index"]),
            frames_per_buffer=chunk,
        )
        state.update(
            enabled=True,
            device=device["name"],
            sample_rate=sample_rate,
            error=None,
        )

        while not stop_event.is_set():
            raw = stream.read(chunk, exception_on_overflow=False)
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
            if channels > 1 and samples.size >= channels:
                samples = samples.reshape(-1, channels).mean(axis=1)
            samples /= 32768.0

            rms = float(np.sqrt(np.mean(samples * samples))) if samples.size else 0.0
            next_envelope = max(0.0, min(1.0, (rms - 0.0035) * 10.0))
            rise = max(0.0, next_envelope - last_envelope)
            now = time.time()
            dt = max(1.0 / 120.0, now - last_time)

            envelope += (next_envelope - envelope) * 0.24
            onset = max(onset * 0.84, min(1.0, rise * 8.0))
            confidence += (max(envelope, onset) - confidence) * 0.10
            phase_speed = 0.34 + envelope * 3.0 + onset * 4.8
            phase = wrap_phase(phase + dt * phase_speed)

            spectrum = np.abs(np.fft.rfft(samples)) if samples.size else np.array([0.0])
            freqs = np.fft.rfftfreq(samples.size, 1.0 / sample_rate) if samples.size else np.array([0.0])
            total = float(np.sum(spectrum) + 1e-9)
            bass = float(np.sum(spectrum[freqs < 180]) / total) if freqs.size else 0.0
            centroid = float(np.sum(freqs * spectrum) / total) if freqs.size else 0.0
            brightness = max(0.0, min(1.0, centroid / 5000.0))

            state.update(
                enabled=True,
                source="wasapi_loopback",
                phase=phase,
                envelope=envelope,
                onset=onset,
                confidence=confidence,
                bass=bass,
                brightness=brightness,
                error=None,
            )
            last_envelope = next_envelope
            last_time = now
    except Exception as exc:
        state.update(enabled=False, error=str(exc))
    finally:
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        pa.terminate()


def audio_worker(state: AudioPhaseState, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        capture_loopback_audio(state, stop_event)
        if not stop_event.is_set():
            time.sleep(1.5)


def make_handler(state: AudioPhaseState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path.startswith("/audio_phase.json"):
                self._send_json(state.snapshot())
                return
            if self.path.startswith("/health"):
                snapshot = state.snapshot()
                self._send_json({"ok": snapshot.get("enabled", False), "state": snapshot})
                return
            self._send_json({"error": "not found"}, status=404)

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=57322)
    args = parser.parse_args()

    state = AudioPhaseState()
    stop_event = threading.Event()
    worker = threading.Thread(target=audio_worker, args=(state, stop_event), daemon=True)
    worker.start()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    print(f"Shion audio loopback phase bridge: http://{args.host}:{args.port}/audio_phase.json")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.server_close()


if __name__ == "__main__":
    main()
