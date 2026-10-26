"""Data-only ports of the frozen generators, with identical RNG call order.

NumPy 2.4.4 is pinned for archival reproduction; the module needs nothing else.
"""
import math
import numpy as np

def generate_raw(spec):
    algorithm=spec['algorithm'];n=spec['jobs'];seed=spec['seed']
    time_low,time_high=spec['processing_time_range']
    if [time_low,time_high]!=[5,10]:
        raise ValueError('The archived generator version uses integer processing times 5..10')
    if algorithm in ['small_random_v1','independent_duration_v1']:
        rng=np.random.default_rng(seed)
        low,high=spec['operations_per_job']
        modes=[]
        for _ in range(n):
            length=int(rng.integers(low,high+1))
            modes.append([int(rng.choice([0,1,2],p=spec['mode_probabilities'])) for _ in range(length)])
        if algorithm=='independent_duration_v1':
            duration_rng=np.random.default_rng(np.random.SeedSequence([seed,20261016,1]))
        else:
            duration_rng=rng
        times=[[int(duration_rng.integers(time_low,time_high+1)) for _ in ms] for ms in modes]
    elif algorithm=='paired_hr_controls_v1':
        if n==50:lengths=np.array([3]*12+[4]*13+[5]*13+[6]*12)
        elif n==200:lengths=np.array([3]*50+[4]*50+[5]*50+[6]*50)
        else:raise ValueError('This frozen paired protocol supports 50 or 200 jobs')
        np.random.default_rng(np.random.SeedSequence([20261019,n,seed,0])).shuffle(lengths)
        amount=int(lengths.sum())
        flat_times=np.random.default_rng(np.random.SeedSequence([20261019,n,seed,1])).integers(time_low,time_high+1,amount).tolist()
        positions=np.random.default_rng(np.random.SeedSequence([20261019,n,seed,2])).permutation(amount)
        hr=spec['hr_fraction'];mix=[(2-3*hr)/5,(3-2*hr)/5,hr]
        targets=[amount*x for x in mix];quota=[math.floor(x+1e-9) for x in targets]
        remainder=amount-sum(quota)
        for mode in sorted(range(3),key=lambda x:(-round(targets[x]-quota[x],12),x))[:remainder]:quota[mode]+=1
        flat_modes=[None]*amount;begin=0
        for mode,count in enumerate(quota):
            for pos in positions[begin:begin+count]:flat_modes[int(pos)]=mode
            begin+=count
        modes=[];times=[];begin=0
        for length in lengths:
            length=int(length);modes.append(flat_modes[begin:begin+length]);times.append(flat_times[begin:begin+length]);begin+=length
        if spec['order']!='random':
            for job,ms in enumerate(modes):
                rank={0:0,2:1,1:2} if spec['order']=='aligned' or job%2==0 else {1:0,2:1,0:2}
                pairs=sorted(zip(ms,times[job]),key=lambda x:rank[x[0]])
                modes[job],times[job]=[list(x) for x in zip(*pairs)]
    else:raise ValueError(f'Unknown frozen algorithm: {algorithm}')
    return dict(seed=seed,jobs=n,stations=len(spec['layouts_humans_robots']),
                layouts_humans_robots=spec['layouts_humans_robots'],modes=modes,durations=times)
