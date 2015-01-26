"""
Utility routines for loading and saving lists of datafiles (raw or calibrated).
"""
import json

class Datatype:
    magic_key = '#DATATYPE'
    ami_la_raw='AMILA_RAWFILES'
    ami_la_calibrated='AMILA_CALIBRATED_UVFITS'


def save_rawfile_listing(raw_obs_groups_dict, filepointer):
    savedict = raw_obs_groups_dict.copy()
    savedict[Datatype.magic_key] = Datatype.ami_la_raw
    json.dump(savedict, filepointer,
                  sort_keys=True, indent=4)

def save_calfile_listing(list_of_calobs, filepointer):
    savedict = list_of_calobs.copy()
    savedict[Datatype.magic_key] = Datatype.ami_la_calibrated
    json.dump(savedict, filepointer,
              sort_keys=True, indent=4)


def load_listing(filepointer, expected_datatype=None):
    listing = json.load(filepointer)
    if (Datatype.magic_key not in listing):
        raise ValueError(
            "{} does not appear to be an AMI listing".format(filepointer)
        )
    found_datatype = listing[Datatype.magic_key]
    if expected_datatype is not None:
        if found_datatype != expected_datatype:
            raise ValueError(
            "{} does not appear to be an AMI listing of type {}".format(
                filepointer, expected_datatype)
            )
    listing.pop(Datatype.magic_key)
    return listing, found_datatype
