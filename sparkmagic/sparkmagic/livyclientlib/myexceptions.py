

# == EXCEPTIONS ==
class LivyClientLibException(Exception):
    """Base class for all LivyClientLib exceptions. All exceptions that are explicitly raised by
    code in this package should be a subclass of LivyClientLibException. If you need to account for a
    new error condition, either use one of the existing LivyClientLibException subclasses,
    or create a new subclass with a descriptive name and add it to this file.

    We distinguish between "expected" errors, which represent errors that a user is likely
    to encounter in normal use, and "internal" errors, which represents exceptions that happen
    due to a bug in the library. Check EXPECTED_EXCEPTIONS to see which exceptions
    are considered "expected"."""


class HttpClientException(LivyClientLibException):
    """An exception thrown by the HTTP client when it fails to make a request."""


class LivyClientTimeoutException(LivyClientLibException):
    """An exception for timeouts while interacting with Livy."""

class DataFrameParseException(LivyClientLibException):
    """An internal error which suggests a bad implementation of dataframe parsing from JSON --
    if we get a JSON parsing error when parsing the results from the Livy server, this exception
    is thrown."""


class LivyUnexpectedStatusException(LivyClientLibException):
    """An exception that will be shown if some unexpected error happens on the Livy side."""


class SessionManagementException(LivyClientLibException):
    """An exception that is thrown by the Session Manager when it is a
    given session name is invalid in some way."""


class BadUserConfigurationException(LivyClientLibException):
    """An exception that is thrown when configuration provided by the user is invalid
    in some way."""


class BadUserDataException(LivyClientLibException):
    """An exception that is thrown when data provided by the user is invalid
    in some way."""

class GcloudNotInstalledException(LivyClientLibException):
    """Exception that is thrown when gloud is not installed."""
    

class SqlContextNotFoundException(LivyClientLibException):
    """Exception that is thrown when the SQL context is not found."""


class SparkStatementException(LivyClientLibException):
    """Exception that is thrown when an error occurs while parsing or executing Spark statements."""
