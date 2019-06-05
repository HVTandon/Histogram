
import numpy as np

import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling, MaskFlags, ColorInterp

def _stats(arr, percentiles=(2, 98)):
    """
    Calculate array statistics.

    Attributes
    ----------
    arr: numpy ndarray
        Input array data to get the stats from.
    percentiles: tuple, optional
        Tuple of Min/Max percentiles to compute.
    kwargs: dict, optional
        These will be passed to the numpy.histogram function.

    Returns
    -------
    dict
        numpy array statistics: percentiles, min, max, stdev, histogram

        e.g.
        {
            'pc': [38, 147],
            'min': 20,
            'max': 180,
            'std': 28.123562304138662,
            'histogram': [
                [1625, 219241, 28344, 15808, 12325, 10687, 8535, 7348, 4656, 1208],
                [20.0, 36.0, 52.0, 68.0, 84.0, 100.0, 116.0, 132.0, 148.0, 164.0, 180.0]
            ]
        }
    """
    sample, edges = np.histogram(arr[~arr.mask], max(100,int(arr.max().item()-arr.min().item())))
    '''
    return {
        "pc": np.percentile(arr[~arr.mask], percentiles).astype(arr.dtype).tolist(),
        "min": arr.min().item(),
        "max": arr.max().item(),
        "std": arr.std().item(),
        "histogram": [sample.tolist(), edges.tolist()],
    }
    '''
    return {'sample':sample.tolist(), 'edges':edges.tolist()}
    


def raster_get_stats(
    src_path,
    indexes=None,
    nodata=None,
    overview_level=None,
    max_size=1024,
    percentiles=(2, 98),
    histogram_range=None,
):
    """
    Retrieve dataset statistics.

    Attributes
    ----------
    src_path : str or PathLike object
        A dataset path or URL. Will be opened in "r" mode.
    indexes : tuple, list, int, optional
        Dataset band indexes.
    nodata, int, optional
        Custom nodata value if not preset in dataset.
    overview_level : int, optional
        Overview (decimation) level to fetch.
    max_size: int, optional
        Maximum size of dataset to retrieve
        (will be used to calculate the overview level to fetch).
    percentiles : tulple, optional
        Percentile or sequence of percentiles to compute,
        which must be between 0 and 100 inclusive (default: (2, 98)).
    dst_crs: CRS or dict
        Target coordinate reference system (default: EPSG:4326).
    histogram_bins: int, optional
        Defines the number of equal-width histogram bins (default: 10).
    histogram_range: tuple or list, optional
        The lower and upper range of the bins. If not provided, range is simply
        the min and max of the array.

    Returns
    -------
    out : dict
        bounds, mercator zoom range, band descriptions
        and band statistics: (percentiles), min, max, stdev, histogram

        e.g.
        {
            'bounds': {
                'value': (145.72265625, 14.853515625, 145.810546875, 14.94140625),
                'crs': '+init=EPSG:4326'
            },
            'minzoom': 8,
            'maxzoom': 12,
            'band_descriptions': [(1, 'red'), (2, 'green'), (3, 'blue'), (4, 'nir')]
            'statistics': {
                1: {
                    'pc': [38, 147],
                    'min': 20,
                    'max': 180,
                    'std': 28.123562304138662,
                    'histogram': [
                        [1625, 219241, 28344, 15808, 12325, 10687, 8535, 7348, 4656, 1208],
                        [20.0, 36.0, 52.0, 68.0, 84.0, 100.0, 116.0, 132.0, 148.0, 164.0, 180.0]
                    ]
                }
                ...
                3: {...}
                4: {...}
            }
        }
    """
    
    if isinstance(indexes, int):
        indexes = [indexes]
    elif isinstance(indexes, tuple):
        indexes = list(indexes)

    with rasterio.open(src_path) as src_dst:
        levels = src_dst.overviews(1)
        width = src_dst.width
        height = src_dst.height
        indexes = indexes if indexes else src_dst.indexes
        nodata = nodata if nodata is not None else src_dst.nodata
        
        if len(levels):
            if overview_level:
                decim = levels[overview_level]
            else:
                # determine which zoom level to read
                for ii, decim in enumerate(levels):
                    if max(width // decim, height // decim) < max_size:
                        break
        else:
            decim = 1
            warnings.warn(
                "Dataset has no overviews, reading the full dataset", NoOverviewWarning
            )

        out_shape = (len(indexes), height // decim, width // decim)

        vrt_params = dict(add_alpha=True, resampling=Resampling.bilinear)
        if has_alpha_band(src_dst):
            vrt_params.update(dict(add_alpha=False))

        if nodata is not None:
            vrt_params.update(dict(nodata=nodata, add_alpha=False, src_nodata=nodata))

        with WarpedVRT(src_dst, **vrt_params) as vrt:
            arr = vrt.read(out_shape=out_shape, indexes=indexes, masked=True)

            params = {}
            if histogram_range:
                params.update(dict(range=histogram_range))

            stats = {
                indexes[b]: _stats(arr[b], percentiles=percentiles)
                for b in range(arr.shape[0])
                if vrt.colorinterp[b] != ColorInterp.alpha
            }

    return stats

def has_alpha_band(src_dst):
    """Check for alpha band or mask in source."""
    if (
        any([MaskFlags.alpha in flags for flags in src_dst.mask_flag_enums])
        or ColorInterp.alpha in src_dst.colorinterp
    ):
        return True
    return False


