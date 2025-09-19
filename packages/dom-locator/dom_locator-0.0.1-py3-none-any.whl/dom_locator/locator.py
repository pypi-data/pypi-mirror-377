"""
Module used to extract data from XML files using xpath to find elements
"""

from typing import Any
import lxml.etree as etree

from .exceptions import ElementNotFoundError
from .dom_source import DOMSource, HTMLSource, XMLSource


class Locator:
    """
    Class used to access XML information from a string or from an XML file.

    This class provides methods to load XML data and to find elements within the XML
    using XPath expressions.
    It also provides methods for including new elements inside the XML file.

    Examples
    --------
    >>> locator = Locator(xml_path="test.xml")
    >>> locator2 = Locator(
    >>>     xml_string="<user><name>John</name><surname>Doe</surname></user>",
    >>>     encoding="utf-8",
    >>> )
    >>> var1 = locator.get_text("//tag1", "Not Found") # Not Found if tag1 does not exist, else its text
    >>> name = locator2.get_text("//name", None) # John
    """

    def __init__(self, source: HTMLSource | DOMSource) -> None:
        """
        Instantiates a Locator object containing the contents of DOMSource subclasses.

        Parameters
        ----------
        source : HTMLSource | DOMSource
            Class with DOM data inside a file or string

        Returns
        -------
        None


        Raises
        ------
        ValueError
            source is not of the correct type

        Examples
        --------
        >>> locator = Locator(XMLSource("test.xml"))
        >>> locator2 = Locator(
        >>>     XMLSource(
        >>>         content="<user><name>John</name><surname>Doe</surname></user>",
        >>>         encoding="utf-8"
        >>>     )
        >>> )
        >>> locator3 = Locator(HTMLSource("test.html"))
        """

        self.source = source

        if source.content is None:  # used to remove linter error
            source.content = ""

        if isinstance(source, XMLSource):
            parser = etree.XMLParser(remove_blank_text=True)
        elif isinstance(source, HTMLSource):
            parser = etree.HTMLParser(encoding=source.encoding)
        else:
            raise ValueError("source must be a XMLSource or HTMLSource")

        if source.source == "path":
            self.tree = etree.parse(source.path, parser)
        elif source.source == "content":
            self.tree = etree.ElementTree(
                etree.fromstring(bytes(source.content, encoding=source.encoding), parser)
            )

        self.root = self.tree.getroot()
        self.remove_namespaces()

    def remove_namespaces(self) -> None:
        """
        Removes namespaces from the XML elements.

        This is needed to search by xpath without problems.

        Returns
        -------
        None
        """

        for elem in self.root.getiterator():
            # The following line is a guard for Comment tags
            # Comments don't have the attribute and would raise an
            # exception
            if not hasattr(elem.tag, "find"):
                continue
            # the namespace appear as "{namespace}tag"
            # and we want to get only "tag", after '}'
            i = elem.tag.find("}")
            if i >= 0:
                elem.tag = elem.tag[i + 1 :]

    def save(self, output_path: str, **kwargs) -> None:
        """
        Saves the XML to the specified output path.

        Parameters
        ----------
        output_path : str
            Path where the XML should be saved.
        **kwargs : dict, optional
            Additional arguments for `etree.write()`. For example:

            - pretty_print: bool
                If True, formats the XML for a more appealing visual. This is the default value
                If False, won't format the XML
            - encoding: str
                The encoding of the output file. The default is the same as the source used for instantiation
            - xml_declaration: bool
                Include xml declaration at the beginning of xml file. The default is True

            Check `etree.write()` documentation for more options.

        Returns
        -------
        None

        Examples
        --------
        >>> locator = Locator(xml_path="test.xml")
        >>> locator.set_text("//tag1", "NewValue")
        >>> locator.save(output_path="test_modified.xml")
        """

        if "pretty_print" not in kwargs:
            kwargs["pretty_print"] = True
        if "encoding" not in kwargs:
            kwargs["encoding"] = self.source.encoding
        if self.source.type == "xml":
            kwargs["method"] = "xml"
            if "xml_declaration" not in kwargs:
                kwargs["xml_declaration"] = True
        if self.source.type == "html":
            kwargs["method"] = "html"

        self.tree.write(output_path, **kwargs)

    def find_elements(self, xpath: str) -> list[etree._Element]:
        """
        Finds all elements from the root of the tree by a XPath expression.

        Parameters
        ----------
        xpath : str
            The XPath expression to search for.

        Returns
        -------
        list of etree._Element
            A list of elements matching the XPath expression.

        Examples
        --------
        >>> locator = Locator(xml_path="test.xml")
        >>> # From root
        >>> list_elem = locator.find_elements("//tag1")
        >>> elem1 = list_elem[0]
        >>> # From another element
        >>> elem2 = elem1.xpath(".//tag2")[0]
        """

        return self.tree.xpath(xpath)

    def find_element(self, xpath: str) -> None | etree._Element:
        """
        Finds all of the elements from the root of the tree and returns
        the first element.

        Parameters
        ----------
        xpath : str
            The XPath expression to search for.

        Returns
        -------
        etree._Element or None
            The first element matching the XPath expression, or None if no element is found.

        Examples
        --------
        >>> locator = Locator(xml_path="test.xml")
        >>> # From root
        >>> list_elem = locator.find_element("//tag1")
        >>> # From another element
        >>> elem2 = elem1.xpath(".//tag2")[0]
        """

        elements = self.find_elements(xpath)
        if len(elements) > 0:
            return elements[0]
        return None

    def get_text(
        self, element_id: str | list[str] | etree._Element, default_value: Any | None = None
    ) -> Any | None:
        """
        Gets the text of an element or returns a default value if provided.
        The element can be passed by a single xpath, a list of xpaths (in order of priority) or as an Element from find_element

        Parameters
        ----------
        xpath : str
            The XPath expression to search for.

        Returns
        -------
        str or None
            The text of the element if found, otherwise None.

        Raises
        ------
        ElementNotFoundError
            If no element is found with any XPath from `element_id` and the default value is None.

        Examples
        --------
        >>> locator = Locator(xml_path="test.xml")
        >>> name = locator.get_text("//name")
        """

        element = None
        if isinstance(element_id, etree._Element):
            element = element_id
        else:
            if not isinstance(element_id, list):
                element_id = [element_id]

            for xpath in element_id:
                _elem = self.find_element(xpath)
                if _elem is not None:
                    element = _elem
                    break

        if isinstance(element, etree._Element):
            return element.text  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        if element is None:
            if default_value is not None:
                return default_value
            raise ElementNotFoundError(
                f"It was not possible to find any elements that match element_id: {element_id}"
            )
        else:
            raise AssertionError(
                f"incorrect type for element, should be None or ElementTree. Type: {type(element)}"
            )

    def set_text(self, element_id: str | etree._Element, value: Any) -> bool:
        """
        Sets the text field of an element to a specific value.
        If `element_id` is a str, it will be treated an an XPath expression and will use it to find the element.
        If `element_id` is an etree._Element, its value will be changed directly without trying to find the element.
        Finds an element using its XPath expression and sets its text field to a specified value.

        Parameters
        ----------
        element_id : str or etree._Element
            If a string, will be treated as XPath. If an etree._Element, it will be used without searching by XPath
        value : Any
            The value to set as the text of the element.

        Returns
        -------
        bool
            True if the value is set successfully, False if the element is not found.

        Examples
        --------
        >>> locator = Locator(xml_path="test.xml")
        >>> # Before: ...<name>John</name>...
        >>> locator.set_text("//name", "Bob")
        >>> # After: ...<name>Bob</name>...
        >>> # Save to make changes persistent
        >>> locator.save(output_path="test_modified.xml")
        """

        if isinstance(element_id, str):
            element = self.find_element(element_id)
        else:
            element = element_id

        if element is None:
            return False

        element.text = str(value)
        return True

    def create_element_by_xpath(
        self, absolute_xpath: str, allow_duplicate: bool = False
    ) -> etree._Element:
        """
        Creates an element using an absolute XPath (from the root of the XML).
        If the elements between the root and the target element don't exist, they are created.

        Parameters
        ----------
        absolute_xpath : str
            The absolute XPath expression to create the element.
        allow_duplicate : bool, optional
            If False and the target already exists, returns it. If True, always creates the target even if it already exists. Default is False.

        Returns
        -------
        etree._Element
            The created tree element.

        Examples
        --------
        >>> # Valid xpaths:
        >>> absolute_xpath = "/tag1/tag2/tag3/target" # will search from root
        >>> absolute_xpath = "./tag1/tag2/tag3/target" # will search from root
        >>> # Invalid xpaths:
        >>> absolute_xpath = "/tag1/tag2/tag3/target/"
        >>> absolute_xpath = "//tag1/tag2/tag3/target"
        >>> absolute_xpath = "/tag1/tag2/tag3//target"

        >>> locator = Locator(
        >>>     xml_string="<users><user><name>John</name><surname>Doe</surname></user></users>",
        >>>     encoding="utf-8",
        >>> )
        >>> locator.create_element_by_xpath(absolute_xpath="./user/age", allow_duplicate=False)
        >>> locator.set_text(xpath="./user/age", value=25)
        >>> locator.save("./tests/files/output.xml")

        Raises
        ------
        ValueError
            If the `absolute_xpath` is invalid (xpath format check)
        """

        # Check if the xpath is absolute
        # 1) Must start with "/" or "./"
        # 2) Must not end with "/"
        # 3) Must not contain "//" in Any position

        if (
            len(absolute_xpath) == 0
            or not (absolute_xpath[0] == "/" or absolute_xpath[:2] == "./")
            or absolute_xpath[-1] == "/"
            or "//" in absolute_xpath
        ):
            raise ValueError(
                "The passed absolute_xpath is invalid. "
                "It should: start with / or ./, not end with /, not contain // in Any position"
            )

        # We are going to create all parts from the root to the target
        parts = absolute_xpath.split("/")[1:]
        current = self.tree.getroot()
        for index, part in enumerate(parts):
            children = list(current)
            tmp = [x for x in children if x.tag == part]
            if len(tmp) == 0 or (allow_duplicate and index + 1 == len(parts)):
                current = etree.SubElement(current, part, attrib=None, nsmap=None)
            else:
                current = tmp[0]

        return current

    def create_child_element(
        self, parent_element: etree._Element, child_tag: str, allow_duplicate: bool = False
    ) -> etree._Element:
        """
        Receives an element and creates a child element with a given tag.

        Parameters
        ----------
        parent_element : etree._Element
            The parent element to which the child will be added.
        child_tag : str
            The tag for the child element.
        allow_duplicate : bool, optional
            If False and a child element with the tag already exists, returns the existing child element.
            If True, always creates a new element. Default is False.

        Returns
        -------
        etree._Element
            The created child element.

        Examples
        --------
        >>> locator = Locator(
        >>>     xml_string="<users><user><name>John</name><surname>Doe</surname></user></users>",
        >>>     encoding="utf-8",
        >>> )
        >>> parent_elem = locator.find_element("//user")
        >>> locator.create_child_element(
        >>>     parent_element=parent_elem, child_tag="age", allow_duplicate=False
        >>> )
        >>> locator.set_text(xpath="./user/age", value=25)
        >>> locator.save("output.xml")
        """

        # the conversion below seems weird, but is the way recommended in parent_element.getchildren()
        children = list(parent_element)
        tmp = [x for x in children if x.tag == child_tag]
        if len(tmp) == 0 or allow_duplicate:
            child = etree.SubElement(parent_element, child_tag, attrib=None, nsmap=None)
        else:
            child = tmp[0]

        return child
