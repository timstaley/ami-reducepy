"""
Provides a pythonic wrapper about the AMI reduce pipeline.

(Uses an instance of the interactive `reduce` program driven via pexpect.)

NB It may be possible to do this more directly by writing python wrappers about
the underlying fortran code, but this is a reasonably good quick solution.
"""

# NB I have adopted the convention that each function leaves the
# spawned instance in a 'ready to receive' state.
# So the last call should usually be to 'expect(blah)'

# Calls to ami often finish with a '\' (backslash),
# which means 'use defaults'.
# Unfortunately, this is also the python string escape character.
# So I often use raw strings to make it clear what is being sent.

import os
import shutil
import pexpect
from environments import ami_env
from collections import defaultdict, namedtuple
import logging
import astropysics.coords
import warnings
import datetime

RaDecPair = namedtuple('RaDecPair', 'ra dec')

import keys

logger = logging.getLogger(__name__)

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


class Reduce(object):
    """Class to provide an interface to AMI-reduce package"""
    prompt = 'AMI-reduce>'

    def __init__(self,
                 ami_rootdir,
                 array='LA',
                 working_dir='/tmp'
                 ):
        if len(ami_rootdir) > 16:
            warnings.warn("Long AMI root path detected - this may cause bugs!\n"
                          "It is recommended to use a short symlink instead.\n")
        if working_dir is None:
            working_dir = ami_rootdir
        if not os.access(os.path.join(ami_rootdir, 'bin', 'reduce'), os.R_OK):
            raise IOError("Cannot access ami-reduce binary at: " +
                               os.path.join(ami_rootdir, 'bin', 'reduce'))
        self.working_dir = working_dir
        self.child = pexpect.spawn('tcsh -c reduce',
                          cwd=self.working_dir,
                          env=ami_env(ami_rootdir))
        self.child.expect(self.prompt)
        # Records all known information about the fileset.
        # Each file entry is initialised to a ``defaultdict(lambda : None)``
        # So if we attempt to access an unknown file attribute we get a sensible
        # answer rather than an exception.
        self.files = dict()
        # Used for updating the relevant record in self.files, also logging:
        self.active_file = None

        if array == 'LA':
            self.switch_to_large_array()
        elif array != 'SA':
            raise ValueError("Initialisation error: Array must be 'LA' or 'SA'.")
        self.array = array
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
        # First line in 'before' is command.
        # second line is blank
        # last 4 lines are blanks and 'total obs time'
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
                    self.files[fname][keys.comment] = cols[1]

    def get_obs_details(self, filename):
        p = self.child
        p.sendline(r'list observation {0} \ '.format(filename))
        p.expect(self.prompt)
        obs_lines = p.before.split('\n')[2:]
        info = self.files[filename]

        hms_dms = Reduce._parse_coords(filename, obs_lines)
        info[keys.pointing_hms_dms] = hms_dms
        info[keys.pointing_fk5] = Reduce._convert_to_ap_FK5_coords(hms_dms)
        info[keys.calibrator] = Reduce._parse_calibrator(obs_lines)
        info.update(Reduce._parse_obs_datetime(obs_lines))
        return info

    @staticmethod
    def _parse_calibrator(obs_listing):
        for line in obs_listing:
            if 'with calibrator' in line:
                tokens = line.split()
                return tokens[-1]

    @staticmethod
    def _parse_times(line):
        """Returns (UTC time, sidereal time)"""
        tokens = line.split()
        format = '%H.%M.%S'
        ut = datetime.datetime.strptime(tokens[3], format).time()
        st = tokens[5].replace('.', ':')
        mjd = float(tokens[-2])
        return ut, st, mjd

    @staticmethod
    def _parse_obs_datetime(obs_listing):
        timeinfo = {}
        for idx, line in enumerate(obs_listing):
            if 'Tracking ' in line:
                date_str = obs_listing[idx + 1].split()[-1]
                d0 = datetime.datetime.strptime(date_str, '%d/%m/%Y')
            if 'Start time' in line:
                ut0, st0, mjd0 = Reduce._parse_times(line)
            if 'Stop time' in line:
                ut1, st1, mjd1 = Reduce._parse_times(line)

        timeinfo[keys.time_st] = (st0, st1)
        timeinfo[keys.time_mjd] = (mjd0, mjd1)
        d0 = datetime.datetime.combine(d0, ut0)
        d1 = datetime.datetime.combine(d0, ut1)
        if d1 < d0:  # Crossed midnight
            d1 = d1 + datetime.timedelta(days=1)
        timeinfo[keys.time_ut] = (d0, d1)
        duration = d1 - d0
        timeinfo[keys.duration] = duration.total_seconds() / 3600.
        return timeinfo


    @staticmethod
    def _parse_coords(filename, obs_listing):
        for line in obs_listing:
            if 'Tracking' in line:
                if not 'J2000' in line:
                    logging.warn("Obs pointing may not be in J2000 format:"
                         + filename + ", co-ord conversion may be incorrect.")

                coords_str = line[len('Tracking    : '):]
                coords_str = coords_str.strip()
                coords_str = coords_str[:-len('J2000')].strip()
                # Two cases depending whether declination is +ve or -ve:
                if '-' in coords_str:
                    ra_dec = coords_str.split('  ')
                else:
                    ra_dec = coords_str.split('   ')
                pointing = RaDecPair(ra_dec[0].replace(' ', ':'),
                                     ra_dec[1].replace(' ', ':'))
                return pointing
        raise ValueError("Parsing error for file: %s, coords not found"
                            % filename)

    @staticmethod
    def _convert_to_ap_FK5_coords(hms_dms_pair):
        """
        Args:

          - a tuple-pair of ('h:m:s','d:m:s') strings representing ra/dec
        """
        ra = astropysics.coords.AngularCoordinate(
              hms_dms_pair.ra, sghms=True)
        dec = astropysics.coords.AngularCoordinate(
              hms_dms_pair.dec, sghms=False)
        return astropysics.coords.FK5Coordinates(ra, dec)


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
        group_pointings = defaultdict(list)  # Dict, pointing --> Files
        tolerance_deg = pointing_tolerance_in_degrees

        for filename, info in self.files.iteritems():
            if info[keys.pointing_fk5] is None:
                self.get_obs_details(filename)

        for f, info in self.files.iteritems():
            file_pointing = info[keys.pointing_fk5]
            matched = False
            for gp in group_pointings.iterkeys():
                if (gp - file_pointing).degrees < tolerance_deg:
                    group_pointings[gp].append(f)
                    matched = True
#                    print "MATCH", f
#                    print group_pointings[gp]

            if matched is False:
                group_pointings[file_pointing].append(f)
#                print "NEW GROUP", f
#                print group_pointings[file_pointing]

        # Generally the filenames / target names are more recognisable than
        # plain co-ords
        # So we rename each group by the first (alphabetical) filename,
        # Which should be a target name.
        # (After splitting off the date suffix.)
        named_groups = {}
        for p, files in group_pointings.iteritems():
            name = sorted(files)[0].split('-')[0]
            named_groups[name] = {}
            named_groups[name][keys.files] = files
            # Also convert FK5coordinates into something JSON friendly:
            named_groups[name][keys.pointing_fk5] = RaDecPair(p.ra.d, p.dec.d)

        for grpname, grp_info in named_groups.iteritems():
            for f in grp_info[keys.files]:
                self.files[f][keys.group_name] = grpname
                fk5 = self.files[f][keys.pointing_fk5]
                self.files[f][keys.pointing_fk5] = RaDecPair(fk5.ra.d, fk5.dec.d)
        return named_groups

    def _setup_file_loggers(self, filename, file_logdir):
#        if (self.logger is not None) or (file_logdir is not None):
        target = os.path.splitext(filename)[0]
        # It does no harm to set up the loggers,
        # irrespective of whether we write them to file-
        # The calling code could potentially grab them for other uses.
        self.file_log = logging.getLogger('.'.join((logger.name, target)))
        self.file_log.propagate = False
        self.file_log.setLevel(logging.DEBUG)
        self.file_cmd_log = logging.getLogger(
                              '.'.join((logger.name, 'commands', target)))
        self.file_cmd_log.propagate = False
        self.file_cmd_log.setLevel(logging.DEBUG)

        if file_logdir is not None:
            ensure_dir(file_logdir)
            fh = logging.FileHandler(
                         os.path.join(file_logdir, target + '.ami.log'),
                         mode='w')
            self.file_log.addHandler(fh)

            fh = logging.FileHandler(
                         os.path.join(file_logdir, target + '.ami.commands'),
                         mode='w')
            self.file_cmd_log.addHandler(fh)
        else:
            self.file_log.addHandler(logging.NullHandler())
            self.file_cmd_log.addHandler(logging.NullHandler())

    def run_command(self, command):
        self.file_cmd_log.debug(command)
        self.child.sendline(command)
        self.child.expect(self.prompt)
        self.file_log.debug('%s%s', self.prompt, self.child.before)
        self._parse_command_output(command, self.child.before.split('\n'))
        return self.child.before.split('\n')

    def _parse_command_output(self, command, output_lines):
#        try:
        file_info = self.files[self.active_file]
        if 'apply rain' in command:
            rain_amp_corr = self._parse_rain_results(output_lines)
            file_info[keys.rain] = rain_amp_corr
#            logger.info("Rain mean amplitude correction factor: %s",
#                             rain_amp_corr)
        if 'flag' in command:
            flagging = self._parse_flagging_results(output_lines)
            file_info[keys.flagged_max] = max(flagging,
                                                  file_info[keys.flagged_max])

        if 'reweight' in command:
            est_noise = self._parse_reweight_results(output_lines)
            file_info[keys.est_noise_jy] = est_noise
#            logger.info("Estimated noise: %s mJy", est_noise * 1000.0)
                # self.files[self.active_file][keys.flagging_max]

#        except Exception as e:
#            raise ValueError("Problem parsing command output for file: %s,",
#                             "command: %s, error message:\n%s"
#                             ,self.active_file, command, e.msg)


    def _parse_rain_results(self, output_lines):
        for line in output_lines:
            if "Mean amplitude correction factor" in line:
                return float(line.strip().split()[-1])
        raise ValueError("Parsing error, could not find rain modulation.")

    def _parse_flagging_results(self, output_lines):
        for line in output_lines:
            if "samples flagged" in line:
                if "Total of" in line:
                    tokens = line.strip().split()
                    for t in tokens:
                        if '%' in t:
                            return float(t.strip('%'))

    def _parse_reweight_results(self, output_lines):
        for line in output_lines:
            if "estimated noise" in line:
                tokens = line.strip().split()
                return float(tokens[-2])
        raise ValueError("Parsing error, could not find noise estimate.")

    def run_script(self, script_string):
        """Takes a script of commands, one command per line"""
        command_list = script_string.split('\n')
        for command in command_list:
            self.run_command(command)


    def set_active_file(self, filename, file_logdir=None):
        filename = filename.strip()  # Ensure no stray whitespace
        self.active_file = filename
        self._setup_file_loggers(filename, file_logdir)
        self.run_command(r'file %s \ ' % filename)
        self.get_obs_details(filename)
        logger.debug('Active file: %s', filename)


    def write_files(self, rawfile, output_dir):
        """Writes out UVFITs files.

        NB: You should use this rather than performing writes manually:
        ``reduce`` cannot handle long file paths,
        so rather than cripple the scripting functionality,
        this function hacks around the limitations.
        Kludgey but effective.
        """
        ensure_dir(output_dir)
        tgt_name = os.path.splitext(rawfile)[0]
        tgt_path = os.path.join(output_dir, tgt_name + '.fits')
        if self.files[rawfile][keys.calibrator] is not None:
            cal_basename = (self.files[rawfile][keys.calibrator] + '-' +
                            tgt_name.split('-')[-1] + 'C.fits')
            cal_path = os.path.join(output_dir, cal_basename)
        else:
            cal_path=None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tgt_temp = os.tempnam(self.working_dir, 'ami_') + '.fits'
            cal_temp = os.tempnam(self.working_dir, 'ami_') + '.fits'

        if cal_path is None:
            output_paths_string = os.path.basename(tgt_temp)
        else:
            output_paths_string = " ".join((os.path.basename(tgt_temp),
                                            os.path.basename(cal_temp)))
        logger.debug("Writing to temp files %s" % output_paths_string)
        self.run_command(r'write fits yes no all 3-8 all %s \ ' %
                         output_paths_string)

        logger.debug("Renaming tempfile %s -> %s", tgt_temp, tgt_path)
        shutil.move(tgt_temp, tgt_path)
        info = self.files[self.active_file]
        info[keys.target_uvfits] = os.path.abspath(tgt_path)
        if cal_path is not None:
            logger.debug("Renaming tempfile %s -> %s", cal_temp, cal_path)
            shutil.move(cal_temp, cal_path)
            info[keys.cal_uvfits] = os.path.abspath(cal_path)
        logger.debug("Wrote target, calib. UVFITs to:\n\t%s\n\t%s",
                         tgt_path, cal_path)

    def update_flagging_info(self):
        lines = self.run_command(r'show flagging no yes \ ')
        final_flagging = self._parse_flagging_results(lines)
        self.files[self.active_file][keys.flagged_final] = final_flagging
#        logger.info("Final flagging estimate: %s%%", final_flagging)
