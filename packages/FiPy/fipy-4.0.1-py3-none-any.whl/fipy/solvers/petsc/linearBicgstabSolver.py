__docformat__ = 'restructuredtext'

from fipy.solvers.petsc.petscKrylovSolver import PETScKrylovSolver

__all__ = ["LinearBicgstabSolver"]

class LinearBicgstabSolver(PETScKrylovSolver):
    """Interface to the Biconjugate Gradient (Stabilized) (:term:`BiCGSTAB`)
    solver in :ref:`PETSC`.
    """
      
    solver = 'bcgs'
