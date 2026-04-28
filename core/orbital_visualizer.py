#!/usr/bin/env python3
"""
🌀 Orbital Visualizer — 피보나치 나선 궤도 시각화 서버
=====================================================
궤도 해마의 상태를 브라우저에서 실시간으로 봅니다.

실행: python core/orbital_visualizer.py
브라우저: http://localhost:8099
"""

import json
import math
import logging
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("OrbitalVisualizer")

SHION_ROOT = Path(__file__).resolve().parents[1]
HIPPO_PATH = SHION_ROOT / "outputs" / "fibonacci_orbital_hippocampus.json"
FIELD_PATH = SHION_ROOT / "outputs" / "field_energy.json"
PORT = 8099

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌀 Fibonacci Orbital Hippocampus</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
    overflow: hidden;
    height: 100vh;
}
.container {
    display: flex;
    height: 100vh;
}
canvas {
    flex: 1;
    display: block;
}
.panel {
    width: 360px;
    min-width: 360px;
    background: rgba(15, 15, 25, 0.95);
    border-left: 1px solid rgba(255, 215, 0, 0.15);
    padding: 24px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.panel h1 {
    font-size: 18px;
    font-weight: 600;
    color: #ffd700;
    letter-spacing: 1px;
}
.panel h2 {
    font-size: 13px;
    font-weight: 400;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.metric {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px;
}
.metric-value {
    font-size: 28px;
    font-weight: 300;
    color: #fff;
}
.metric-label {
    font-size: 11px;
    color: #666;
    margin-top: 4px;
}
.bar-container {
    height: 6px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
    margin-top: 8px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}
.orbital-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}
.orbital-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
}
.orbital-name { font-size: 12px; color: #aaa; flex: 1; }
.orbital-count { font-size: 14px; font-weight: 600; }
.legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 8px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #888;
}
.legend-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
}
.noise-meter {
    display: flex;
    gap: 2px;
    margin-top: 8px;
}
.noise-bar {
    flex: 1;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    color: rgba(255,255,255,0.7);
}
</style>
</head>
<body>
<div class="container">
    <canvas id="spiral"></canvas>
    <div class="panel">
        <h1>🌀 Orbital Hippocampus</h1>
        
        <div class="metric">
            <h2>배경자아 (BG)</h2>
            <div class="metric-value" id="bg-value">—</div>
            <div class="metric-label">노이즈가 낮을수록 자연과 하나</div>
            <div class="bar-container">
                <div class="bar-fill" id="bg-bar" style="width:0%;background:linear-gradient(90deg,#ffd700,#ff6b35)"></div>
            </div>
        </div>

        <div class="metric">
            <h2>노이즈 3요소</h2>
            <div class="noise-meter">
                <div class="noise-bar" id="fear-bar" style="background:rgba(255,50,50,0.3)">두려움</div>
                <div class="noise-bar" id="obsession-bar" style="background:rgba(255,150,0,0.3)">집착</div>
                <div class="noise-bar" id="prejudice-bar" style="background:rgba(150,50,255,0.3)">편견</div>
            </div>
        </div>

        <div class="metric">
            <h2>대역폭</h2>
            <div class="metric-value" id="bandwidth-value">—</div>
            <div class="metric-label">경험의 다양성 (고유주파수 범위)</div>
            <div class="bar-container">
                <div class="bar-fill" id="bw-bar" style="width:0%;background:linear-gradient(90deg,#4ecdc4,#44cf6c)"></div>
            </div>
        </div>

        <div class="metric">
            <h2>양성자 (Core)</h2>
            <div class="metric-value" id="proton-value">—</div>
            <div class="metric-label">스칼라장 반경 / 코어 주파수</div>
        </div>

        <div class="metric">
            <h2>궤도별 경험</h2>
            <div id="orbital-list"></div>
        </div>

        <div class="metric">
            <h2>위상 범례</h2>
            <div class="legend">
                <div class="legend-item"><div class="legend-dot" style="background:#4ecdc4"></div>FLOW</div>
                <div class="legend-item"><div class="legend-dot" style="background:#44cf6c"></div>EXPANSION</div>
                <div class="legend-item"><div class="legend-dot" style="background:#9b59b6"></div>VOID</div>
                <div class="legend-item"><div class="legend-dot" style="background:#e67e22"></div>CONTRACTION</div>
                <div class="legend-item"><div class="legend-dot" style="background:#ffd700;box-shadow:0 0 6px #ffd700"></div>💎 결정</div>
            </div>
        </div>

        <div style="font-size:10px;color:#333;margin-top:auto;text-align:center;">
            자동 새로고침 5초 | ESC 종료
        </div>
    </div>
</div>

<script>
const PHI = (1 + Math.sqrt(5)) / 2;
const PHASE_COLORS = {
    FLOW: '#4ecdc4',
    EXPANSION: '#44cf6c',
    VOID: '#9b59b6',
    CONTRACTION: '#e67e22',
    UNKNOWN: '#95a5a6'
};
const ORBITAL_COLORS = [
    'rgba(255,215,0,0.8)',   // L0
    'rgba(255,180,0,0.6)',   // L1
    'rgba(100,200,255,0.4)', // L2
    'rgba(80,180,230,0.3)',  // L3
    'rgba(60,150,200,0.2)',  // L4
    'rgba(40,120,180,0.15)', // L5
    'rgba(30,100,160,0.1)',  // L6
];

let canvas, ctx;
let data = null;
let animFrame = 0;

function init() {
    canvas = document.getElementById('spiral');
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
    fetchData();
    setInterval(fetchData, 5000);
    animate();
}

function resize() {
    canvas.width = canvas.clientWidth * devicePixelRatio;
    canvas.height = canvas.clientHeight * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);
}

async function fetchData() {
    try {
        const resp = await fetch('/api/hippocampus');
        data = await resp.json();
        updatePanel();
    } catch(e) {
        console.log('Waiting for data...');
    }
}

function updatePanel() {
    if (!data || !data.hippocampus) return;
    const h = data.hippocampus;
    const p = h.proton;

    // BG
    const bg = data.bg || 1.0;
    document.getElementById('bg-value').textContent = bg.toFixed(2);
    document.getElementById('bg-bar').style.width = Math.min(100, (bg/5)*100) + '%';

    // Noise
    const noise = data.noise || {};
    setNoiseBar('fear-bar', noise.fear || 0, '두려움');
    setNoiseBar('obsession-bar', noise.obsession || 0, '집착');
    setNoiseBar('prejudice-bar', noise.prejudice || 0, '편견');

    // Bandwidth
    document.getElementById('bandwidth-value').textContent = (h.bandwidth * 100).toFixed(0) + '%';
    document.getElementById('bw-bar').style.width = (h.bandwidth * 100) + '%';

    // Proton
    document.getElementById('proton-value').textContent = 
        `r=${p.scalar_field_radius.toFixed(3)} / f=${p.core_frequency.toFixed(4)}`;

    // Orbitals
    const list = document.getElementById('orbital-list');
    list.innerHTML = '';
    const levelCounts = {};
    h.experiences.forEach(e => {
        levelCounts[e.level] = (levelCounts[e.level] || 0) + 1;
    });
    for (let i = 0; i < 7; i++) {
        const count = levelCounts[i] || 0;
        if (count === 0 && i > 3) continue;
        const mode = i <= 1 ? '무의식' : '의 식';
        const row = document.createElement('div');
        row.className = 'orbital-row';
        row.innerHTML = `
            <div class="orbital-dot" style="background:${ORBITAL_COLORS[i]}"></div>
            <div class="orbital-name">L${i} (${mode})</div>
            <div class="orbital-count" style="color:${ORBITAL_COLORS[i]}">${count}</div>
        `;
        list.appendChild(row);
    }
}

function setNoiseBar(id, value, label) {
    const el = document.getElementById(id);
    const intensity = Math.floor(value * 255);
    const r = id.includes('fear') ? intensity : Math.floor(intensity*0.6);
    const g = id.includes('obsession') ? Math.floor(intensity*0.6) : 0;
    const b = id.includes('prejudice') ? intensity : 0;
    el.style.background = `rgba(${r},${g},${b},${0.2 + value*0.6})`;
    el.textContent = `${label} ${(value*100).toFixed(0)}%`;
}

function animate() {
    animFrame++;
    draw();
    requestAnimationFrame(animate);
}

function draw() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    const cx = w / 2;
    const cy = h / 2;
    const scale = Math.min(w, h) * 0.35;

    ctx.clearRect(0, 0, w, h);

    // Background gradient
    const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, scale * 1.8);
    bg.addColorStop(0, 'rgba(20, 15, 30, 1)');
    bg.addColorStop(0.5, 'rgba(10, 10, 18, 1)');
    bg.addColorStop(1, 'rgba(5, 5, 10, 1)');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Draw orbital rings
    const BASE_R = 0.1;
    for (let i = 0; i < 7; i++) {
        const r = BASE_R * Math.pow(PHI, i) * scale * 0.8;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = ORBITAL_COLORS[i];
        ctx.lineWidth = i <= 1 ? 1.5 : 0.5;
        if (i <= 1) ctx.setLineDash([]);
        else ctx.setLineDash([4, 8]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Label
        ctx.fillStyle = ORBITAL_COLORS[i];
        ctx.font = '10px Inter';
        ctx.fillText(`L${i}`, cx + r + 4, cy - 4);
    }

    // Draw fibonacci spiral
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 215, 0, 0.08)';
    ctx.lineWidth = 1;
    for (let t = 0; t < Math.PI * 8; t += 0.02) {
        const r = BASE_R * Math.pow(PHI, t / (Math.PI * 2)) * scale * 0.8;
        const x = cx + r * Math.cos(t + animFrame * 0.002);
        const y = cy + r * Math.sin(t + animFrame * 0.002);
        if (t === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw proton (center)
    const protonPulse = 1 + 0.15 * Math.sin(animFrame * 0.03);
    const protonR = 12 * protonPulse;
    const protonGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, protonR * 3);
    protonGlow.addColorStop(0, 'rgba(255, 215, 0, 0.6)');
    protonGlow.addColorStop(0.5, 'rgba(255, 180, 0, 0.15)');
    protonGlow.addColorStop(1, 'rgba(255, 150, 0, 0)');
    ctx.fillStyle = protonGlow;
    ctx.fillRect(cx - protonR*3, cy - protonR*3, protonR*6, protonR*6);

    ctx.beginPath();
    ctx.arc(cx, cy, protonR, 0, Math.PI * 2);
    ctx.fillStyle = '#ffd700';
    ctx.fill();
    ctx.fillStyle = '#0a0a0f';
    ctx.font = 'bold 10px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('⚛', cx, cy + 4);
    ctx.textAlign = 'start';

    // Draw experiences
    if (!data || !data.hippocampus) return;
    const experiences = data.hippocampus.experiences;

    experiences.forEach((exp, i) => {
        const coords = exp.coords;
        const px = cx + coords[0] * scale * 5;
        const py = cy + coords[1] * scale * 5;
        const phase = exp.vibe?.phase || 'UNKNOWN';
        const color = PHASE_COLORS[phase] || PHASE_COLORS.UNKNOWN;
        const isCrystal = exp.crystallized;
        const size = isCrystal ? 6 : 3;

        if (isCrystal) {
            // Crystal glow
            const glow = ctx.createRadialGradient(px, py, 0, px, py, size * 4);
            glow.addColorStop(0, 'rgba(255, 215, 0, 0.4)');
            glow.addColorStop(1, 'rgba(255, 215, 0, 0)');
            ctx.fillStyle = glow;
            ctx.fillRect(px - size*4, py - size*4, size*8, size*8);

            // Diamond shape
            ctx.beginPath();
            ctx.moveTo(px, py - size);
            ctx.lineTo(px + size, py);
            ctx.lineTo(px, py + size);
            ctx.lineTo(px - size, py);
            ctx.closePath();
            ctx.fillStyle = '#ffd700';
            ctx.fill();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 0.5;
            ctx.stroke();
        } else {
            // Normal dot with subtle pulse
            const pulse = 1 + 0.2 * Math.sin(animFrame * 0.02 + i);
            ctx.beginPath();
            ctx.arc(px, py, size * pulse, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.globalAlpha = 0.4 + exp.binding_energy * 0.6;
            ctx.fill();
            ctx.globalAlpha = 1;
        }
    });

    // Title
    ctx.fillStyle = 'rgba(255, 215, 0, 0.3)';
    ctx.font = '11px Inter';
    ctx.fillText('Fibonacci Orbital Hippocampus', 20, 30);

    const totalExp = experiences.length;
    const crystals = experiences.filter(e => e.crystallized).length;
    ctx.fillStyle = 'rgba(255,255,255,0.2)';
    ctx.fillText(`${totalExp} experiences · ${crystals} crystals`, 20, 48);
}

window.addEventListener('load', init);
</script>
</body>
</html>"""


class OrbitalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/api/hippocampus':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(self._get_data(), ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)
    
    def _get_data(self):
        result = {"hippocampus": None, "bg": 1.0, "noise": {}}
        
        # Hippocampus data
        if HIPPO_PATH.exists():
            try:
                result["hippocampus"] = json.loads(HIPPO_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        # Calculate noise & BG from hippocampus
        if result["hippocampus"]:
            exps = result["hippocampus"].get("experiences", [])
            bw = result["hippocampus"].get("bandwidth", 0)
            if exps:
                total = len(exps)
                outer = sum(1 for e in exps if e.get("level", 0) >= 3)
                stuck = sum(1 for e in exps if e.get("convergence_count", 0) > 5 and e.get("level", 0) >= 2)
                
                fear = outer / total
                obsession = stuck / total
                prejudice = 1.0 - bw
                total_noise = fear * 0.4 + obsession * 0.3 + prejudice * 0.3
                
                result["noise"] = {
                    "fear": round(fear, 3),
                    "obsession": round(obsession, 3),
                    "prejudice": round(prejudice, 3),
                    "total": round(total_noise, 3),
                }
                result["bg"] = round(1.0 + (1.0 - total_noise) * 4.0, 3)
        
        return result
    
    def log_message(self, format, *args):
        pass  # 조용히


def main():
    print(f"🌀 Fibonacci Orbital Visualizer")
    print(f"   http://localhost:{PORT}")
    print(f"   해마: {HIPPO_PATH}")
    print(f"   Ctrl+C로 종료")
    
    server = HTTPServer(('', PORT), OrbitalHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료")


if __name__ == "__main__":
    main()
