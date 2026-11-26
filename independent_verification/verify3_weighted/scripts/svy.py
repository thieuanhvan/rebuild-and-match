"""Taylor-linearised SE of a weighted proportion (ratio mean), with-replacement PSUs within strata."""
import numpy as np, pandas as pd


def tr4(x):
    return int(x * 10000) / 10000


def taylor(y, w, strata, psu, domain):
    """Domain estimate on the full design: rows outside the domain keep their PSU with z = 0.
    Returns (estimate, se, n_domain, n_strata, n_singleton_strata)."""
    y = np.asarray(y, float); w = np.asarray(w, float); d = np.asarray(domain, bool)
    wd = w * d
    W = wd.sum()
    p = (wd * y).sum() / W
    z = wd * (y - p) / W
    df = pd.DataFrame({'h': np.asarray(strata), 'c': np.asarray(psu), 'z': z})
    t = df.groupby(['h', 'c'], sort=False).z.sum().reset_index()
    g = t.groupby('h').z
    n_h = g.transform('size')
    zbar = g.transform('mean')
    t['dev2'] = (t.z - zbar) ** 2
    s = t.assign(n=n_h).groupby('h').agg(n=('n', 'first'), ss=('dev2', 'sum'))
    single = int((s.n == 1).sum())
    s = s[s.n > 1]
    var = (s.n / (s.n - 1) * s.ss).sum()
    return p, float(np.sqrt(var)), int(d.sum()), int(len(s) + single), single


def report(P, label, y, w, h, c, dom, sub=True):
    p, se, n, ns, s1 = taylor(y, w, h, c, dom)
    P(f'{label}: n={n} weighted p={p:.6f} (trunc {tr4(p)}) SE domain={se:.6f} (trunc {tr4(se)}); strata {ns}, singleton {s1}')
    if sub:
        m = np.asarray(dom, bool)
        p2, se2, n2, ns2, s2 = taylor(np.asarray(y)[m], np.asarray(w)[m], np.asarray(h)[m], np.asarray(c)[m], np.ones(m.sum(), bool))
        P(f'   subset-only design: p={p2:.6f} SE={se2:.6f} (trunc {tr4(se2)}); strata {ns2}, singleton {s2}')
    return p, se
