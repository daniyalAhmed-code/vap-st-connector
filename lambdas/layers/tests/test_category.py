import pytest
from utils import exceptions, category
from utils.codes import Code


def test_category_validation_notexist(categories):
    with pytest.raises(exceptions.VapInputValidationFailureException) as excinfo:
        category.assert_valid_cat_subcat("notexists", "...", categories)
    assert excinfo.value.code == Code.VALIDATION_FAILURE
    assert excinfo.value.message == "Invalid category: notexists"


def test_category_validation_wrong_subcategory(categories):
    with pytest.raises(exceptions.VapInputValidationFailureException) as excinfo:
        category.assert_valid_cat_subcat(
            "Supply Technology", "Concrete Tower", categories
        )
    assert excinfo.value.code == Code.VALIDATION_FAILURE
    assert (
        excinfo.value.message
        == "Invalid subcategory: Concrete Tower is not part of Supply Technology"
    )


def test_category_validation_ok(categories):
    category.assert_valid_cat_subcat("Tower", "Concrete Tower", categories)
