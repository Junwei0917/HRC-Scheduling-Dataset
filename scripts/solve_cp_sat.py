"""Portable entry point for the archived complete-HRC CP-SAT model (MIT)."""
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[0]))
from hrc_bench.io import raw_from_public
from hrc_bench.archived_hr_model import solve_cp
from hrc_bench.schedule_validation import verify_schedule,original_schedule,public_schedule

def serial_reference(instance):
    rows=[];time=0
    for op in instance['operations']:
        station=next((s for s in instance['workstations'] if s['workstation_id'] in op['eligible_workstations']
            and s['human_capacity']>=op['resource_demand']['humans']
            and s['robot_capacity']>=op['resource_demand']['robots']),None)
        if station is None:raise ValueError('An operation has no feasible workstation')
        rows.append(dict(operation_id=op['operation_id'],job_id=op['job_id'],type=op['type'],
            workstation_id=station['workstation_id'],start=time,end=time+op['processing_time']))
        time+=op['processing_time']
    verify_schedule(instance,rows)
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('instance',type=Path);p.add_argument('--warm-start',type=Path)
    p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=8)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.seconds<=0 or args.workers<1:p.error('Positive time budget and worker count required')
    instance=json.loads(args.instance.read_text(encoding='utf-8'))
    if any(o['eligible_workstations']!=list(range(instance['n_workstations'])) for o in instance['operations']):
        raise ValueError('Archived model assumes all workstations are eligible')
    warm=json.loads(args.warm_start.read_text(encoding='utf-8')) if args.warm_start else serial_reference(instance)
    verify_schedule(instance,warm)
    result=solve_cp(raw_from_public(instance),original_schedule(instance,warm),args.seconds,args.workers)
    result['initialization']='User-supplied schedule' if args.warm_start else 'Serial reference (not the historical MWKR hint)'
    result['schedule']=public_schedule(instance,result['schedule'])
    result['schedule_validation']=verify_schedule(instance,result['schedule'])
    result['instance_id']=instance['instance_id']
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['schedule','analytic','work']}))

if __name__=='__main__':main()
