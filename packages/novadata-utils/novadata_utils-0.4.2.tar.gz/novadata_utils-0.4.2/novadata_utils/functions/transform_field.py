from django_admin_listfilter_dropdown.filters import (
    ChoiceDropdownFilter,
    RelatedOnlyDropdownFilter,
)
from rangefilter.filters import (
    DateRangeQuickSelectListFilterBuilder,
    NumericRangeFilterBuilder,
)

filters = {
    "foreign_keys": RelatedOnlyDropdownFilter,
    "choices_fields": ChoiceDropdownFilter,
    "dates": DateRangeQuickSelectListFilterBuilder(),
    "numerics": NumericRangeFilterBuilder(),
}


def transform_field(list_of_fields, prop, field):
    """Transforma um field em um filtro de acordo com a propriedade."""
    return (field, filters[prop]) if field in list_of_fields else field
