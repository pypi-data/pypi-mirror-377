"""Mardown viewers for Module and Port."""
from cosapp.ports.port import BasePort
from cosapp.systems import System
from typing import List, Dict, Union


def upper_first(s: str) -> str:
    """Return a copy of the input string, with the first character in upper case."""
    return s[0].upper() + s[1:]


class PortMarkdownFormatter:
    """Markdown table formatter for ports"""
    
    def __init__(self, port: BasePort) -> None:
        self.port = port

    def content(self, contextual=True) -> List[str]:
        """Returns the port representation in Markdown format, as a list of strings.

        Parameters
        ----------
        contextual: bool
            If `True` (default), uses port full name; if `False`, displays only port name.

        Returns
        -------
        List[str]
            List of Markdown strings representing port variables as a table, with header.
        """
        port = self.port
        name = port.full_name() if contextual else port.name
        info = type(port).__name__
        if (desc := port.description.strip()):
            info += f". {upper_first(desc)}"
        doc = []
        doc.append(f"`{name}`: {info}")
        doc.extend(self.var_repr())
        return doc

    def var_repr(self) -> List[str]:
        """Returns the representation of port variables in Markdown format,
        as a list of strings (same as `content`, without name header).

        Returns
        -------
        List[str]
            List of Markdown strings representing port variables as a table.
        """
        content = [
            f"  {variable._repr_markdown_()}"
            for variable in self.port.variables()
        ]
        return self.wrap(content)

    def markdown(self, contextual=True) -> str:
        """Returns the port representation in Markdown format.

        Parameters
        ----------
        contextual: bool
            If `True` (default), uses port full name; if `False`, displays only port name.

        Returns
        -------
        str
            Markdown formatted representation
        """
        return "\n".join(self.content(contextual))

    @classmethod
    def wrap(cls, content: Union[str, List[str]]) -> List[str]:
        if isinstance(content, str):
            content = [content]
        header = ["|  |  |", "---|---"]
        doc = ["", cls.div_header(), ""]
        doc.extend(header)
        doc.extend(content)
        doc.append("</div>")
        return doc

    @classmethod
    def div_header(cls) -> str:
        """Div header used to override Jupyter Lab table CSS"""
        return "".join([
            r"<div class='cosapp-port-table' style='margin-left: 25px; margin-top: -12px'>",
            r"<style type='text/css'>",
            r".cosapp-port-table >table >thead{display: none}",  # suppress empty table header
            r".cosapp-port-table tbody tr{background: rgba(255, 255, 255, 0)!important}",  # override even/odd coloring
            r".cosapp-port-table tbody tr:hover{background: #e1f5fe!important}",  # set hover color
            r".cosapp-port-table >table {margin-left: unset; margin-right: unset}",
            r"</style>",
        ])


def port_to_md(port: BasePort) -> str:
    """Returns the representation of `port` in Markdown format.

    Parameters
    ----------
    port: BasePort
        Port to describe

    Returns
    -------
    str
        Markdown formatted representation
    """
    formatter = PortMarkdownFormatter(port)
    return formatter.markdown()


def system_to_md(system: System) -> str:
    """Returns the representation of `system` in Markdown format.

    Parameters
    ----------
    system: System
        System to describe

    Returns
    -------
    str
        Markdown formatted representation
    """
    doc = list()
    if system.tags:
        doc.extend(["", f"**Tags**: {list(system.tags)!s}", ""])

    def get_child_doc(s: System) -> str:
        info = type(s).__name__
        if (desc := s.description.strip()):
            info += f". {upper_first(desc)}"
        return f"- `{s.name}`: {info}"

    if (children := system.children):
        doc.extend(["", "### Child components", ""])
        doc.extend(map(get_child_doc, children.values()))

    def dump_port_data(header, port_dict: Dict[str, BasePort]):
        port_docs = []
        for port in port_dict.values():
            if len(port) > 0:
                formatter = PortMarkdownFormatter(port)
                port_doc = formatter.content(contextual=False)
                port_doc[0] = f"\n- {port_doc[0]}"
                port_docs.extend(port_doc)
        if port_docs:
            doc.extend(["", f"### {header.title()}", ""])
            doc.extend(port_docs)

    dump_port_data("inputs", system.inputs)
    dump_port_data("outputs", system.outputs)

    if (residues := system.residues):
        doc.extend(["", "### Residues", ""])
        doc.append(", ".join(f"`{key}`" for key in residues))

    return "\n".join(doc)
