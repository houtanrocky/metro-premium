from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[3]
REVISION = "e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85"

def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str) + "\n", encoding="utf-8")

@contextmanager
def run_record(command, config, inputs=()):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    folder = ROOT / "artifacts/runs" / run_id
    folder.mkdir(parents=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    state = {"run_id": run_id, "command": command, "config": config, "dataset_revision": REVISION, "started_utc": datetime.now(timezone.utc).isoformat(), "git_commit": git.stdout.strip() or None, "git_dirty": bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout), "python": platform.python_version(), "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}, "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in inputs if p.exists()], "outputs": [], "validation": [], "failures": []}
    try:
        # A dirty Git flag alone cannot recover the code used by a local run.
        # Snapshot only code/configuration; never collect raw/private datasets.
        code = [p for pattern in ['pipeline/src/**/*.py', 'scripts/*.py', 'scripts/*.mjs', 'configs/*.yaml'] for p in ROOT.glob(pattern)]
        code += [ROOT/p for p in ['pipeline/pyproject.toml', 'pipeline/uv.lock'] if (ROOT/p).exists()]
        state['source_code_snapshot'] = []
        for path in sorted(code):
            relative = path.relative_to(ROOT)
            saved = folder/'source-code'/relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(path.read_bytes())
            state['source_code_snapshot'].append({'source_path':str(relative), 'snapshot_path':str(saved.relative_to(folder)), 'sha256':digest(saved)})
        yield folder, state
        state["status"] = "completed"
    except Exception as e:
        state["status"] = "failed"
        state["failures"].append({"type": type(e).__name__, "message": str(e), "traceback": traceback.format_exc()})
        raise
    finally:
        state["finished_utc"] = datetime.now(timezone.utc).isoformat()
        state["output_hashes"] = [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in folder.rglob("*") if p.is_file()]
        write_json(folder / "manifest.json", state)
