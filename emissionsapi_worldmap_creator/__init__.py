import datetime
import logging
import os

import geopandas
import h3
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# Logger
logger = logging.getLogger(__name__)

# H3 resolution of the Emissions API points
RESOLUTION = 4


def revert(polygon):
    """Revert longitude and latitude in a polygon

    :param polygon: polygon as a list of 2-tuple
    :type polygon: list
    :return: polygon as a list of 2-tuple
    :rtype: list
    """
    return [(lon, lat) for lat, lon in polygon]


def download_points(url, product, day):
    """Download the points from the Emissions API

    :param url: URL of the Emissions API instance
    :type url: str
    :param product: product to download
    :type product: str
    :param day: day to download
    :type day: datetime.datetime
    :return: Downloaded data
    :rtype: geopandas.GeoDataFrame
    """
    logger.info("Downloading data from Emissions API")
    return geopandas.read_file(
        f"{url}/api/v2/{product}/geo.json"
        f"?begin={day.isoformat()}"
        f"&end={(datetime.timedelta(days=1) + day).isoformat()}"
    )


def cache_filename(product, day):
    """Helper function to get the name of the cache

    :param product: product of the data to cache
    :type product: str
    :param day: day of the data to cache
    :type day: datetime.datetime
    :return: Filename of the cache
    :rtype: str
    """
    return f"cache-{product}-{day.isoformat()}"


def cache_load(product, day):
    """Load data from the cache

    :param product: product of the data to cache
    :type product: str
    :param day: day of the data to cache
    :type day: datetime.datetime
    :return: Cached data or None
    :rtype: geopandas.GeoDataFrame
    """
    fn = cache_filename(product, day)
    if not os.path.exists(fn):
        return None

    logger.debug("Loading data from cache %s", fn)
    return geopandas.read_file(fn)


def cache_save(df, product, day):
    """Save data in the cache

    :param df: data to cache
    :type df: geopandas.GeoDataFrame
    :param product: product of the data to cache
    :type product: str
    :param day: day of the data to cache
    :type day: datetime.datetime
    """
    fn = cache_filename(product, day)
    logger.debug("Saving data to cache %s", fn)
    df.to_file(fn)


def prepare(df):
    """Prepare the data to make them plottable

    This includes

    * generating the polygons to every point
    * Merging overlapping points
    * Removing unplottable polygons.

    :param df: Data to prepare
    :type df: geopandas.GeoDataFrame
    :return: Prepared data
    :rtype: geopandas.GeoDataFrame
    """
    logger.info("Preparing the data")
    logger.debug("Generating h3 indices")
    df["hex"] = [
        h3.geo_to_h3(lat, lon, RESOLUTION)
        for lat, lon in zip(df.geometry.y, df.geometry.x)
    ]

    logger.debug("Merging overlapping points")
    df = df.groupby("hex", as_index=False).agg({"value": "mean"})

    logger.debug("Calculating hexagonal polygons")
    df["geometry"] = geopandas.GeoSeries(
        [
            Polygon(revert(polygon))
            for polygon in [h3.h3_to_geo_boundary(h) for h in df.hex]
        ]
    )
    df = geopandas.GeoDataFrame(df, geometry=df.geometry)

    logger.debug("Calculating bounds of the polygons")
    bounds = df.bounds

    logger.debug("Removing polygons crossing the map border")
    df = df.mask(bounds.maxy - bounds.miny > 180)
    df = df.mask(bounds.maxx - bounds.minx > 180)

    return df


def get_points(url, product, day, cache):
    """Get plottable point.

    This includes using the cache or the Emissions API
    and prepare the points to make them plottable.

    :param url: URL of the Emissions API instance
    :type url: str
    :param product: product to get
    :type product: str
    :param day: day to get
    :type day: datetime.datetime
    :param cache: Use the cache or not
    :type cache: bool
    :return: Prepared data
    :rtype: geopandas.GeoDataFrame
    """
    logger.info("Getting data.")
    df = None
    if cache:
        df = cache_load(product, day)
    if df is not None:
        return df

    df = download_points(url, product, day)
    df = prepare(df)

    if cache:
        cache_save(df, product, day)

    return df


def plot(
    data,
    output,
    size,
    dpi,
    legend,
    cmap,
    title,
    legend_title,
    font_size,
    vmin,
    vmax,
):
    """Generate the plot and save it.

    :param data: data to plot
    :type data: geopandas.GeoDataFrame
    :param output: Output filename
    :type output: str
    :param size: Size of the image in inch as a 2-tuple
    :type size: tuple
    :param dpi: DPI of the saved image
    :type dpi: int
    :param legend: Show legend in image or not
    :type legend: bool
    :param cmap: Colormap of the image
    :type cmap: str
    :param title: Title of the image
    :type title: str
    :param legend_title: Title of the legend
    :type legend_title: str
    :param font_size: Font size in the image
    :type font_size: int
    """
    logger.info("Starting to plot")
    matplotlib.rc("font", size=font_size)

    fig, ax = plt.subplots(1, 1, figsize=size)
    fig.tight_layout()
    ax.set_axis_off()

    world = geopandas.read_file(
        geopandas.datasets.get_path("naturalearth_lowres")
    )
    logger.info("Plotting hexagonal polygons")
    data.plot(
        column="value",
        cmap=cmap,
        ax=ax,
        legend=legend,
        legend_kwds={
            "label": legend_title,
            "orientation": "horizontal",
        },
        vmin=vmin,
        vmax=vmax,
    )

    logger.info("Loading world map")
    world = geopandas.read_file(
        geopandas.datasets.get_path("naturalearth_lowres")
    )

    logger.info("Plotting country borders")
    world.geometry.boundary.plot(color=None, edgecolor="black", ax=ax)

    logger.info("Saving output to %s", output)
    plt.title(title)
    plt.savefig(output, dpi=dpi)
