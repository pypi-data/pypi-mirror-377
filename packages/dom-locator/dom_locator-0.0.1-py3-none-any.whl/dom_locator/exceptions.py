class ElementNotFoundError(Exception):
    """
    Exception raised when an element is not found in the XML.

    Attributes
    ----------
    message : str
        Explanation of the error.

    Methods
    -------
    __str__():
        Returns the string representation of the error message.
    """

    def __init__(self, message: str = "Element was not found in XML"):
        self.message: str = message
        super().__init__(self.message)


class XPathNotFound(Exception):
    """
    Exception raised when an element with the given xpath is not found in the XML

    Attributes
    ----------
    message : str
        Explanation of the error.

    Methods
    -------
    __str__():
        Returns the string representation of the error message.
    """

    def __init__(self, xpath: str):
        self.message: str = f"Element was not found in XML. XPath: {xpath}"
        super().__init__(self.message)
