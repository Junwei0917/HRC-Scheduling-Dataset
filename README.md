# Human–Robot Collaborative Scheduling Benchmark Dataset

 · 1,140 instances · 203 certified optima · 340 archived CP-SAT runs · 572,603 operations

This dataset provides benchmark instances for scheduling problems in which an
operation may need a human, a robot, or a human and a robot working at the same
workstation at the same time. Every instance is synthetic and fully
reproducible from a frozen generator and an integer seed. Operation type,
duration, precedence and workstation capacity are written out explicitly in
each file, so an instance can be read without any solver library.

## Problem

Each job is an independent chain of operations. An operation has a fixed type:

| Type | Human demand | Robot demand | Semantics |
|---|---:|---:|---|
| `H` | 1 | 0 | One human at the selected workstation |
| `R` | 0 | 1 | One robot at the selected workstation |
| `HR` | 1 | 1 | Both at the **same workstation**, with identical start and end |

Processing times are integers from 5 to 10 and do not depend on the chosen
workstation. Operations are non-preemptive, every job has release time 0, and
there are no setup or transfer times. Operation types are fixed: the decision
is which ready operation to schedule on which eligible workstation, not how to
execute an operation. Each workstation has its own human and robot capacity;
summing the stations into one global pool is a relaxation, not an equivalent
model. Capacity is released before new operations start at the same timestamp
(`[start, end)` convention). The objective is makespan minimisation, and time is
measured in abstract integer units.

## Collections

| Collection | Jobs | Instances | Certified optima | Generator |
|---|---|---:|---:|---|
| `small_random_v1` | 5, 10, 15, 20, 25, 30 | 120 | 120 | `small_random_v1` |
| `paired_hr_controls_v1` | 50, 200 | 900 | 49 | `paired_hr_controls_v1` |
| `large_random_integer_v1` | 50, 200 | 20 | 18 | `independent_duration_v1` |
| `robot_bottleneck_v1` | 50, 200 | 20 | 16 | `independent_duration_v1` |
| `source_integer_v1` | 50, 200 | 40 | 0 | `independent_duration_v1` |
| `small_random_reserved_v1` | 50, 200 | 40 | 0 | `small_random_v1` |

File names follow `collection__setting_seed<seed>.json`, for example
`paired_hr_controls_v1__n50_anchor_seed930101.json`.

Across the release there are 230 generation-base groups and 640 distinct
type–duration workloads. Instances that share a base seed, or that differ only
in workstation layout or operation order, are **not** independent samples:
`paired_hr_controls_v1` builds nine scenarios on one workload so that each
effect can be isolated, and those variants must stay grouped in any
statistical comparison.

## Scenario suite S1–S9

`paired_hr_controls_v1` contains nine settings on the same workload, at 50 and
200 jobs, for seeds 930101–930150. Each workstation pair is written as
(humans, robots).

| Code | Setting key | Target H/R/HR | Workstation capacities | HR pair capacity |
|---|---|---|---|---:|
| S1 | `anchor` | 0.10/0.40/0.50 | (3,2); (2,3); (1,4) | 5 |
| S2 | `capacity_x2` | 0.10/0.40/0.50 | (6,4); (4,6); (2,8) | 10 |
| S3 | `capacity_x3` | 0.10/0.40/0.50 | (9,6); (6,9); (3,12) | 15 |
| S4 | `demand_hr30` | 0.22/0.48/0.30 | (3,2); (2,3); (1,4) | 5 |
| S5 | `demand_hr60` | 0.04/0.36/0.60 | (3,2); (2,3); (1,4) | 5 |
| S6 | `layout_P6` | 0.10/0.40/0.50 | (2,3); (2,3); (2,3) | 6 |
| S7 | `layout_P4` | 0.10/0.40/0.50 | (3,1); (2,3); (1,5) | 4 |
| S8 | `order_aligned` | 0.10/0.40/0.50 | (3,2); (2,3); (1,4) | 5 |
| S9 | `order_opposed` | 0.10/0.40/0.50 | (3,2); (2,3); (1,4) | 5 |

S1, S2 and S3 differ only in local capacity; S4 and S5 change the type quotas;
S6 and S7 rearrange the same 6 humans and 9 robots into different local pairs;
S8 and S9 reorder each job's operations without changing its multiset of
(type, duration) pairs. The HR pair capacity is `P = sum_j min(H_j, R_j)`.

## Layout

```text
instances/<collection>/   One JSON file per instance, 1,140 in total
scripts/                  Generator, reader, exact CP-SAT entry point and checker
cpsat/                    Archived exact-solving results and schedules
configs/                  Exact generation parameters, one file per collection
bounds.json               Lower bound and known optimum for every instance
CITATION.cff              Dataset citation metadata
LICENSE                   CC BY 4.0 for the data, MIT for the scripts
```

## Instance file

```json
{
  "instance_id": "small_random_v1__n5_1H2R_seed810001",
  "collection": "small_random_v1",
  "n_jobs": 5, "n_workstations": 3, "n_operations": 17,
  "workstations": [{"workstation_id": 0, "human_capacity": 1, "robot_capacity": 2}],
  "operations": [{
    "operation_id": 1, "job_id": 0, "sequence_index": 1, "type": "HR",
    "processing_time": 9, "resource_demand": {"humans": 1, "robots": 1},
    "eligible_workstations": [0, 1, 2], "predecessors": [0]
  }],
  "jobs": [{"job_id": 0, "release_time": 0, "operation_ids": [0, 1, 2, 3]}],
  "precedences": [{"before": 0, "after": 1, "minimum_lag": 0}]
}
```

Operation IDs are unique and zero-based within an instance. `predecessors` and
`precedences` state the same chain edges twice, once per operation and once as a
graph edge list. `generation` records the algorithm, seed, setting and base ID
used to build the instance, and `provenance` keeps the SHA-256 of the original
input file.

## Bounds

`bounds.json` holds one record per instance:

```json
{"instance_id": "small_random_v1__n5_1H2R_seed810001", "lb": 31, "optimum": 31}
```

All 1,140 instances have a valid integer lower bound; 203 have a certified exact
optimum and 937 are `null`. Null means only that the optimum is not established —
it does not mean zero, infeasible or failed. A certified optimum always equals
the published lower bound and the makespan of a fully checked schedule in
`cpsat/optimum_witnesses/`.

## Exact solving results

`cpsat/` archives 340 CP-SAT runs: 120 on the small instances, 110 at 50 jobs and
110 at 200 jobs. The time budget was 600 s for instances with up to 50 jobs and
1,800 s for the 200-job instances, always with 8 search workers.

| Path | Content |
|---|---|
| `runs.json` | One record per run: status, reported lower bound, reference upper bound, budget, seed and paths to the archived artifacts |
| `raw_results/` | Solver output as recorded, including status and runtime |
| `schedules/` | Feasible schedule for every run, with one row per operation |
| `optimum_witnesses/` | Feasible schedule matching a certified optimum |
| `optimum_certificates.json` | Which witness closes which bound |
| `warm_starts/` | Archived MWKR hints used as the solver initialisation |

Of the 340 runs, 191 finished `OPTIMAL` and 149 finished `FEASIBLE`. A
`FEASIBLE` status is not an optimality proof; a case is closed either by
`OPTIMAL` or by a witness that equals the published lower bound.

## Scripts

Python 3.11 or newer. Reading instances, checking schedules and validating the
release use only the standard library.

```bash
# Re-verify every instance, bound and archived schedule; prints a JSON summary
python -B scripts/validate.py

# Print one instance in readable form
python -B scripts/read_example.py instances/small_random_v1/small_random_v1__n5_1H2R_seed810001.json

# Regenerate all instances from configs/ (needs NumPy)
python -m pip install "numpy==2.4.4"
python -B scripts/generate.py --all --output regenerated
```

The generator reproduces the published files byte for byte. NumPy 2.4.4 is the
pinned version; NumPy 2.3.5 also reproduced them exactly in testing. Because the
RNG call order is part of the recipe, changing the order changes the dataset.

An exact CP-SAT solve of one instance can be started with OR-Tools:

```bash
python -m pip install "ortools==9.15.6755"
python -B scripts/solve_cp_sat.py instances/paired_hr_controls_v1/paired_hr_controls_v1__n50_anchor_seed930101.json \
    --warm-start cpsat/warm_starts/paired_hr_controls_v1__n50_anchor_seed930101.json \
    --seconds 600 --workers 8 --output local_run.json
```

Solver runs are not bit-for-bit reproducible across hardware and versions, so
`runs.json` records what was archived rather than promising a replay. Without
`--warm-start` the script uses a serial constructive reference and labels the
output as such.

## Usage notes

These instances have been published and inspected, so the collection is not a
blind or held-out test set. Seeds 930111–930140 were originally reserved for
later tests and have since been used. Repeated runs of a stochastic algorithm
are algorithm-seed repeats, not new instances. Auxiliary training and validation
inputs from the wider study, the generation code of the original experiments,
and the raw input bytes are kept in the full reproducibility package rather than
in this release.

## Scope

This release contains instances, generation parameters, lower bounds, certified
optima and exact CP-SAT results. It contains no policy or learning model weights,
no training code and no algorithm performance comparison tables.

## License and citation

Data and documentation: Creative Commons Attribution 4.0 International
(CC BY 4.0). Python scripts: MIT. The full legal texts are in `LICENSE`.

Citation metadata is in `CITATION.cff`. Please cite the dataset if you use
these instances.

```bibtex
@misc{hrc_scheduling_benchmarks,
  title  = {Human-Robot Collaborative Scheduling Benchmark Dataset},
  author = {Gao, Junwei and Cheng, Bayi and Wang, Lingjun and Zhou, Mi},
  year   = {2026},
  version = {2.0.0},
  note   = {CC BY 4.0}
}
```
