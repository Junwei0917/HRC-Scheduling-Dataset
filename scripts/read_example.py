"""Print every operation of one instance with the standard-library reader."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[0]))
from hrc_bench.io import load_instance

p=argparse.ArgumentParser();p.add_argument('instance',type=Path);args=p.parse_args()
x=load_instance(args.instance)
print(x['instance_id'])
for station in x['workstations']:
    print(f"Station {station['workstation_id']}: H={station['human_capacity']}, R={station['robot_capacity']}")
for op in x['operations']:
    print(f"Job {op['job_id']} step {op['sequence_index']}: {op['type']}, p={op['processing_time']}, predecessors={op['predecessors']}")
