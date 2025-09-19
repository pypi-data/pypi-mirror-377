from ece241_submission_static_analyzer.exceptions.base_exceptions import ECE241StaticAnalyzerException


class ECE241StaticAnalyzerParsingException(ECE241StaticAnalyzerException):
    """Exception raised for errors in the parsing process of the ECE241 static analyzer."""

    def __init__(self, e: Exception):
        self.e_ = e
