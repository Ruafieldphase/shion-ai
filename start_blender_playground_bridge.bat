@echo off
cd /d C:\workspace2\shion
echo [SHION_BLENDER_PLAYGROUND] Watching Shion outputs and reflecting them into Blender...
echo [SHION_BLENDER_PLAYGROUND] Keep Blender open with C:\workspace\agi\scripts\blender_direct_listener.py running.
python scripts\blender_shion_playground_bridge.py --watch --interval 5 --max-edges 80 --max-trace 48
