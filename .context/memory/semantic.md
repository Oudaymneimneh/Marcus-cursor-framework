# Semantic Memory - WHAT things mean

> Definitions, mappings, and conceptual knowledge specific to this project.
> Update when defining or discovering new concepts.

---

## PAD Emotional Framework

**PAD** = Pleasure-Arousal-Dominance

| Dimension | Range | Low (-1) | High (+1) |
|-----------|-------|----------|-----------|
| Pleasure | -1 to 1 | Negative emotion | Positive emotion |
| Arousal | -1 to 1 | Calm, relaxed | Excited, alert |
| Dominance | -1 to 1 | Submissive | Dominant, controlling |

### Marcus Emotional States
| State | P | A | D | Visual Expression |
|-------|---|---|---|-------------------|
| Contemplative | 0.0 | -0.3 | 0.2 | Slightly raised inner brows, eyes up |
| Teaching | 0.3 | 0.4 | 0.4 | Mild smile, raised outer brows, wide eyes |
| Stern | -0.2 | 0.3 | 0.6 | Lowered brows, forward jaw, pressed mouth |
| Warm | 0.5 | 0.2 | 0.3 | Smile, squinted eyes, raised cheeks |
| Melancholic | -0.4 | -0.2 | -0.1 | Raised inner brows, down eyes, slight frown |

---

## FLAME Model

**FLAME** = Faces Learned with an Articulated Model and Expressions

### Output Parameters
| Parameter | Dimensions | Description |
|-----------|------------|-------------|
| expression | 50 | Facial expression coefficients |
| jaw | 3 | Jaw rotation (pitch, yaw, roll) |
| neck | 3 | Neck rotation (pitch, yaw, roll) |

### Why FLAME over Audio2Face
- Audio2Face: Lip sync only
- FLAME: Unified system for lip sync + micro expressions + head movement + eyelid movement
- All derived from speech, creating more realistic animation

---

## ARKit Blend Shapes

MetaHuman uses **52 ARKit-compatible blend shapes**.

### Key Blend Shapes
| Shape | Range | Controls |
|-------|-------|----------|
| jawOpen | 0-1 | Jaw drop |
| mouthSmile_L/R | 0-1 | Lip corner pull up |
| mouthFrown_L/R | 0-1 | Lip corner pull down |
| browInnerUp | 0-1 | Inner brow raise |
| browDown_L/R | 0-1 | Brow furrow |
| eyeSquint_L/R | 0-1 | Eye squint |
| eyeWide_L/R | 0-1 | Eye wide |
| cheekSquint_L/R | 0-1 | Cheek raise (smile) |

### FLAME → ARKit Mapping
The `metahuman_mapper.py` converts FLAME's 50-dim expression vector to 52 ARKit shapes.

---

## MetaHuman Architecture

### What We Keep (from MetaHuman)
- Topology (mesh structure)
- Rig (skeletal system)
- Subsurface scattering profile
- Blend shape names/structure

### What We Rebuild
- Textures (better quality)
- Face shape (match Marcus bust)
- Hair grooms (period-appropriate)

### Known Issues (from community)
- Root bone aligns to heels, not mesh bottom
- Expression editor can take weeks to fix manually
- Grooms can only be added to head, not body

---

## Latency Terminology

| Term | Definition |
|------|------------|
| E2E Latency | Time from user input to first animation frame rendered |
| TTFB | Time To First Byte (audio chunk) |
| P95 | 95th percentile latency (used for SLOs) |
| Cold start | First inference after model load (slower) |
| Warm inference | Subsequent inferences (faster) |

### Target Breakdown
| Stage | Target | Hard Limit |
|-------|--------|------------|
| LLM response | <800ms | 1200ms |
| TTS first chunk | <400ms | 800ms |
| FLAME inference | <200ms | 400ms |
| Network overhead | <200ms | 400ms |
| **Total E2E** | **<1600ms** | **<2800ms** |

---

## Chatterbox TTS

Local text-to-speech system chosen over ElevenLabs.

### Why Chatterbox
- Local hosting = no API latency
- No per-character costs
- Full control over voice parameters
- Can achieve <400ms TTFB

### Voice Parameters for Marcus
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Speaking rate | 0.9x | Deliberate, philosophical |
| Pitch | Slightly lower | Gravitas |
| Accent | Slight British | "Educated Roman" approximation |
| Pauses | Before quotes | Emphasis on wisdom |

---

## Unreal Engine Terms

| Term | Definition |
|------|------------|
| Blueprint | Visual scripting system |
| Skeletal Mesh | 3D mesh with bone hierarchy |
| Morph Target | UE name for blend shape |
| Live Link | Real-time animation streaming protocol |
| MetaHuman Animator | Tool for facial mocap |

---

## File Extensions

| Extension | Tool | Purpose |
|-----------|------|---------|
| .fbx | Universal | 3D model exchange |
| .uasset | Unreal | UE asset file |
| .blend | Blender | Blender project |
| .dna | MetaHuman | MetaHuman definition |
| .pth | PyTorch | Model weights |
| .onnx | ONNX | Cross-platform model |

