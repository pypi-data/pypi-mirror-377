"""
SolverKinematic

A Python module for solving kinematics problems, supporting:
- Algebra-based uniform acceleration motion (UAM)
- Symbolic calculus using sympy
- Numeric evaluation over time intervals

Functions:
- KinematicSolverUAM(SUVAT): Solve algebraic UAM problems.
- kinematicSolverSymbolic(SVA, conV=None, conD=None): Solve symbolically with derivatives and integrals.
- kinematicSolverNumeric(completeSVA, t1, t2): Evaluate numeric results from symbolic solutions.

Requirements:
- Python 3.8+
- sympy
"""
import math
import sympy as sp

t = sp.symbols('t')
def parseInfo(cond):
    """
    Parses a string representing an initial condition into numeric components.

    Parameters
    ----------
    cond : str or None
        A string representing an initial condition in the format "F(t)=value", 
        e.g., "V(0)=10" or "D(2)=5". If None, the function returns None.

    Returns
    -------
    list or None
        A two-element list [time, value], both as floats. Returns None if `cond` is None.

    Example
    -------
    >>> parseInfo("V(0)=10")
    [0.0, 10.0]
    >>> parseInfo("D(2)=5")
    [2.0, 5.0]
    >>> parseInfo(None)
    None
    """
    if cond != None:
        lhs, rhs = cond.split("=")
        rhs = rhs.strip()
        rhs = float(rhs)
        func, arg = lhs.split("(")   
        arg = arg[:-1]
        info = [float(arg), rhs]
        return info
    return None 
def KinematicSolverUAM(SUVAT):
    """
    Solves uniform acceleration motion (UAM) problems algebraically.

    Parameters
    ----------
    SUVAT : list of length 5
        [S, U, V, A, T] where:
        - S : displacement (float, meters) or None
        - U : initial velocity (float, m/s) or None
        - V : final velocity (float, m/s) or None
        - A : acceleration (float, m/s²) or None
        - T : time (float, seconds) or None
        Use None for unknown variables.

    Returns
    -------
    list
        Completed list [S, U, V, A, T] with all unknowns calculated.

    Notes
    -----
    - Time (T) must be non-zero when used in calculations.
    - Handles all combinations of known/unknown variables for UAM.
    
    Example
    -------
    >>> SUVAT = [None, 0, 20, 2, None]
    >>> KinematicSolverUAM(SUVAT)
    [50.0, 0, 20, 2, 10.0]
    """
    newSUVAT = SUVAT.copy()
    if SUVAT[0] == None:
        if SUVAT[1] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[0] = SUVAT[1]*SUVAT[4]+(1/2)*SUVAT[3]*SUVAT[4]*SUVAT[4]
        else:
            if SUVAT[3] == 0:
                newSUVAT[0] = SUVAT[1]*SUVAT[4]
            else:
                newSUVAT[0] = ((SUVAT[2]*SUVAT[2])-(SUVAT[1]*SUVAT[1]))/(2*SUVAT[3])
    if SUVAT[1] is None:
        if SUVAT[2] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[1] = SUVAT[2] - SUVAT[3] * SUVAT[4]
        elif SUVAT[2] is None:
            newSUVAT[1] = (newSUVAT[0] - (1/2)*SUVAT[3]*SUVAT[4]*SUVAT[4])/SUVAT[4]
        elif SUVAT[4] is None:
            newSUVAT[1] = (SUVAT[2]*SUVAT[2])-(2*SUVAT[3]*newSUVAT[0])
            newSUVAT[1] = math.sqrt(newSUVAT[1])
    if SUVAT[2] is None:
        if SUVAT[1] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[2]= newSUVAT[1]+SUVAT[3]*SUVAT[4]
        elif SUVAT[4] is None:
            newSUVAT[2] = newSUVAT[1]*newSUVAT[1]+ 2* SUVAT[3] * SUVAT[0]
            newSUVAT[2] = math.sqrt(newSUVAT[2])
    if SUVAT[3] is None:
        if SUVAT[1] is not None and SUVAT[2] is not None and SUVAT[4] is not None:
            newSUVAT[3] = (newSUVAT[2]-newSUVAT[1])/SUVAT[4]
        elif SUVAT[2] is None:
            newSUVAT[3] = (newSUVAT[0] - (SUVAT[4]*newSUVAT[1]))/((1*SUVAT[4]*SUVAT[4])/2)
        else:
            newSUVAT[3] = ((newSUVAT[2]*newSUVAT[2])-(newSUVAT[1]*newSUVAT[1]))/(2*newSUVAT[0])
    if SUVAT[4] is None:
        if SUVAT[1] is not None and SUVAT[2] is not None and SUVAT[3] is not None:
            newSUVAT[4] = (newSUVAT[2]-newSUVAT[1])/ newSUVAT[3]
        else:
            if newSUVAT[3] == 0:
                newSUVAT[4] = newSUVAT[0]/newSUVAT[1]
            else:
                t1 = (-newSUVAT[1] + math.sqrt((newSUVAT[1]*newSUVAT[1])+2*newSUVAT[3]*newSUVAT[0]))/newSUVAT[3]
                t2 = (-newSUVAT[1] - math.sqrt((newSUVAT[1]*newSUVAT[1])+2*newSUVAT[3]*newSUVAT[0]))/newSUVAT[3]
                if t1>=t2:
                    newSUVAT[4] = t1
                else:
                    newSUVAT[4] = t2
    return newSUVAT
def kinematicSolverSymbolic(SVA, conV = None, conD = None):
    """
    Solves kinematics symbolically using derivatives and integrals, applying 
    initial conditions if provided.

    Parameters
    ----------
    SVA : list
        A list of three elements [displacement, velocity, acceleration] where each
        element can be a sympy expression or None if unknown.
    conV : str, optional
        Initial condition for velocity in the format "V(time)=value", e.g., "V(0)=10".
    conD : str, optional
        Initial condition for displacement in the format "D(time)=value", e.g., "D(0)=5".

    Returns
    -------
    list
        A list [displacement_expr, velocity_expr, acceleration_expr] where unknowns
        have been computed symbolically and integration constants have been applied 
        based on the provided initial conditions.

    Notes
    -----
    - If displacement is provided, velocity and acceleration are computed via differentiation.
    - If velocity is provided, displacement is computed via integration.
    - If acceleration is provided, velocity and displacement are computed via integration.
    - Integration constants C1 (for velocity) and C2 (for displacement) are substituted 
      using initial conditions if available.

    Example
    -------
    >>> import sympy as sp
    >>> t = sp.symbols('t')
    >>> SVA = [None, 5*t, None]  # [Displacement, Velocity, Acceleration]
    >>> kinematicSolverSymbolic(SVA, conV="V(0)=0", conD="D(0)=0")
    [5*t, 5, 0]
    """
    constantD = None
    ConstantV = None
    vInfo = parseInfo(conV)
    dInfo = parseInfo(conD)
    C1 = sp.symbols('C1')
    C2 = sp.symbols('C2')
    if SVA[0] is not None:
        if SVA[1] is None:
            SVA[1] = sp.diff(SVA[0], t, n=1)
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[0], t, n=2)
    if SVA[1] is not None:
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[1], t, n=1)
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1]) + C2
    if SVA[2] is not None:
        if SVA[1] is None:
            SVA[1] = sp.integrate(SVA[2]) + C1
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1]) + C2
    if vInfo is not None:
        vVal = SVA[1].subs(t, vInfo[0])
        constantV = vInfo[1] - vVal
    if dInfo is not None:
        dVal = SVA[0].subs(t, dInfo[0])
        constantD = dInfo[1] - dVal
    if constantV is not None:
        SVA[1] = SVA[1].subs(C1, constantV)
    if constantD is not None:
        SVA[0] = SVA[0].subs(C2, constantD)
    return SVA
def kinematicSolverNumeric(completeSVA, t1, t2):
    """
    Evaluates displacement, velocity, and acceleration numerically over a time interval.

    Parameters
    ----------
    completeSVA : list
        Symbolic solution returned by kinematicSolverSymbolic.
    t1 : float
        Start time (use 0 to get absolute values from start).
    t2 : float
        End time.

    Returns
    -------
    list
        Numeric changes [ΔS, ΔV, ΔA] over the interval [t1, t2].

    Notes
    -----
    - ΔS = displacement change, ΔV = velocity change, ΔA = acceleration change.
    - For absolute values at time t, set t1 = 0 and t2 = desired time.

    Example
    -------
    >>> numeric_vals = kinematicSolverNumeric(sol, 0, 5)
    >>> print(numeric_vals)
    [25.0, 10.0, 2.0]
    """
    finalSVA= [None, None, None]
    finalSVA[0] = completeSVA[0].subs(t, t2)-completeSVA[0].subs(t, t1)
    finalSVA[1] = completeSVA[1].subs(t, t2)-completeSVA[1].subs(t, t1)
    finalSVA[2] = completeSVA[2].subs(t, t2)-completeSVA[2].subs(t, t1)
    return finalSVA
    
    



