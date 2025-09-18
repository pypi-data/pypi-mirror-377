try:
    from opensees.openseespy import Model
except:
    Model = None


successful = 0


from ._analysis import StaticAnalysis, EigenAnalysis, DynamicAnalysis
from .load import NodalLoad

# def __getattr__(name):
#     global successful
#     if name == "Model":
#         try:
#             from opensees.openseespy import Model
#         except:
#             Model = None
#         if Model is None:
#             raise ImportError("opensees is not installed or not available.")
#         return Model
# 
#     elif name == "successful":
#         return successful
#     else:
#         raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


try:
    from jax import tree_util
#   import opensees.openseespy as ops
# 1) Tell JAX that ops.Model is an opaque leaf
    def _flatten_model(model):
        # no children, carry the model object in aux_data
        return (), model

    def _unflatten_model(aux_data, _children):
        # aux_data *is* the original model
        return aux_data

    tree_util.register_pytree_node(Model, _flatten_model, _unflatten_model)
except:
    pass



def solve(model, loading, output=None, algorithm=None, scale=1.0, constraints="Plain", operation=None):
    """
    Solve a static equilibrium problem for the model with the given loading.

    Parameters
    ----------
    model : :py:class:`Model`
        The structural model to analyze.
    loading : Load or list of Loads
        The loads to apply during the analysis.
    algorithm : Algorithm, optional
        The solution algorithm to use. If None, the :ref:`Newton` algorithm is used.
    constraints : ConstraintHandler, optional
        The constraint handler to manage boundary conditions. Default is :ref:`"Plain" <PlainConstraints>`.
    """
    analysis = StaticAnalysis(loading, algorithm=algorithm)
    if analysis.analyze(model) != successful:
        message = "Analysis did not complete successfully."
        message = model._openseespy._interp.read_error()
        raise RuntimeError(message)

    if output is not None:
        node, dof = output
        return model.nodeDisp(node, dof)
    return None


def eigen(model, modes, solver=None, output=None, problem="Frequency"):
    """
    Perform eigenvalue analysis on the model.

    Parameters
    ----------
    model : Model
        The structural model to analyze.
    modes : int
        The number of eigenmodes to compute.
    solver : EigenSolver, optional
        The eigenvalue solver to use. If None, a default solver is used.
    problem : str, optional
        The type of eigenvalue problem to solve. Options are "Frequency" or "Buckling".

    Returns
    -------
    eigenvalues : list
        The computed eigenvalues.
    """
    model.eigen(modes)


def trace(model, loading, output=None, algorithm=None, method=None):
    """
    Perform a static analysis while tracing the response of the model.
    """
    analysis = StaticAnalysis(loading, algorithm=algorithm)
    if analysis.analyze(model) != successful:
        raise RuntimeError("Analysis did not complete successfully.")

    if output is not None:
        node, dof = output
        return model.nodeDisp(node, dof)
    return None



def integrate(model, loading, time_step, output=None, algorithm=None, method=None):
    """
    integrate the dynamic response of the model.
    """


class Integrator:
    pass

class _LoadControl:
    pass

class ArcLengthControl(_LoadControl):
    pass

class DisplacementControl(_LoadControl):
    pass

class EnergyControl(_LoadControl):
    pass

class LoadControl(_LoadControl):
    pass
