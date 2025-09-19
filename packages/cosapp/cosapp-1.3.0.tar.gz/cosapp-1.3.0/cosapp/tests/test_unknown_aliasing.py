"""Test problems with unknown aliased by pulling"""
import pytest
import logging, re
from numpy import sqrt, cbrt
from dataclasses import dataclass

from cosapp.systems import System
from cosapp.drivers import NonLinearSolver, RunSingleCase


class Quadratic(System):
    """System computing y = 1 + k * x**2"""
    def setup(self):
        self.add_inward('k', 0.8)
        self.add_inward('x', 1.0)
        self.add_outward('y', 0.0)
    
    def compute(self):
        self.y = 1 + self.k * self.x**2


class NestedQuad(System):
    """System combining two Quadratic subsystems, with pulling"""
    def setup(self):
        foo = self.add_child(Quadratic('foo'), pulling={'k': 'c'})
        bar = self.add_child(Quadratic('bar'))

        self.connect(foo, bar, {'y': 'k'})


def test_design_unknown_aliasing_1(caplog):
    """Design test using an unknown aliased by a pulling.
    System is a `NestedQuad` instance.

    Case 1: Use pulled input variable `foo.k` as unknown.

    Successful; log simply informs that unknown was substituted.
    """
    top = NestedQuad('top')
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9))
    solver.add_child(RunSingleCase('runner'))
    solver.runner.add_equation('foo.y == 7').add_unknown('foo.k')
    solver.runner.set_values({
        'foo.x': 2,
        'bar.x': 0.1,
    })
    caplog.clear()
    with caplog.at_level(logging.INFO):
        top.run_drivers()
    
    assert len(caplog.records) > 0
    assert re.match(
        r"Replace unknown 'foo\.k' by 'c'",
        caplog.records[0].message
    )
    assert top.foo.k == pytest.approx(1.5)
    assert top.foo.y == pytest.approx(7)
    assert top.bar.k == top.foo.y
    assert top.foo.k == top.c


def test_design_unknown_aliasing_2(caplog):
    """Design test using an unknown aliased by a pulling.
    System is a `NestedQuad` instance.

    Case 2:
        Driver is attached to subsystem `foo`.
        Unknown is pulled inward `foo.k`.
    
    Works, but issues a warning because unknown is aliased
    by a higher-level, free input.
    """
    top = NestedQuad('top')
    top.c = 0.1
    top.run_once()
    assert top.c == 0.1
    assert top.foo.k == top.c

    solver = top.foo.add_driver(NonLinearSolver('solver', tol=1e-9))
    solver.add_child(RunSingleCase('runner'))
    solver.runner.add_unknown('k').add_equation('y == 7')
    solver.runner.set_values({'x': 2})

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        top.run_drivers()
    
    assert len(caplog.records) > 0
    assert any(
        re.match(
            r"Unknown 'foo\.k' is aliased by 'top\.c', defined outside the context of 'foo'",
            record.message
        )
        for record in caplog.records
    )
    assert top.foo.k == pytest.approx(1.5)
    assert top.c == 0.1  # unchanged top value


def test_design_unknown_aliasing_3(caplog):
    """Same as `test_design_unknown_aliasing_1`, except `NestedQuad` system
    is now a sub-system in which inward `c` is connected to an output.
    """
    top = System('top')
    sub1 = top.add_child(Quadratic('sub1'))
    sub2 = top.add_child(NestedQuad('sub2'))
    top.connect(sub1.outwards, sub2.inwards, {'y': 'c'})  # sub2.c is no longer free

    solver = top.add_driver(NonLinearSolver('solver'))
    # Use input `bar.k` connected to an output as unknown:
    solver.add_equation('sub2.foo.y == 7').add_unknown('sub2.bar.k')

    caplog.clear()
    with pytest.raises(ArithmeticError, match=r"numbers of params \[0\] and residues \[1\]"):
        with caplog.at_level(logging.WARNING):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert re.match(
        r"Skip connected unknown 'sub2\.bar\.k'",
        caplog.records[0].message
    )


def test_design_unknown_aliasing_4(caplog):
    """Same as `test_design_unknown_aliasing_1`, with
    one additional hierarchical level.
    """
    top = System('top')
    sub = top.add_child(NestedQuad('sub'))
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9))
    solver.add_equation('sub.foo.y == 7').add_unknown('sub.foo.k')

    sub.foo.x = 2.0
    sub.bar.x = 0.1
    caplog.clear()
    with caplog.at_level(logging.INFO):
        top.run_drivers()
    
    assert sub.foo.k == pytest.approx(1.5)
    assert sub.foo.y == pytest.approx(7)
    assert sub.bar.k == sub.foo.y
    assert sub.foo.k == sub.c
    assert len(caplog.records) > 0
    assert re.match(
        r"Replace unknown 'sub\.foo\.k' by 'sub\.c'",
        caplog.records[0].message
    )


def test_design_connected_unknown_1(caplog):
    """Tests that unknowns connected to an output variable are discarded"""
    top = NestedQuad('top')
    solver = top.add_driver(NonLinearSolver('solver'))
    # Use input `bar.k` connected to an output as unknown:
    solver.add_equation('bar.y == 7').add_unknown('bar.k')

    caplog.clear()
    with pytest.raises(ArithmeticError, match=r"numbers of params \[0\] and residues \[1\]"):
        with caplog.at_level(logging.WARNING):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert re.match(
        r"Skip connected unknown 'bar\.k'",
        caplog.records[0].message
    )


def test_design_connected_unknown_2(caplog):
    """Same as `test_design_connected_unknown_1`,
    except driver is attached to subsystem `bar`.
    
    Fails because unknown is connected.
    """
    top = NestedQuad('top')
    # Attach driver to sub-system `bar`
    solver = top.bar.add_driver(NonLinearSolver('solver', tol=1e-9))
    solver.add_unknown('k').add_equation('y == 7')

    caplog.clear()
    with pytest.raises(ArithmeticError, match=r"numbers of params \[0\] and residues \[1\]"):
        with caplog.at_level(logging.WARNING):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert re.match(
        r"Skip connected unknown 'k'",
        caplog.records[0].message
    )


def test_design_offdesign_aliasing_1(caplog):
    """Design test involving off-design and design unknowns
    aliased by the same variable.

    Case 1: free unknown is off-design
    """
    class TopSystem(NestedQuad):
        """NestedQuad with off-design problem"""
        def setup(self):
            super().setup()
            # Use parent (free) variable 'c' as off-design unknown
            self.add_unknown('c').add_equation('c == 0')
    
    top = TopSystem('top')
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9))
    # Use pulled variable `foo.k` as design unknown:
    solver.add_equation('foo.y == 7').add_unknown('foo.k')

    caplog.clear()
    with pytest.raises(ValueError, match="'c' is defined as design and off-design unknown"):
        with caplog.at_level(logging.INFO):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert any(
        re.match(
            r"Replace unknown 'foo\.k' by 'c'",
            record.message
        )
        for record in caplog.records
    )


def test_design_offdesign_aliasing_2(caplog):
    """Design test involving off-design and design unknowns
    aliased by the same variable.

    Case 2: free unknown is declared in design problem
    """
    class TopSystem(NestedQuad):
        """NestedQuad with off-design problem"""
        def setup(self):
            super().setup()
            # Use pulled variable `foo.k` as off-design unknown
            self.add_unknown('foo.k').add_equation('c == 0')
    
    top = TopSystem('top')
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9))
    # Use parent variable 'c' as design unknown
    solver.add_equation('foo.y == 7').add_unknown('c')

    caplog.clear()
    with pytest.raises(ValueError, match="'c' is defined as design and off-design unknown"):
        with caplog.at_level(logging.INFO):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert any(
        re.match(
            r"Replace unknown 'foo\.k' by 'c'",
            record.message
        )
        for record in caplog.records
    )


def test_design_offdesign_aliasing_3(caplog):
    """Design test involving off-design and design unknowns
    aliased by the same variable.

    Case 3: free unknown is off-design; design unknown defined at solver level
    """
    class TopSystem(NestedQuad):
        """NestedQuad with off-design problem"""
        def setup(self):
            super().setup()
            # Use parent (free) variable 'c' as off-design unknown
            self.add_unknown('c').add_equation('c == 0')
    
    top = TopSystem('top')
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9))
    # Use pulled variable `foo.k` as design unknown:
    solver.add_equation('foo.y == 7').add_unknown('foo.k')

    caplog.clear()
    with pytest.raises(ValueError, match="'c' is defined as design and off-design unknown"):
        with caplog.at_level(logging.INFO):
            top.run_drivers()
            # print(solver.problem)
    
    assert len(caplog.records) > 0
    assert any(
        re.match(
            r"Replace unknown 'foo\.k' by 'c'",
            record.message
        )
        for record in caplog.records
    )


def test_connected_unknown_changing_conf(caplog):
    """Test with an originally free input variable,
    later connected to an output after a first design problem.
    """
    class DoubleQuad(System):
        def setup(self):
            self.add_child(Quadratic('foo'))
            self.add_child(Quadratic('bar'))

    top = DoubleQuad('top')
    foo, bar = top.foo, top.bar
    solver = top.add_driver(NonLinearSolver('solver', tol=1e-9, max_iter=100))

    # First problem: `bar.x` is unknown
    solver.add_unknown('bar.x').add_equation('bar.y == 5.5')

    foo.k = 1
    bar.k = 2
    top.run_drivers()
    assert bar.y == pytest.approx(5.5)
    assert bar.x == pytest.approx(1.5)
    assert set(solver.problem.unknowns) == {'bar.x'}
    assert set(solver.problem.residues) == {'bar.y == 5.5'}

    # Add connector foo.y -> bar.x
    # Unknown `bar.x` is no longer free
    top.connect(foo, bar, {'y': 'x'})

    caplog.clear()
    with pytest.raises(ArithmeticError, match=r"numbers of params \[0\] and residues \[1\]"):
        with caplog.at_level(logging.WARNING):
            top.run_drivers()
    
    assert len(caplog.records) > 0
    assert re.match(
        r"Skip connected unknown 'bar\.x'",
        caplog.records[0].message
    )

    # Declare `foo.x` as unknown - problem is balanced again
    solver.add_unknown('foo.x')

    top.run_drivers()
    assert foo.x == pytest.approx(sqrt(0.5))
    assert bar.y == pytest.approx(5.5)
    assert set(solver.problem.unknowns) == {'foo.x'}
    assert set(solver.problem.residues) == {'bar.y == 5.5'}

    # Introduce cyclic dependency with new sub-system
    class CubicRoot(System):
        def setup(self):
            self.add_inward('x', 1.0)
            self.add_outward('y', 1.0)
        
        def compute(self) -> None:
            self.y = cbrt(self.x)

    coupling = CubicRoot('coupling')
    top.add_child(coupling)
    # Make `foo.k` a function of `bar.y`
    # with:
    #     bar.y -> coupling.x
    #     coupling.y -> foo.k
    top.connect(bar, coupling, {'y': 'x'})
    top.connect(coupling, foo, {'y': 'k'})

    assert top.assembled_problem().is_empty()
    top.open_loops()
    problem = top.assembled_problem()
    assert problem.shape == (1, 1)
    assert set(problem.unknowns) == {'foo.k'}
    assert set(problem.residues) == {'foo.k == coupling.y (loop)'}
    top.close_loops()

    # Cyclic dependency induces a change in system structure,
    # which must be captured at driver execution
    top.run_drivers()
    assert bar.y == pytest.approx(5.5)
    assert foo.k == pytest.approx(cbrt(5.5))
    assert foo.x == pytest.approx(0.5322200367)
    assert set(solver.problem.unknowns) == {
        'foo.x',
        'foo.k',
    }
    assert set(solver.problem.residues) == {
        'bar.y == 5.5',
        'foo.k == coupling.y (loop)',
    }


@dataclass
class Foo:
    a: float
    x: float


class SystemWithCustomObject(System):
    def setup(self):
        self.add_inward("foo", Foo(a=1.0, x=1.0))
        self.add_outward("y", 0.0)

    def compute(self):
        self.y = self.foo.a - self.foo.x**3


class Top(System):
    def setup(self):
        self.add_child(SystemWithCustomObject("sub"), pulling={"foo": "bar"})


def test_dealias_problem_with_custom_object():
    """Test function `dealias_problem` with composite system `top` including custom object.
    Related to https ://gitlab.com/cosapp/cosapp/-/issues/171"""

    top = Top("top")
    solver = top.add_driver(NonLinearSolver("solver"))

    solver.add_unknown("sub.foo.x")
    solver.add_equation("sub.y == 0")

    top.bar.a = -2.0
    top.bar.x = 10.0
    top.sub.foo.a = 12.0
    top.sub.foo.x = -5.0
    top.run_drivers()

    assert top.bar.x == pytest.approx(cbrt(top.bar.a), rel=1e-14)
    assert top.sub.foo.x == top.bar.x
    assert top.sub.foo.a == -2.0
    assert top.sub.y == pytest.approx(0, abs=1e-14)
