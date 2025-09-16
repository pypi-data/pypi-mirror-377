from ece241_submission_static_analyzer.rules.rule import Rule, ViolationResult
from ece241_submission_static_analyzer.all_rules import RequireClassRule, RequireFunctionRule, NoInputFuncRule, NoRootStatementsRule, FunctionMustReturnRule
from typing import NamedTuple


class StaticAnalysisItem(NamedTuple):
    rule: Rule
    kwargs: dict[str, list[str]]
    file: str


def bundle(file: str, classes: list[str], functions: list[str]) -> list[StaticAnalysisItem]:
    return [StaticAnalysisItem(
        rule=RequireClassRule(),
        kwargs={"class_names": classes},
        file=file
    ), StaticAnalysisItem(
        rule=RequireFunctionRule(),
        kwargs={"function_names": functions},
        file=file
    ), StaticAnalysisItem(
        rule=NoInputFuncRule(),
        kwargs={},
        file=file
    ), StaticAnalysisItem(
        rule=NoRootStatementsRule(),
        kwargs={},
        file=file
    ), StaticAnalysisItem(
        rule=FunctionMustReturnRule(),
        kwargs={"function_names": functions},
        file=file
    )]


def check(static_analysis_request: list[StaticAnalysisItem]) -> list[ViolationResult]:
    """Check a list of static analysis requests."""
    results = []
    for item in static_analysis_request:
        results.extend(item.rule.check(item.file, **item.kwargs))
    return results
