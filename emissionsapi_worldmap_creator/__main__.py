import logging
import datetime
import argparse

from emissionsapi_worldmap_creator import get_points, plot

logger = logging.getLogger(__name__)


def parse_command_line():
    """Parse the command line arguments

    :return: Parsed command line arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Generate images from emission data",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Be more verbose"
    )

    parser.add_argument(
        "--url",
        default="https://api.v2.emissions-api.org",
        help="URL to receive data from."
        " Defaults to https://api.v2.emissions-api.org",
    )
    parser.add_argument(
        "--no-caching",
        action="store_true",
        help="Disable caching of already downloaded data from the"
        " Emissions API.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Where to save the image. Default to <product>-<day>.png",
    )

    parser.add_argument(
        "--colormap",
        default="gist_rainbow",
        help="Colors of the map. Defaults to 'gist_rainbow'."
        " For a full list of colormaps,"
        " see the https://matplotlib.org/tutorials/colors/colormaps.html.",
    )

    parser.add_argument(
        "--legend",
        action="store_true",
        help="Enables the legend on the map.",
    )

    parser.add_argument(
        "--pixels_x",
        default=8000,
        help="Horizontal image size in pixels. Defaults to 8000.",
    )

    parser.add_argument(
        "--pixels_y",
        default=4000,
        help="Vertical image size in pixels. Defaults to 4000.",
    )

    parser.add_argument(
        "--dpi", default=96, help="DPI of the image. Defaulst to 96."
    )

    parser.add_argument(
        "--title", help="Title of the image. Defaults to '<Product> <date>'"
    )

    parser.add_argument(
        "--legend-title", help="Title of the legend. Defaults to '<Product>'"
    )

    parser.add_argument(
        "--font-size",
        default=50,
        help="Size of the font on the image. Defaults to 100.",
    )

    parser.add_argument(
        "--vmin",
        type=float,
        help="value where the colormap starts."
    )

    parser.add_argument(
        "--vmax",
        type=float,
        help="value where the colormap stops."
    )

    parser.add_argument("product", help="Type of product to search for.")
    parser.add_argument(
        "day",
        help="Day of the data. Example: 2019-09-01",
    )
    args = parser.parse_args()
    args.day = datetime.date.fromisoformat(args.day)

    # Set defaults, if neccessary
    if not args.output:
        args.output = f"{args.product}-{args.day.isoformat()}.png"
    if not args.title:
        args.title = f"{args.product.capitalize()} {args.day.isoformat()}"
    if not args.legend_title:
        args.legend_title = args.product.capitalize()

    return args


def main():
    """Entrypoint
    """
    # Parse command line
    args = parse_command_line()

    # logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(message)s",
    )

    # Get the points
    df = get_points(args.url, args.product, args.day, not args.no_caching)

    # Plot the points
    plot(
        df,
        args.output,
        (args.pixels_x / args.dpi, args.pixels_y / args.dpi),
        args.dpi,
        args.legend,
        args.colormap,
        args.title,
        args.legend_title,
        args.font_size,
        args.vmin,
        args.vmax,
    )


if __name__ == "__main__":
    main()
