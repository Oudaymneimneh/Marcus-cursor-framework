# M4 Max Configuration Guide

> **Hardware-Optimized Settings** for Apple M4 Max
> Generated: 2025-11-26

---

## Hardware Profile

**Device:** Apple M4 Max (2024)
- **CPU:** 16 cores (12 performance + 4 efficiency)
- **GPU:** 40 cores (Metal-accelerated)
- **RAM:** 64 GB unified memory
- **Storage:** 926 GB SSD
- **Acceleration:** Metal Performance Shaders (MPS)

---

## Performance Targets

### Latency Goals (All Services Combined)

| Service | Original Target | M4 Max Target | Stretch Goal |
|---------|----------------|---------------|--------------|
| **Total E2E** | <2000ms | <800ms | <500ms |
| **LLM Response** | <800ms | <400ms | <250ms |
| **TTS TTFB** | <400ms | <150ms | <100ms |
| **FLAME Inference** | <200ms | <50ms | <30ms |
| **Frame Rate** | 30fps | 60fps | 120fps |

### Quality Targets

| Aspect | Original | M4 Max Enhanced |
|--------|----------|-----------------|
| **Audio Quality** | 16kHz, 16-bit | 48kHz, 24-bit studio |
| **Blend Shapes** | 512x512 | 1024x1024 |
| **Render Resolution** | 1080p | 4K (3840x2160) |
| **Particle Count** | 1,000 | 50,000 |
| **Texture Resolution** | 2K | 4K |
| **Model Precision** | Quantized (int8) | Full (float32) |
| **LLM Context** | 8K tokens | 32K-128K tokens |

---

## Service Configurations

### 1. FLAME Server (Port 5001)

**Quality Settings:**
```python
QUALITY_CONFIG = {
    "resolution": 1024,           # High-res blend shape maps
    "target_fps": 60,              # Smooth animation
    "use_metal": True,             # Metal GPU acceleration
    "precision": "float32",        # No quantization
    "batch_size": 1,               # Real-time processing
    "blend_shape_count": 52,       # ARKit standard
    "smoothing_window": 5          # Frame smoothing
}
```

**GPU Configuration:**
```bash
# PyTorch with Metal backend
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
```

**Expected Performance:**
- Inference: <50ms per frame
- GPU utilization: 30-50%
- Memory: ~8GB VRAM

---

### 2. TTS Chatterbox (Port 5002)

**Audio Settings:**
```python
AUDIO_CONFIG = {
    "sample_rate": 48000,          # Studio quality
    "bit_depth": 24,               # High dynamic range
    "channels": 1,                 # Mono
    "format": "pcm_s24le",         # Lossless
    "use_gpu": True,               # Metal acceleration
    "streaming": True,             # Low-latency chunks
    "chunk_size": 4096             # Larger for quality
}
```

**Voice Profile (Marcus):**
```python
MARCUS_VOICE = {
    "age": 58,                     # Historical accuracy
    "tone": "contemplative",       # Stoic philosopher
    "pitch": -0.1,                 # Slightly lower
    "speaking_rate": 0.9,          # Measured pace
    "accent": "neutral",           # Clear articulation
    "emotion_range": 0.6           # Subtle expressiveness
}
```

**Expected Performance:**
- TTFB: <150ms (first audio chunk)
- Total synthesis: <300ms for 10 words
- GPU utilization: 20-40%
- Memory: ~4GB VRAM

---

### 3. API Bridge / Orchestrator (Port 8000)

**Pipeline Configuration:**
```python
PIPELINE_CONFIG = {
    "mode": "parallel",            # LLM + prep simultaneously
    "llm_context": 32000,          # 32K token window
    "history_length": 50,          # Keep full conversation
    "cache_embeddings": True,      # Speed up context retrieval
    "max_concurrent": 5,           # Support multiple users
    "timeout_ms": 800              # Total pipeline timeout
}
```

**Parallel Orchestration:**
```
User Input
    ↓
    ├─→ LLM (async) ─────────┐
    │                        ↓
    └─→ PAD State (async) ───┼─→ Merge → TTS → FLAME → Response
                             ↓
                        History Retrieval
```

**Expected Performance:**
- Context retrieval: <50ms (Redis cache)
- LLM inference: <400ms
- Total orchestration overhead: <100ms

---

### 4. Frontend (Next.js + R3F)

**3D Scene Settings:**
```typescript
const SCENE_CONFIG = {
  particleCount: 50000,           // High particle density
  renderResolution: [3840, 2160], // 4K
  targetFPS: 60,                  // Smooth animation
  postProcessing: true,           // Bloom, DOF, etc.
  shadowQuality: "ultra",         // High-quality shadows
  antialiasing: "MSAA x4",        // Smooth edges
  useWebGL2: true                 // Modern features
};
```

**Particle System:**
```typescript
const PARTICLES = {
  count: 50000,
  size: 0.05,
  opacity: 0.8,
  colorRange: ["#4A90E2", "#50E3C2"],
  animation: {
    speed: 0.0005,
    turbulence: 0.002,
    attraction: 0.001
  }
};
```

**Expected Performance:**
- Frame rate: 60fps sustained
- GPU utilization: 40-60% (browser)
- Memory: ~2GB VRAM
- Page load: <2s

---

## Environment Variables

**Create `.env` file:**
```bash
# Hardware
DEVICE=mps                          # Metal Performance Shaders
GPU_MEMORY_FRACTION=0.8             # Use 80% of unified memory

# Quality
AUDIO_SAMPLE_RATE=48000
FLAME_RESOLUTION=1024
RENDER_TARGET_FPS=60
RENDER_RESOLUTION=3840x2160

# Performance
MAX_BATCH_SIZE=1                    # Real-time
ENABLE_QUANTIZATION=false           # Full precision
PARALLEL_PROCESSING=true            # Enable parallel pipeline

# Latency Targets
TARGET_TOTAL_LATENCY_MS=800
TARGET_LLM_LATENCY_MS=400
TARGET_TTS_TTFB_MS=150
TARGET_FLAME_LATENCY_MS=50

# Backend
OPENAI_API_KEY=your_key_here
DATABASE_URL=your_postgres_url
REDIS_URL=redis://localhost:6379

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Docker Resource Limits

**Update `docker-compose.yml`:**

```yaml
services:
  api-bridge:
    deploy:
      resources:
        limits:
          memory: 16G              # Increased from 4G
          cpus: '8'                # More CPU cores
        reservations:
          memory: 8G

  flame-server:
    deploy:
      resources:
        limits:
          memory: 16G              # High-res models
          cpus: '6'
        reservations:
          memory: 8G

  tts-chatterbox:
    deploy:
      resources:
        limits:
          memory: 8G               # Voice models
          cpus: '4'
        reservations:
          memory: 4G
```

---

## Monitoring & Benchmarking

### Latency Tracking

**Prometheus Metrics:**
```yaml
# Custom metrics for M4 Max
- flame_inference_seconds{quantile="0.95"} < 0.050
- tts_ttfb_seconds{quantile="0.95"} < 0.150
- llm_response_seconds{quantile="0.95"} < 0.400
- total_e2e_seconds{quantile="0.95"} < 0.800
```

### Performance Testing

**Benchmark Script:**
```bash
# Run comprehensive performance test
python scripts/benchmark_m4max.py

# Expected output:
# ✅ FLAME: 45ms avg (target: <50ms)
# ✅ TTS TTFB: 135ms avg (target: <150ms)
# ✅ LLM: 380ms avg (target: <400ms)
# ✅ Total E2E: 720ms avg (target: <800ms)
```

---

## Optimization Tips

### 1. Metal GPU Optimization
```python
import torch

# Enable Metal optimizations
if torch.backends.mps.is_available():
    torch.mps.set_per_process_memory_fraction(0.8)
    device = torch.device("mps")
else:
    raise RuntimeError("MPS not available - M4 Max required")
```

### 2. Unified Memory Management
- M4 Max has 64GB unified memory (shared CPU/GPU)
- Allocate 48GB to services, 16GB for system
- No explicit GPU memory transfers needed

### 3. Parallel Pipeline
```python
import asyncio

async def parallel_pipeline(user_input):
    # Run LLM and context retrieval simultaneously
    llm_task = asyncio.create_task(generate_llm_response(user_input))
    context_task = asyncio.create_task(retrieve_context(user_input))
    
    response, context = await asyncio.gather(llm_task, context_task)
    
    # Then TTS and FLAME in sequence (TTS needs response text)
    audio = await generate_audio(response)
    expressions = await generate_expressions(audio)
    
    return response, audio, expressions
```

### 4. Context Window Usage
```python
# With 64GB RAM, use large context windows
LLM_CONFIG = {
    "max_tokens": 32000,        # Full conversation history
    "context_window": 128000,   # Claude 3.5 Sonnet max
    "cache_prompt": True        # Reuse system prompt
}
```

---

## Quality Verification Checklist

### Audio Quality
- [ ] Sample rate: 48kHz confirmed
- [ ] Bit depth: 24-bit confirmed
- [ ] No clipping or distortion
- [ ] TTFB < 150ms sustained

### Visual Quality
- [ ] 4K rendering confirmed
- [ ] 60fps sustained (no drops)
- [ ] Particles: 50,000 rendered
- [ ] No aliasing or artifacts

### Latency
- [ ] E2E < 800ms (p95)
- [ ] LLM < 400ms (p95)
- [ ] TTS TTFB < 150ms (p95)
- [ ] FLAME < 50ms (p95)

### GPU Utilization
- [ ] Metal acceleration confirmed
- [ ] GPU usage 40-70% (healthy)
- [ ] No thermal throttling
- [ ] Memory < 50GB used

---

## Troubleshooting

### Issue: MPS Not Available
```bash
# Check PyTorch Metal backend
python -c "import torch; print(torch.backends.mps.is_available())"

# If False, reinstall PyTorch with MPS:
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Issue: High Memory Usage
```bash
# Monitor memory
top -o MEM

# If >80%, reduce settings:
FLAME_RESOLUTION=768  # Down from 1024
PARTICLE_COUNT=25000  # Down from 50000
```

### Issue: Latency Targets Missed
```bash
# Run profiler
python scripts/profile_latency.py

# Check bottlenecks:
# - Network I/O (use localhost)
# - Disk I/O (use SSD)
# - API rate limits (OpenAI)
```

---

## Upgrade Path (Future)

| Component | Current | Future Upgrade |
|-----------|---------|----------------|
| Particles | 50K | 100K with compute shaders |
| Resolution | 4K | 8K for displays |
| Frame rate | 60fps | 120fps for VR |
| Audio | 48kHz | 96kHz audiophile |
| Context | 32K tokens | 200K tokens (Claude) |

---

## Summary

The M4 Max configuration transforms Marcus AI from a basic conversational agent into a **photorealistic, real-time avatar** with:

- **3x lower latency** (<800ms vs 2000ms)
- **3x higher quality** (4K, 48kHz, 50K particles)
- **Zero cloud costs** (local GPU processing)
- **10x larger context** (32K vs 8K tokens)

All quality targets are achievable with proper configuration. 🚀

