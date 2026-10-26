"""Check that instances, bounds and the CP-SAT archive are mutually consistent.

Run from the repository root:

    python -B scripts/validate.py

The check needs only the standard library. It re-verifies every archived CP
schedule and every optimum witness against the instance files, but it does not
re-solve anything.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from hrc_bench.schedule_validation import verify_schedule


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    bounds = load(root / "bounds.json")
    bound_by_id = {row["instance_id"]: row for row in bounds}
    assert len(bound_by_id) == len(bounds), "duplicate instance_id in bounds.json"
    for row in bounds:
        assert set(row) == {"instance_id", "lb", "optimum"}, row

    instances = {}
    for path in sorted((root / "instances").glob("*/*.json")):
        data = load(path)
        instance_id = data["instance_id"]
        assert path.stem == instance_id, path
        assert len(data["operations"]) == data["n_operations"], instance_id
        assert [o["operation_id"] for o in data["operations"]] == list(range(data["n_operations"]))
        assert data["n_jobs"] == len(data["jobs"]), instance_id
        instances[instance_id] = data
    assert set(instances) == set(bound_by_id), "bounds.json and instances/ disagree"

    runs = load(root / "cpsat/runs.json")
    for run in runs:
        instance = instances[run["instance_id"]]
        checked = verify_schedule(instance, load(root / run["schedule_path"]))
        assert checked["makespan"] == run["reference_upper"], run["instance_id"]
        assert run["reported_lower"] <= run["reference_upper"], run["instance_id"]
        if run["status"] == "OPTIMAL":
            assert run["reported_lower"] == run["reference_upper"], run["instance_id"]
        assert load(root / run["raw_result_path"])["status"] == run["status"], run["instance_id"]

    certificates = {row["instance_id"]: row for row in load(root / "cpsat/optimum_certificates.json")}
    known = 0
    for instance_id, row in sorted(bound_by_id.items()):
        assert type(row["lb"]) is int and row["lb"] > 0, instance_id
        if row["optimum"] is None:
            assert instance_id not in certificates, instance_id
            continue
        assert row["optimum"] == row["lb"], instance_id
        certificate = certificates[instance_id]
        assert certificate["optimum"] == row["optimum"], instance_id
        witness = load(root / certificate["witness_path"])
        assert verify_schedule(instances[instance_id], witness)["makespan"] == row["optimum"], instance_id
        known += 1

    print(json.dumps({
        "passed": True,
        "instances": len(instances),
        "bound_records": len(bounds),
        "certified_optima": known,
        "unknown_optima": len(bounds) - known,
        "cp_runs": len(runs),
        "cp_schedules_checked": len(runs),
        "optimum_witnesses_checked": known,
    }, indent=2))


if __name__ == "__main__":
    main()
