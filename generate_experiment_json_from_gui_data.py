import json
import os
from datetime import datetime
from typing import Any, Dict, List

def _safe_filename(name: str) -> str:
    # keeps filenames clean: spaces -> _, removes weird chars
    keep = []
    for ch in name.strip():
        if ch.isalnum() or ch in ("_", "-", "."):
            keep.append(ch)
        elif ch.isspace():
            keep.append("_")
    out = "".join(keep)
    return out or "experiment"

def normalize_couplings(raw: Any) -> List[Dict[str, str]]:
    """
    Expects GUI format:
      [{"port_from": "...", "port_to": "..."}, ...]
    Returns the same format, cleaned + validated.
    """
    if raw is None:
        return []

    if not isinstance(raw, list):
        raise ValueError("Couplings must be an array (list).")

    out: List[Dict[str, str]] = []

    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Coupling at index {i} must be an object.")

        if "port_from" not in item or "port_to" not in item:
            raise ValueError(f"Coupling at index {i} must have port_from and port_to.")

        port_from = str(item["port_from"]).strip()
        port_to   = str(item["port_to"]).strip()

        if not port_from or not port_to:
            raise ValueError(f"Coupling at index {i} has empty port_from/port_to.")

        out.append({"port_from": port_from, "port_to": port_to})

    return out

def build_experiment_json(payload: dict) -> dict:
    mut_model = (payload.get("mutModel") or "").strip()
    ef_model  = (payload.get("efModel")  or "").strip()
    mut_init  = (payload.get("mutInit")  or "").strip()
    ef_init   = (payload.get("efInit")   or "").strip()

    time_span_val = payload.get("timeSpan", "")
    try:
        ts = float(time_span_val)
    except (TypeError, ValueError):
        raise ValueError("Time span must be a valid number.")
    if ts <= 0:
        raise ValueError("Time span must be a positive number.")

    time_span = str(ts)

    cpic = normalize_couplings(payload.get("cpic", []))
    pocc = normalize_couplings(payload.get("pocc", []))

    if len(cpic) == 0 and len(pocc) == 0:
        raise ValueError("Add at least one coupling: CPIC or POCC.")

    return {
        "model_under_test": {
            "model": mut_model,
            "initial_state": mut_init,
            "parameters": ""
        },
        "experimental_frame": {
            "model": ef_model,
            "initial_state": ef_init,
            "parameters": ""
        },
        "cpic": cpic,
        "pocc": pocc,
        "time_span": time_span
    }

def save_experiment(repo_root: str, exp_name: str, experiment: dict) -> str:
    """
    Writes the experiment.json to input/experiments and returns the file path.
    """
    experiments_dir = os.path.join(repo_root, "input", "experiments")
    os.makedirs(experiments_dir, exist_ok=True)

    safe = _safe_filename(exp_name)
    filename = f"{safe}_experiment.json"
    out_path = os.path.join(experiments_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(experiment, f, indent=2)

    return out_path

