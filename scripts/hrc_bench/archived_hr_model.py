"""Unchanged function bodies from the archived complete HRC CP-SAT model (MIT)."""
import math,time
from fractions import Fraction
NAMES={0:"H",1:"R",2:"HR"}

def lower_bounds(data):
    w = {m: sum(p for ms, ps in zip(data["modes"], data["durations"]) for mode, p in zip(ms, ps) if mode == m) for m in range(3)}
    h = sum(x[0] for x in data["layouts_humans_robots"])
    r = sum(x[1] for x in data["layouts_humans_robots"])
    pairs = sum(min(x) for x in data["layouts_humans_robots"])
    b = dict(human=math.ceil(Fraction(w[0]+w[2], h)), robot=math.ceil(Fraction(w[1]+w[2], r)),
             hr_pair=math.ceil(Fraction(w[2], pairs)), chain=max(map(sum, data["durations"])))
    return max(b.values()), b, {NAMES[m]: w[m] for m in range(3)}

def solve_cp(data, warm, seconds, workers=8):
    """One exact integer interval model, with arbitrary per-station capacities."""
    from ortools.sat.python import cp_model
    lb, components, work = lower_bounds(data)
    horizon = max(r["end"] for r in warm)
    assert lb <= horizon
    model = cp_model.CpModel()
    starts, ends, present = {}, {}, {}
    local_h = [[] for _ in range(data["stations"])]
    local_r = [[] for _ in range(data["stations"])]
    global_h, global_r, global_hr = [], [], []
    for j, modes in enumerate(data["modes"]):
        ps = data["durations"][j]
        for s, mode in enumerate(modes):
            duration = ps[s]
            earliest = sum(ps[:s])
            latest = horizon - sum(ps[s+1:])
            starts[j,s] = model.new_int_var(earliest, latest-duration, f"s_{j}_{s}")
            ends[j,s] = model.new_int_var(earliest+duration, latest, f"e_{j}_{s}")
            mandatory = model.new_interval_var(starts[j,s], duration, ends[j,s], f"g_{j}_{s}")
            if mode in (0,2): global_h.append(mandatory)
            if mode in (1,2): global_r.append(mandatory)
            if mode == 2: global_hr.append(mandatory)
            choices = []
            for i in range(data["stations"]):
                selected = model.new_bool_var(f"x_{j}_{s}_{i}")
                interval = model.new_optional_interval_var(starts[j,s], duration, ends[j,s], selected, f"o_{j}_{s}_{i}")
                present[j,s,i] = selected
                choices.append(selected)
                # The identical optional interval enters both resources for HR.
                if mode in (0,2): local_h[i].append(interval)
                if mode in (1,2): local_r[i].append(interval)
            model.add_exactly_one(choices)
            if s: model.add(starts[j,s] >= ends[j,s-1])
    for i, (humans, robots) in enumerate(data["layouts_humans_robots"]):
        if local_h[i]: model.add_cumulative(local_h[i], [1]*len(local_h[i]), humans)
        if local_r[i]: model.add_cumulative(local_r[i], [1]*len(local_r[i]), robots)
    for intervals, cap in ((global_h, sum(x[0] for x in data["layouts_humans_robots"])),
                           (global_r, sum(x[1] for x in data["layouts_humans_robots"])),
                           (global_hr, sum(min(x) for x in data["layouts_humans_robots"]))):
        if intervals: model.add_cumulative(intervals, [1]*len(intervals), cap)
    cmax = model.new_int_var(lb, horizon, "cmax")
    model.add_max_equality(cmax, [ends[j,len(modes)-1] for j,modes in enumerate(data["modes"])])
    model.minimize(cmax)
    for row in warm:
        j, s, selected = row["job_id"], row["operation_id"], row["workstation_id"]
        model.add_hint(starts[j,s], row["start"])
        model.add_hint(ends[j,s], row["end"])
        for i in range(data["stations"]): model.add_hint(present[j,s,i], int(i == selected))
    model.add_hint(cmax, horizon)
    error = model.validate()
    assert not error, error
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = data["seed"]
    solver.parameters.relative_gap_limit = 0.
    solver.parameters.absolute_gap_limit = 0.
    solver.parameters.log_search_progress = False
    solver.parameters.symmetry_level = 2
    solver.parameters.exploit_all_precedences = True
    solver.parameters.use_overload_checker_in_cumulative = True
    solver.parameters.use_timetable_edge_finding_in_cumulative = True
    began = time.perf_counter()
    code = solver.solve(model)
    status = solver.status_name(code)
    assert status not in ("MODEL_INVALID", "INFEASIBLE"), status
    result_rows = warm
    if code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        result_rows = []
        for j, modes in enumerate(data["modes"]):
            for s, mode in enumerate(modes):
                selected = [i for i in range(data["stations"]) if solver.value(present[j,s,i])]
                assert len(selected) == 1
                result_rows.append(dict(job_id=j, operation_id=s, workstation_id=selected[0], mode=NAMES[mode], start=solver.value(starts[j,s]), end=solver.value(ends[j,s])))
    upper = max(r["end"] for r in result_rows)
    bound = max(lb, math.ceil(solver.best_objective_bound-1e-8))
    assert bound <= upper
    if status == "OPTIMAL": assert bound == upper
    return dict(status=status, lower=bound, upper=upper, seconds=time.perf_counter()-began,
                analytic=components, work=work, proven=(bound==upper), schedule=result_rows,
                mwkr_upper=horizon, initialization="MWKR only; no learned hints or bounds")
