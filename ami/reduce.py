"""
Provides a pythonic wrapper about the AMI reduce pipeline.

(Uses an instance of the interactive `reduce` program driven via pexpect.)

NB It may be possible to do this more directly by writing python wrappers about
the underlying fortran code, but this is a reasonably good quick solution.
"""

## NB I have adopted the convention that each function leaves the 
## spawned instance in a 'ready to receive' state.
## So the last call should usually be to 'expect(blah)'

## Calls to ami often finish with a '\' (backslash), 
# which means 'use defaults'. 
# Unfortunately, this is also the python string escape character.
# So I often use raw strings to make it clear what is being sent. 

import os
import pexpect
from environments import ami_env
from collections import defaultdict
import logging
import astropysics.coords

class RawFileKeys:
    comment = 'comment'
    target_pointing = 'pointing'

class Reduce(object):
    """Class to provide an interface to AMI-reduce package"""
    prompt = 'AMI-reduce>'

    def __init__(self,
                 ami_rootdir,
                 array='LA',
#                 working_dir=None
                 ):
#        if working_dir is None:
#            working_dir = os.getcwd()

        self.child = pexpect.spawn('tcsh -c reduce',
#                          cwd=working_dir,
                          env=ami_env(ami_rootdir))
        self.child.expect(self.prompt)
        self.files = dict()
        #Ready for action.
        if array=='LA':
            self.switch_to_large_array()
        self.update_files()

    def switch_to_large_array(self):
        """NB resets file list"""
        p = self.child
        p.sendline('set def la')
        self.files = dict()
        p.expect(self.prompt)

    def update_files(self):
        p = self.child
        p.sendline(r'list files \ ')
#        p.sendline(r'list comment \ ')
        p.expect(self.prompt)
        #First line in 'before' is command.
        #second line is blank
        #last 4 lines are blanks and 'total obs time'
        file_lines = p.before.split('\n')[2:-4]
        for l in file_lines:
            l = l.strip('\r').strip(' ')
            cols = l.split(' ', 1)
            fname = cols[0]
            if fname not in self.files:
                self.files[fname] = defaultdict(lambda : None)

        p.sendline(r'list comment \ ')
#        p.sendline(r'list comment \ ')
        p.expect(self.prompt)
        file_lines = p.before.split('\n')[2:]
        for l in file_lines:
            l = l.strip('\r').strip(' ')
            cols = l.split(' ', 1)
            fname = cols[0]
            if fname in self.files:
                if len(cols) > 1:
                    self.files[fname][RawFileKeys.comment] = cols[1]

    def get_obs_details(self, filename):
        p = self.child
        p.sendline(r'list observation {0} \ '.format(filename))
        p.expect(self.prompt)
        obs_lines = p.before.split('\n')[2:]
        for line in obs_lines:
            if 'Tracking' in line:
                if not 'J2000' in line:
                    logging.warn("Obs pointing may not be in J2000 format:" 
                         + filename +", co-ord conversion may be incorrect.")

                coords_str = line[len('Tracking    : '):]
                coords_str = coords_str.strip()
                coords_str = coords_str[:-len('J2000')].strip()
#                print "COSTR", coords_str
                if '-' in coords_str:
                    ra_dec = coords_str.split('  ')
                else:
                    ra_dec = coords_str.split('   ')
                ra = astropysics.coords.AngularCoordinate(
                      ra_dec[0].replace(' ', ':'), sghms=True)
                dec = astropysics.coords.AngularCoordinate(
                      ra_dec[1].replace(' ', ':'), sghms=False)
                pointing = astropysics.coords.FK5Coordinates(ra, dec)
                self.files[filename][RawFileKeys.target_pointing] = pointing
        return self.files[filename]

    def group_pointings(self, pointing_tolerance_in_degrees=0.5):
        """
        Attempt to group together datasets by inspecting pointing target.
        
        Returns:         
        Nested dict with structure:
        { FIRST_FILENAME_IN_GROUP:
            {
            files: [ <list of files>],
            pointing: <string representation of group pointing> 
            },
            ...
        }
        """        
        group_pointings = defaultdict(list) #Dict, pointing --> Files
        tolerance_deg = pointing_tolerance_in_degrees
        
        for f in self.files:
            if RawFileKeys.target_pointing not in self.files[f]:
                self.get_obs_details(f)

        for f, info in self.files.iteritems():
            pointing = info[RawFileKeys.target_pointing]
            matched = False
            for p0 in group_pointings.iterkeys():
                if (pointing - p0).degrees < tolerance_deg:
                    group_pointings[p0].append(f)
                    matched = True
#                    print "MATCH", f
                    print group_pointings[p0]

            if matched is False:
                group_pointings[pointing].append(f)
#                print "NEW GROUP", f
                print group_pointings[pointing]
        
        # Now we have a bunch of dicts, that look like:
        # { FK5Coordinates --> [list of filenames] } 
        # Unfortunately, FK5 class doesn't serialize well - so we massage 
        # the data structures a bit next:
        
        #Convert keys to strings:
        sgroups = { str(k.ra.d) + ' ' + str(k.dec.d) : {'files':v}
                    for k, v in group_pointings.iteritems()}
        
        #Generally the filenames are more recognisable than plain co-ords
        #So we rename each group by the first (alphabetical) filename:
        named_groups = {}
        for k, grp in sgroups.iteritems():
            name = sorted(grp['files'])[0].split('-')[0]
            named_groups[name] = {}
            named_groups[name]['files'] = grp['files']
            named_groups[name]['pointing'] = k
        return named_groups








