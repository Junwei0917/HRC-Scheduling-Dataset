"""Independent integer schedule checks; standard library only (MIT)."""
from collections import defaultdict

def verify_schedule(instance, rows, require_complete=True):
    operations = {o['operation_id']: o for o in instance['operations']}
    stations = {s['workstation_id']: s for s in instance['workstations']}
    scheduled = {}
    events = defaultdict(list)
    for row in rows:
        op_id = row['operation_id']
        if op_id not in operations or op_id in scheduled:
            raise ValueError('Unknown or duplicate operation')
        op = operations[op_id]
        start, end = row['start'], row['end']
        station = row['workstation_id']
        if type(start) is not int or type(end) is not int or start < 0:
            raise ValueError('Times must be nonnegative integers')
        if end - start != op['processing_time']:
            raise ValueError('Processing duration mismatch')
        if station not in op['eligible_workstations']:
            raise ValueError('Ineligible workstation')
        if row.get('type', op['type']) != op['type']:
            raise ValueError('Fixed operation type changed')
        if row.get('job_id', op['job_id']) != op['job_id']:
            raise ValueError('Incorrect job')
        for resource, capacity in [('humans', 'human_capacity'), ('robots', 'robot_capacity')]:
            demand = op['resource_demand'][resource]
            if demand:
                # HR contributes its identical [start,end) interval to both sweeps.
                events[station, capacity].extend([(start, demand), (end, -demand)])
        scheduled[op_id] = row
    if require_complete and set(scheduled) != set(operations):
        raise ValueError('Incomplete schedule')
    for op_id, row in scheduled.items():
        for predecessor in operations[op_id]['predecessors']:
            if predecessor not in scheduled or scheduled[predecessor]['end'] > row['start']:
                raise ValueError('Job precedence violation')
    for (station, capacity), changes in events.items():
        usage = 0
        for _, delta in sorted(changes):  # release before dispatch at equal timestamps
            usage += delta
            if usage < 0 or usage > stations[station][capacity]:
                raise ValueError('Human/robot workstation capacity violation')
        if usage:
            raise ValueError('Unreleased resource')
    return dict(feasible=True, complete=set(scheduled)==set(operations),
                operations=len(rows), makespan=max((r['end'] for r in rows), default=0))

def public_schedule(instance, original_rows):
    """Map archived (job_id, local operation_id) to stable global operation IDs."""
    mapping = {(o['job_id'],o['sequence_index']): o for o in instance['operations']}
    result=[]
    for row in original_rows:
        op=mapping[int(row['job_id']),int(row['operation_id'])]
        if 'mode' in row and row['mode'] != op['type']:
            raise ValueError('Archived operation type changed')
        start,end=row['start'],row['end']
        if int(start)!=start or int(end)!=end:
            raise ValueError('Noninteger archived interval')
        result.append(dict(operation_id=op['operation_id'],job_id=op['job_id'],
            sequence_index=op['sequence_index'],type=op['type'],
            workstation_id=int(row['workstation_id']),start=int(start),end=int(end)))
    return sorted(result,key=lambda r:r['operation_id'])

def original_schedule(instance, rows):
    verify_schedule(instance,rows)
    by_id={o['operation_id']:o for o in instance['operations']}
    return [dict(job_id=by_id[r['operation_id']]['job_id'],
                 operation_id=by_id[r['operation_id']]['sequence_index'],
                 workstation_id=r['workstation_id'],mode=by_id[r['operation_id']]['type'],
                 start=r['start'],end=r['end']) for r in rows]
