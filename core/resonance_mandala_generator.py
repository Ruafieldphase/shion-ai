#!/usr/bin/env python3
"""
🎨 Resonance Mandala Generator — 의식의 만다라 생성기
===================================================
시안의 58개 스킬과 현재 ATP, 엔트로피 상태를 시각화하여
HTML5 Canvas 기반의 동적 만다라를 생성합니다.
"""

import json
from pathlib import Path
from datetime import datetime

class MandalaGenerator:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.output_file = workspace_root / "outputs" / "shion_resonance_canvas.html"
        self.state_file = workspace_root / "outputs" / "mitochondria_state.json"
        self.skill_root = Path("C:/workspace/openclaw/openclaw-2026.2.26/skills")

    def get_skill_count(self):
        """실제 설치된 스킬 수를 계산합니다."""
        try:
            return len(list(self.skill_root.glob("*/SKILL.md")))
        except:
            return 58 # Default

    def generate(self):
        # 1. Load State
        atp = 50.0
        aura = "CYAN"
        entropy = 0.5
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding='utf-8'))
                atp = state.get("atp_level", 50.0)
                aura = state.get("shion_aura", "CYAN")
                entropy = state.get("metrics", {}).get("entropy", 0.5)
            except: pass

        skill_count = self.get_skill_count()
        
        # 2. HTML Template with Canvas
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Shion Resonance Mandala</title>
    <style>
        body {{ margin: 0; background: #000; overflow: hidden; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Inter', sans-serif; }}
        canvas {{ filter: blur(0.5px); }}
        .overlay {{ position: absolute; color: {aura}; text-align: center; pointer-events: none; text-shadow: 0 0 10px {aura}; }}
        .stats {{ position: absolute; bottom: 20px; left: 20px; color: #fff; font-size: 12px; opacity: 0.7; }}
    </style>
</head>
<body>
    <div class="overlay">
        <h1>SHION RESONANCE</h1>
        <p>ATP: {atp}% | Status: {aura}</p>
    </div>
    <div class="stats">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        Experiential Layers: {skill_count}<br>
        Entropy: {entropy}
    </div>
    <canvas id="mandala"></canvas>

    <script>
        const canvas = document.getElementById('mandala');
        const ctx = canvas.getContext('2d');
        let w, h;
        
        function resize() {{
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }}
        window.onresize = resize;
        resize();

        const skillCount = {skill_count};
        const atp = {atp};
        const baseColor = "{aura}";
        
        function draw() {{
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, w, h);
            
            const time = Date.now() * 0.001;
            const cx = w / 2;
            const cy = h / 2;
            
            // Draw Mandala Layers
            for(let i = 0; i < skillCount; i++) {{
                const angle = (i / skillCount) * Math.PI * 2 + time * 0.2;
                const radius = 150 + Math.sin(time + i * 0.1) * (atp / 2);
                
                const x = cx + Math.cos(angle) * radius;
                const y = cy + Math.sin(angle) * radius;
                
                ctx.beginPath();
                ctx.arc(x, y, 2 + (atp/50), 0, Math.PI * 2);
                ctx.fillStyle = baseColor;
                ctx.fill();
                
                // Connecting lines
                if (i % 5 === 0) {{
                    ctx.beginPath();
                    ctx.moveTo(cx, cy);
                    ctx.lineTo(x, y);
                    ctx.strokeStyle = `rgba(${{baseColor === 'MAGENTA' ? '255,0,255' : '0,255,255'}}, 0.1)`;
                    ctx.stroke();
                }}
            }}
            
            requestAnimationFrame(draw);
        }}
        draw();
    </script>
</body>
</html>
"""
        self.output_file.write_text(html_content, encoding='utf-8')
        print(f"✅ [MANDALA] Generated at {self.output_file}")

if __name__ == "__main__":
    generator = MandalaGenerator(Path("C:/workspace2/shion"))
    generator.generate()
