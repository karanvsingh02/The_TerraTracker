"""Aggregation and exploratory statistical inference on authentic observations."""
import calendar
from collections import Counter, defaultdict
from datetime import date
import math
import numpy as np
from scipy import stats
from backend.services.aggregation import aggregate_native, timestamp

def aggregate(rows, resolution, precipitation=False):
    groups = defaultdict(list)
    for row in rows:
        key = row['date'][:4] if resolution == 'annual' else row['date'][:7] if resolution == 'monthly' else row['date']
        groups[key].append(row)
    result = []
    for key, group in sorted(groups.items()):
        values = [r['value'] for r in group if r['value'] is not None]
        year = int(key[:4])
        expected = (366 if calendar.isleap(year) else 365) if resolution == 'annual' else calendar.monthrange(year, int(key[5:7]))[1] if resolution == 'monthly' else 1
        # Exclude partial periods and periods with >10% missing days.
        if len(values) / expected < .9:
            continue
        value = sum(values) if precipitation else float(np.mean(values))
        result.append({'date': key + ('-07-01' if resolution == 'annual' else '-15' if resolution == 'monthly' else ''), 'value': value})
    return result

def mann_kendall(values):
    n = len(values)
    score = sum(int(np.sign(values[j] - values[i])) for i in range(n) for j in range(i + 1, n))
    ties = Counter(values)
    variance = (n*(n-1)*(2*n+5) - sum(t*(t-1)*(2*t+5) for t in ties.values())) / 18
    z = (score - np.sign(score)) / math.sqrt(variance) if variance else 0
    return {'statistic': score, 'pValue': float(2 * stats.norm.sf(abs(z))), 'method': 'Mann–Kendall (tie-corrected, unadjusted for autocorrelation)'}

def analyze(rows, variable, unit, resolution='annual', deseasonalize=False, native_resolution='daily',range_start=None,range_end=None):
    if variable == 'WD10M':
        raise ValueError('Wind direction is circular and requires a dedicated circular analysis.')
    series = aggregate_native(rows, resolution, native_resolution, variable == 'PRECTOTCORR',range_start,range_end)
    if deseasonalize:
        if resolution != 'monthly':
            raise ValueError('Deseasonalization requires monthly aggregation.')
        months = defaultdict(list)
        for row in series:
            months[row['date'][5:7]].append(row['value'])
        series = [dict(row, value=row['value'] - float(np.mean(months[row['date'][5:7]]))) for row in series]
    if len(series) < 3:
        raise ValueError('At least three valid, sufficiently complete periods are needed. Expand the range or choose a finer supported aggregation.')
    if len(series) > 1500:
        raise ValueError('Aggregate daily data to monthly or annual resolution for trend analysis (maximum 1500 periods).')
    x = np.array([timestamp(r['date']).timestamp() / (365.2425*86400) for r in series])
    y = np.array([r['value'] for r in series])
    fit = stats.linregress(x, y)
    constant = bool(np.ptp(y) == 0)
    p = 1.0 if constant else float(fit.pvalue)
    margin = float(stats.t.ppf(.975, len(x)-2) * fit.stderr)
    residuals = y - (fit.intercept + fit.slope*x)
    autocorrelation = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1]) if np.std(residuals[:-1]) > 1e-12 and np.std(residuals[1:]) > 1e-12 else None
    slope = float(fit.slope)
    result_unit = ('mm/period' if variable == 'PRECTOTCORR' and resolution != 'daily' else unit)
    result = dict(kind='continuous', series=series, slopePerYear=slope, slopePerDecade=slope*10,
                confidenceIntervalPerDecade=[(slope-margin)*10, (slope+margin)*10],
                pValue=p, rSquared=0.0 if constant else float(fit.rvalue**2), sampleSize=len(x),
                completeness=sum(r['value'] is not None for r in rows)/len(rows),
                mannKendall=mann_kendall(y.tolist()), lagOneResidualCorrelation=autocorrelation,
                unit=result_unit, resolution=resolution, deseasonalized=deseasonalize,
                fitted=[{'date': r['date'], 'value': float(fit.intercept+fit.slope*t)} for r,t in zip(series,x)],
                interpretation=f'Estimated change: {slope*10:+.3g} {result_unit} per decade. ' +
                ('Evidence of a trend at the 5% level under independent-residual assumptions.' if p < .05 else 'Insufficient evidence of a linear trend at the 5% level; this does not establish zero change.'),
                caveats='Exploratory tests assume independent observations. Seasonality and autocorrelation can overstate significance. Statistical significance does not establish causation. Periods with less than 90% coverage are excluded; precipitation totals may omit up to 10% of days.')

    result['nativeResolution']=native_resolution
    if variable=='FIRE':
        result['rateUnit']='hour'
        result['rateChange']=slope/(365.2425*24)
        result['rateInterval']=[(slope-margin)/(365.2425*24),(slope+margin)/(365.2425*24)]
        result['caveats']+=' Fire analysis is conditional on observed detections at this pixel; missing detections are not treated as zero. Short fire-event trends do not describe long-term climate.'
        result['interpretation']=f"Estimated change among recorded fire detections: {result['rateChange']:+.3g} {unit} per hour. This describes the selected event and sampling interval only."
    return result
