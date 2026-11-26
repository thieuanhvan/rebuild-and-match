"""Figure 1: flow from raw BRFSS respondents to rows in each published file.
Counts are the verified rebuild counts (rebuild_2015_out.txt, rebuild_2020_out.txt, rebuild_2022_out.txt, idea-hunt-surveybench-20261125 counts_i360_out.txt;
recomputed in verify2/verify3). Usage: python -I -X utf8 figure1.py <out_dir>"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def t4(x):
    return int(x * 10000) / 10000

def fmt(n):
    return f"{n:,}"

P = {
 'A': ("A. BRFSS 2015: diabetes file", [
    ("main", f"Raw respondents\n{fmt(441456)}"),
    ("excl", f"Excluded: no valid diabetes answer\n{fmt(798)}"),
    ("main", f"Valid label\n{fmt(440658)}"),
    ("excl", f"Excluded: any missing feature\n(complete cases over 22 columns)\n{fmt(186978)}"),
    ("main", f"Binary and three-class files\n{fmt(253680)} ({t4(253680/441456)})\nclass 1: {fmt(35346)} diabetes\nclass 0 includes {fmt(4631)} prediabetes\nand {fmt(1978)} pregnancy-only"),
    ("main", f"50:50 file\n{fmt(70692)} ({fmt(35346)} per class)"),
 ]),
 'B': ("B. BRFSS 2020: heart file", [
    ("main", f"Raw respondents\n{fmt(401958)}"),
    ("excl", f"Excluded: complete cases\nover 18 columns\n{fmt(82163)}"),
    ("main", f"heart_2020_cleaned\n{fmt(319795)} ({t4(319795/401958)})\npositives {fmt(27373)}\nof which without infarction {fmt(9874)}"),
 ]),
 'C': ("C. BRFSS 2022: heart files", [
    ("main", f"Raw respondents\n{fmt(445132)}"),
    ("main", f"heart_2022_with_nans\n{fmt(445132)} (all respondents)"),
    ("excl", f"Excluded: complete cases\nover 40 columns\n{fmt(199110)}\nof which only \"don't know\"\n{fmt(98073)}"),
    ("main", f"heart_2022_no_nans\n{fmt(246022)} ({t4(246022/445132)})"),
 ]),
 'D': ("D. BRFSS 2021: CVD file", [
    ("main", f"Raw respondents\n{fmt(438693)}"),
    ("excl", f"Excluded: missing, don't know or refused\non any of 19 columns (correct coding)\n{fmt(102042)}"),
    ("main", f"Complete under correct coding\n{fmt(336651)}"),
    ("excl", f"Excluded by undocumented steps {fmt(27797)}:\n\"less than once a month\" {fmt(15097)}\nvalue > 128 after recode {fmt(5101)}\nPHYSHLTH/MENTHLTH not valid {fmt(7599)}"),
    ("main", f"CVD_cleaned\n{fmt(308854)} ({t4(308854/438693):.4f})\n{fmt(1666)} rows with a\nmis-converted food value"),
 ]),
 'E': ("E. NHFS 2009-10: flu vaccine files", [
    ("main", f"Raw interview records\n{fmt(70944)}"),
    ("excl", f"Not in files: children\n{fmt(14288)}"),
    ("main", f"Adults\n{fmt(56656)}"),
    ("excl", f"Absent adults {fmt(3241)} (removal not documented):\nno vaccination answer {fmt(429)}\nboth answers present {fmt(2812)}"),
    ("main", f"Training {fmt(26707)} + test {fmt(26708)}\n= {fmt(53415)} ({t4(53415/56656):.4f} of adults)\ninterview month not included"),
 ]),
}

def draw(out):
    fig, axes = plt.subplots(1, 5, figsize=(21, 7.2))
    for ax, key in zip(axes, 'ABCDE'):
        title, steps = P[key]
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        ax.set_title(title, fontsize=11, loc='left', fontweight='bold')
        n = len(steps); top = 0.93; gap = 0.147
        prev = None
        for i, (kind, txt) in enumerate(steps):
            yc = top - gap * (i + 0.5)
            h = gap * 0.78
            x0, w = (0.05, 0.9) if kind == 'main' else (0.18, 0.78)
            fc = '#ffffff' if kind == 'main' else '#ededed'
            ls = '-' if kind == 'main' else '--'
            ax.add_patch(FancyBboxPatch((x0, yc - h / 2), w, h, boxstyle='round,pad=0.005,rounding_size=0.015',
                                        fc=fc, ec='#333333', lw=1.0, ls=ls))
            ax.text(x0 + w / 2, yc, txt, ha='center', va='center', fontsize=8.6, color='#111111')
            if prev is not None:
                ax.annotate('', xy=(0.11, yc + h / 2), xytext=(0.11, prev),
                            arrowprops=dict(arrowstyle='->', color='#333333', lw=1.0))
            prev = yc - h / 2
    fig.text(0.01, 0.01, 'Dashed boxes: respondents excluded. Shares are of raw respondents (panel E: of adults), truncated to four decimals.',
             fontsize=8.5, color='#333333')
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out + '/figure1_flow.png', dpi=300)
    fig.savefig(out + '/figure1_flow.pdf')

if __name__ == '__main__':
    draw(sys.argv[1])
