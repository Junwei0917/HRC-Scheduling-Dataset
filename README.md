# Human–Robot Collaborative Scheduling Benchmarks

· 1,140 benchmark configurations · 340 archived CP-SAT runs · 203 certified optima**

This repository contains the positive-integer H/R/HR inputs used or prepared for the experiments, the generation recipes and seeds that reproduce them, portable readers, lower bounds and the exact optima that are known. Operation orders, types, durations and workstation capacities are written out explicitly for every instance. The original input bytes and the earlier release packages are preserved unchanged.

An H operation occupies one human, an R operation occupies one robot, and an HR operation occupies one human and one robot at the same workstation for one identical interval. Operation types are fixed attributes of the input. Processing times are integers from 5 to 10, jobs are precedence chains, and operations are non-preemptive and may move between eligible workstations. There are no setup or transfer times. All times are abstract integer units.

## Collections

| Collection | Jobs | Configurations | Known optima |
|---|---|---:|---:|
| `large_random_integer_v1` | 50, 200 | 20 | 18 |
| `paired_hr_controls_v1` | 50, 200 | 900 | 49 |
| `robot_bottleneck_v1` | 50, 200 | 20 | 16 |
| `small_random_reserved_v1` | 50, 200 | 40 | 0 |
| `small_random_v1` | 5, 10, 15, 20, 25, 30 | 120 | 120 |
| `source_integer_v1` | 50, 200 | 40 | 0 |

S1–S9 cover seeds 930101–930150 at both 50 and 200 jobs, which gives 900 paired configurations with 225 and 900 operations per instance respectively. The other collections use their own documented random job lengths. See the [scenario definitions](docs/SCENARIOS.md), the [seed registry](SEEDS.md) and the [statistics summary](dataset_statistics.json). Related configurations and the alternate JSON and text serializations are not independent random instances.

The separate `auxiliary/` directory holds 1,800 integer training inputs, 8 validation inputs and 1 warmup input from the paired integer experiment. They are excluded from the benchmark count and are not fresh test data. The earlier continuous-time training runs are not represented by these integer files.

## Quick start

Python 3.11 or newer is required, and NumPy 2.4.4 reproduces the archived RNG streams. Reading inputs, checking schedules and inspecting bounds use only the standard library; OR-Tools is optional.

```bash
python -m pip install -r requirements.txt
python -B scripts/validate_dataset.py --root .
python -B scripts/generate.py --all --output regenerated --verify-against .
python -B scripts/validate_bounds.py --root .
python -B scripts/generate_auxiliary.py --output regenerated_auxiliary
```

The checks reconstruct every benchmark JSON and text input and every auxiliary input byte for byte. They do not rerun experiments, train models or solve benchmarks.

```python
from hrc_bench.io import load_instance
data = load_instance("instances/small_random_v1/small_random_v1__n5_1H2R_seed810001.json")
print(data["workstations"])
print(data["operations"][0])
```

## Repository layout

```text
instances.json, instances.csv   Stable IDs, dimensions, paths, hashes, lower bound and optimum
instances/<collection>/         Full explicit operation-level JSON inputs
text/<collection>/              Lossless, documented compact .hrc files
original_inputs/                Unchanged original input bytes
configs/, seeds.json, SEEDS.md  Exact generation configurations and seed rules
scenarios.json                  S1–S9 definitions
instance_usage.json             Experiment input-use registry
bounds.json, bounds.csv         Only instance_id, lb, optimum
cpsat/runs.json                 Archived full-problem solver runs and parameters
cpsat/raw_results/              Original CP result records, unchanged
cpsat/schedules/                Independently checked CP feasible schedules
cpsat/warm_starts/              Archived neutral MWKR hints
cpsat/optimum_witnesses/        Feasible schedules matching certified lower bounds
auxiliary/                      Separate integer training/validation/warmup inputs
hrc_bench/, scripts/, tests/    Portable generation, reading, validation, CP entry point
schema/, docs/, provenance/     Formats, semantics, limitations and source hashes
LICENSE*, CITATION.cff          CC BY 4.0 data, MIT code, dataset citation
SHA256SUMS                      SHA-256 of every public file
```

## Lower bounds and certified optima

`bounds.json` keeps a three-field record:

```json
{"instance_id":"small_random_v1__n5_1H2R_seed810001","lb":31,"optimum":31}
```

All 1,140 configurations have a valid lower bound; 203 exact optima are established and 937 remain unknown (`null`). A lower bound is not an optimum, and an unknown optimum does not mean zero, failure or infeasibility. The release contains no MPPO/Lei/GA/PSO performance tables and no model weights. Raw CP upper bounds and statuses stay in a separate solver archive instead of being mixed into the bound table. Optimum witnesses are feasibility certificates, not a ranking of policies.

The independent checker rechecks every primal schedule and all bound arithmetic. It does not re-prove historical CP dual bounds or rerun long solves; [bound semantics](docs/BOUNDS.md) documents the distinction.

## CP-SAT model and reproduction

```bash
python -m pip install -r requirements-solver.txt
python -B -m unittest discover -s tests -v
python -B scripts/solve_cp_sat.py instances/paired_hr_controls_v1/paired_hr_controls_v1__n50_anchor_seed930101.json --warm-start cpsat/warm_starts/paired_hr_controls_v1__n50_anchor_seed930101.json --seconds 600 --workers 8 --output local_runs/my_run.json
```

The last command starts a new solve only when it is run. The complete interval model keeps local capacities, job precedence and identical HR intervals on both resources. Historical budgets were 600 s for instances with 5–50 jobs and 1,800 s for 200 jobs, with 8 workers and MWKR initialization only. The function bodies of the complete heterogeneous model are archived unchanged, and the earlier uniform-capacity implementation is retained as well. The [CP-SAT documentation](docs/CPSAT.md) explains the models, hints, version limits and stopped or reused runs.

## Usage history and interpretation

These inputs have been published and inspected, so they are not a blind test set. Seeds 930111–930140 were once reserved for future tests; they have since been used, and the [usage registry](instance_usage.json) records how each input was actually used. Different policies, decoding rules, evaluation repeats, resource seeds and serialization formats do not create new input instances. S1, S4 and S5 also change the H:R composition, so these comparisons do not isolate the effect of the HR share alone.

## License, citation and upload

Data and documentation are released under **CC BY 4.0**, and the generator, reader, validator and solver code under **MIT**. The existing license texts and author attribution are retained, and no additional citation of the paper is required. See `LICENSE`, `LICENSE-DATA`, `LICENSE-CODE` and `CITATION.cff`.

To publish the dataset, upload the contents of this directory as the repository root; see the [upload instructions](docs/PUBLISHING.md). This version has no remote repository, DOI or remote CI run.

The layout follows [PSPLIB](https://www.om-db.wi.tum.de/psplib/library.php), [JSPLIB](https://github.com/tamy0612/JSPLIB) and [FJSPLIB](https://github.com/PyJobShop/FJSPLIB): separate instance files, index metadata, parsers, bound and optimum tables, and solver records. The `.hrc` format is specific to this dataset and keeps HR synchronization explicit; it is not an unmodified JSSP or FJSP format. No third-party benchmark data or implementation is redistributed. See the [comparison with public libraries](docs/REFERENCE_DATASETS.md).
