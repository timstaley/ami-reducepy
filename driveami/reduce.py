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
from __future__ import absolute_import, print_function
import os
import shutil
import pexpect
from collections import defaultdict, namedtuple
import logging
from astropy.coordinates import SkyCoord, Longitude, Latitude
import astropy.units
import warnings
import datetime

from numpy import median

from driveami.environments import init_ami_env
import driveami.scripts as scripts

RaDecPair = namedtuple('RaDecPair', 'ra dec')

import driveami.keys as keys

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
                 working_dir='/tmp',
                 additional_env_variables=None,
                 timeout=120,
                 ):
        """
        Spawn an AMI-REDUCE instance.

        This will automatically update the list of available files,
        but will not load the full info for each file, as this is time consuming.
        (See :py:func:`load_obs_info`.)

        """
        if len(ami_rootdir) > 16:
            warnings.warn("Long AMI root path detected - this may cause bugs!\n"
                          "It is recommended to use a short symlink instead.\n")
        if working_dir is None:
            working_dir = ami_rootdir
        if not os.access(os.path.join(ami_rootdir, 'bin', 'reduce'), os.R_OK):
            raise IOError("Cannot access ami-reduce binary at: " +
                               os.path.join(ami_rootdir, 'bin', 'reduce'))
        self.working_dir = working_dir
        ami_env = init_ami_env(ami_rootdir)
        if additional_env_variables is not None:
            ami_env.update(additional_env_variables)
        self.child = pexpect.spawn('tcsh -c reduce',
                          cwd=self.working_dir,
                          env=ami_env,
                          timeout=timeout)
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

        self.file_log = None
        self.file_cmd_log = None

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
                self.files[fname] = {}

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

    def get_obs_details(self, filename, incomplete=False):
        p = self.child
        if not incomplete:
            p.sendline(r'list observation {0} \ '.format(filename))
            p.expect(self.prompt)
        else: #incomplete observation, load fully to check end-timetamp:
            if not self.active_file==filename:
                self.set_active_file(filename)
            p.sendline(r'show observation \ ')
            p.expect(self.prompt)
        obs_lines = p.before.decode('ascii').split('\n')[2:]
        info = self.files[filename]
        if incomplete:
            warnings_dict = info.setdefault(keys.warnings, {})
            warnings_dict[keys.warning_incomplete]=True

        info[keys.raw_obs_text] = p.before
        hms_dms = Reduce._parse_coords(filename, obs_lines)
        info[keys.pointing_hms_dms] = hms_dms
        info[keys.pointing_degrees] = Reduce._convert_to_decimal_degrees(hms_dms)
        info[keys.calibrator] = Reduce._parse_calibrator(obs_lines)
        info[keys.field] = Reduce._parse_field(obs_lines)
        info.update(Reduce._parse_obs_datetime(obs_lines))
        if (info[keys.duration]==0.0 and not incomplete):
            logger.warn(
                "Incomplete obs ({}), pulling timestamps from filedata".format(
                    filename))
            self.get_obs_details(filename,incomplete=True)

        return info

    @staticmethod
    def _parse_calibrator(obs_listing):
        for line in obs_listing:
            if 'with calibrator' in line:
                tokens = line.split()
                return tokens[-1]


    @staticmethod
    def _parse_field(obs_listing):
        for line in obs_listing:
            if 'field observation' in line:
                tokens = line.split()
                return tokens[0]

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
    def _convert_to_decimal_degrees(hms_dms_pair):
        """
        Args:

          - a tuple-pair of ('h:m:s','d:m:s') strings representing ra/dec
        """
        ra = Longitude(hms_dms_pair.ra, unit = astropy.units.hourangle)
        dec = Latitude(hms_dms_pair.dec, unit = astropy.units.deg)
        return RaDecPair(ra.degree, dec.degree)


    def load_obs_info(self):
        logger.info("Loading observation information, patience...")
        self.update_files()
        for filename, info in sorted(self.files.items()):
            if info.get(keys.pointing_degrees,None) is None:
                logger.debug("Getting obs info for %s", filename)
                try:
                    self.get_obs_details(filename)
                except Exception as error:
                    logger.exception("\n"
                                 "**********************\n"
                                 "Warning! Threw an exception trying to parse "
                                 "details for %s"
                                 "***********************\n"
                                 "\n",  filename)


    def group_obs_by_target_id(self):
        """
        Group together datasets by target id.

        Where 'target id' is everything in the filename, up to the last '-'

        Returns:
        Nested dict with structure:
        { Field name:
            {
            files: [ <list of files>],
            median_pointing: <string representation of group pointing>
            },
            ...
        }
        """

        target_groups = {}

        #Set up empty lists first:
        for filename, info in self.files.iteritems():
            target_id = filename.rsplit('-',1)[0]
            target_groups[target_id]={}
            target_groups[target_id][keys.files]=[]

        #Now put the files in
        for filename, info in self.files.iteritems():
            target_id = filename.rsplit('-',1)[0]
            target_groups[target_id][keys.files].append(filename)

        for target_id in target_groups:
            ra_list, dec_list = [],[]
            for filename in target_groups[target_id][keys.files]:
                info = self.files[filename]
                obs_pointing = info.get(keys.pointing_degrees, None)
                if obs_pointing is not None:
                    ra, dec = obs_pointing.ra, obs_pointing.dec
                    ra_list.append(ra)
                    dec_list.append(dec)
            if ra_list:
                median_ra, median_dec = median(ra_list), median(dec_list)
                target_groups[target_id][keys.target_pointing_deg] = (median_ra,median_dec)

        return target_groups


    def group_target_ids_by_pointing(self,
                                 target_id_groups,
                                 pointing_tolerance_in_degrees=0.5):
        """
        Attempt to group together datasets by inspecting pointing target.

        Returns:
        Nested dict with structure:
        { TARGET_ID:
            {
            files: [ <list of files>],
            pointing: <string representation of group pointing>
            },
            ...
        }
        """

        def _find_close_targets(first_target_id, ungrouped, skycoords_cache,
                               tolerance_deg):
            """
            Grow a network graph to include all points separated by less than
            'tolerance_deg'.

            Given a starting point ('first_target_id', and a bunch of
            un-matched positions ('ungrouped'), work through checking for
            close positions. Once a new network node has been added,
            re-run to see if this puts us close enough to another point.
            """
            logger.debug("Finding observations near "+first_target_id+" ... ")
            cluster_ids = [first_target_id]

            # Take the list of positions belonging to the current group
            # Split it into three lists, to avoid modifying the list as we
            # iterate over it:
            # Cluster positions we've already scanned for matches previously
            processed = []
            # Positions we're about to scan for matches:
            process_next = [skycoords_cache[first_target_id]]
            # Newly added positions that could extend the cluster in the next
            # iteration:
            newly_included = []

            while process_next:
                for pointing1 in process_next:
                    for id2 in list(ungrouped):
                        pointing2 = skycoords_cache[id2]
                        if pointing1.separation(pointing2).degree < tolerance_deg:
                            cluster_ids.append(id2)
                            newly_included.append(pointing2)
                            ungrouped.remove(id2)
                            logger.debug("... " + id2 + " added to group.")
                # Cycle the lists before next iteration
                processed.extend(process_next)
                process_next = newly_included
                newly_included = []
            logger.debug("... {} rawfiles in group.".format(len(cluster_ids)))
            return cluster_ids


        ungrouped = set(target_id_groups.keys())
        # Cache a pre-built set of Astropy SkyCoord objects, one for each id
        # This avoids constantly rebuilding as we iterate through.
        temp_skycoords = {}
        for id in ungrouped:
            ra_dec = target_id_groups[id][keys.target_pointing_deg]
            temp_skycoords[id] =SkyCoord(ra_dec[0], ra_dec[1], unit='deg')

        pointing_groups_dict = {}

        #Now, pop off un-searched IDs and match them up, one-by-one until done
        while ungrouped:
            cluster_ids = _find_close_targets(ungrouped.pop(), ungrouped,
                                              temp_skycoords,
                                              pointing_tolerance_in_degrees)
            first_id = sorted(cluster_ids)[0]
            pointing_groups_dict[first_id] = {}
            pointing_groups_dict[first_id][keys.target_pointing_deg]=(
                target_id_groups[first_id][keys.target_pointing_deg])
            pointing_groups_dict[first_id][keys.files]=[]
            for target_id in cluster_ids:
                pointing_groups_dict[first_id][keys.files].extend(
                    target_id_groups[target_id][keys.files])

        return pointing_groups_dict


    def close_per_file_logs(self):
        """Close any logging file handlers from the last file"""
        if self.file_log is not None:
            for hdlr in self.file_log.handlers:
                if hasattr(hdlr, 'close'):
                    hdlr.close()
        if self.file_cmd_log is not None:
            for hdlr in self.file_cmd_log.handlers:
                if hasattr(hdlr, 'close'):
                    hdlr.close()

    def _setup_file_loggers(self, filename, file_logdir):
        target = os.path.splitext(filename)[0]

        self.close_per_file_logs()

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
                                          file_info.get(keys.flagged_max,None))

        if 'reweight' in command:
            est_noise = self._parse_reweight_results(output_lines)
            file_info[keys.est_noise_jy] = est_noise
#            logger.info("Estimated noise: %s mJy", est_noise * 1000.0)
                # self.files[self.active_file][keys.flagging_max]

        if 'cal inter' in command:
            avail, daysep = self._parse_cal_inter_results(output_lines)
            file_info[keys.archive_cal_available]=avail
            file_info[keys.archive_cal_days_apart]=daysep

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

    def _parse_cal_inter_results(self, output_lines):
        days_apart=None
        archive_cal_available=True
        for line in output_lines:
            if 'fluxes for this source not available' in line:
                archive_cal_available=False
            if 'days apart' in line:
                tokens = line.strip().split()
                days_apart=float(tokens[6])
        return archive_cal_available, days_apart

    def run_script(self, script_string):
        """Takes a script of commands, one command per line"""
        command_list = script_string.split('\n')
        for command in command_list:
            self.run_command(command)


    def set_active_file(self, filename, file_logdir=None):
        filename = filename.strip()  # Ensure no stray whitespace
        self.active_file = filename
        self._setup_file_loggers(filename, file_logdir)
        file_listing = self.run_command(r'file %s \ ' % filename)
        incomplete_obs = False
        for line in file_listing:
            if 'incomplete observation' in line:
                incomplete_obs = True

        if incomplete_obs:
            self.get_obs_details(filename, incomplete=True)
        else:
            self.get_obs_details(filename, incomplete=False)
        logger.debug('Active file: %s', filename)


    def write_files(self, rawfile, output_dir,
                    write_command_template = scripts.write_command,
                    write_command_overrides=None):
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
            cal_basename = (tgt_name+'_cal_'+
                            self.files[rawfile][keys.calibrator]+'.fits')
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

        write_command_args = scripts.write_command_defaults.copy()
        if write_command_overrides is not None:
            write_command_args.update(write_command_overrides)

        write_command_args['output_paths']=output_paths_string
        write_command = write_command_template.format(**write_command_args)
        self.run_command(write_command)

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
