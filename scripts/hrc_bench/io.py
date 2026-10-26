"""Explicit JSON representation and lossless compact HRC text representation."""
import json
from pathlib import Path

MODE_NAMES=['H','R','HR']
DEMANDS={'H':{'humans':1,'robots':0},'R':{'humans':0,'robots':1},'HR':{'humans':1,'robots':1}}

def json_bytes(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def public_instance(raw,spec):
    operations=[];jobs=[];precedences=[];next_id=0
    for j,(modes,times) in enumerate(zip(raw['modes'],raw['durations'])):
        ids=[]
        for step,(mode,duration) in enumerate(zip(modes,times)):
            op_id=next_id;next_id+=1;ids.append(op_id)
            pred=[] if step==0 else [op_id-1]
            name=MODE_NAMES[mode]
            operations.append(dict(operation_id=op_id,job_id=j,sequence_index=step,type=name,
                                   processing_time=duration,resource_demand=dict(DEMANDS[name]),
                                   eligible_workstations=list(range(raw['stations'])),predecessors=pred))
            if pred:precedences.append({'before':pred[0],'after':op_id,'minimum_lag':0})
        jobs.append(dict(job_id=j,release_time=0,operation_ids=ids))
    return dict(schema_version='1.0',instance_id=spec['instance_id'],collection=spec['collection'],
                n_jobs=raw['jobs'],n_workstations=raw['stations'],n_operations=next_id,
                workstations=[dict(workstation_id=i,human_capacity=h,robot_capacity=r) for i,(h,r) in enumerate(raw['layouts_humans_robots'])],
                jobs=jobs,operations=operations,precedences=precedences,
                generation=dict(algorithm=spec['algorithm'],instance_seed=raw['seed'],setting=spec['setting'],
                                generation_base_id=spec['generation_base_id'],role=spec['role']),
                provenance=dict(source_run=spec['source_run'],source_case_id=spec['source_case_id'],
                                original_instance_sha256=spec['original_instance_sha256']),
                model=dict(objective='minimize_makespan',nonpreemptive=True,precedence='independent_job_chains',
                           processing_time_station_invariant=True,operation_type_fixed=True,
                           hr_requires_same_station_simultaneous_interval=True,
                           setup_times=0,transfer_times=0,time_unit='abstract_integer_unit',interval_convention='[start,end)'))

def raw_from_public(data):
    ordered=sorted(data['operations'],key=lambda x:(x['job_id'],x['sequence_index']))
    modes=[[] for _ in range(data['n_jobs'])];times=[[] for _ in range(data['n_jobs'])]
    for op in ordered:
        modes[op['job_id']].append(MODE_NAMES.index(op['type']))
        times[op['job_id']].append(op['processing_time'])
    return dict(seed=data['generation']['instance_seed'],jobs=data['n_jobs'],stations=data['n_workstations'],
                layouts_humans_robots=[[x['human_capacity'],x['robot_capacity']] for x in data['workstations']],
                modes=modes,durations=times)

def text_instance(raw,spec):
    lines=['HRC_BENCH 1',f"INSTANCE {spec['instance_id']}",f"COLLECTION {spec['collection']}",
           f"SEED {raw['seed']}",f"SIZE {raw['jobs']} {raw['stations']}",'CAPACITIES']
    for i,(h,r) in enumerate(raw['layouts_humans_robots']):lines.append(f'{i} {h} {r}')
    lines.append('JOBS')
    for j,(modes,times) in enumerate(zip(raw['modes'],raw['durations'])):
        lines.append(f'JOB {j} {len(modes)}')
        for i,(mode,duration) in enumerate(zip(modes,times)):lines.append(f'{i} {MODE_NAMES[mode]} {duration}')
    lines.append('END')
    return '\n'.join(lines)+'\n'

def parse_text(text):
    lines=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
    assert lines[0]=='HRC_BENCH 1'
    instance_id=lines[1].split()[1];collection=lines[2].split()[1];seed=int(lines[3].split()[1])
    _,nj,ns=lines[4].split();nj=int(nj);ns=int(ns);assert lines[5]=='CAPACITIES'
    layout=[]
    for i in range(ns):
        sid,h,r=map(int,lines[6+i].split());assert sid==i;layout.append([h,r])
    pos=6+ns;assert lines[pos]=='JOBS';pos+=1;modes=[];times=[]
    for job in range(nj):
        tag,j,amount=lines[pos].split();assert tag=='JOB' and int(j)==job;pos+=1
        ms=[];ps=[]
        for step in range(int(amount)):
            op,mode,duration=lines[pos].split();assert int(op)==step
            ms.append(MODE_NAMES.index(mode));ps.append(int(duration));pos+=1
        modes.append(ms);times.append(ps)
    assert lines[pos:]==['END']
    return dict(instance_id=instance_id,collection=collection,raw=dict(seed=seed,jobs=nj,stations=ns,
                layouts_humans_robots=layout,modes=modes,durations=times))

def load_instance(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
