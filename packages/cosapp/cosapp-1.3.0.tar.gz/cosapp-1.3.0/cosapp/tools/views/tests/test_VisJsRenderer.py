import pytest

from cosapp.base import System
from cosapp.tests.library.systems import FanComplex, ComplexTurbofan
from cosapp.tools.views.visjs import VisJsRenderer
from cosapp.utils.testing import no_exception, assert_keys


pytest.importorskip("jinja2")


@pytest.fixture(scope="function")
def fan():
    return FanComplex("fan")


@pytest.fixture(scope="function")
def renderer(fan):
    return VisJsRenderer(fan)


def test_VisJsRenderer_html_tags(renderer):
    tags = renderer.html_tags()
    assert_keys(tags, "html_begin_tags", "html_end_tags")


def test_VisJsRenderer_html_resources(renderer):
    resources = renderer.html_resources()
    assert_keys(resources, "visJS", "visCSS")


def test_VisJsRenderer_html_template(renderer):
    with no_exception():
        template = renderer.html_template()


def test_VisJsRenderer_get_globals(renderer):

    common = renderer.get_globals()
    assert_keys(
        common, "template", "html_begin_tags", "html_end_tags", "visJS", "visCSS"
    )


def test_VisJsRenderer_html_content(renderer):
    with no_exception():
        renderer.html_content()


@pytest.mark.parametrize("name, expected", [
    ('foo', 'foo'),
    ('very_long_name', 'very_l…'),
])
def test_VisJsRenderer_get_system_label(name, expected):
    s = System(name)
    label = VisJsRenderer.get_system_label(s)
    assert label == expected


def test_VisJsRenderer_get_system_title():
    class Head(System):
        pass

    class Sub1(System):
        pass

    class Sub2(System):
        pass

    head = Head('head')
    sub1 = head.add_child(Sub1('sub1'))
    sub2 = sub1.add_child(Sub2('sub2'))
    visjs = VisJsRenderer(head)
    assert visjs.get_system_title(head) == "head - Head"
    assert visjs.get_system_title(sub1) == "sub1 - Sub1"
    assert visjs.get_system_title(sub2) == "sub1.sub2 - Sub2"

    # New renderer, based on a sub-system
    visjs = VisJsRenderer(sub1)
    assert visjs.get_system_title(sub1) == "sub1 - Sub1"
    assert visjs.get_system_title(sub2) == "sub2 - Sub2"
    with pytest.raises(ValueError, match="not a child"):
        visjs.get_system_title(head)


def test_VisJsRenderer_get_data():
    turbofan = ComplexTurbofan("turbofan")

    visjs = VisJsRenderer(turbofan)
    data = visjs.get_data()
    assert set(data) == {
        "title",
        "nodes",
        "edges",
        "groups",
    }
    assert set(data["groups"]) == {
        "turbofan",
        "turbofan.fanC",
        "turbofan.fanC.ductC",
    }
    assert set(node["title"] for node in data["nodes"]) == {
        # Systems:
        "turbofan - ComplexTurbofan",
        "atm - Atm",
        "inlet - Inlet",
        "fanC - FanComplex",
        "fanC.ductC - ComplexDuct",
        "fanC.ductC.merger - Merger",
        "fanC.ductC.duct - Duct",
        "fanC.ductC.bleed - Splitter",
        "fanC.fan - Fan",
        "merger - Merger",
        "duct - Duct",
        "bleed - Splitter",
        "noz - Nozzle",
        # Ports:
        "fanC.inwards",
        "fanC.fl_out - FluidPort",
        "fanC.fl_in - FluidPort",
        "fanC.mech_in - MechPort",
        "fanC.ductC.fl_out - FluidPort",
        "fanC.ductC.fl_in - FluidPort",
    }

    # Test on sub-system
    visjs = VisJsRenderer(turbofan.fanC)
    data = visjs.get_data()
    assert set(data) == {
        "title",
        "nodes",
        "edges",
        "groups",
    }
    assert set(data["groups"]) == {
        "fanC",
        "fanC.ductC",
    }
    assert set(node["title"] for node in data["nodes"]) == {
        # Systems:
        "fanC - FanComplex",
        "ductC - ComplexDuct",
        "ductC.merger - Merger",
        "ductC.duct - Duct",
        "ductC.bleed - Splitter",
        "fan - Fan",
        # Ports:
        "fanC.inwards",
        "fanC.fl_in - FluidPort",
        "fanC.fl_out - FluidPort",
        "fanC.mech_in - MechPort",
        "fanC.ductC.fl_out - FluidPort",
        "fanC.ductC.fl_in - FluidPort",
    }
