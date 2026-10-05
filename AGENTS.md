# 3D Modeling with Blender Headless - Agent Guidelines

This repository is dedicated to procedurally generating, rendering, and exporting low-poly 3D models using **Blender in Headless mode** (`blender --background`).

## Workflow & Project Structure

1. **Shared Utilities (`blender_utils.py`)**:
   - Contains general-purpose procedural functions for scene resets, materials (Principled BSDF with emission), camera placement, studio three-point lighting, image rendering, and exports (`.glb`, `.obj`).
   - Standardizes render settings to use `CYCLES` with CPU device fallback for headless environments lacking GPU display servers/X11.

2. **Model Directories (e.g., `mystic_token/`, `hoverbike/`)**:
   - Each distinct 3D asset lives in its own dedicated directory.
   - Contains a Python generation script (e.g., `generate_token.py`), output files (`.blend`, `.glb`, `.obj`), and rendered screenshots in a `captures/` subdirectory.

3. **Execution Directive**:
   - Always run scripts using `blender --background --python <path_to_script.py>`.

4. **Iterative Reporting (`report.md`)**:
   - **Mandatory**: On every iteration or commit, update or generate `report.md` in the repository root.
   - The `report.md` file must detail:
     - The status of generated renders and visual captures.
     - Any headless environment constraints, limitations, or technical workarounds applied.
     - Summary of model features, materials, and stylized artistic decisions (e.g., *Sable* / *Chants of Sennaar* low-poly aesthetic).
     - Next steps and plan for subsequent 3D model tasks.
