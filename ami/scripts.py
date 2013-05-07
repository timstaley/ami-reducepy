standard_reduction = \
r"""
flag all
flag int \
subtract modmeans \
subtract zeros \
subtract means \
update pcal \
fft \
frotate forward y n \
flag amp field yes no 1 \
apply rain \
flag amp field no 0.432 1 \
flag amp field no 0.1 20 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 50 \
show flagging no yes \
flag bad cal all all all \
scan dat cal yes \
scan dat field yes \
show flagging no yes \
"""

