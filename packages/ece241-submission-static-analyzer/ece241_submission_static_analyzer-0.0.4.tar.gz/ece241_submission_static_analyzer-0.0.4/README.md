
### Usage:
```python
from ece241_submission_static_analyzer.main import check, StaticAnalysisItem
from ece241_submission_static_analyzer.all_rules import RULES_YOU_ARE_CHECKING

request = [
    StaticAnalysisItem(
        rule=RULES_YOU_ARE_CHECKING(), 
        kwargs=KWARGS,
        file=FILE_NAME
    ),
    # other rules
]

results = check(request)
```
### Rules

#### FunctionMustReturnRule
This rule checks if the last statement of given functions are return statements. If students uses print instead of return, this rule will be violated. 

```python
kwargs={"function_names": ["func1", "func2"]}
```
Note, if you meant to check member function of a class, the function name should be `ClassName.FunctionName`


#### RequireClassRule
This rule checks if the given class is defined in a file/module. 

```python
kwargs={"class_names": ["class1", "class2"]}
```


#### RequireFileRule
This rule checks if the a file exist. 

```python
kwargs={}
```

#### RequireFunctionRule
This rule checks if given functions are defined. 

```python
kwargs={"function_names": ["func1", "func2"]}
```
Note, if you meant to check member function of a class, the function name should be `ClassName.FunctionName`


#### NoInputFuncRule
This rule requires no `input` function is used inside the given file. This applies whether students use them inside the class definition, function definition, regardless the function might be called. One exception is node under `if __name__ == "__main__":` block is NOT checked. 

```python
kwargs={}
```

#### NoRootStatementsRule
This rule that no statement is allowed at root level. This checks if there is any function calls, print statements, input statements are used at root level. Class definitions function definitions, package imports, `if __name__ == "__main__":` block are allowed. 

```python
kwargs={}
```


### Returns: 
A list of `ViolationResult` objects. 
```python 
class ViolationResult(NamedTuple):
    file_path: str
    line_number: int
    message: str
    rule: RuleType
    severity: SeverityType  # Updated to use SeverityType
```

SeverityType values: 
```python
class SeverityType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

### Bundled check
Usage
```python 
from ece241_submission_static_analyzer.main import bundle
```

Function bundle signature
```python
def bundle(file: str, classes: list[str], functions: list[str]) -> list[StaticAnalysisItem]:
```

This function builds `RequireClassRule`->`RequireFunctionRule`->`NoInputFuncRule`->`NoRootStatementsRule`->`FunctionMustReturnRule` lists. 
Note: there is no file check. File check is suggested as a upstream parent check.
