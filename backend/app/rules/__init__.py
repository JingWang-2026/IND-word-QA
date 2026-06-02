from app.rules.abbreviation_rules import AbbreviationFirstDefinitionRule, AbbreviationMultipleDefinitionsRule
from app.rules.heading_rules import HeadingNumberingGapRule
from app.rules.numeric_rules import PercentageCalculationRule
from app.rules.reference_rules import MissingTableFigureReferenceRule
from app.rules.table_rules import EmptyTableCellRule, InconsistentNANotationRule, SimpleTableTotalRule
from app.rules.terminology_rules import SimpleTerminologyInconsistencyRule
from app.rules.text_rules import DuplicateWordRule, RepeatedSpacesRule
from app.rules.word_metadata_rules import HeaderFooterVersionRule, RemainingCommentsRule, TrackedChangesRule


def default_rules():
    return [
        DuplicateWordRule(),
        RepeatedSpacesRule(),
        PercentageCalculationRule(),
        SimpleTableTotalRule(),
        EmptyTableCellRule(),
        InconsistentNANotationRule(),
        MissingTableFigureReferenceRule(),
        HeadingNumberingGapRule(),
        HeaderFooterVersionRule(),
        RemainingCommentsRule(),
        TrackedChangesRule(),
        AbbreviationFirstDefinitionRule(),
        AbbreviationMultipleDefinitionsRule(),
        SimpleTerminologyInconsistencyRule(),
    ]
