def _generate_default_keys(someclass):
    """Sets the values of class attributes according to their name.

       NB. ignores any attributes with values other than None.
    """
    for att_name, att_val in vars(someclass).iteritems():
        if(att_name[:2] != "__" and att_val == None):
            setattr(someclass, att_name,
                    "".join([someclass.__name__, ".", att_name]))


class ImageKeys:
    rawfile = 'Raw data filename'
    target = 'Target image path'
    calibrator = 'Calibrator image path',
    date = 'Date of obs'
    start = 'Obs start time'
    end = 'Obs end time'
    days = 'Days since burst alert'
    rain = 'Rain amp. correction '
    flagged = 'Visibilities flagged (%)'
    noise = 'Estimated noise (Jy)'
    std = 'Image standard deviation (Jy)'
    dbid = 'Image Database id'
    sources = 'Detected sources'



class DatasetKeys:
    id = 'Id'
    images = 'List of image info dicts'
    target_dsid = 'Target dataset id'
    cal_dsid = 'Calibrator dataset id'
    dtime = 'Burst alert DateTime'
    monitor = 'Monitoring list entries'


class SourceKeys:
    id = 'id'
    pflux = 'f_peak'
    pflux_err = 'f_peak_err'
    iflux = 'f_int'
    iflux_err = 'f_int_err'



