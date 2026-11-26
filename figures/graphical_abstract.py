"""Graphical abstract for P9 (JBI requires one at submission). Numbers are copied from the manuscript abstract.
Usage: python -I -X utf8 graphical_abstract.py <out_dir>"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK, MUTED, LINE, ACCENT, FILL = '#1a1a1a', '#555555', '#444444', '#1f5f99', '#eef3f8'


def box(ax, x, y, w, h, fc='#ffffff', ec=LINE, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.004,rounding_size=0.012',
                                fc=fc, ec=ec, lw=lw))


def arrow(ax, x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='-|>', color=LINE, lw=1.4))


def draw(out):
    fig = plt.figure(figsize=(13.3, 5.3))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.02, 0.94, 'Rebuild-and-match: tracing how survey-derived ML benchmarks were built',
            fontsize=15, fontweight='bold', color=INK, va='center')

    # inputs
    box(ax, 0.02, 0.56, 0.2, 0.25)
    ax.text(0.12, 0.685, 'Raw public survey file\nBRFSS 2015, 2020,\n2021, 2022; NHFS 2009-10',
            ha='center', va='center', fontsize=10.5, color=INK)
    box(ax, 0.02, 0.17, 0.2, 0.25)
    ax.text(0.12, 0.295, 'Published benchmark\nUCI, Kaggle, DrivenData\n(no respondent ID)',
            ha='center', va='center', fontsize=10.5, color=INK)
    arrow(ax, 0.22, 0.685, 0.27, 0.6)
    arrow(ax, 0.22, 0.295, 0.27, 0.38)

    # method
    box(ax, 0.27, 0.12, 0.36, 0.74, fc=FILL, ec=ACCENT, lw=1.6)
    ax.text(0.45, 0.82, 'Seven steps', ha='center', va='center', fontsize=12, fontweight='bold', color=ACCENT)
    steps = ['1  Identify and hash the source file',
             '2  Write a recode rule for every column',
             '3  Rebuild all respondents, apply deletions',
             '4  Multiset match: rebuilt vs published rows',
             '5  Compare documentation with the data',
             '6  Account for exclusions, design, missing codes, time',
             '7  Test consequences under a pre-hashed rule']
    for i, s in enumerate(steps):
        ax.text(0.29, 0.75 - i * 0.075, s, fontsize=10.3, color=INK, va='center')
    ax.text(0.45, 0.165, 'Validated by a positive control, a sensitivity check\nand independently written scripts (no gold standard)',
            ha='center', va='center', fontsize=9.3, color=MUTED, style='italic')
    arrow(ax, 0.63, 0.49, 0.67, 0.49)

    # findings
    box(ax, 0.67, 0.12, 0.31, 0.74)
    ax.text(0.825, 0.82, 'Demonstration on four datasets', ha='center', va='center', fontsize=12,
            fontweight='bold', color=INK)
    finds = ['Six BRFSS file versions rebuilt exactly\n(multiset match 1.0)',
             '4,631 prediabetes respondents in class 0\nunder a "prediabetes or diabetes" label',
             'Angina item kept as a predictor:\nheart AUC 0.84 to 0.89',
             'Interview month dropped:\nflu H1N1 AUC +0.0130 to +0.0159 when restored',
             'Undocumented exclusions; design variables\nand missing-code meanings lost']
    for i, s in enumerate(finds):
        ax.text(0.69, 0.725 - i * 0.115, '•  ' + s, fontsize=9.8, color=INK, va='center', linespacing=1.15)
    ax.text(0.825, 0.165, 'Outputs: rebuild scripts, corrected data cards,\nnine-item reporting checklist',
            ha='center', va='center', fontsize=9.3, color=MUTED)
    fig.savefig(out + '/graphical_abstract.png', dpi=300)
    fig.savefig(out + '/graphical_abstract.pdf')


if __name__ == '__main__':
    draw(sys.argv[1])
