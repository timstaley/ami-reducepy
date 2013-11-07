standard_reduction = \
r"""
version
flag all
flag int \
flag amp field no \
flag data \
update pcal \
subtract modmeans \
subtract zeros \
subtract means \
fft \
frotate forward y n \
apply rain \
flag amp field no 0.19 1 yes \
flag amp field no 0.03 30 yes \
flag amp field yes no 60 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 20 \
show flagging no yes \
flag bad cal \
flag amp field no 0.05 1 yes \
smooth 10 \
flag amp field no 0.015 1 yes \
scan dat cal yes \
scan dat field yes \
show flagging no yes \
"""

no_calibrator_reduction = \
r"""
version
flag all
flag int \
flag amp no \
flag data \
update pcal \
subtract modmeans \
subtract zeros \
subtract means \
fft \
frotate forward y n \
apply rain \
flag amp  no 0.19 1 yes \
flag amp  no 0.03 30 yes \
flag amp  yes no 60 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 20 \
show flagging no yes \
flag bad \
flag amp no 0.05 1 yes \
smooth 10 \
flag amp  no 0.015 1 yes \
scan dat yes \
show flagging no yes \
"""

