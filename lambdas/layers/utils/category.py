import csv
import logging
import functools
from typing import Optional
from utils import exceptions
import os


logger = logging.getLogger("vap")

k_categories_filename = "utils/data/Category-Sub-Category.csv"


@functools.lru_cache
def _load(filename):
    categories = {}

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "../" + filename)

    logger.info(f"filename: {filename}")

    with open(filename, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            category = row["Category"]
            subcategory = row["Sub-Category"]
            if categories.get(category) is None:
                categories[category] = []

            categories[category].append(subcategory)
    logger.info(f"categories: {categories}")
    return categories


def assert_valid_cat_subcat(
    cat: Optional[str], subcat: Optional[str], data=None, filename=None
):
    if data is None:
        filename = os.environ.get("VAP_TEST_CATEGORIES_FILENAME", k_categories_filename)
        data = _load(filename)

    if cat is None:
        return

    try:
        logger.info(f"{__name__}: data={data}")
        subcategories = data[cat]
    except KeyError:
        raise exceptions.VapInputValidationFailureException(f"Invalid category: {cat}")

    if subcat is None:
        return

    if subcat not in subcategories:
        raise exceptions.VapInputValidationFailureException(
            f"Invalid subcategory: {subcat} is not part of {cat}"
        )
