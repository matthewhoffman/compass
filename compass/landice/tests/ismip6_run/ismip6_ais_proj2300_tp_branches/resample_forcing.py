import numpy as np
import xarray as xr
from cftime import datetime
from mpas_tools.io import write_netcdf


def __xtime2cftime(xtime_str, format="%Y-%m-%d_%H:%M:%S"):
    """Convert a single xtime value to a cftime datetime object
    """

    stripped_str = xtime_str.tobytes().decode("utf-8").strip().strip('\x00')

    return datetime.strptime(stripped_str, format)


def parse_xtime(ds):
    """Parse `xtime` vaules to cftime datetimes and create new coordinate
       from parsed values, named `Time`
    """

    times = list(map(__xtime2cftime, ds.xtime.values))

    time_da = xr.DataArray(times, [('Time', times)])

    return ds.assign_coords({"Time": time_da})


def generate_samples(ds, sampling_start, sampling_end, rng, repeat_period=200):
    """Generate array of sample indices from `Time` dimension of `ds`
    """

    sampling_period = sampling_end - sampling_start

    # 0 index assumes `Time` coordinate is sorted
    forcing_start = int(ds.Time.dt.year[0])

    # get the offset for the indexes
    idx_offset = sampling_start - forcing_start

    samples = idx_offset + rng.integers(0, sampling_period, repeat_period)

    return samples


def extend_forcing(src_ds, sample_idxs, newstart, newend):
    """Create new "extended" dataset using the `sample_idxs`
    """

    # create new time index based on input start and
    # end years with an calendar occurence on the first of every year
    time_da = xr.cftime_range(f"{newstart}-01-01", f"{newend}-01-01",
                              freq="YS", inclusive="both", calendar="noleap")
    # conver the CFtimeindex to a left justified string
    xtime_da = time_da.strftime("%Y-%m-%d_%H:%M:%S").str.ljust(64)

    # create a "new" extended datatset with the xtime variable
    new_ds = xr.Dataset({"xtime": ("Time", xtime_da)})
    # convert xtime from string to character array
    new_ds["xtime"] = new_ds.xtime.astype("S")

    for var in src_ds:
        # do not copy xtime, as it was created above
        if var == "xtime":
            continue

        # only sample variables w/ Time dimension
        if "Time" in src_ds[var].dims:
            new_ds[var] = src_ds[var].isel(Time=sample_idxs).drop_vars("Time")
        else:
            new_ds[var] = src_ds[var].copy()

    return new_ds


def resample_forcing(input_fp, output_fp,
                     refstart, refend,
                     newstart, newend,
                     seed=4727):

    # open the reference dataset and parse the xtime variable
    ref_forcing = xr.open_dataset(input_fp)
    ref_forcing = parse_xtime(ref_forcing)

    # initialize the random number generator and create sample index array
    rng = np.random.default_rng(seed)
    sample_length = newend - newstart + 1
    sample_idxs = generate_samples(ref_forcing, refstart, refend, rng,
                                   sample_length)

    # generate the extended forcing file and write it to disk
    new_forcing = extend_forcing(ref_forcing, sample_idxs, newstart, newend)
    write_netcdf(new_forcing, output_fp)
