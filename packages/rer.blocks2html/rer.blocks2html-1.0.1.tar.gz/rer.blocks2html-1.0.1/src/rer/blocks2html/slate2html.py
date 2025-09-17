"""slate2html module"""

from .config import ACCEPTED_TAGS
from lxml.html import builder as E
from lxml.html import tostring

import json
import logging


logger = logging.getLogger(__name__)

SLATE_ACCEPTED_TAGS = ACCEPTED_TAGS + ["link"]


def join(element, children):
    """join.

    :param element:
    :param children:
    """
    res = []
    for bit in children:
        res.append(bit)
        res.append(element)
    return res[:-1]  # remove the last break


class Blocks2HTML(object):
    """Blocks2HTML."""

    def serialize(self, element):
        """serialize.

        :param element:
        """
        if "text" in element:
            text_elements = element["text"].split("\n")
            if element.get("style-text-larger", False):
                text_elements = [
                    E.SPAN(
                        x,
                        **{"class": "text-larger"},
                    )
                    for x in text_elements
                ]

            return join(E.BR(), text_elements)

        if element["type"] == "paragraph":
            element["type"] = "p"
        tagname = element["type"]
        if element.get("data") and tagname not in SLATE_ACCEPTED_TAGS:
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in SLATE_ACCEPTED_TAGS:
                handler = self.handle_block
        if not handler:
            logger.warning(f"Unhandled tag: {tagname}. Skipping.")
            return []
        res = handler(element)
        if isinstance(res, list):
            return res
        return [res]

    def handle_tag_link(self, element):
        """handle_tag_link.

        :param element:
        """
        url = element.get("data", {}).get("url")

        attributes = {}
        if url is not None:
            attributes["href"] = url

        el = getattr(E, "A")

        children = []
        for child in element["children"]:
            children += self.serialize(child)
        return el(*children, **attributes)

    def handle_slate_data_element(self, element):
        """handle_slate_data_element.

        :param element:
        """
        el = E.SPAN

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        data = {"type": element["type"], "data": element["data"]}
        attributes = {"data-slate-data": json.dumps(data)}

        return el(*children, **attributes)

    def handle_tag_hr(self, element):
        elements = []
        for child in element.get("children", []):
            elements.extend(self.serialize(child))
        elements.append(getattr(E, "HR")())
        return elements

    def handle_block(self, element):
        """handle_block.

        :param element:
        """
        el = getattr(E, element["type"].upper())

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        return el(*children)

    def to_html(self, value):
        """to_html.

        :param value:
        """
        children = []
        for child in value:
            children += self.serialize(child)

        html = ""
        for child in children:
            if not isinstance(child, str):
                child = tostring(child).decode("utf-8")
            html += child
        return html
        # # TO DO: handle unicode properly
        # return "".join(tostring(f).decode("utf-8") for f in children)


def slate_to_html(value):
    """slate_to_html.

    :param value:
    """
    convert = Blocks2HTML()
    return convert.to_html(value)
