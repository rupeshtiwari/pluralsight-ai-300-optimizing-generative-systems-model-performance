"""Declared experiment gates. These helpers score observations; they never invent them."""
from collections import Counter
from .core import require, summarize

def quality_checks(rows, gates, minimums, baseline=None):
    require(rows, 'No responses to evaluate.')
    counts=Counter(r['query_type'] for r in rows)
    checks={'samples_'+kind:counts[kind]>=minimum for kind,minimum in minimums.items()}
    metrics=summarize(rows); reference=summarize(baseline) if baseline else None
    regression=gates.get('max_regression',0.)
    for key,floor in gates.items():
        if key=='max_regression': continue
        checks[key]=metrics[key]>=floor and (reference is None or metrics[key]>=reference[key]-regression)
        for kind in minimums:
            group=metrics.get('by_query_type',{}).get(kind,{})
            base=reference.get('by_query_type',{}).get(kind,{}) if reference else None
            checks[kind+'_'+key]=key in group and group[key]>=floor and (base is None or key in base and group[key]>=base[key]-regression)
    return checks

def sample_counts(rows, deployments, minimums):
    counts={name:{kind:sum(r['deployment']==name and r['query_type']==kind for r in rows) for kind in minimums} for name in deployments}
    return counts,all(counts[name][kind]>=minimum for name in deployments for kind,minimum in minimums.items())
