import sys, json, re
from stlib import *
from stkinds import KINDS
FILE_DUR = {'A': 512.5, 'B': 490.1, 'C': 470.7}
C = lambda *l, **k: ('cards', dict(lines=list(l), **k))
M = [  # (id, first sentence, last sentence, kind, params)
 ('v01_open', 0, 0, 'zoom', dict(s0=0, s1=1.3)),
 ('v02_atoms', 1, 3, 'zoom', dict(s0=1.3, s1=2.6)),
 ('v03_quarks', 4, 4, 'zoom', dict(s0=2.6, s1=4.2)),
 ('v04_stops', 5, 6, 'point', dict(title='THEN PHYSICS STOPS', lines=['IT STOPS.'])),
 ('v05_sm', 7, 8, 'web', dict(nodes=[('ELECTRON', CYAN), ('UP QUARK', RED), ('DOWN QUARK', GREEN), ('PHOTON', GOLD), ('GLUON', VIOLET)], title='THE STANDARD MODEL · FUNDAMENTAL PARTICLES', center='NO SMALLER PARTS')),
 ('v06_point', 9, 9, 'point', dict(title='IN THE MATHEMATICS · A POINT', lines=['NO SIZE', 'NO PARTS'])),
 ('v07_lhc', 10, 10, 'ladder', dict(mode='size', title='NOTHING FOUND INSIDE THEM', reveal=3, foot='THE HIGHEST ENERGY COLLISIONS AT THE LHC')),
 ('v08_gravity', 11, 13, 'sing', dict()),
 ('v09_biggest', 14, 15, 'cards', dict(lines=['THE BIGGEST UNFINISHED', 'PROJECT IN PHYSICS'], bg='grid', cols=[WHITE, GOLD])),
 ('v10_question', 16, 16, 'dotloop', dict()),
 ('v11_notes', 17, 18, 'two', dict(title='DIFFERENT NOTES · SAME THING?', sub='ONE THING · DIFFERENT NOTES')),
 ('v12_proposal', 19, 20, 'cards', dict(lines=['STRING THEORY'], bg='string', sizes=[96])),
 ('v13_honest', 21, 22, 'cards', dict(lines=['A SERIOUS BRANCH OF THEORETICAL PHYSICS', 'NOT AN EXPERIMENTALLY ESTABLISHED DESCRIPTION OF NATURE'], sizes=[38, 32], cols=[WHITE, RED], bg='none', gap=90)),
 ('v14_noseen', 23, 24, 'cards', dict(lines=['NO ONE HAS EVER SEEN A STRING', 'NO EXPERIMENT HAS CONFIRMED THEM'], sizes=[46, 38], cols=[WHITE, RED], bg='dots', gap=90)),
 ('v15_gap', 25, 26, 'gap', dict(sub='A STUBBORN GAP')),
 ('v16_lives', 27, 29, 'gap', dict(sub='THIS DOCUMENTARY LIVES INSIDE THAT GAP')),
 ('v17_pillars', 30, 30, 'pillars', dict()),
 ('v18_qm', 31, 32, 'qm', dict()),
 ('v19_forces', 33, 37, 'forces', dict()),
 ('v20_gr', 38, 40, 'gr', dict(title='GENERAL RELATIVITY · EINSTEIN · 1915', sub='GRAVITY IS THE SHAPE OF SPACETIME')),
 ('v21_curve', 41, 41, 'gr', dict(title='MASS AND ENERGY TELL SPACETIME HOW TO CURVE', sub='CURVED SPACETIME TELLS EVERYTHING HOW TO MOVE')),
 ('v22_ligo', 42, 42, 'waves', dict(real='merger')),
 ('v23_eht', 43, 43, 'cards', dict(lines=['THE SHADOW OF THE BLACK HOLE', 'IN MESSIER 87 · 2019'], sizes=[44, 34], cols=[WHITE, GOLD], bg='none', real='m87')),
 ('v24_triumph', 44, 47, 'ratio', dict()),
 ('v25_both', 48, 50, 'sing', dict()),
 ('v26_qg', 51, 52, 'cards', dict(lines=['QUANTUM GRAVITY', 'NOT COMPLETE · NOT CONFIRMED'], sizes=[64, 36], cols=[WHITE, RED], bg='grid', gap=100)),
 ('v27_quantize', 53, 55, 'exchange', dict()),
 ('v28_blowup', 56, 57, 'blowup', dict()),
 ('v29_renorm', 58, 61, 'renorm', dict(end=True)),
 ('v30_pic', 62, 63, 'vertex', dict()),
 ('v31_energy', 64, 65, 'well', dict()),
 ('v32_planck', 66, 67, 'ladder', dict(mode='size', title='THE PLANCK LENGTH', reveal=4, foot='A THEORY BUILT FROM DIMENSIONLESS POINTS HAS NO WAY TO COPE')),
 ('v33_others', 68, 70, 'others', dict()),
 ('v34_notbegin', 71, 72, 'cards', dict(lines=['IT BEGAN AS A FAILED THEORY', 'OF THE STRONG FORCE'], sizes=[52, 52], cols=[WHITE, GOLD], bg='dots', gap=80)),
 ('v35_veneziano', 73, 74, 'amp', dict()),
 ('v36_strings', 75, 77, 'morph', dict()),
 ('v37_qcd', 78, 78, 'cards', dict(lines=['QUANTUM CHROMODYNAMICS', 'A BETTER THEORY OF THE STRONG FORCE'], sizes=[48, 30], cols=[WHITE, GREY], bg='dots', gap=70)),
 ('v38_spin2', 79, 80, 'quad', dict()),
 ('v39_1974', 81, 83, 'timeline', dict(year='1974', lines=['SCHWARZ · SCHERK · YONEYA', 'A MASSLESS PARTICLE WITH SPIN TWO', 'THE PROPERTIES EXPECTED OF THE GRAVITON'], bg='none', s=34)),
 ('v40_proposal', 84, 85, 'dotstring', dict()),
 ('v41_loops', 86, 87, 'dotstring', dict(title='CLOSED LOOPS · OPEN STRINGS')),
 ('v42_small', 88, 88, 'ladder_string', dict()),
 ('v43_vibration', 89, 90, 'vib', dict(modes=[1, 2, 3, 4], labels=['NOTE 1', 'NOTE 2', 'NOTE 3', 'NOTE 4'], title='THE KEY IDEA IS VIBRATION', sub='EACH PATTERN · A DIFFERENT NOTE')),
 ('v44_fund', 91, 91, 'vib', dict(modes=[1, 2, 3], labels=['MASS', 'CHARGE', 'SPIN'], title='EACH PATTERN · DIFFERENT PARTICLE PROPERTIES')),
 ('v45_species', 92, 93, 'two', dict(title='TWO VIBRATIONS OF THE SAME KIND OF STRING', sub='NOT TWO SPECIES')),
 ('v46_guitar', 94, 95, 'guitar', dict()),
 ('v47_basic', 96, 98, 'tension', dict()),
 ('v48_lowest', 99, 100, 'spectrum', dict(title='THE LOWEST PATTERNS · THE PARTICLES WE KNOW')),
 ('v49_heavy', 101, 103, 'spectrum', dict(title='THE HIGHER PATTERNS · ENORMOUSLY HEAVY', heavy=True)),
 ('v50_open', 104, 104, 'brane', dict()),
 ('v51_closed', 105, 106, 'quad', dict(title='CLOSED LOOPS · THE UNEXPECTED GUEST', sub='A MASSLESS PARTICLE WITH SPIN TWO')),
 ('v52_graviton', 107, 108, 'eq', dict()),
 ('v53_finds', 109, 111, 'cards', dict(lines=['NOT PUT IN BY HAND', 'FOUND'], sizes=[56, 90], cols=[WHITE, GOLD], bg='loop', gap=110)),
 ('v54_second', 112, 113, 'vertex', dict()),
 ('v55_ws', 114, 115, 'worldsheet', dict()),
 ('v56_careful', 116, 118, 'cards', dict(lines=['A FEATURE OF THE MATHEMATICS', 'NOT A DETECTION'], sizes=[46, 62], cols=[WHITE, RED], bg='string', gap=100)),
 ('v57_nodetect', 119, 119, 'cards', dict(lines=['NO GRAVITON HAS EVER', 'BEEN OBSERVED'], sizes=[56, 56], cols=[WHITE, RED], bg='none', gap=80)),
 ('v58_possible', 120, 121, 'web', dict(nodes=[('GRAVITY', CYAN), ('THE OTHER FORCES', GREEN), ('QUANTUM MECHANICS', VIOLET), ('SPACETIME GEOMETRY', RED)], title='NOT PROOF · A POSSIBILITY', center='ONE UNDERLYING OBJECT', merge=True)),
 ('v59_price', 122, 123, 'cards', dict(lines=['THE MATHEMATICS CAME WITH A PRICE'], sizes=[56], cols=[GOLD], bg='cy')),
 ('v60_1984', 124, 127, 'timeline', dict(year='1984', lines=['GREEN · SCHWARZ', 'A DEEP INCONSISTENCY CANCELS OUT', 'TEN DIMENSIONS · ONE OF TIME · NINE OF SPACE'], bg='cy', s=34, cols=[WHITE, WHITE, GOLD])),
 ('v61_1995', 128, 129, 'web', dict(nodes=[('TYPE I', CYAN), ('TYPE IIA', GREEN), ('TYPE IIB', VIOLET), ('HETEROTIC SO(32)', RED), ('HETEROTIC E8×E8', GOLD)], title='1995 · WITTEN · DUALITIES · M-THEORY · ELEVEN DIMENSIONS', center='M-THEORY', merge=True)),
 ('v62_where', 130, 131, 'dims', dict(title='WE EXPERIENCE THREE DIMENSIONS OF SPACE · WHERE ARE THE REST?')),
 ('v63_dim', 132, 132, 'dims', dict()),
 ('v64_cable', 133, 135, 'cable', dict()),
 ('v65_ant', 136, 139, 'ant', dict()),
 ('v66_compact', 140, 142, 'compact', dict()),
 ('v67_limits', 143, 145, 'cards', dict(lines=['AN ANALOGY · NOT A DEMONSTRATION', 'HIDDEN DIMENSIONS WOULD NOT SIT INSIDE ANYTHING'], sizes=[44, 30], cols=[WHITE, GOLD], bg='none', gap=90)),
 ('v68_cy', 146, 147, 'cy', dict()),
 ('v69_trumpet', 148, 149, 'trumpet', dict()),
 ('v70_family', 150, 152, 'family', dict()),
 ('v71_test', 153, 153, 'cards', dict(lines=['CAN WE TEST ANY OF THIS?'], sizes=[64], cols=[WHITE], bg='dots')),
 ('v72_large', 154, 155, 'forcedev', dict()),
 ('v73_lab', 156, 156, 'lab', dict()),
 ('v74_lhc', 157, 157, 'lhcring', dict()),
 ('v75_ruleout', 158, 160, 'search', dict()),
 ('v76_why', 161, 161, 'cards', dict(lines=['WHY IS IT STILL UNCONFIRMED?'], sizes=[60], cols=[GOLD], bg='string')),
 ('v77_scale', 162, 164, 'ladder', dict(mode='energy', title='THE PLANCK ENERGY')),
 ('v78_susy', 165, 167, 'sparticles', dict()),
 ('v79_cosmic', 168, 169, 'sky', dict()),
 ('v80_cmb', 170, 171, 'sky', dict(cmb=True)),
 ('v81_deeper', 172, 174, 'cards', dict(lines=['A DEEPER DIFFICULTY', 'NOT ONE ANSWER · AN ENORMOUS NUMBER'], sizes=[56, 34], cols=[WHITE, GOLD], bg='cy', gap=100)),
 ('v82_shapes', 175, 175, 'shapes', dict()),
 ('v83_landscape', 176, 178, 'land', dict(num=True, title='THE STRING LANDSCAPE')),
 ('v84_one', 179, 180, 'land', dict(title='ONE THEORY · A VAST SET OF SOLUTIONS', sub='HOW DO YOU TEST IT AGAINST OURS?')),
 ('v85_critics', 181, 183, 'cols2', dict()),
 ('v86_three', 184, 184, 'cards', dict(lines=['THREE DIFFERENT QUESTIONS'], sizes=[64], cols=[WHITE], bg='none')),
 ('v87_q1', 185, 186, 'checks', dict(which=[0])),
 ('v88_q2', 187, 189, 'checks', dict(which=[1])),
 ('v89_q3', 190, 192, 'checks', dict(which=[2])),
 ('v90_notinter', 193, 198, 'balance', dict()),
 ('v91_bh', 199, 200, 'bh', dict(title='STRING THEORY AND BLACK HOLES', sub='ALREADY CHANGED HOW PHYSICISTS THINK')),
 ('v92_entropy', 201, 201, 'entropy', dict()),
 ('v93_micro', 202, 204, 'micro', dict()),
 ('v94_sv', 205, 207, 'count', dict()),
 ('v95_cousins', 208, 209, 'cards', dict(lines=['NOT THE BLACK HOLES OF THE REAL SKY', 'CAREFULLY CHOSEN MATHEMATICAL COUSINS'], sizes=[40, 34], cols=[WHITE, GOLD], bg='none', gap=90)),
 ('v96_holo', 210, 212, 'region', dict()),
 ('v97_ads', 213, 214, 'ads', dict()),
 ('v98_dict', 215, 218, 'dict', dict()),
 ('v99_hologram', 219, 222, 'holo', dict()),
 ('v100_notours', 223, 226, 'dsads', dict()),
 ('v101_emerge', 227, 228, 'emerge', dict()),
 ('v102_suppose', 229, 230, 'cards', dict(lines=['SUPPOSE NATURE DID CHOOSE STRINGS', 'WHAT WOULD IT MEAN?'], sizes=[50, 40], cols=[WHITE, GOLD], bg='loop', gap=90)),
 ('v103_states', 231, 232, 'two', dict(a='ELECTRON', b='PHOTON', title='STATES OF ONE THING', sub='DIFFERENCES IN VIBRATION')),
 ('v104_geom', 233, 233, 'family', dict()),
 ('v105_emergent', 234, 234, 'cards', dict(lines=['SPACETIME NOT FUNDAMENTAL', 'BUT EMERGENT'], sizes=[48, 48], cols=[WHITE, GOLD], bg='dots', gap=80)),
 ('v106_infinities', 235, 235, 'sing', dict()),
 ('v107_horizon', 236, 238, 'tiers', dict()),
 ('v108_return', 239, 241, 'return', dict()),
 ('v109_two', 242, 244, 'split', dict()),
 ('v110_matters', 245, 246, 'matters', dict()),
 ('v111_math', 247, 248, 'nowhat', dict()),
 ('v112_window', 249, 250, 'windows', dict()),
 ('v113_dot_note', 251, 253, 'final', dict()),
 ('v114_ask', 254, 255, 'final', dict()),
]
DUR_LIST = [4.531,15.373,7.267,4.575,11.03,7.122,10.784,16.936,11.03,4.922,12.391,9.467,12.203,6.92,17.081,20.252,3.749,7.904,23.074,13.81,7.079,8.642,11.957,18.341,14.982,11.219,11.465,8.295,18.732,9.858,7.904,17.081,16.734,10.046,12.985,8.917,7.469,9.076,19.079,11.421,5.559,13.911,8.685,12.203,10.437,9.284,17.516,7.685,23.913,7.24,7.877,16.879,11.12,9.684,17.072,9.328,9.239,17.916,6.278,25.201,15.873,5.879,4.842,14.17,19.16,21.514,11.727,13.874,8.084,21.114,2.843,10.483,9.239,6.841,16.717,7.833,23.513,14.925,8.484,9.876,12.926,11.238,22.713,15.251,32.246,5.823,11.498,15.931,9.547,27.192,10.256,12.812,21.473,20.881,13.049,24.709,24.029,15.931,19.33,15.739,22.625,7.064,12.857,6.827,9.62,9.221,12.695,8.512,16.685,18.236,7.271,25.019,10.906,7.463]
IDS = [m[0] for m in M]
FILE_OF = {sid: ('A' if i < 45 else 'B' if i < 83 else 'C') for i, sid in enumerate(IDS)}
DURV = dict(zip(IDS, DUR_LIST))
SEQV = [(sid, '', 0) for sid in IDS]
STARTV = {}; _acc = 0.0
for sid in IDS:
    STARTV[sid] = _acc; _acc += DURV[sid]
TOTALV = _acc
KP = {sid: (kind, P) for sid, i0, i1, kind, P in M}
def make(sid):
    kind, P = KP[sid]; fn = KINDS[kind]
    TAGLESS = ('cards', 'timeline', 'checks', 'tiers', 'cols2', 'matters', 'nowhat', 'windows', 'ladder', 'gap', 'final', 'balance', 'split')
    def f(t, T, tg, cap):
        u = t / T
        cv = Cv(0.6, 0.55)
        its = fn(cv, t, T, u, P)
        fade = 1.0
        if sid == 'v01_open': fade = float(np.clip(0.2 + 0.8 * sm(A(u, 0, 0.5)), 0, 1))
        return frame(cv, its, cap=cap, tag=None if kind in TAGLESS else 'ILLUSTRATION', fade=fade)
    return f
FUNCSV = {sid: make(sid) for sid in IDS}
