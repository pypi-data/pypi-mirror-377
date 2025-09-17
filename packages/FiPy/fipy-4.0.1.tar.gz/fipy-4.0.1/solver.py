r"""
>>> import fipy as fp
>>> from fipy.tools import numerix

For sufficiently constrained circumstances, all solver suites
should do the same thing.  The following problem setup is designed
to ensure that all interpret solver criteria correctly and achieve
the "same" tolerance in the same number of iterations.

Consider a steady-state 1D diffusion problem with a
position-dependent diffusivity and Dirichlet boundary conditions:

.. math::

   \begin{aligned}
   \frac{\partial}{\partial x}\left[
       \left(1 + x\right)
       \frac{\partial \phi}{\partial x}
   \right] &= 0
   \\
   \left.\phi\right\rvert_{x=0} &= \phi_L
   \\
   \left.\phi\right\rvert_{x=1} &= \phi_R
   \end{aligned}

with the analytical solution

.. math::

   \phi = \frac{\phi_R - \phi_L}{\ln 2} \ln\left(1 + x\right) + \phi_L

>>> N = 100
>>> mesh = fp.Grid1D(nx=N, Lx=1)
>>> phi = fp.CellVariable(mesh=mesh, name=r"$\phi")
>>> phiL = 1000.
>>> phiR = 2000.
>>> phi_analytical = ((((phiR - phiL)/fp.numerix.log(2.))
...                    * fp.numerix.log(1 + mesh.x))
...                   + phiL)
>>> phi_analytical.name = r"$\phi_\mathrm{analytical}$"

>>> fp.numerix.random.seed(12345)
>>> variance = 1e-3
>>> phi_initial = phi_analytical + fp.GaussianNoiseVariable(mesh=mesh, variance=variance)
>>> phi.value = phi_initial
>>> phi.constrain(phiL, where=mesh.facesLeft)
>>> phi.constrain(phiR, where=mesh.facesRight)
>>> D = fp.FaceVariable(mesh=mesh, value=1 + mesh.faceCenters[0])
>>> eq = fp.DiffusionTerm(coeff=D) == 0

For reproducibility between suites, we select a solver with
predictable characteristics (that counts out GMRES) and no
preconditioning.

>>> Solver = fp.LinearCGSSolver
>>> solver = Solver(precon=None)

>>> solver = eq._prepareLinearSystem(var=phi,
...                                  solver=solver,
...                                  boundaryConditions=(),
...                                  dt=1.)
>>> L, x, b = solver._Lxb

The problem parameters were chosen to give good separation between the
different convergence norms.

The norm of the matrix is the infinity norm

.. math::

   \left\| L_{ij}\right\|_\infty &= \max_i \sum_j \left| A_ij \right|
   \\
   &= \max_i \left[
       \left| -N(1 + x_i) \right|
       + \left| 2N(1 + x_i) \right|
       + \left| -N(1 + x_i) \right|
   \right]
   \\
   &= \max_i 4N(1 + x_i)
   &= \mathcal{O}(8 N)

>>> Lnorm = solver._matrixNorm(L, x, b)
>>> print(numerix.allclose(Lnorm, 8 * N, rtol=0.1))
True

The right-hand-side vector is zero except at the boundaries,
where the contribution is

.. math::

   \frac{(1 + x) \phi_{BC} A_f}{d_{AP}} &= (1 + x) \phi_{BC} 2 N
   \\
   &= 2 N \phi_L = 2000 N\qquad\text{at $x = 0$}
   \\
   &= 4 N \phi_R = 8000 N\qquad\text{at $x = 1$}

Thus the :math:`L_2` norm of the right-hand-side vector is
:math:`\left\| b \right\|_2 = \math{O}(8000 N}`.

>>> bnorm = solver._rhsNorm(L, x, b)
>>> print(numerix.allclose(bnorm, 8000 * N, rtol=0.1))
True

We choose the initial condition such that the initial residual will
be small.

.. math::

   \phi_0 &= \phi_\text{analytical} + \mathcal{O}(\sigma)
   \\
   r = L \phi_0 - b
   &= L \phi_\text{analytical} - b + L \mathcal{O}(\sigma)
   \\
   &= L \mathcal{O}(\sigma)
   \\
   \left\| r \right\|_2 &= \left\| L \mathcal{O}(\sigma) \right\|_2
   \\
   &= \sqrt{\sum_{0 \le i < N} \left[
       N(1 + x_i) \mathcal{O}(\sigma)
       + 2N(1 + x_i) \mathcal{O}(\sigma)
       + N(1 + x_i) \mathcal{O}(\sigma)
   \right]^2}
   \\
   &= 4 N \mathcal{O}(\sigma) \sqrt{\sum_{0 \le i < N} (1 + x_i)^2}
   \\
   &= \text{probably $\sqrt{\pi}$ or something}
   \\
   &= \mathcal{O}(4 N \sqrt{N} \sigma)

>>> rnorm = solver._residualNorm(L, x, b)
>>> print(numerix.allclose(rnorm, 4 * N * numerix.sqrt(N * variance),
...                        rtol=0.1))
True

Calculate the error of the initial condition (probably could be
estimated via truncation error blah blah blah).

>>> enorm = fp.numerix.L2norm(phi - phi_analytical) / fp.numerix.L2norm(phi_analytical)

>>> from fipy.solvers.convergence import Convergence

Check that:
- the solution is converged,
- the solver reaches the desired residual for the
  criterion, without overshooting too much.  Most get close, but
  "unscaled" overshoots a lot for most suites.
- the iteration count is as expected
- the error has been reduced from the initial guess

>>> criteria = [
...     ("unscaled", 1., 0.003, 114),
...     ("RHS", bnorm, 0.6, 2),
...     ("matrix", Lnorm, 0.6, 58),
...     ("initial", rnorm, 0.6, 110)
... ] # doctest: +NOT_SCIPY_SOLVER, +SCIPY_FORTRAN_SOLVERS
>>> criteria = [
...     ("unscaled", 1., 0.003, 118),
...     ("RHS", bnorm, 0.6, 2),
...     ("matrix", Lnorm, 0.6, 60),
...     ("initial", rnorm, 0.6, 114)
... ] # doctest: +SCIPY_PYTHON_SOLVERS
>>> # criteria += ["solution"]  doctest: +TRILINOS_SOLVER
>>> criteria += [
...     ("preconditioned", bnorm, 0.6, 2),
...     ("natural", bnorm, 0.6, 6)
... ] # doctest: +PETSC_SOLVER
>>> satisfied = []
>>> for (criterion, target, lower_bound, iterations) in criteria:
...     phi.setValue(phi_initial)
...     with Solver(criterion=criterion, precon=None) as s:
...         res = eq.sweep(var=phi, solver=s)
...         error = (fp.numerix.L2norm(phi - phi_analytical)
...                  / fp.numerix.L2norm(phi_analytical))
...         checks = [isinstance(s.convergence, Convergence),
...                   (lower_bound
...                    < (s.convergence.residual
...                       / (s.tolerance * target))
...                    < 1.0),
...                   numerix.allclose(s.convergence.iterations,
...                                    iterations,
...                                    atol=1),
...                   error < enorm]
...         print(criterion, s.convergence, target, lower_bound, s.convergence.residual / (s.tolerance * target), iterations, s.convergence.iterations, error, enorm)
...         satisfied.append(all(checks))
>>> print(all(satisfied))
True
>>> print(satisfied)
"""

__docformat__ = 'restructuredtext'

if __name__ == '__main__':
    from fipy import solvers
    import fipy.tests.doctestPlus
    exec(fipy.tests.doctestPlus._getScript())
