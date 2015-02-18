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
flag amp field no 0.95 1 yes \
flag amp field no 0.15 30 yes \
flag amp field yes no 60 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 20 \
show flagging no yes \
flag bad calibrator \
flag amp field no 0.25 1 yes \
smooth 10 \
flag amp field no 0.075 1 yes \
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
flag amp  no 0.95 1 yes \
flag amp  no 0.15 30 yes \
flag amp  yes no 60 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 20 \
show flagging no yes \
flag bad \
flag amp no 0.25 1 yes \
smooth 10 \
flag amp  no 0.075 1 yes \
scan dat yes \
show flagging no yes \
"""
# NB second arg refers to 'update entry in observation database'
# I currently know of no use cases for that to be 'yes'.
write_command=\
r'write fits {if_severely_flagged} no {baselines} {channels} {sample_range} {output_paths} \  '

write_command_defaults = {'if_severely_flagged':'yes',
                          'baselines':'all',
                          'channels':'3-8',
                          'sample_range':'all'}