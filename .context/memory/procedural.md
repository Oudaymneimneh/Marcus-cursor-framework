# Procedural Memory - HOW to do things

> Learned workflows, commands, and processes specific to this project.
> Update this file when discovering new procedures.

---

## Server Operations

### Starting the Full Pipeline
```bash
# Terminal 1: FLAME server
cd flame-server && python server.py --port 5001

# Terminal 2: TTS server
cd tts-chatterbox && python tts_server.py --port 5002

# Terminal 3: Orchestrator
cd api-bridge && python orchestrator.py --port 5000
```

### Health Check All Services
```bash
curl http://localhost:5001/health  # FLAME
curl http://localhost:5002/health  # TTS
curl http://localhost:5000/health  # Orchestrator
```

### Running Latency Benchmark
```bash
python -m tests.benchmark_pipeline --iterations 100
# Output: latency_report.json with per-stage breakdown
```

---

## Blender Workflows

### Import MetaHuman with Poly Hammer
1. Open Blender
2. Enable Poly Hammer addon
3. File → Import → MetaHuman DNA
4. Select exported FBX from Unreal
5. Verify rig integrity in Armature

### Set Up Reference Images
```python
# Run in Blender scripting tab
bpy.ops.import_image.to_plane(files=[{"name":"front_view.png"}])
# Position as background for sculpting
```

---

## Git Workflows

### Feature Branch Pattern
```bash
git checkout -b feature/phase-X-description
# ... work ...
git add .
git commit -m "feat(phase-X): description"
git push origin feature/phase-X-description
```

### Commit Message Format
```
type(scope): description

Types: feat, fix, docs, refactor, test, chore
Scope: phase number or component name
```

---

## Testing Workflows

### Run All Tests
```bash
pytest tests/ -v --tb=short
```

### Run Specific Test
```bash
pytest tests/test_flame.py::test_inference_latency -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting Procedures

### FLAME Server Not Starting
1. Check GPU availability: `nvidia-smi`
2. Verify CUDA version matches PyTorch
3. Check model path in config
4. Review logs: `tail -f logs/flame.log`

### Latency Exceeding Target
1. Run benchmark: `python -m tests.benchmark_pipeline`
2. Identify bottleneck stage in output
3. Check for blocking I/O in that component
4. Verify network overhead with `/health` endpoints

### MetaHuman Expression Broken
1. Verify blend shape names match ARKit spec
2. Check value ranges (must be 0-1)
3. Test with known-good frame data
4. Compare FLAME output mapping

