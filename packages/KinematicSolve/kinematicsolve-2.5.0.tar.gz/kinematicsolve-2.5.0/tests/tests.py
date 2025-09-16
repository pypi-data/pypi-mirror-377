"""
test.py

A simple test suite for the solverKinematic package.
"""

import sympy as sp
from KinematicSolve import (
    parseInfo,
    KinematicSolverUAM,
    kinematicSolverSymbolic,
    kinematicSolverNumeric
)

t = sp.symbols('t')

# ------------------------
# 1. Test KinematicSolverUAM (Algebraic)
# ------------------------
print("=== Algebraic UAM Test ===")
SUVAT = [None, 0, 20, 2, None]  # [S, U, V, A, T]
result_algebraic = KinematicSolverUAM(SUVAT)
print("Input SUVAT:", SUVAT)
print("Solved SUVAT:", result_algebraic)
print()

# ------------------------
# 2. Test kinematicSolverSymbolic (Symbolic)
# ------------------------
print("=== Symbolic Test ===")
# Only provide displacement as a function of time
SVA = [None, 5*t, None, None]  # [None, displacement, velocity, acceleration]
# Provide initial conditions for velocity and displacement
sol_symbolic = kinematicSolverSymbolic(SVA, conV="V(0)=0", conD="D(0)=0")
print("Symbolic solution:")
print("Displacement:", sol_symbolic[1])
print("Velocity:", sol_symbolic[2])
print("Acceleration:", sol_symbolic[3])
print()

# ------------------------
# 3. Test kinematicSolverNumeric (Numeric evaluation)
# ------------------------
print("=== Numeric Test ===")
t_start = 0
t_end = 5
numeric_result = kinematicSolverNumeric(sol_symbolic, t_start, t_end)
print(f"Numeric values from t={t_start} to t={t_end}:")
print("ΔDisplacement:", numeric_result[1])
print("ΔVelocity:", numeric_result[2])
print("ΔAcceleration:", numeric_result[3])
print()

# ------------------------
# 4. Test parseInfo
# ------------------------
print("=== parseInfo Test ===")
cond = "V(2)=10"
parsed = parseInfo(cond)
print(f"Input: '{cond}' -> Parsed:", parsed)
print()

print("All tests completed successfully.")
