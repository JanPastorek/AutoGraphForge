import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 100000

-- A?  (n=2, m=0)
abbrev G0 : SimpleGraph (Fin 2) := GraphCalc.ofEdges 2 []
example : GraphCalc.order G0 = 2 := by decide
example : GraphCalc.size G0 = 0 := by decide
example : SimpleGraph.minDegree G0 = 0 := by decide
example : SimpleGraph.maxDegree G0 = 0 := by decide
example : GraphCalc.indepNum G0 = 2 := by decide
example : GraphCalc.cliqueNum G0 = 1 := by decide
example : GraphCalc.dominationNumber G0 = 2 := by decide
example : GraphCalc.independentDominationNumber G0 = 2 := by decide
example : GraphCalc.slaterNumber G0 = 2 := by decide
example : GraphCalc.annihilationNumber G0 = 2 := by decide
example : GraphCalc.zeroForcingNumber G0 = 2 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G0 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G0 := by decide
example : GraphCalc.vertexCoverNumber G0 = 0 := by decide
example : GraphCalc.romanDominationNumber G0 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G0 = 4 := by decide
example : ¬ GraphCalc.IsConnectedClass G0 := by decide
example : ¬ GraphCalc.IsTreeClass G0 := by decide
example : GraphCalc.IsClawFreeClass G0 := by decide
example : GraphCalc.IsCographClass G0 := by decide
example : GraphCalc.IsRegularClass G0 := by decide
example : ¬ GraphCalc.IsCubicClass G0 := by decide
example : GraphCalc.IsSubcubicClass G0 := by decide
example : ¬ GraphCalc.IsEulerianClass G0 := by decide
example : GraphCalc.IsTriangleFreeClass G0 := by decide
example : GraphCalc.IsK4FreeClass G0 := by decide
example : GraphCalc.IsNontrivialClass G0 := by decide
example : GraphCalc.IsBipartiteClass G0 := by decide

-- A_  (n=2, m=1)
abbrev G1 : SimpleGraph (Fin 2) := GraphCalc.ofEdges 2 [(0, 1)]
example : GraphCalc.order G1 = 2 := by decide
example : GraphCalc.size G1 = 1 := by decide
example : SimpleGraph.minDegree G1 = 1 := by decide
example : SimpleGraph.maxDegree G1 = 1 := by decide
example : GraphCalc.indepNum G1 = 1 := by decide
example : GraphCalc.cliqueNum G1 = 2 := by decide
example : GraphCalc.dominationNumber G1 = 1 := by decide
example : GraphCalc.independentDominationNumber G1 = 1 := by decide
example : GraphCalc.slaterNumber G1 = 1 := by decide
example : GraphCalc.annihilationNumber G1 = 1 := by decide
example : GraphCalc.zeroForcingNumber G1 = 1 := by decide
example : GraphCalc.totalZeroForcingNumber G1 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G1 = 1 := by decide
example : GraphCalc.vertexCoverNumber G1 = 1 := by decide
example : GraphCalc.totalDominationNumber G1 = 2 := by decide
example : GraphCalc.edgeCoverNumber G1 = 1 := by decide
example : GraphCalc.subTotalDominationNumber G1 = 2 := by decide
example : GraphCalc.romanDominationNumber G1 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G1 = 3 := by decide
example : GraphCalc.radius G1 = 1 := by decide
example : GraphCalc.IsConnectedClass G1 := by decide
example : GraphCalc.IsTreeClass G1 := by decide
example : GraphCalc.IsClawFreeClass G1 := by decide
example : GraphCalc.IsCographClass G1 := by decide
example : GraphCalc.IsRegularClass G1 := by decide
example : ¬ GraphCalc.IsCubicClass G1 := by decide
example : GraphCalc.IsSubcubicClass G1 := by decide
example : ¬ GraphCalc.IsEulerianClass G1 := by decide
example : GraphCalc.IsTriangleFreeClass G1 := by decide
example : GraphCalc.IsK4FreeClass G1 := by decide
example : GraphCalc.IsNontrivialClass G1 := by decide
example : GraphCalc.IsBipartiteClass G1 := by decide

-- B?  (n=3, m=0)
abbrev G2 : SimpleGraph (Fin 3) := GraphCalc.ofEdges 3 []
example : GraphCalc.order G2 = 3 := by decide
example : GraphCalc.size G2 = 0 := by decide
example : SimpleGraph.minDegree G2 = 0 := by decide
example : SimpleGraph.maxDegree G2 = 0 := by decide
example : GraphCalc.indepNum G2 = 3 := by decide
example : GraphCalc.cliqueNum G2 = 1 := by decide
example : GraphCalc.dominationNumber G2 = 3 := by decide
example : GraphCalc.independentDominationNumber G2 = 3 := by decide
example : GraphCalc.slaterNumber G2 = 3 := by decide
example : GraphCalc.annihilationNumber G2 = 3 := by decide
example : GraphCalc.zeroForcingNumber G2 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G2 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G2 := by decide
example : GraphCalc.vertexCoverNumber G2 = 0 := by decide
example : GraphCalc.romanDominationNumber G2 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G2 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G2 := by decide
example : ¬ GraphCalc.IsTreeClass G2 := by decide
example : GraphCalc.IsClawFreeClass G2 := by decide
example : GraphCalc.IsCographClass G2 := by decide
example : GraphCalc.IsRegularClass G2 := by decide
example : ¬ GraphCalc.IsCubicClass G2 := by decide
example : GraphCalc.IsSubcubicClass G2 := by decide
example : ¬ GraphCalc.IsEulerianClass G2 := by decide
example : GraphCalc.IsTriangleFreeClass G2 := by decide
example : GraphCalc.IsK4FreeClass G2 := by decide
example : GraphCalc.IsNontrivialClass G2 := by decide
example : GraphCalc.IsBipartiteClass G2 := by decide

-- BG  (n=3, m=1)
abbrev G3 : SimpleGraph (Fin 3) := GraphCalc.ofEdges 3 [(1, 2)]
example : GraphCalc.order G3 = 3 := by decide
example : GraphCalc.size G3 = 1 := by decide
example : SimpleGraph.minDegree G3 = 0 := by decide
example : SimpleGraph.maxDegree G3 = 1 := by decide
example : GraphCalc.indepNum G3 = 2 := by decide
example : GraphCalc.cliqueNum G3 = 2 := by decide
example : GraphCalc.dominationNumber G3 = 2 := by decide
example : GraphCalc.independentDominationNumber G3 = 2 := by decide
example : GraphCalc.slaterNumber G3 = 2 := by decide
example : GraphCalc.annihilationNumber G3 = 2 := by decide
example : GraphCalc.zeroForcingNumber G3 = 2 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G3 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G3 := by decide
example : GraphCalc.vertexCoverNumber G3 = 1 := by decide
example : GraphCalc.romanDominationNumber G3 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G3 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G3 := by decide
example : ¬ GraphCalc.IsTreeClass G3 := by decide
example : GraphCalc.IsClawFreeClass G3 := by decide
example : GraphCalc.IsCographClass G3 := by decide
example : ¬ GraphCalc.IsRegularClass G3 := by decide
example : ¬ GraphCalc.IsCubicClass G3 := by decide
example : GraphCalc.IsSubcubicClass G3 := by decide
example : ¬ GraphCalc.IsEulerianClass G3 := by decide
example : GraphCalc.IsTriangleFreeClass G3 := by decide
example : GraphCalc.IsK4FreeClass G3 := by decide
example : GraphCalc.IsNontrivialClass G3 := by decide
example : GraphCalc.IsBipartiteClass G3 := by decide

-- Bo  (n=3, m=2)
abbrev G4 : SimpleGraph (Fin 3) := GraphCalc.ofEdges 3 [(0, 1), (0, 2)]
example : GraphCalc.order G4 = 3 := by decide
example : GraphCalc.size G4 = 2 := by decide
example : SimpleGraph.minDegree G4 = 1 := by decide
example : SimpleGraph.maxDegree G4 = 2 := by decide
example : GraphCalc.indepNum G4 = 2 := by decide
example : GraphCalc.cliqueNum G4 = 2 := by decide
example : GraphCalc.dominationNumber G4 = 1 := by decide
example : GraphCalc.independentDominationNumber G4 = 1 := by decide
example : GraphCalc.slaterNumber G4 = 1 := by decide
example : GraphCalc.annihilationNumber G4 = 2 := by decide
example : GraphCalc.zeroForcingNumber G4 = 1 := by decide
example : GraphCalc.totalZeroForcingNumber G4 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G4 = 1 := by decide
example : GraphCalc.vertexCoverNumber G4 = 1 := by decide
example : GraphCalc.totalDominationNumber G4 = 2 := by decide
example : GraphCalc.edgeCoverNumber G4 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G4 = 2 := by decide
example : GraphCalc.romanDominationNumber G4 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G4 = 3 := by decide
example : GraphCalc.radius G4 = 1 := by decide
example : GraphCalc.IsConnectedClass G4 := by decide
example : GraphCalc.IsTreeClass G4 := by decide
example : GraphCalc.IsClawFreeClass G4 := by decide
example : GraphCalc.IsCographClass G4 := by decide
example : ¬ GraphCalc.IsRegularClass G4 := by decide
example : ¬ GraphCalc.IsCubicClass G4 := by decide
example : GraphCalc.IsSubcubicClass G4 := by decide
example : ¬ GraphCalc.IsEulerianClass G4 := by decide
example : GraphCalc.IsTriangleFreeClass G4 := by decide
example : GraphCalc.IsK4FreeClass G4 := by decide
example : GraphCalc.IsNontrivialClass G4 := by decide
example : GraphCalc.IsBipartiteClass G4 := by decide

-- Bw  (n=3, m=3)
abbrev G5 : SimpleGraph (Fin 3) := GraphCalc.ofEdges 3 [(0, 1), (0, 2), (1, 2)]
example : GraphCalc.order G5 = 3 := by decide
example : GraphCalc.size G5 = 3 := by decide
example : SimpleGraph.minDegree G5 = 2 := by decide
example : SimpleGraph.maxDegree G5 = 2 := by decide
example : GraphCalc.indepNum G5 = 1 := by decide
example : GraphCalc.cliqueNum G5 = 3 := by decide
example : GraphCalc.dominationNumber G5 = 1 := by decide
example : GraphCalc.independentDominationNumber G5 = 1 := by decide
example : GraphCalc.slaterNumber G5 = 1 := by decide
example : GraphCalc.annihilationNumber G5 = 1 := by decide
example : GraphCalc.zeroForcingNumber G5 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G5 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G5 = 2 := by decide
example : GraphCalc.vertexCoverNumber G5 = 2 := by decide
example : GraphCalc.totalDominationNumber G5 = 2 := by decide
example : GraphCalc.edgeCoverNumber G5 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G5 = 2 := by decide
example : GraphCalc.romanDominationNumber G5 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G5 = 3 := by decide
example : GraphCalc.radius G5 = 1 := by decide
example : GraphCalc.IsConnectedClass G5 := by decide
example : ¬ GraphCalc.IsTreeClass G5 := by decide
example : GraphCalc.IsClawFreeClass G5 := by decide
example : GraphCalc.IsCographClass G5 := by decide
example : GraphCalc.IsRegularClass G5 := by decide
example : ¬ GraphCalc.IsCubicClass G5 := by decide
example : GraphCalc.IsSubcubicClass G5 := by decide
example : GraphCalc.IsEulerianClass G5 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G5 := by decide
example : GraphCalc.IsK4FreeClass G5 := by decide
example : GraphCalc.IsNontrivialClass G5 := by decide
example : ¬ GraphCalc.IsBipartiteClass G5 := by decide

-- C?  (n=4, m=0)
abbrev G6 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 []
example : GraphCalc.order G6 = 4 := by decide
example : GraphCalc.size G6 = 0 := by decide
example : SimpleGraph.minDegree G6 = 0 := by decide
example : SimpleGraph.maxDegree G6 = 0 := by decide
example : GraphCalc.indepNum G6 = 4 := by decide
example : GraphCalc.cliqueNum G6 = 1 := by decide
example : GraphCalc.dominationNumber G6 = 4 := by decide
example : GraphCalc.independentDominationNumber G6 = 4 := by decide
example : GraphCalc.slaterNumber G6 = 4 := by decide
example : GraphCalc.annihilationNumber G6 = 4 := by decide
example : GraphCalc.zeroForcingNumber G6 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G6 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G6 := by decide
example : GraphCalc.vertexCoverNumber G6 = 0 := by decide
example : GraphCalc.romanDominationNumber G6 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G6 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G6 := by decide
example : ¬ GraphCalc.IsTreeClass G6 := by decide
example : GraphCalc.IsClawFreeClass G6 := by decide
example : GraphCalc.IsCographClass G6 := by decide
example : GraphCalc.IsRegularClass G6 := by decide
example : ¬ GraphCalc.IsCubicClass G6 := by decide
example : GraphCalc.IsSubcubicClass G6 := by decide
example : ¬ GraphCalc.IsEulerianClass G6 := by decide
example : GraphCalc.IsTriangleFreeClass G6 := by decide
example : GraphCalc.IsK4FreeClass G6 := by decide
example : GraphCalc.IsNontrivialClass G6 := by decide
example : GraphCalc.IsBipartiteClass G6 := by decide

-- C@  (n=4, m=1)
abbrev G7 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(2, 3)]
example : GraphCalc.order G7 = 4 := by decide
example : GraphCalc.size G7 = 1 := by decide
example : SimpleGraph.minDegree G7 = 0 := by decide
example : SimpleGraph.maxDegree G7 = 1 := by decide
example : GraphCalc.indepNum G7 = 3 := by decide
example : GraphCalc.cliqueNum G7 = 2 := by decide
example : GraphCalc.dominationNumber G7 = 3 := by decide
example : GraphCalc.independentDominationNumber G7 = 3 := by decide
example : GraphCalc.slaterNumber G7 = 2 := by decide
example : GraphCalc.annihilationNumber G7 = 3 := by decide
example : GraphCalc.zeroForcingNumber G7 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G7 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G7 := by decide
example : GraphCalc.vertexCoverNumber G7 = 1 := by decide
example : GraphCalc.romanDominationNumber G7 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G7 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G7 := by decide
example : ¬ GraphCalc.IsTreeClass G7 := by decide
example : GraphCalc.IsClawFreeClass G7 := by decide
example : GraphCalc.IsCographClass G7 := by decide
example : ¬ GraphCalc.IsRegularClass G7 := by decide
example : ¬ GraphCalc.IsCubicClass G7 := by decide
example : GraphCalc.IsSubcubicClass G7 := by decide
example : ¬ GraphCalc.IsEulerianClass G7 := by decide
example : GraphCalc.IsTriangleFreeClass G7 := by decide
example : GraphCalc.IsK4FreeClass G7 := by decide
example : GraphCalc.IsNontrivialClass G7 := by decide
example : GraphCalc.IsBipartiteClass G7 := by decide

-- CB  (n=4, m=2)
abbrev G8 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(1, 3), (2, 3)]
example : GraphCalc.order G8 = 4 := by decide
example : GraphCalc.size G8 = 2 := by decide
example : SimpleGraph.minDegree G8 = 0 := by decide
example : SimpleGraph.maxDegree G8 = 2 := by decide
example : GraphCalc.indepNum G8 = 3 := by decide
example : GraphCalc.cliqueNum G8 = 2 := by decide
example : GraphCalc.dominationNumber G8 = 2 := by decide
example : GraphCalc.independentDominationNumber G8 = 2 := by decide
example : GraphCalc.slaterNumber G8 = 2 := by decide
example : GraphCalc.annihilationNumber G8 = 3 := by decide
example : GraphCalc.zeroForcingNumber G8 = 2 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G8 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G8 := by decide
example : GraphCalc.vertexCoverNumber G8 = 1 := by decide
example : GraphCalc.subTotalDominationNumber G8 = 3 := by decide
example : GraphCalc.romanDominationNumber G8 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G8 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G8 := by decide
example : ¬ GraphCalc.IsTreeClass G8 := by decide
example : GraphCalc.IsClawFreeClass G8 := by decide
example : GraphCalc.IsCographClass G8 := by decide
example : ¬ GraphCalc.IsRegularClass G8 := by decide
example : ¬ GraphCalc.IsCubicClass G8 := by decide
example : GraphCalc.IsSubcubicClass G8 := by decide
example : ¬ GraphCalc.IsEulerianClass G8 := by decide
example : GraphCalc.IsTriangleFreeClass G8 := by decide
example : GraphCalc.IsK4FreeClass G8 := by decide
example : GraphCalc.IsNontrivialClass G8 := by decide
example : GraphCalc.IsBipartiteClass G8 := by decide

-- C`  (n=4, m=2)
abbrev G9 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 1), (2, 3)]
example : GraphCalc.order G9 = 4 := by decide
example : GraphCalc.size G9 = 2 := by decide
example : SimpleGraph.minDegree G9 = 1 := by decide
example : SimpleGraph.maxDegree G9 = 1 := by decide
example : GraphCalc.indepNum G9 = 2 := by decide
example : GraphCalc.cliqueNum G9 = 2 := by decide
example : GraphCalc.dominationNumber G9 = 2 := by decide
example : GraphCalc.independentDominationNumber G9 = 2 := by decide
example : GraphCalc.slaterNumber G9 = 2 := by decide
example : GraphCalc.annihilationNumber G9 = 2 := by decide
example : GraphCalc.zeroForcingNumber G9 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G9 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G9 := by decide
example : GraphCalc.vertexCoverNumber G9 = 2 := by decide
example : GraphCalc.totalDominationNumber G9 = 4 := by decide
example : GraphCalc.edgeCoverNumber G9 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G9 = 4 := by decide
example : GraphCalc.romanDominationNumber G9 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G9 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G9 := by decide
example : ¬ GraphCalc.IsTreeClass G9 := by decide
example : GraphCalc.IsClawFreeClass G9 := by decide
example : GraphCalc.IsCographClass G9 := by decide
example : GraphCalc.IsRegularClass G9 := by decide
example : ¬ GraphCalc.IsCubicClass G9 := by decide
example : GraphCalc.IsSubcubicClass G9 := by decide
example : ¬ GraphCalc.IsEulerianClass G9 := by decide
example : GraphCalc.IsTriangleFreeClass G9 := by decide
example : GraphCalc.IsK4FreeClass G9 := by decide
example : GraphCalc.IsNontrivialClass G9 := by decide
example : GraphCalc.IsBipartiteClass G9 := by decide

-- CJ  (n=4, m=3)
abbrev G10 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G10 = 4 := by decide
example : GraphCalc.size G10 = 3 := by decide
example : SimpleGraph.minDegree G10 = 0 := by decide
example : SimpleGraph.maxDegree G10 = 2 := by decide
example : GraphCalc.indepNum G10 = 2 := by decide
example : GraphCalc.cliqueNum G10 = 3 := by decide
example : GraphCalc.dominationNumber G10 = 2 := by decide
example : GraphCalc.independentDominationNumber G10 = 2 := by decide
example : GraphCalc.slaterNumber G10 = 2 := by decide
example : GraphCalc.annihilationNumber G10 = 2 := by decide
example : GraphCalc.zeroForcingNumber G10 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G10 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G10 := by decide
example : GraphCalc.vertexCoverNumber G10 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G10 = 2 := by decide
example : GraphCalc.romanDominationNumber G10 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G10 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G10 := by decide
example : ¬ GraphCalc.IsTreeClass G10 := by decide
example : GraphCalc.IsClawFreeClass G10 := by decide
example : GraphCalc.IsCographClass G10 := by decide
example : ¬ GraphCalc.IsRegularClass G10 := by decide
example : ¬ GraphCalc.IsCubicClass G10 := by decide
example : GraphCalc.IsSubcubicClass G10 := by decide
example : ¬ GraphCalc.IsEulerianClass G10 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G10 := by decide
example : GraphCalc.IsK4FreeClass G10 := by decide
example : GraphCalc.IsNontrivialClass G10 := by decide
example : ¬ GraphCalc.IsBipartiteClass G10 := by decide

-- CF  (n=4, m=3)
abbrev G11 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 3), (1, 3), (2, 3)]
example : GraphCalc.order G11 = 4 := by decide
example : GraphCalc.size G11 = 3 := by decide
example : SimpleGraph.minDegree G11 = 1 := by decide
example : SimpleGraph.maxDegree G11 = 3 := by decide
example : GraphCalc.indepNum G11 = 3 := by decide
example : GraphCalc.cliqueNum G11 = 2 := by decide
example : GraphCalc.dominationNumber G11 = 1 := by decide
example : GraphCalc.independentDominationNumber G11 = 1 := by decide
example : GraphCalc.slaterNumber G11 = 1 := by decide
example : GraphCalc.annihilationNumber G11 = 3 := by decide
example : GraphCalc.zeroForcingNumber G11 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G11 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G11 = 3 := by decide
example : GraphCalc.vertexCoverNumber G11 = 1 := by decide
example : GraphCalc.totalDominationNumber G11 = 2 := by decide
example : GraphCalc.edgeCoverNumber G11 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G11 = 2 := by decide
example : GraphCalc.romanDominationNumber G11 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G11 = 3 := by decide
example : GraphCalc.radius G11 = 1 := by decide
example : GraphCalc.IsConnectedClass G11 := by decide
example : GraphCalc.IsTreeClass G11 := by decide
example : ¬ GraphCalc.IsClawFreeClass G11 := by decide
example : GraphCalc.IsCographClass G11 := by decide
example : ¬ GraphCalc.IsRegularClass G11 := by decide
example : ¬ GraphCalc.IsCubicClass G11 := by decide
example : GraphCalc.IsSubcubicClass G11 := by decide
example : ¬ GraphCalc.IsEulerianClass G11 := by decide
example : GraphCalc.IsTriangleFreeClass G11 := by decide
example : GraphCalc.IsK4FreeClass G11 := by decide
example : GraphCalc.IsNontrivialClass G11 := by decide
example : GraphCalc.IsBipartiteClass G11 := by decide

-- Ck  (n=4, m=3)
abbrev G12 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 1), (0, 3), (1, 2)]
example : GraphCalc.order G12 = 4 := by decide
example : GraphCalc.size G12 = 3 := by decide
example : SimpleGraph.minDegree G12 = 1 := by decide
example : SimpleGraph.maxDegree G12 = 2 := by decide
example : GraphCalc.indepNum G12 = 2 := by decide
example : GraphCalc.cliqueNum G12 = 2 := by decide
example : GraphCalc.dominationNumber G12 = 2 := by decide
example : GraphCalc.independentDominationNumber G12 = 2 := by decide
example : GraphCalc.slaterNumber G12 = 2 := by decide
example : GraphCalc.annihilationNumber G12 = 2 := by decide
example : GraphCalc.zeroForcingNumber G12 = 1 := by decide
example : GraphCalc.totalZeroForcingNumber G12 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G12 = 1 := by decide
example : GraphCalc.vertexCoverNumber G12 = 2 := by decide
example : GraphCalc.totalDominationNumber G12 = 2 := by decide
example : GraphCalc.edgeCoverNumber G12 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G12 = 2 := by decide
example : GraphCalc.romanDominationNumber G12 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G12 = 5 := by decide
example : GraphCalc.radius G12 = 2 := by decide
example : GraphCalc.IsConnectedClass G12 := by decide
example : GraphCalc.IsTreeClass G12 := by decide
example : GraphCalc.IsClawFreeClass G12 := by decide
example : ¬ GraphCalc.IsCographClass G12 := by decide
example : ¬ GraphCalc.IsRegularClass G12 := by decide
example : ¬ GraphCalc.IsCubicClass G12 := by decide
example : GraphCalc.IsSubcubicClass G12 := by decide
example : ¬ GraphCalc.IsEulerianClass G12 := by decide
example : GraphCalc.IsTriangleFreeClass G12 := by decide
example : GraphCalc.IsK4FreeClass G12 := by decide
example : GraphCalc.IsNontrivialClass G12 := by decide
example : GraphCalc.IsBipartiteClass G12 := by decide

-- CN  (n=4, m=4)
abbrev G13 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 3), (1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G13 = 4 := by decide
example : GraphCalc.size G13 = 4 := by decide
example : SimpleGraph.minDegree G13 = 1 := by decide
example : SimpleGraph.maxDegree G13 = 3 := by decide
example : GraphCalc.indepNum G13 = 2 := by decide
example : GraphCalc.cliqueNum G13 = 3 := by decide
example : GraphCalc.dominationNumber G13 = 1 := by decide
example : GraphCalc.independentDominationNumber G13 = 1 := by decide
example : GraphCalc.slaterNumber G13 = 1 := by decide
example : GraphCalc.annihilationNumber G13 = 2 := by decide
example : GraphCalc.zeroForcingNumber G13 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G13 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G13 = 2 := by decide
example : GraphCalc.vertexCoverNumber G13 = 2 := by decide
example : GraphCalc.totalDominationNumber G13 = 2 := by decide
example : GraphCalc.edgeCoverNumber G13 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G13 = 2 := by decide
example : GraphCalc.romanDominationNumber G13 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G13 = 3 := by decide
example : GraphCalc.radius G13 = 1 := by decide
example : GraphCalc.IsConnectedClass G13 := by decide
example : ¬ GraphCalc.IsTreeClass G13 := by decide
example : GraphCalc.IsClawFreeClass G13 := by decide
example : GraphCalc.IsCographClass G13 := by decide
example : ¬ GraphCalc.IsRegularClass G13 := by decide
example : ¬ GraphCalc.IsCubicClass G13 := by decide
example : GraphCalc.IsSubcubicClass G13 := by decide
example : ¬ GraphCalc.IsEulerianClass G13 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G13 := by decide
example : GraphCalc.IsK4FreeClass G13 := by decide
example : GraphCalc.IsNontrivialClass G13 := by decide
example : ¬ GraphCalc.IsBipartiteClass G13 := by decide

-- Cl  (n=4, m=4)
abbrev G14 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 1), (0, 3), (1, 2), (2, 3)]
example : GraphCalc.order G14 = 4 := by decide
example : GraphCalc.size G14 = 4 := by decide
example : SimpleGraph.minDegree G14 = 2 := by decide
example : SimpleGraph.maxDegree G14 = 2 := by decide
example : GraphCalc.indepNum G14 = 2 := by decide
example : GraphCalc.cliqueNum G14 = 2 := by decide
example : GraphCalc.dominationNumber G14 = 2 := by decide
example : GraphCalc.independentDominationNumber G14 = 2 := by decide
example : GraphCalc.slaterNumber G14 = 2 := by decide
example : GraphCalc.annihilationNumber G14 = 2 := by decide
example : GraphCalc.zeroForcingNumber G14 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G14 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G14 = 2 := by decide
example : GraphCalc.vertexCoverNumber G14 = 2 := by decide
example : GraphCalc.totalDominationNumber G14 = 2 := by decide
example : GraphCalc.edgeCoverNumber G14 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G14 = 2 := by decide
example : GraphCalc.romanDominationNumber G14 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G14 = 4 := by decide
example : GraphCalc.radius G14 = 2 := by decide
example : GraphCalc.IsConnectedClass G14 := by decide
example : ¬ GraphCalc.IsTreeClass G14 := by decide
example : GraphCalc.IsClawFreeClass G14 := by decide
example : GraphCalc.IsCographClass G14 := by decide
example : GraphCalc.IsRegularClass G14 := by decide
example : ¬ GraphCalc.IsCubicClass G14 := by decide
example : GraphCalc.IsSubcubicClass G14 := by decide
example : GraphCalc.IsEulerianClass G14 := by decide
example : GraphCalc.IsTriangleFreeClass G14 := by decide
example : GraphCalc.IsK4FreeClass G14 := by decide
example : GraphCalc.IsNontrivialClass G14 := by decide
example : GraphCalc.IsBipartiteClass G14 := by decide

-- C|  (n=4, m=5)
abbrev G15 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
example : GraphCalc.order G15 = 4 := by decide
example : GraphCalc.size G15 = 5 := by decide
example : SimpleGraph.minDegree G15 = 2 := by decide
example : SimpleGraph.maxDegree G15 = 3 := by decide
example : GraphCalc.indepNum G15 = 2 := by decide
example : GraphCalc.cliqueNum G15 = 3 := by decide
example : GraphCalc.dominationNumber G15 = 1 := by decide
example : GraphCalc.independentDominationNumber G15 = 1 := by decide
example : GraphCalc.slaterNumber G15 = 1 := by decide
example : GraphCalc.annihilationNumber G15 = 2 := by decide
example : GraphCalc.zeroForcingNumber G15 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G15 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G15 = 2 := by decide
example : GraphCalc.vertexCoverNumber G15 = 2 := by decide
example : GraphCalc.totalDominationNumber G15 = 2 := by decide
example : GraphCalc.edgeCoverNumber G15 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G15 = 2 := by decide
example : GraphCalc.romanDominationNumber G15 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G15 = 3 := by decide
example : GraphCalc.radius G15 = 1 := by decide
example : GraphCalc.IsConnectedClass G15 := by decide
example : ¬ GraphCalc.IsTreeClass G15 := by decide
example : GraphCalc.IsClawFreeClass G15 := by decide
example : GraphCalc.IsCographClass G15 := by decide
example : ¬ GraphCalc.IsRegularClass G15 := by decide
example : ¬ GraphCalc.IsCubicClass G15 := by decide
example : GraphCalc.IsSubcubicClass G15 := by decide
example : ¬ GraphCalc.IsEulerianClass G15 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G15 := by decide
example : GraphCalc.IsK4FreeClass G15 := by decide
example : GraphCalc.IsNontrivialClass G15 := by decide
example : ¬ GraphCalc.IsBipartiteClass G15 := by decide

-- C~  (n=4, m=6)
abbrev G16 : SimpleGraph (Fin 4) := GraphCalc.ofEdges 4 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G16 = 4 := by decide
example : GraphCalc.size G16 = 6 := by decide
example : SimpleGraph.minDegree G16 = 3 := by decide
example : SimpleGraph.maxDegree G16 = 3 := by decide
example : GraphCalc.indepNum G16 = 1 := by decide
example : GraphCalc.cliqueNum G16 = 4 := by decide
example : GraphCalc.dominationNumber G16 = 1 := by decide
example : GraphCalc.independentDominationNumber G16 = 1 := by decide
example : GraphCalc.slaterNumber G16 = 1 := by decide
example : GraphCalc.annihilationNumber G16 = 2 := by decide
example : GraphCalc.zeroForcingNumber G16 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G16 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G16 = 3 := by decide
example : GraphCalc.vertexCoverNumber G16 = 3 := by decide
example : GraphCalc.totalDominationNumber G16 = 2 := by decide
example : GraphCalc.edgeCoverNumber G16 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G16 = 2 := by decide
example : GraphCalc.romanDominationNumber G16 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G16 = 3 := by decide
example : GraphCalc.radius G16 = 1 := by decide
example : GraphCalc.IsConnectedClass G16 := by decide
example : ¬ GraphCalc.IsTreeClass G16 := by decide
example : GraphCalc.IsClawFreeClass G16 := by decide
example : GraphCalc.IsCographClass G16 := by decide
example : GraphCalc.IsRegularClass G16 := by decide
example : GraphCalc.IsCubicClass G16 := by decide
example : GraphCalc.IsSubcubicClass G16 := by decide
example : ¬ GraphCalc.IsEulerianClass G16 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G16 := by decide
example : ¬ GraphCalc.IsK4FreeClass G16 := by decide
example : GraphCalc.IsNontrivialClass G16 := by decide
example : ¬ GraphCalc.IsBipartiteClass G16 := by decide

-- D??  (n=5, m=0)
abbrev G17 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 []
example : GraphCalc.order G17 = 5 := by decide
example : GraphCalc.size G17 = 0 := by decide
example : SimpleGraph.minDegree G17 = 0 := by decide
example : SimpleGraph.maxDegree G17 = 0 := by decide
example : GraphCalc.indepNum G17 = 5 := by decide
example : GraphCalc.cliqueNum G17 = 1 := by decide
example : GraphCalc.dominationNumber G17 = 5 := by decide
example : GraphCalc.independentDominationNumber G17 = 5 := by decide
example : GraphCalc.slaterNumber G17 = 5 := by decide
example : GraphCalc.annihilationNumber G17 = 5 := by decide
example : GraphCalc.zeroForcingNumber G17 = 5 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G17 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G17 := by decide
example : GraphCalc.vertexCoverNumber G17 = 0 := by decide
example : GraphCalc.romanDominationNumber G17 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G17 = 10 := by decide
example : ¬ GraphCalc.IsConnectedClass G17 := by decide
example : ¬ GraphCalc.IsTreeClass G17 := by decide
example : GraphCalc.IsClawFreeClass G17 := by decide
example : GraphCalc.IsCographClass G17 := by decide
example : GraphCalc.IsRegularClass G17 := by decide
example : ¬ GraphCalc.IsCubicClass G17 := by decide
example : GraphCalc.IsSubcubicClass G17 := by decide
example : ¬ GraphCalc.IsEulerianClass G17 := by decide
example : GraphCalc.IsTriangleFreeClass G17 := by decide
example : GraphCalc.IsK4FreeClass G17 := by decide
example : GraphCalc.IsNontrivialClass G17 := by decide
example : GraphCalc.IsBipartiteClass G17 := by decide

-- D?C  (n=5, m=1)
abbrev G18 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(3, 4)]
example : GraphCalc.order G18 = 5 := by decide
example : GraphCalc.size G18 = 1 := by decide
example : SimpleGraph.minDegree G18 = 0 := by decide
example : SimpleGraph.maxDegree G18 = 1 := by decide
example : GraphCalc.indepNum G18 = 4 := by decide
example : GraphCalc.cliqueNum G18 = 2 := by decide
example : GraphCalc.dominationNumber G18 = 4 := by decide
example : GraphCalc.independentDominationNumber G18 = 4 := by decide
example : GraphCalc.slaterNumber G18 = 3 := by decide
example : GraphCalc.annihilationNumber G18 = 4 := by decide
example : GraphCalc.zeroForcingNumber G18 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G18 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G18 := by decide
example : GraphCalc.vertexCoverNumber G18 = 1 := by decide
example : GraphCalc.romanDominationNumber G18 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G18 = 9 := by decide
example : ¬ GraphCalc.IsConnectedClass G18 := by decide
example : ¬ GraphCalc.IsTreeClass G18 := by decide
example : GraphCalc.IsClawFreeClass G18 := by decide
example : GraphCalc.IsCographClass G18 := by decide
example : ¬ GraphCalc.IsRegularClass G18 := by decide
example : ¬ GraphCalc.IsCubicClass G18 := by decide
example : GraphCalc.IsSubcubicClass G18 := by decide
example : ¬ GraphCalc.IsEulerianClass G18 := by decide
example : GraphCalc.IsTriangleFreeClass G18 := by decide
example : GraphCalc.IsK4FreeClass G18 := by decide
example : GraphCalc.IsNontrivialClass G18 := by decide
example : GraphCalc.IsBipartiteClass G18 := by decide

-- Dg?  (n=5, m=2)
abbrev G19 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (1, 2)]
example : GraphCalc.order G19 = 5 := by decide
example : GraphCalc.size G19 = 2 := by decide
example : SimpleGraph.minDegree G19 = 0 := by decide
example : SimpleGraph.maxDegree G19 = 2 := by decide
example : GraphCalc.indepNum G19 = 4 := by decide
example : GraphCalc.cliqueNum G19 = 2 := by decide
example : GraphCalc.dominationNumber G19 = 3 := by decide
example : GraphCalc.independentDominationNumber G19 = 3 := by decide
example : GraphCalc.slaterNumber G19 = 2 := by decide
example : GraphCalc.annihilationNumber G19 = 4 := by decide
example : GraphCalc.zeroForcingNumber G19 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G19 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G19 := by decide
example : GraphCalc.vertexCoverNumber G19 = 1 := by decide
example : GraphCalc.romanDominationNumber G19 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G19 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G19 := by decide
example : ¬ GraphCalc.IsTreeClass G19 := by decide
example : GraphCalc.IsClawFreeClass G19 := by decide
example : GraphCalc.IsCographClass G19 := by decide
example : ¬ GraphCalc.IsRegularClass G19 := by decide
example : ¬ GraphCalc.IsCubicClass G19 := by decide
example : GraphCalc.IsSubcubicClass G19 := by decide
example : ¬ GraphCalc.IsEulerianClass G19 := by decide
example : GraphCalc.IsTriangleFreeClass G19 := by decide
example : GraphCalc.IsK4FreeClass G19 := by decide
example : GraphCalc.IsNontrivialClass G19 := by decide
example : GraphCalc.IsBipartiteClass G19 := by decide

-- DOC  (n=5, m=2)
abbrev G20 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 2), (3, 4)]
example : GraphCalc.order G20 = 5 := by decide
example : GraphCalc.size G20 = 2 := by decide
example : SimpleGraph.minDegree G20 = 0 := by decide
example : SimpleGraph.maxDegree G20 = 1 := by decide
example : GraphCalc.indepNum G20 = 3 := by decide
example : GraphCalc.cliqueNum G20 = 2 := by decide
example : GraphCalc.dominationNumber G20 = 3 := by decide
example : GraphCalc.independentDominationNumber G20 = 3 := by decide
example : GraphCalc.slaterNumber G20 = 3 := by decide
example : GraphCalc.annihilationNumber G20 = 3 := by decide
example : GraphCalc.zeroForcingNumber G20 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G20 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G20 := by decide
example : GraphCalc.vertexCoverNumber G20 = 2 := by decide
example : GraphCalc.romanDominationNumber G20 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G20 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G20 := by decide
example : ¬ GraphCalc.IsTreeClass G20 := by decide
example : GraphCalc.IsClawFreeClass G20 := by decide
example : GraphCalc.IsCographClass G20 := by decide
example : ¬ GraphCalc.IsRegularClass G20 := by decide
example : ¬ GraphCalc.IsCubicClass G20 := by decide
example : GraphCalc.IsSubcubicClass G20 := by decide
example : ¬ GraphCalc.IsEulerianClass G20 := by decide
example : GraphCalc.IsTriangleFreeClass G20 := by decide
example : GraphCalc.IsK4FreeClass G20 := by decide
example : GraphCalc.IsNontrivialClass G20 := by decide
example : GraphCalc.IsBipartiteClass G20 := by decide

-- Dw?  (n=5, m=3)
abbrev G21 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 2), (1, 2)]
example : GraphCalc.order G21 = 5 := by decide
example : GraphCalc.size G21 = 3 := by decide
example : SimpleGraph.minDegree G21 = 0 := by decide
example : SimpleGraph.maxDegree G21 = 2 := by decide
example : GraphCalc.indepNum G21 = 3 := by decide
example : GraphCalc.cliqueNum G21 = 3 := by decide
example : GraphCalc.dominationNumber G21 = 3 := by decide
example : GraphCalc.independentDominationNumber G21 = 3 := by decide
example : GraphCalc.slaterNumber G21 = 2 := by decide
example : GraphCalc.annihilationNumber G21 = 3 := by decide
example : GraphCalc.zeroForcingNumber G21 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G21 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G21 := by decide
example : GraphCalc.vertexCoverNumber G21 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G21 = 3 := by decide
example : GraphCalc.romanDominationNumber G21 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G21 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G21 := by decide
example : ¬ GraphCalc.IsTreeClass G21 := by decide
example : GraphCalc.IsClawFreeClass G21 := by decide
example : GraphCalc.IsCographClass G21 := by decide
example : ¬ GraphCalc.IsRegularClass G21 := by decide
example : ¬ GraphCalc.IsCubicClass G21 := by decide
example : GraphCalc.IsSubcubicClass G21 := by decide
example : ¬ GraphCalc.IsEulerianClass G21 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G21 := by decide
example : GraphCalc.IsK4FreeClass G21 := by decide
example : GraphCalc.IsNontrivialClass G21 := by decide
example : ¬ GraphCalc.IsBipartiteClass G21 := by decide

-- DBC  (n=5, m=3)
abbrev G22 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G22 = 5 := by decide
example : GraphCalc.size G22 = 3 := by decide
example : SimpleGraph.minDegree G22 = 0 := by decide
example : SimpleGraph.maxDegree G22 = 3 := by decide
example : GraphCalc.indepNum G22 = 4 := by decide
example : GraphCalc.cliqueNum G22 = 2 := by decide
example : GraphCalc.dominationNumber G22 = 2 := by decide
example : GraphCalc.independentDominationNumber G22 = 2 := by decide
example : GraphCalc.slaterNumber G22 = 2 := by decide
example : GraphCalc.annihilationNumber G22 = 4 := by decide
example : GraphCalc.zeroForcingNumber G22 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G22 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G22 := by decide
example : GraphCalc.vertexCoverNumber G22 = 1 := by decide
example : GraphCalc.subTotalDominationNumber G22 = 3 := by decide
example : GraphCalc.romanDominationNumber G22 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G22 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G22 := by decide
example : ¬ GraphCalc.IsTreeClass G22 := by decide
example : ¬ GraphCalc.IsClawFreeClass G22 := by decide
example : GraphCalc.IsCographClass G22 := by decide
example : ¬ GraphCalc.IsRegularClass G22 := by decide
example : ¬ GraphCalc.IsCubicClass G22 := by decide
example : GraphCalc.IsSubcubicClass G22 := by decide
example : ¬ GraphCalc.IsEulerianClass G22 := by decide
example : GraphCalc.IsTriangleFreeClass G22 := by decide
example : GraphCalc.IsK4FreeClass G22 := by decide
example : GraphCalc.IsNontrivialClass G22 := by decide
example : GraphCalc.IsBipartiteClass G22 := by decide

-- D@c  (n=5, m=3)
abbrev G23 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (2, 3), (3, 4)]
example : GraphCalc.order G23 = 5 := by decide
example : GraphCalc.size G23 = 3 := by decide
example : SimpleGraph.minDegree G23 = 0 := by decide
example : SimpleGraph.maxDegree G23 = 2 := by decide
example : GraphCalc.indepNum G23 = 3 := by decide
example : GraphCalc.cliqueNum G23 = 2 := by decide
example : GraphCalc.dominationNumber G23 = 3 := by decide
example : GraphCalc.independentDominationNumber G23 = 3 := by decide
example : GraphCalc.slaterNumber G23 = 2 := by decide
example : GraphCalc.annihilationNumber G23 = 3 := by decide
example : GraphCalc.zeroForcingNumber G23 = 2 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G23 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G23 := by decide
example : GraphCalc.vertexCoverNumber G23 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G23 = 3 := by decide
example : GraphCalc.romanDominationNumber G23 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G23 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G23 := by decide
example : ¬ GraphCalc.IsTreeClass G23 := by decide
example : GraphCalc.IsClawFreeClass G23 := by decide
example : ¬ GraphCalc.IsCographClass G23 := by decide
example : ¬ GraphCalc.IsRegularClass G23 := by decide
example : ¬ GraphCalc.IsCubicClass G23 := by decide
example : GraphCalc.IsSubcubicClass G23 := by decide
example : ¬ GraphCalc.IsEulerianClass G23 := by decide
example : GraphCalc.IsTriangleFreeClass G23 := by decide
example : GraphCalc.IsK4FreeClass G23 := by decide
example : GraphCalc.IsNontrivialClass G23 := by decide
example : GraphCalc.IsBipartiteClass G23 := by decide

-- DgC  (n=5, m=3)
abbrev G24 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (1, 2), (3, 4)]
example : GraphCalc.order G24 = 5 := by decide
example : GraphCalc.size G24 = 3 := by decide
example : SimpleGraph.minDegree G24 = 1 := by decide
example : SimpleGraph.maxDegree G24 = 2 := by decide
example : GraphCalc.indepNum G24 = 3 := by decide
example : GraphCalc.cliqueNum G24 = 2 := by decide
example : GraphCalc.dominationNumber G24 = 2 := by decide
example : GraphCalc.independentDominationNumber G24 = 2 := by decide
example : GraphCalc.slaterNumber G24 = 2 := by decide
example : GraphCalc.annihilationNumber G24 = 3 := by decide
example : GraphCalc.zeroForcingNumber G24 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G24 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G24 := by decide
example : GraphCalc.vertexCoverNumber G24 = 2 := by decide
example : GraphCalc.totalDominationNumber G24 = 4 := by decide
example : GraphCalc.edgeCoverNumber G24 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G24 = 4 := by decide
example : GraphCalc.romanDominationNumber G24 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G24 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G24 := by decide
example : ¬ GraphCalc.IsTreeClass G24 := by decide
example : GraphCalc.IsClawFreeClass G24 := by decide
example : GraphCalc.IsCographClass G24 := by decide
example : ¬ GraphCalc.IsRegularClass G24 := by decide
example : ¬ GraphCalc.IsCubicClass G24 := by decide
example : GraphCalc.IsSubcubicClass G24 := by decide
example : ¬ GraphCalc.IsEulerianClass G24 := by decide
example : GraphCalc.IsTriangleFreeClass G24 := by decide
example : GraphCalc.IsK4FreeClass G24 := by decide
example : GraphCalc.IsNontrivialClass G24 := by decide
example : GraphCalc.IsBipartiteClass G24 := by decide

-- DJC  (n=5, m=4)
abbrev G25 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(1, 2), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G25 = 5 := by decide
example : GraphCalc.size G25 = 4 := by decide
example : SimpleGraph.minDegree G25 = 0 := by decide
example : SimpleGraph.maxDegree G25 = 3 := by decide
example : GraphCalc.indepNum G25 = 3 := by decide
example : GraphCalc.cliqueNum G25 = 3 := by decide
example : GraphCalc.dominationNumber G25 = 2 := by decide
example : GraphCalc.independentDominationNumber G25 = 2 := by decide
example : GraphCalc.slaterNumber G25 = 2 := by decide
example : GraphCalc.annihilationNumber G25 = 3 := by decide
example : GraphCalc.zeroForcingNumber G25 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G25 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G25 := by decide
example : GraphCalc.vertexCoverNumber G25 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G25 = 2 := by decide
example : GraphCalc.romanDominationNumber G25 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G25 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G25 := by decide
example : ¬ GraphCalc.IsTreeClass G25 := by decide
example : GraphCalc.IsClawFreeClass G25 := by decide
example : GraphCalc.IsCographClass G25 := by decide
example : ¬ GraphCalc.IsRegularClass G25 := by decide
example : ¬ GraphCalc.IsCubicClass G25 := by decide
example : GraphCalc.IsSubcubicClass G25 := by decide
example : ¬ GraphCalc.IsEulerianClass G25 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G25 := by decide
example : GraphCalc.IsK4FreeClass G25 := by decide
example : GraphCalc.IsNontrivialClass G25 := by decide
example : ¬ GraphCalc.IsBipartiteClass G25 := by decide

-- Dl?  (n=5, m=4)
abbrev G26 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (1, 2), (2, 3)]
example : GraphCalc.order G26 = 5 := by decide
example : GraphCalc.size G26 = 4 := by decide
example : SimpleGraph.minDegree G26 = 0 := by decide
example : SimpleGraph.maxDegree G26 = 2 := by decide
example : GraphCalc.indepNum G26 = 3 := by decide
example : GraphCalc.cliqueNum G26 = 2 := by decide
example : GraphCalc.dominationNumber G26 = 3 := by decide
example : GraphCalc.independentDominationNumber G26 = 3 := by decide
example : GraphCalc.slaterNumber G26 = 2 := by decide
example : GraphCalc.annihilationNumber G26 = 3 := by decide
example : GraphCalc.zeroForcingNumber G26 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G26 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G26 := by decide
example : GraphCalc.vertexCoverNumber G26 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G26 = 3 := by decide
example : GraphCalc.romanDominationNumber G26 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G26 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G26 := by decide
example : ¬ GraphCalc.IsTreeClass G26 := by decide
example : GraphCalc.IsClawFreeClass G26 := by decide
example : GraphCalc.IsCographClass G26 := by decide
example : ¬ GraphCalc.IsRegularClass G26 := by decide
example : ¬ GraphCalc.IsCubicClass G26 := by decide
example : GraphCalc.IsSubcubicClass G26 := by decide
example : ¬ GraphCalc.IsEulerianClass G26 := by decide
example : GraphCalc.IsTriangleFreeClass G26 := by decide
example : GraphCalc.IsK4FreeClass G26 := by decide
example : GraphCalc.IsNontrivialClass G26 := by decide
example : GraphCalc.IsBipartiteClass G26 := by decide

-- D?{  (n=5, m=4)
abbrev G27 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (1, 4), (2, 4), (3, 4)]
example : GraphCalc.order G27 = 5 := by decide
example : GraphCalc.size G27 = 4 := by decide
example : SimpleGraph.minDegree G27 = 1 := by decide
example : SimpleGraph.maxDegree G27 = 4 := by decide
example : GraphCalc.indepNum G27 = 4 := by decide
example : GraphCalc.cliqueNum G27 = 2 := by decide
example : GraphCalc.dominationNumber G27 = 1 := by decide
example : GraphCalc.independentDominationNumber G27 = 1 := by decide
example : GraphCalc.slaterNumber G27 = 1 := by decide
example : GraphCalc.annihilationNumber G27 = 4 := by decide
example : GraphCalc.zeroForcingNumber G27 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G27 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G27 = 4 := by decide
example : GraphCalc.vertexCoverNumber G27 = 1 := by decide
example : GraphCalc.totalDominationNumber G27 = 2 := by decide
example : GraphCalc.edgeCoverNumber G27 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G27 = 2 := by decide
example : GraphCalc.romanDominationNumber G27 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G27 = 3 := by decide
example : GraphCalc.radius G27 = 1 := by decide
example : GraphCalc.IsConnectedClass G27 := by decide
example : GraphCalc.IsTreeClass G27 := by decide
example : ¬ GraphCalc.IsClawFreeClass G27 := by decide
example : GraphCalc.IsCographClass G27 := by decide
example : ¬ GraphCalc.IsRegularClass G27 := by decide
example : ¬ GraphCalc.IsCubicClass G27 := by decide
example : ¬ GraphCalc.IsSubcubicClass G27 := by decide
example : ¬ GraphCalc.IsEulerianClass G27 := by decide
example : GraphCalc.IsTriangleFreeClass G27 := by decide
example : GraphCalc.IsK4FreeClass G27 := by decide
example : GraphCalc.IsNontrivialClass G27 := by decide
example : GraphCalc.IsBipartiteClass G27 := by decide

-- DBc  (n=5, m=4)
abbrev G28 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G28 = 5 := by decide
example : GraphCalc.size G28 = 4 := by decide
example : SimpleGraph.minDegree G28 = 1 := by decide
example : SimpleGraph.maxDegree G28 = 3 := by decide
example : GraphCalc.indepNum G28 = 3 := by decide
example : GraphCalc.cliqueNum G28 = 2 := by decide
example : GraphCalc.dominationNumber G28 = 2 := by decide
example : GraphCalc.independentDominationNumber G28 = 2 := by decide
example : GraphCalc.slaterNumber G28 = 2 := by decide
example : GraphCalc.annihilationNumber G28 = 3 := by decide
example : GraphCalc.zeroForcingNumber G28 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G28 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G28 = 3 := by decide
example : GraphCalc.vertexCoverNumber G28 = 2 := by decide
example : GraphCalc.totalDominationNumber G28 = 2 := by decide
example : GraphCalc.edgeCoverNumber G28 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G28 = 2 := by decide
example : GraphCalc.romanDominationNumber G28 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G28 = 5 := by decide
example : GraphCalc.radius G28 = 2 := by decide
example : GraphCalc.IsConnectedClass G28 := by decide
example : GraphCalc.IsTreeClass G28 := by decide
example : ¬ GraphCalc.IsClawFreeClass G28 := by decide
example : ¬ GraphCalc.IsCographClass G28 := by decide
example : ¬ GraphCalc.IsRegularClass G28 := by decide
example : ¬ GraphCalc.IsCubicClass G28 := by decide
example : GraphCalc.IsSubcubicClass G28 := by decide
example : ¬ GraphCalc.IsEulerianClass G28 := by decide
example : GraphCalc.IsTriangleFreeClass G28 := by decide
example : GraphCalc.IsK4FreeClass G28 := by decide
example : GraphCalc.IsNontrivialClass G28 := by decide
example : GraphCalc.IsBipartiteClass G28 := by decide

-- Dh_  (n=5, m=4)
abbrev G29 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 4), (1, 2), (2, 3)]
example : GraphCalc.order G29 = 5 := by decide
example : GraphCalc.size G29 = 4 := by decide
example : SimpleGraph.minDegree G29 = 1 := by decide
example : SimpleGraph.maxDegree G29 = 2 := by decide
example : GraphCalc.indepNum G29 = 3 := by decide
example : GraphCalc.cliqueNum G29 = 2 := by decide
example : GraphCalc.dominationNumber G29 = 2 := by decide
example : GraphCalc.independentDominationNumber G29 = 2 := by decide
example : GraphCalc.slaterNumber G29 = 2 := by decide
example : GraphCalc.annihilationNumber G29 = 3 := by decide
example : GraphCalc.zeroForcingNumber G29 = 1 := by decide
example : GraphCalc.totalZeroForcingNumber G29 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G29 = 1 := by decide
example : GraphCalc.vertexCoverNumber G29 = 2 := by decide
example : GraphCalc.totalDominationNumber G29 = 3 := by decide
example : GraphCalc.edgeCoverNumber G29 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G29 = 3 := by decide
example : GraphCalc.romanDominationNumber G29 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G29 = 6 := by decide
example : GraphCalc.radius G29 = 2 := by decide
example : GraphCalc.IsConnectedClass G29 := by decide
example : GraphCalc.IsTreeClass G29 := by decide
example : GraphCalc.IsClawFreeClass G29 := by decide
example : ¬ GraphCalc.IsCographClass G29 := by decide
example : ¬ GraphCalc.IsRegularClass G29 := by decide
example : ¬ GraphCalc.IsCubicClass G29 := by decide
example : GraphCalc.IsSubcubicClass G29 := by decide
example : ¬ GraphCalc.IsEulerianClass G29 := by decide
example : GraphCalc.IsTriangleFreeClass G29 := by decide
example : GraphCalc.IsK4FreeClass G29 := by decide
example : GraphCalc.IsNontrivialClass G29 := by decide
example : GraphCalc.IsBipartiteClass G29 := by decide

-- DwC  (n=5, m=4)
abbrev G30 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 2), (1, 2), (3, 4)]
example : GraphCalc.order G30 = 5 := by decide
example : GraphCalc.size G30 = 4 := by decide
example : SimpleGraph.minDegree G30 = 1 := by decide
example : SimpleGraph.maxDegree G30 = 2 := by decide
example : GraphCalc.indepNum G30 = 2 := by decide
example : GraphCalc.cliqueNum G30 = 3 := by decide
example : GraphCalc.dominationNumber G30 = 2 := by decide
example : GraphCalc.independentDominationNumber G30 = 2 := by decide
example : GraphCalc.slaterNumber G30 = 2 := by decide
example : GraphCalc.annihilationNumber G30 = 3 := by decide
example : GraphCalc.zeroForcingNumber G30 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G30 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G30 := by decide
example : GraphCalc.vertexCoverNumber G30 = 3 := by decide
example : GraphCalc.totalDominationNumber G30 = 4 := by decide
example : GraphCalc.edgeCoverNumber G30 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G30 = 3 := by decide
example : GraphCalc.romanDominationNumber G30 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G30 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G30 := by decide
example : ¬ GraphCalc.IsTreeClass G30 := by decide
example : GraphCalc.IsClawFreeClass G30 := by decide
example : GraphCalc.IsCographClass G30 := by decide
example : ¬ GraphCalc.IsRegularClass G30 := by decide
example : ¬ GraphCalc.IsCubicClass G30 := by decide
example : GraphCalc.IsSubcubicClass G30 := by decide
example : ¬ GraphCalc.IsEulerianClass G30 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G30 := by decide
example : GraphCalc.IsK4FreeClass G30 := by decide
example : GraphCalc.IsNontrivialClass G30 := by decide
example : ¬ GraphCalc.IsBipartiteClass G30 := by decide

-- D|?  (n=5, m=5)
abbrev G31 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
example : GraphCalc.order G31 = 5 := by decide
example : GraphCalc.size G31 = 5 := by decide
example : SimpleGraph.minDegree G31 = 0 := by decide
example : SimpleGraph.maxDegree G31 = 3 := by decide
example : GraphCalc.indepNum G31 = 3 := by decide
example : GraphCalc.cliqueNum G31 = 3 := by decide
example : GraphCalc.dominationNumber G31 = 2 := by decide
example : GraphCalc.independentDominationNumber G31 = 2 := by decide
example : GraphCalc.slaterNumber G31 = 2 := by decide
example : GraphCalc.annihilationNumber G31 = 3 := by decide
example : GraphCalc.zeroForcingNumber G31 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G31 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G31 := by decide
example : GraphCalc.vertexCoverNumber G31 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G31 = 2 := by decide
example : GraphCalc.romanDominationNumber G31 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G31 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G31 := by decide
example : ¬ GraphCalc.IsTreeClass G31 := by decide
example : GraphCalc.IsClawFreeClass G31 := by decide
example : GraphCalc.IsCographClass G31 := by decide
example : ¬ GraphCalc.IsRegularClass G31 := by decide
example : ¬ GraphCalc.IsCubicClass G31 := by decide
example : GraphCalc.IsSubcubicClass G31 := by decide
example : ¬ GraphCalc.IsEulerianClass G31 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G31 := by decide
example : GraphCalc.IsK4FreeClass G31 := by decide
example : GraphCalc.IsNontrivialClass G31 := by decide
example : ¬ GraphCalc.IsBipartiteClass G31 := by decide

-- D@{  (n=5, m=5)
abbrev G32 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G32 = 5 := by decide
example : GraphCalc.size G32 = 5 := by decide
example : SimpleGraph.minDegree G32 = 1 := by decide
example : SimpleGraph.maxDegree G32 = 4 := by decide
example : GraphCalc.indepNum G32 = 3 := by decide
example : GraphCalc.cliqueNum G32 = 3 := by decide
example : GraphCalc.dominationNumber G32 = 1 := by decide
example : GraphCalc.independentDominationNumber G32 = 1 := by decide
example : GraphCalc.slaterNumber G32 = 1 := by decide
example : GraphCalc.annihilationNumber G32 = 3 := by decide
example : GraphCalc.zeroForcingNumber G32 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G32 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G32 = 3 := by decide
example : GraphCalc.vertexCoverNumber G32 = 2 := by decide
example : GraphCalc.totalDominationNumber G32 = 2 := by decide
example : GraphCalc.edgeCoverNumber G32 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G32 = 2 := by decide
example : GraphCalc.romanDominationNumber G32 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G32 = 3 := by decide
example : GraphCalc.radius G32 = 1 := by decide
example : GraphCalc.IsConnectedClass G32 := by decide
example : ¬ GraphCalc.IsTreeClass G32 := by decide
example : ¬ GraphCalc.IsClawFreeClass G32 := by decide
example : GraphCalc.IsCographClass G32 := by decide
example : ¬ GraphCalc.IsRegularClass G32 := by decide
example : ¬ GraphCalc.IsCubicClass G32 := by decide
example : ¬ GraphCalc.IsSubcubicClass G32 := by decide
example : ¬ GraphCalc.IsEulerianClass G32 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G32 := by decide
example : GraphCalc.IsK4FreeClass G32 := by decide
example : GraphCalc.IsNontrivialClass G32 := by decide
example : ¬ GraphCalc.IsBipartiteClass G32 := by decide

-- Dx_  (n=5, m=5)
abbrev G33 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3)]
example : GraphCalc.order G33 = 5 := by decide
example : GraphCalc.size G33 = 5 := by decide
example : SimpleGraph.minDegree G33 = 1 := by decide
example : SimpleGraph.maxDegree G33 = 3 := by decide
example : GraphCalc.indepNum G33 = 3 := by decide
example : GraphCalc.cliqueNum G33 = 3 := by decide
example : GraphCalc.dominationNumber G33 = 2 := by decide
example : GraphCalc.independentDominationNumber G33 = 2 := by decide
example : GraphCalc.slaterNumber G33 = 2 := by decide
example : GraphCalc.annihilationNumber G33 = 3 := by decide
example : GraphCalc.zeroForcingNumber G33 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G33 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G33 = 2 := by decide
example : GraphCalc.vertexCoverNumber G33 = 2 := by decide
example : GraphCalc.totalDominationNumber G33 = 2 := by decide
example : GraphCalc.edgeCoverNumber G33 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G33 = 2 := by decide
example : GraphCalc.romanDominationNumber G33 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G33 = 5 := by decide
example : GraphCalc.radius G33 = 2 := by decide
example : GraphCalc.IsConnectedClass G33 := by decide
example : ¬ GraphCalc.IsTreeClass G33 := by decide
example : GraphCalc.IsClawFreeClass G33 := by decide
example : ¬ GraphCalc.IsCographClass G33 := by decide
example : ¬ GraphCalc.IsRegularClass G33 := by decide
example : ¬ GraphCalc.IsCubicClass G33 := by decide
example : GraphCalc.IsSubcubicClass G33 := by decide
example : ¬ GraphCalc.IsEulerianClass G33 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G33 := by decide
example : GraphCalc.IsK4FreeClass G33 := by decide
example : GraphCalc.IsNontrivialClass G33 := by decide
example : ¬ GraphCalc.IsBipartiteClass G33 := by decide

-- DJc  (n=5, m=5)
abbrev G34 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (1, 2), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G34 = 5 := by decide
example : GraphCalc.size G34 = 5 := by decide
example : SimpleGraph.minDegree G34 = 1 := by decide
example : SimpleGraph.maxDegree G34 = 3 := by decide
example : GraphCalc.indepNum G34 = 2 := by decide
example : GraphCalc.cliqueNum G34 = 3 := by decide
example : GraphCalc.dominationNumber G34 = 2 := by decide
example : GraphCalc.independentDominationNumber G34 = 2 := by decide
example : GraphCalc.slaterNumber G34 = 2 := by decide
example : GraphCalc.annihilationNumber G34 = 3 := by decide
example : GraphCalc.zeroForcingNumber G34 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G34 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G34 = 2 := by decide
example : GraphCalc.vertexCoverNumber G34 = 3 := by decide
example : GraphCalc.totalDominationNumber G34 = 2 := by decide
example : GraphCalc.edgeCoverNumber G34 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G34 = 2 := by decide
example : GraphCalc.romanDominationNumber G34 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G34 = 5 := by decide
example : GraphCalc.radius G34 = 2 := by decide
example : GraphCalc.IsConnectedClass G34 := by decide
example : ¬ GraphCalc.IsTreeClass G34 := by decide
example : GraphCalc.IsClawFreeClass G34 := by decide
example : ¬ GraphCalc.IsCographClass G34 := by decide
example : ¬ GraphCalc.IsRegularClass G34 := by decide
example : ¬ GraphCalc.IsCubicClass G34 := by decide
example : GraphCalc.IsSubcubicClass G34 := by decide
example : ¬ GraphCalc.IsEulerianClass G34 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G34 := by decide
example : GraphCalc.IsK4FreeClass G34 := by decide
example : GraphCalc.IsNontrivialClass G34 := by decide
example : ¬ GraphCalc.IsBipartiteClass G34 := by decide

-- DbW  (n=5, m=5)
abbrev G35 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G35 = 5 := by decide
example : GraphCalc.size G35 = 5 := by decide
example : SimpleGraph.minDegree G35 = 1 := by decide
example : SimpleGraph.maxDegree G35 = 3 := by decide
example : GraphCalc.indepNum G35 = 3 := by decide
example : GraphCalc.cliqueNum G35 = 2 := by decide
example : GraphCalc.dominationNumber G35 = 2 := by decide
example : GraphCalc.independentDominationNumber G35 = 2 := by decide
example : GraphCalc.slaterNumber G35 = 2 := by decide
example : GraphCalc.annihilationNumber G35 = 3 := by decide
example : GraphCalc.zeroForcingNumber G35 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G35 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G35 = 2 := by decide
example : GraphCalc.vertexCoverNumber G35 = 2 := by decide
example : GraphCalc.totalDominationNumber G35 = 2 := by decide
example : GraphCalc.edgeCoverNumber G35 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G35 = 2 := by decide
example : GraphCalc.romanDominationNumber G35 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G35 = 5 := by decide
example : GraphCalc.radius G35 = 2 := by decide
example : GraphCalc.IsConnectedClass G35 := by decide
example : ¬ GraphCalc.IsTreeClass G35 := by decide
example : ¬ GraphCalc.IsClawFreeClass G35 := by decide
example : ¬ GraphCalc.IsCographClass G35 := by decide
example : ¬ GraphCalc.IsRegularClass G35 := by decide
example : ¬ GraphCalc.IsCubicClass G35 := by decide
example : GraphCalc.IsSubcubicClass G35 := by decide
example : ¬ GraphCalc.IsEulerianClass G35 := by decide
example : GraphCalc.IsTriangleFreeClass G35 := by decide
example : GraphCalc.IsK4FreeClass G35 := by decide
example : GraphCalc.IsNontrivialClass G35 := by decide
example : GraphCalc.IsBipartiteClass G35 := by decide

-- Dhc  (n=5, m=5)
abbrev G36 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)]
example : GraphCalc.order G36 = 5 := by decide
example : GraphCalc.size G36 = 5 := by decide
example : SimpleGraph.minDegree G36 = 2 := by decide
example : SimpleGraph.maxDegree G36 = 2 := by decide
example : GraphCalc.indepNum G36 = 2 := by decide
example : GraphCalc.cliqueNum G36 = 2 := by decide
example : GraphCalc.dominationNumber G36 = 2 := by decide
example : GraphCalc.independentDominationNumber G36 = 2 := by decide
example : GraphCalc.slaterNumber G36 = 2 := by decide
example : GraphCalc.annihilationNumber G36 = 2 := by decide
example : GraphCalc.zeroForcingNumber G36 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G36 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G36 = 2 := by decide
example : GraphCalc.vertexCoverNumber G36 = 3 := by decide
example : GraphCalc.totalDominationNumber G36 = 3 := by decide
example : GraphCalc.edgeCoverNumber G36 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G36 = 3 := by decide
example : GraphCalc.romanDominationNumber G36 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G36 = 6 := by decide
example : GraphCalc.radius G36 = 2 := by decide
example : GraphCalc.IsConnectedClass G36 := by decide
example : ¬ GraphCalc.IsTreeClass G36 := by decide
example : GraphCalc.IsClawFreeClass G36 := by decide
example : ¬ GraphCalc.IsCographClass G36 := by decide
example : GraphCalc.IsRegularClass G36 := by decide
example : ¬ GraphCalc.IsCubicClass G36 := by decide
example : GraphCalc.IsSubcubicClass G36 := by decide
example : GraphCalc.IsEulerianClass G36 := by decide
example : GraphCalc.IsTriangleFreeClass G36 := by decide
example : GraphCalc.IsK4FreeClass G36 := by decide
example : GraphCalc.IsNontrivialClass G36 := by decide
example : ¬ GraphCalc.IsBipartiteClass G36 := by decide

-- Des  (n=5, m=6)
abbrev G37 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (0, 4), (1, 3), (1, 4), (3, 4)]
example : GraphCalc.order G37 = 5 := by decide
example : GraphCalc.size G37 = 6 := by decide
example : SimpleGraph.minDegree G37 = 0 := by decide
example : SimpleGraph.maxDegree G37 = 3 := by decide
example : GraphCalc.indepNum G37 = 2 := by decide
example : GraphCalc.cliqueNum G37 = 4 := by decide
example : GraphCalc.dominationNumber G37 = 2 := by decide
example : GraphCalc.independentDominationNumber G37 = 2 := by decide
example : GraphCalc.slaterNumber G37 = 2 := by decide
example : GraphCalc.annihilationNumber G37 = 3 := by decide
example : GraphCalc.zeroForcingNumber G37 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G37 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G37 := by decide
example : GraphCalc.vertexCoverNumber G37 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G37 = 2 := by decide
example : GraphCalc.romanDominationNumber G37 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G37 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G37 := by decide
example : ¬ GraphCalc.IsTreeClass G37 := by decide
example : GraphCalc.IsClawFreeClass G37 := by decide
example : GraphCalc.IsCographClass G37 := by decide
example : ¬ GraphCalc.IsRegularClass G37 := by decide
example : ¬ GraphCalc.IsCubicClass G37 := by decide
example : GraphCalc.IsSubcubicClass G37 := by decide
example : ¬ GraphCalc.IsEulerianClass G37 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G37 := by decide
example : ¬ GraphCalc.IsK4FreeClass G37 := by decide
example : GraphCalc.IsNontrivialClass G37 := by decide
example : ¬ GraphCalc.IsBipartiteClass G37 := by decide

-- DjW  (n=5, m=6)
abbrev G38 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G38 = 5 := by decide
example : GraphCalc.size G38 = 6 := by decide
example : SimpleGraph.minDegree G38 = 1 := by decide
example : SimpleGraph.maxDegree G38 = 4 := by decide
example : GraphCalc.indepNum G38 = 3 := by decide
example : GraphCalc.cliqueNum G38 = 3 := by decide
example : GraphCalc.dominationNumber G38 = 1 := by decide
example : GraphCalc.independentDominationNumber G38 = 1 := by decide
example : GraphCalc.slaterNumber G38 = 1 := by decide
example : GraphCalc.annihilationNumber G38 = 3 := by decide
example : GraphCalc.zeroForcingNumber G38 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G38 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G38 = 2 := by decide
example : GraphCalc.vertexCoverNumber G38 = 2 := by decide
example : GraphCalc.totalDominationNumber G38 = 2 := by decide
example : GraphCalc.edgeCoverNumber G38 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G38 = 2 := by decide
example : GraphCalc.romanDominationNumber G38 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G38 = 3 := by decide
example : GraphCalc.radius G38 = 1 := by decide
example : GraphCalc.IsConnectedClass G38 := by decide
example : ¬ GraphCalc.IsTreeClass G38 := by decide
example : ¬ GraphCalc.IsClawFreeClass G38 := by decide
example : GraphCalc.IsCographClass G38 := by decide
example : ¬ GraphCalc.IsRegularClass G38 := by decide
example : ¬ GraphCalc.IsCubicClass G38 := by decide
example : ¬ GraphCalc.IsSubcubicClass G38 := by decide
example : ¬ GraphCalc.IsEulerianClass G38 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G38 := by decide
example : GraphCalc.IsK4FreeClass G38 := by decide
example : GraphCalc.IsNontrivialClass G38 := by decide
example : ¬ GraphCalc.IsBipartiteClass G38 := by decide

-- Db[  (n=5, m=6)
abbrev G39 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G39 = 5 := by decide
example : GraphCalc.size G39 = 6 := by decide
example : SimpleGraph.minDegree G39 = 1 := by decide
example : SimpleGraph.maxDegree G39 = 3 := by decide
example : GraphCalc.indepNum G39 = 2 := by decide
example : GraphCalc.cliqueNum G39 = 3 := by decide
example : GraphCalc.dominationNumber G39 = 2 := by decide
example : GraphCalc.independentDominationNumber G39 = 2 := by decide
example : GraphCalc.slaterNumber G39 = 2 := by decide
example : GraphCalc.annihilationNumber G39 = 3 := by decide
example : GraphCalc.zeroForcingNumber G39 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G39 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G39 = 2 := by decide
example : GraphCalc.vertexCoverNumber G39 = 3 := by decide
example : GraphCalc.totalDominationNumber G39 = 2 := by decide
example : GraphCalc.edgeCoverNumber G39 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G39 = 2 := by decide
example : GraphCalc.romanDominationNumber G39 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G39 = 5 := by decide
example : GraphCalc.radius G39 = 2 := by decide
example : GraphCalc.IsConnectedClass G39 := by decide
example : ¬ GraphCalc.IsTreeClass G39 := by decide
example : GraphCalc.IsClawFreeClass G39 := by decide
example : ¬ GraphCalc.IsCographClass G39 := by decide
example : ¬ GraphCalc.IsRegularClass G39 := by decide
example : ¬ GraphCalc.IsCubicClass G39 := by decide
example : GraphCalc.IsSubcubicClass G39 := by decide
example : ¬ GraphCalc.IsEulerianClass G39 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G39 := by decide
example : GraphCalc.IsK4FreeClass G39 := by decide
example : GraphCalc.IsNontrivialClass G39 := by decide
example : ¬ GraphCalc.IsBipartiteClass G39 := by decide

-- D`{  (n=5, m=6)
abbrev G40 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 4), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G40 = 5 := by decide
example : GraphCalc.size G40 = 6 := by decide
example : SimpleGraph.minDegree G40 = 2 := by decide
example : SimpleGraph.maxDegree G40 = 4 := by decide
example : GraphCalc.indepNum G40 = 2 := by decide
example : GraphCalc.cliqueNum G40 = 3 := by decide
example : GraphCalc.dominationNumber G40 = 1 := by decide
example : GraphCalc.independentDominationNumber G40 = 1 := by decide
example : GraphCalc.slaterNumber G40 = 1 := by decide
example : GraphCalc.annihilationNumber G40 = 3 := by decide
example : GraphCalc.zeroForcingNumber G40 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G40 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G40 = 3 := by decide
example : GraphCalc.vertexCoverNumber G40 = 3 := by decide
example : GraphCalc.totalDominationNumber G40 = 2 := by decide
example : GraphCalc.edgeCoverNumber G40 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G40 = 2 := by decide
example : GraphCalc.romanDominationNumber G40 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G40 = 3 := by decide
example : GraphCalc.radius G40 = 1 := by decide
example : GraphCalc.IsConnectedClass G40 := by decide
example : ¬ GraphCalc.IsTreeClass G40 := by decide
example : GraphCalc.IsClawFreeClass G40 := by decide
example : GraphCalc.IsCographClass G40 := by decide
example : ¬ GraphCalc.IsRegularClass G40 := by decide
example : ¬ GraphCalc.IsCubicClass G40 := by decide
example : ¬ GraphCalc.IsSubcubicClass G40 := by decide
example : GraphCalc.IsEulerianClass G40 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G40 := by decide
example : GraphCalc.IsK4FreeClass G40 := by decide
example : GraphCalc.IsNontrivialClass G40 := by decide
example : ¬ GraphCalc.IsBipartiteClass G40 := by decide

-- Dlc  (n=5, m=6)
abbrev G41 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4)]
example : GraphCalc.order G41 = 5 := by decide
example : GraphCalc.size G41 = 6 := by decide
example : SimpleGraph.minDegree G41 = 2 := by decide
example : SimpleGraph.maxDegree G41 = 3 := by decide
example : GraphCalc.indepNum G41 = 2 := by decide
example : GraphCalc.cliqueNum G41 = 3 := by decide
example : GraphCalc.dominationNumber G41 = 2 := by decide
example : GraphCalc.independentDominationNumber G41 = 2 := by decide
example : GraphCalc.slaterNumber G41 = 2 := by decide
example : GraphCalc.annihilationNumber G41 = 3 := by decide
example : GraphCalc.zeroForcingNumber G41 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G41 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G41 = 2 := by decide
example : GraphCalc.vertexCoverNumber G41 = 3 := by decide
example : GraphCalc.totalDominationNumber G41 = 2 := by decide
example : GraphCalc.edgeCoverNumber G41 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G41 = 2 := by decide
example : GraphCalc.romanDominationNumber G41 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G41 = 5 := by decide
example : GraphCalc.radius G41 = 2 := by decide
example : GraphCalc.IsConnectedClass G41 := by decide
example : ¬ GraphCalc.IsTreeClass G41 := by decide
example : GraphCalc.IsClawFreeClass G41 := by decide
example : ¬ GraphCalc.IsCographClass G41 := by decide
example : ¬ GraphCalc.IsRegularClass G41 := by decide
example : ¬ GraphCalc.IsCubicClass G41 := by decide
example : GraphCalc.IsSubcubicClass G41 := by decide
example : ¬ GraphCalc.IsEulerianClass G41 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G41 := by decide
example : GraphCalc.IsK4FreeClass G41 := by decide
example : GraphCalc.IsNontrivialClass G41 := by decide
example : ¬ GraphCalc.IsBipartiteClass G41 := by decide

-- D]o  (n=5, m=6)
abbrev G42 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]
example : GraphCalc.order G42 = 5 := by decide
example : GraphCalc.size G42 = 6 := by decide
example : SimpleGraph.minDegree G42 = 2 := by decide
example : SimpleGraph.maxDegree G42 = 3 := by decide
example : GraphCalc.indepNum G42 = 3 := by decide
example : GraphCalc.cliqueNum G42 = 2 := by decide
example : GraphCalc.dominationNumber G42 = 2 := by decide
example : GraphCalc.independentDominationNumber G42 = 2 := by decide
example : GraphCalc.slaterNumber G42 = 2 := by decide
example : GraphCalc.annihilationNumber G42 = 3 := by decide
example : GraphCalc.zeroForcingNumber G42 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G42 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G42 = 3 := by decide
example : GraphCalc.vertexCoverNumber G42 = 2 := by decide
example : GraphCalc.totalDominationNumber G42 = 2 := by decide
example : GraphCalc.edgeCoverNumber G42 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G42 = 2 := by decide
example : GraphCalc.romanDominationNumber G42 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G42 = 4 := by decide
example : GraphCalc.radius G42 = 2 := by decide
example : GraphCalc.IsConnectedClass G42 := by decide
example : ¬ GraphCalc.IsTreeClass G42 := by decide
example : ¬ GraphCalc.IsClawFreeClass G42 := by decide
example : GraphCalc.IsCographClass G42 := by decide
example : ¬ GraphCalc.IsRegularClass G42 := by decide
example : ¬ GraphCalc.IsCubicClass G42 := by decide
example : GraphCalc.IsSubcubicClass G42 := by decide
example : ¬ GraphCalc.IsEulerianClass G42 := by decide
example : GraphCalc.IsTriangleFreeClass G42 := by decide
example : GraphCalc.IsK4FreeClass G42 := by decide
example : GraphCalc.IsNontrivialClass G42 := by decide
example : GraphCalc.IsBipartiteClass G42 := by decide

-- DJ{  (n=5, m=7)
abbrev G43 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G43 = 5 := by decide
example : GraphCalc.size G43 = 7 := by decide
example : SimpleGraph.minDegree G43 = 1 := by decide
example : SimpleGraph.maxDegree G43 = 4 := by decide
example : GraphCalc.indepNum G43 = 2 := by decide
example : GraphCalc.cliqueNum G43 = 4 := by decide
example : GraphCalc.dominationNumber G43 = 1 := by decide
example : GraphCalc.independentDominationNumber G43 = 1 := by decide
example : GraphCalc.slaterNumber G43 = 1 := by decide
example : GraphCalc.annihilationNumber G43 = 3 := by decide
example : GraphCalc.zeroForcingNumber G43 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G43 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G43 = 3 := by decide
example : GraphCalc.vertexCoverNumber G43 = 3 := by decide
example : GraphCalc.totalDominationNumber G43 = 2 := by decide
example : GraphCalc.edgeCoverNumber G43 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G43 = 2 := by decide
example : GraphCalc.romanDominationNumber G43 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G43 = 3 := by decide
example : GraphCalc.radius G43 = 1 := by decide
example : GraphCalc.IsConnectedClass G43 := by decide
example : ¬ GraphCalc.IsTreeClass G43 := by decide
example : GraphCalc.IsClawFreeClass G43 := by decide
example : GraphCalc.IsCographClass G43 := by decide
example : ¬ GraphCalc.IsRegularClass G43 := by decide
example : ¬ GraphCalc.IsCubicClass G43 := by decide
example : ¬ GraphCalc.IsSubcubicClass G43 := by decide
example : ¬ GraphCalc.IsEulerianClass G43 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G43 := by decide
example : ¬ GraphCalc.IsK4FreeClass G43 := by decide
example : GraphCalc.IsNontrivialClass G43 := by decide
example : ¬ GraphCalc.IsBipartiteClass G43 := by decide

-- DF{  (n=5, m=7)
abbrev G44 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G44 = 5 := by decide
example : GraphCalc.size G44 = 7 := by decide
example : SimpleGraph.minDegree G44 = 2 := by decide
example : SimpleGraph.maxDegree G44 = 4 := by decide
example : GraphCalc.indepNum G44 = 3 := by decide
example : GraphCalc.cliqueNum G44 = 3 := by decide
example : GraphCalc.dominationNumber G44 = 1 := by decide
example : GraphCalc.independentDominationNumber G44 = 1 := by decide
example : GraphCalc.slaterNumber G44 = 1 := by decide
example : GraphCalc.annihilationNumber G44 = 3 := by decide
example : GraphCalc.zeroForcingNumber G44 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G44 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G44 = 3 := by decide
example : GraphCalc.vertexCoverNumber G44 = 2 := by decide
example : GraphCalc.totalDominationNumber G44 = 2 := by decide
example : GraphCalc.edgeCoverNumber G44 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G44 = 2 := by decide
example : GraphCalc.romanDominationNumber G44 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G44 = 3 := by decide
example : GraphCalc.radius G44 = 1 := by decide
example : GraphCalc.IsConnectedClass G44 := by decide
example : ¬ GraphCalc.IsTreeClass G44 := by decide
example : ¬ GraphCalc.IsClawFreeClass G44 := by decide
example : GraphCalc.IsCographClass G44 := by decide
example : ¬ GraphCalc.IsRegularClass G44 := by decide
example : ¬ GraphCalc.IsCubicClass G44 := by decide
example : ¬ GraphCalc.IsSubcubicClass G44 := by decide
example : GraphCalc.IsEulerianClass G44 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G44 := by decide
example : GraphCalc.IsK4FreeClass G44 := by decide
example : GraphCalc.IsNontrivialClass G44 := by decide
example : ¬ GraphCalc.IsBipartiteClass G44 := by decide

-- Djs  (n=5, m=7)
abbrev G45 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
example : GraphCalc.order G45 = 5 := by decide
example : GraphCalc.size G45 = 7 := by decide
example : SimpleGraph.minDegree G45 = 2 := by decide
example : SimpleGraph.maxDegree G45 = 4 := by decide
example : GraphCalc.indepNum G45 = 2 := by decide
example : GraphCalc.cliqueNum G45 = 3 := by decide
example : GraphCalc.dominationNumber G45 = 1 := by decide
example : GraphCalc.independentDominationNumber G45 = 1 := by decide
example : GraphCalc.slaterNumber G45 = 1 := by decide
example : GraphCalc.annihilationNumber G45 = 3 := by decide
example : GraphCalc.zeroForcingNumber G45 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G45 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G45 = 2 := by decide
example : GraphCalc.vertexCoverNumber G45 = 3 := by decide
example : GraphCalc.totalDominationNumber G45 = 2 := by decide
example : GraphCalc.edgeCoverNumber G45 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G45 = 2 := by decide
example : GraphCalc.romanDominationNumber G45 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G45 = 3 := by decide
example : GraphCalc.radius G45 = 1 := by decide
example : GraphCalc.IsConnectedClass G45 := by decide
example : ¬ GraphCalc.IsTreeClass G45 := by decide
example : GraphCalc.IsClawFreeClass G45 := by decide
example : ¬ GraphCalc.IsCographClass G45 := by decide
example : ¬ GraphCalc.IsRegularClass G45 := by decide
example : ¬ GraphCalc.IsCubicClass G45 := by decide
example : ¬ GraphCalc.IsSubcubicClass G45 := by decide
example : ¬ GraphCalc.IsEulerianClass G45 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G45 := by decide
example : GraphCalc.IsK4FreeClass G45 := by decide
example : GraphCalc.IsNontrivialClass G45 := by decide
example : ¬ GraphCalc.IsBipartiteClass G45 := by decide

-- D]w  (n=5, m=7)
abbrev G46 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4)]
example : GraphCalc.order G46 = 5 := by decide
example : GraphCalc.size G46 = 7 := by decide
example : SimpleGraph.minDegree G46 = 2 := by decide
example : SimpleGraph.maxDegree G46 = 3 := by decide
example : GraphCalc.indepNum G46 = 2 := by decide
example : GraphCalc.cliqueNum G46 = 3 := by decide
example : GraphCalc.dominationNumber G46 = 2 := by decide
example : GraphCalc.independentDominationNumber G46 = 2 := by decide
example : GraphCalc.slaterNumber G46 = 2 := by decide
example : GraphCalc.annihilationNumber G46 = 2 := by decide
example : GraphCalc.zeroForcingNumber G46 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G46 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G46 = 3 := by decide
example : GraphCalc.vertexCoverNumber G46 = 3 := by decide
example : GraphCalc.totalDominationNumber G46 = 2 := by decide
example : GraphCalc.edgeCoverNumber G46 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G46 = 2 := by decide
example : GraphCalc.romanDominationNumber G46 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G46 = 4 := by decide
example : GraphCalc.radius G46 = 2 := by decide
example : GraphCalc.IsConnectedClass G46 := by decide
example : ¬ GraphCalc.IsTreeClass G46 := by decide
example : GraphCalc.IsClawFreeClass G46 := by decide
example : GraphCalc.IsCographClass G46 := by decide
example : ¬ GraphCalc.IsRegularClass G46 := by decide
example : ¬ GraphCalc.IsCubicClass G46 := by decide
example : GraphCalc.IsSubcubicClass G46 := by decide
example : ¬ GraphCalc.IsEulerianClass G46 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G46 := by decide
example : GraphCalc.IsK4FreeClass G46 := by decide
example : GraphCalc.IsNontrivialClass G46 := by decide
example : ¬ GraphCalc.IsBipartiteClass G46 := by decide

-- Df{  (n=5, m=8)
abbrev G47 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G47 = 5 := by decide
example : GraphCalc.size G47 = 8 := by decide
example : SimpleGraph.minDegree G47 = 2 := by decide
example : SimpleGraph.maxDegree G47 = 4 := by decide
example : GraphCalc.indepNum G47 = 2 := by decide
example : GraphCalc.cliqueNum G47 = 4 := by decide
example : GraphCalc.dominationNumber G47 = 1 := by decide
example : GraphCalc.independentDominationNumber G47 = 1 := by decide
example : GraphCalc.slaterNumber G47 = 1 := by decide
example : GraphCalc.annihilationNumber G47 = 3 := by decide
example : GraphCalc.zeroForcingNumber G47 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G47 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G47 = 3 := by decide
example : GraphCalc.vertexCoverNumber G47 = 3 := by decide
example : GraphCalc.totalDominationNumber G47 = 2 := by decide
example : GraphCalc.edgeCoverNumber G47 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G47 = 2 := by decide
example : GraphCalc.romanDominationNumber G47 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G47 = 3 := by decide
example : GraphCalc.radius G47 = 1 := by decide
example : GraphCalc.IsConnectedClass G47 := by decide
example : ¬ GraphCalc.IsTreeClass G47 := by decide
example : GraphCalc.IsClawFreeClass G47 := by decide
example : GraphCalc.IsCographClass G47 := by decide
example : ¬ GraphCalc.IsRegularClass G47 := by decide
example : ¬ GraphCalc.IsCubicClass G47 := by decide
example : ¬ GraphCalc.IsSubcubicClass G47 := by decide
example : ¬ GraphCalc.IsEulerianClass G47 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G47 := by decide
example : ¬ GraphCalc.IsK4FreeClass G47 := by decide
example : GraphCalc.IsNontrivialClass G47 := by decide
example : ¬ GraphCalc.IsBipartiteClass G47 := by decide

-- Dl{  (n=5, m=8)
abbrev G48 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G48 = 5 := by decide
example : GraphCalc.size G48 = 8 := by decide
example : SimpleGraph.minDegree G48 = 3 := by decide
example : SimpleGraph.maxDegree G48 = 4 := by decide
example : GraphCalc.indepNum G48 = 2 := by decide
example : GraphCalc.cliqueNum G48 = 3 := by decide
example : GraphCalc.dominationNumber G48 = 1 := by decide
example : GraphCalc.independentDominationNumber G48 = 1 := by decide
example : GraphCalc.slaterNumber G48 = 1 := by decide
example : GraphCalc.annihilationNumber G48 = 2 := by decide
example : GraphCalc.zeroForcingNumber G48 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G48 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G48 = 3 := by decide
example : GraphCalc.vertexCoverNumber G48 = 3 := by decide
example : GraphCalc.totalDominationNumber G48 = 2 := by decide
example : GraphCalc.edgeCoverNumber G48 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G48 = 2 := by decide
example : GraphCalc.romanDominationNumber G48 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G48 = 3 := by decide
example : GraphCalc.radius G48 = 1 := by decide
example : GraphCalc.IsConnectedClass G48 := by decide
example : ¬ GraphCalc.IsTreeClass G48 := by decide
example : GraphCalc.IsClawFreeClass G48 := by decide
example : GraphCalc.IsCographClass G48 := by decide
example : ¬ GraphCalc.IsRegularClass G48 := by decide
example : ¬ GraphCalc.IsCubicClass G48 := by decide
example : ¬ GraphCalc.IsSubcubicClass G48 := by decide
example : ¬ GraphCalc.IsEulerianClass G48 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G48 := by decide
example : GraphCalc.IsK4FreeClass G48 := by decide
example : GraphCalc.IsNontrivialClass G48 := by decide
example : ¬ GraphCalc.IsBipartiteClass G48 := by decide

-- Dn{  (n=5, m=9)
abbrev G49 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G49 = 5 := by decide
example : GraphCalc.size G49 = 9 := by decide
example : SimpleGraph.minDegree G49 = 3 := by decide
example : SimpleGraph.maxDegree G49 = 4 := by decide
example : GraphCalc.indepNum G49 = 2 := by decide
example : GraphCalc.cliqueNum G49 = 4 := by decide
example : GraphCalc.dominationNumber G49 = 1 := by decide
example : GraphCalc.independentDominationNumber G49 = 1 := by decide
example : GraphCalc.slaterNumber G49 = 1 := by decide
example : GraphCalc.annihilationNumber G49 = 2 := by decide
example : GraphCalc.zeroForcingNumber G49 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G49 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G49 = 3 := by decide
example : GraphCalc.vertexCoverNumber G49 = 3 := by decide
example : GraphCalc.totalDominationNumber G49 = 2 := by decide
example : GraphCalc.edgeCoverNumber G49 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G49 = 2 := by decide
example : GraphCalc.romanDominationNumber G49 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G49 = 3 := by decide
example : GraphCalc.radius G49 = 1 := by decide
example : GraphCalc.IsConnectedClass G49 := by decide
example : ¬ GraphCalc.IsTreeClass G49 := by decide
example : GraphCalc.IsClawFreeClass G49 := by decide
example : GraphCalc.IsCographClass G49 := by decide
example : ¬ GraphCalc.IsRegularClass G49 := by decide
example : ¬ GraphCalc.IsCubicClass G49 := by decide
example : ¬ GraphCalc.IsSubcubicClass G49 := by decide
example : ¬ GraphCalc.IsEulerianClass G49 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G49 := by decide
example : ¬ GraphCalc.IsK4FreeClass G49 := by decide
example : GraphCalc.IsNontrivialClass G49 := by decide
example : ¬ GraphCalc.IsBipartiteClass G49 := by decide

-- D~{  (n=5, m=10)
abbrev G50 : SimpleGraph (Fin 5) := GraphCalc.ofEdges 5 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G50 = 5 := by decide
example : GraphCalc.size G50 = 10 := by decide
example : SimpleGraph.minDegree G50 = 4 := by decide
example : SimpleGraph.maxDegree G50 = 4 := by decide
example : GraphCalc.indepNum G50 = 1 := by decide
example : GraphCalc.cliqueNum G50 = 5 := by decide
example : GraphCalc.dominationNumber G50 = 1 := by decide
example : GraphCalc.independentDominationNumber G50 = 1 := by decide
example : GraphCalc.slaterNumber G50 = 1 := by decide
example : GraphCalc.annihilationNumber G50 = 2 := by decide
example : GraphCalc.zeroForcingNumber G50 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G50 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G50 = 4 := by decide
example : GraphCalc.vertexCoverNumber G50 = 4 := by decide
example : GraphCalc.totalDominationNumber G50 = 2 := by decide
example : GraphCalc.edgeCoverNumber G50 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G50 = 2 := by decide
example : GraphCalc.romanDominationNumber G50 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G50 = 3 := by decide
example : GraphCalc.radius G50 = 1 := by decide
example : GraphCalc.IsConnectedClass G50 := by decide
example : ¬ GraphCalc.IsTreeClass G50 := by decide
example : GraphCalc.IsClawFreeClass G50 := by decide
example : GraphCalc.IsCographClass G50 := by decide
example : GraphCalc.IsRegularClass G50 := by decide
example : ¬ GraphCalc.IsCubicClass G50 := by decide
example : ¬ GraphCalc.IsSubcubicClass G50 := by decide
example : GraphCalc.IsEulerianClass G50 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G50 := by decide
example : ¬ GraphCalc.IsK4FreeClass G50 := by decide
example : GraphCalc.IsNontrivialClass G50 := by decide
example : ¬ GraphCalc.IsBipartiteClass G50 := by decide

-- E???  (n=6, m=0)
abbrev G51 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 []
example : GraphCalc.order G51 = 6 := by decide
example : GraphCalc.size G51 = 0 := by decide
example : SimpleGraph.minDegree G51 = 0 := by decide
example : SimpleGraph.maxDegree G51 = 0 := by decide
example : GraphCalc.indepNum G51 = 6 := by decide
example : GraphCalc.cliqueNum G51 = 1 := by decide
example : GraphCalc.dominationNumber G51 = 6 := by decide
example : GraphCalc.independentDominationNumber G51 = 6 := by decide
example : GraphCalc.slaterNumber G51 = 6 := by decide
example : GraphCalc.annihilationNumber G51 = 6 := by decide
example : GraphCalc.zeroForcingNumber G51 = 6 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G51 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G51 := by decide
example : GraphCalc.vertexCoverNumber G51 = 0 := by decide
example : GraphCalc.romanDominationNumber G51 = 6 := by decide
example : GraphCalc.doubleRomanDominationNumber G51 = 12 := by decide
example : ¬ GraphCalc.IsConnectedClass G51 := by decide
example : ¬ GraphCalc.IsTreeClass G51 := by decide
example : GraphCalc.IsClawFreeClass G51 := by decide
example : GraphCalc.IsCographClass G51 := by decide
example : GraphCalc.IsRegularClass G51 := by decide
example : ¬ GraphCalc.IsCubicClass G51 := by decide
example : GraphCalc.IsSubcubicClass G51 := by decide
example : ¬ GraphCalc.IsEulerianClass G51 := by decide
example : GraphCalc.IsTriangleFreeClass G51 := by decide
example : GraphCalc.IsK4FreeClass G51 := by decide
example : GraphCalc.IsNontrivialClass G51 := by decide
example : GraphCalc.IsBipartiteClass G51 := by decide

-- E??G  (n=6, m=1)
abbrev G52 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(4, 5)]
example : GraphCalc.order G52 = 6 := by decide
example : GraphCalc.size G52 = 1 := by decide
example : SimpleGraph.minDegree G52 = 0 := by decide
example : SimpleGraph.maxDegree G52 = 1 := by decide
example : GraphCalc.indepNum G52 = 5 := by decide
example : GraphCalc.cliqueNum G52 = 2 := by decide
example : GraphCalc.dominationNumber G52 = 5 := by decide
example : GraphCalc.independentDominationNumber G52 = 5 := by decide
example : GraphCalc.slaterNumber G52 = 4 := by decide
example : GraphCalc.annihilationNumber G52 = 5 := by decide
example : GraphCalc.zeroForcingNumber G52 = 5 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G52 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G52 := by decide
example : GraphCalc.vertexCoverNumber G52 = 1 := by decide
example : GraphCalc.romanDominationNumber G52 = 6 := by decide
example : GraphCalc.doubleRomanDominationNumber G52 = 11 := by decide
example : ¬ GraphCalc.IsConnectedClass G52 := by decide
example : ¬ GraphCalc.IsTreeClass G52 := by decide
example : GraphCalc.IsClawFreeClass G52 := by decide
example : GraphCalc.IsCographClass G52 := by decide
example : ¬ GraphCalc.IsRegularClass G52 := by decide
example : ¬ GraphCalc.IsCubicClass G52 := by decide
example : GraphCalc.IsSubcubicClass G52 := by decide
example : ¬ GraphCalc.IsEulerianClass G52 := by decide
example : GraphCalc.IsTriangleFreeClass G52 := by decide
example : GraphCalc.IsK4FreeClass G52 := by decide
example : GraphCalc.IsNontrivialClass G52 := by decide
example : GraphCalc.IsBipartiteClass G52 := by decide

-- EC?G  (n=6, m=2)
abbrev G53 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (4, 5)]
example : GraphCalc.order G53 = 6 := by decide
example : GraphCalc.size G53 = 2 := by decide
example : SimpleGraph.minDegree G53 = 0 := by decide
example : SimpleGraph.maxDegree G53 = 1 := by decide
example : GraphCalc.indepNum G53 = 4 := by decide
example : GraphCalc.cliqueNum G53 = 2 := by decide
example : GraphCalc.dominationNumber G53 = 4 := by decide
example : GraphCalc.independentDominationNumber G53 = 4 := by decide
example : GraphCalc.slaterNumber G53 = 3 := by decide
example : GraphCalc.annihilationNumber G53 = 4 := by decide
example : GraphCalc.zeroForcingNumber G53 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G53 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G53 := by decide
example : GraphCalc.vertexCoverNumber G53 = 2 := by decide
example : GraphCalc.romanDominationNumber G53 = 6 := by decide
example : GraphCalc.doubleRomanDominationNumber G53 = 10 := by decide
example : ¬ GraphCalc.IsConnectedClass G53 := by decide
example : ¬ GraphCalc.IsTreeClass G53 := by decide
example : GraphCalc.IsClawFreeClass G53 := by decide
example : GraphCalc.IsCographClass G53 := by decide
example : ¬ GraphCalc.IsRegularClass G53 := by decide
example : ¬ GraphCalc.IsCubicClass G53 := by decide
example : GraphCalc.IsSubcubicClass G53 := by decide
example : ¬ GraphCalc.IsEulerianClass G53 := by decide
example : GraphCalc.IsTriangleFreeClass G53 := by decide
example : GraphCalc.IsK4FreeClass G53 := by decide
example : GraphCalc.IsNontrivialClass G53 := by decide
example : GraphCalc.IsBipartiteClass G53 := by decide

-- EI??  (n=6, m=2)
abbrev G54 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(1, 2), (1, 3)]
example : GraphCalc.order G54 = 6 := by decide
example : GraphCalc.size G54 = 2 := by decide
example : SimpleGraph.minDegree G54 = 0 := by decide
example : SimpleGraph.maxDegree G54 = 2 := by decide
example : GraphCalc.indepNum G54 = 5 := by decide
example : GraphCalc.cliqueNum G54 = 2 := by decide
example : GraphCalc.dominationNumber G54 = 4 := by decide
example : GraphCalc.independentDominationNumber G54 = 4 := by decide
example : GraphCalc.slaterNumber G54 = 3 := by decide
example : GraphCalc.annihilationNumber G54 = 5 := by decide
example : GraphCalc.zeroForcingNumber G54 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G54 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G54 := by decide
example : GraphCalc.vertexCoverNumber G54 = 1 := by decide
example : GraphCalc.romanDominationNumber G54 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G54 = 9 := by decide
example : ¬ GraphCalc.IsConnectedClass G54 := by decide
example : ¬ GraphCalc.IsTreeClass G54 := by decide
example : GraphCalc.IsClawFreeClass G54 := by decide
example : GraphCalc.IsCographClass G54 := by decide
example : ¬ GraphCalc.IsRegularClass G54 := by decide
example : ¬ GraphCalc.IsCubicClass G54 := by decide
example : GraphCalc.IsSubcubicClass G54 := by decide
example : ¬ GraphCalc.IsEulerianClass G54 := by decide
example : GraphCalc.IsTriangleFreeClass G54 := by decide
example : GraphCalc.IsK4FreeClass G54 := by decide
example : GraphCalc.IsNontrivialClass G54 := by decide
example : GraphCalc.IsBipartiteClass G54 := by decide

-- EJ??  (n=6, m=3)
abbrev G55 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G55 = 6 := by decide
example : GraphCalc.size G55 = 3 := by decide
example : SimpleGraph.minDegree G55 = 0 := by decide
example : SimpleGraph.maxDegree G55 = 2 := by decide
example : GraphCalc.indepNum G55 = 4 := by decide
example : GraphCalc.cliqueNum G55 = 3 := by decide
example : GraphCalc.dominationNumber G55 = 4 := by decide
example : GraphCalc.independentDominationNumber G55 = 4 := by decide
example : GraphCalc.slaterNumber G55 = 2 := by decide
example : GraphCalc.annihilationNumber G55 = 4 := by decide
example : GraphCalc.zeroForcingNumber G55 = 5 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G55 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G55 := by decide
example : GraphCalc.vertexCoverNumber G55 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G55 = 3 := by decide
example : GraphCalc.romanDominationNumber G55 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G55 = 9 := by decide
example : ¬ GraphCalc.IsConnectedClass G55 := by decide
example : ¬ GraphCalc.IsTreeClass G55 := by decide
example : GraphCalc.IsClawFreeClass G55 := by decide
example : GraphCalc.IsCographClass G55 := by decide
example : ¬ GraphCalc.IsRegularClass G55 := by decide
example : ¬ GraphCalc.IsCubicClass G55 := by decide
example : GraphCalc.IsSubcubicClass G55 := by decide
example : ¬ GraphCalc.IsEulerianClass G55 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G55 := by decide
example : GraphCalc.IsK4FreeClass G55 := by decide
example : GraphCalc.IsNontrivialClass G55 := by decide
example : ¬ GraphCalc.IsBipartiteClass G55 := by decide

-- ECa?  (n=6, m=3)
abbrev G56 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5)]
example : GraphCalc.order G56 = 6 := by decide
example : GraphCalc.size G56 = 3 := by decide
example : SimpleGraph.minDegree G56 = 0 := by decide
example : SimpleGraph.maxDegree G56 = 3 := by decide
example : GraphCalc.indepNum G56 = 5 := by decide
example : GraphCalc.cliqueNum G56 = 2 := by decide
example : GraphCalc.dominationNumber G56 = 3 := by decide
example : GraphCalc.independentDominationNumber G56 = 3 := by decide
example : GraphCalc.slaterNumber G56 = 2 := by decide
example : GraphCalc.annihilationNumber G56 = 5 := by decide
example : GraphCalc.zeroForcingNumber G56 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G56 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G56 := by decide
example : GraphCalc.vertexCoverNumber G56 = 1 := by decide
example : GraphCalc.subTotalDominationNumber G56 = 4 := by decide
example : GraphCalc.romanDominationNumber G56 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G56 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G56 := by decide
example : ¬ GraphCalc.IsTreeClass G56 := by decide
example : ¬ GraphCalc.IsClawFreeClass G56 := by decide
example : GraphCalc.IsCographClass G56 := by decide
example : ¬ GraphCalc.IsRegularClass G56 := by decide
example : ¬ GraphCalc.IsCubicClass G56 := by decide
example : GraphCalc.IsSubcubicClass G56 := by decide
example : ¬ GraphCalc.IsEulerianClass G56 := by decide
example : GraphCalc.IsTriangleFreeClass G56 := by decide
example : GraphCalc.IsK4FreeClass G56 := by decide
example : GraphCalc.IsNontrivialClass G56 := by decide
example : GraphCalc.IsBipartiteClass G56 := by decide

-- E?EG  (n=6, m=3)
abbrev G57 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (3, 4), (4, 5)]
example : GraphCalc.order G57 = 6 := by decide
example : GraphCalc.size G57 = 3 := by decide
example : SimpleGraph.minDegree G57 = 0 := by decide
example : SimpleGraph.maxDegree G57 = 2 := by decide
example : GraphCalc.indepNum G57 = 4 := by decide
example : GraphCalc.cliqueNum G57 = 2 := by decide
example : GraphCalc.dominationNumber G57 = 4 := by decide
example : GraphCalc.independentDominationNumber G57 = 4 := by decide
example : GraphCalc.slaterNumber G57 = 2 := by decide
example : GraphCalc.annihilationNumber G57 = 4 := by decide
example : GraphCalc.zeroForcingNumber G57 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G57 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G57 := by decide
example : GraphCalc.vertexCoverNumber G57 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G57 = 4 := by decide
example : GraphCalc.romanDominationNumber G57 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G57 = 9 := by decide
example : ¬ GraphCalc.IsConnectedClass G57 := by decide
example : ¬ GraphCalc.IsTreeClass G57 := by decide
example : GraphCalc.IsClawFreeClass G57 := by decide
example : ¬ GraphCalc.IsCographClass G57 := by decide
example : ¬ GraphCalc.IsRegularClass G57 := by decide
example : ¬ GraphCalc.IsCubicClass G57 := by decide
example : GraphCalc.IsSubcubicClass G57 := by decide
example : ¬ GraphCalc.IsEulerianClass G57 := by decide
example : GraphCalc.IsTriangleFreeClass G57 := by decide
example : GraphCalc.IsK4FreeClass G57 := by decide
example : GraphCalc.IsNontrivialClass G57 := by decide
example : GraphCalc.IsBipartiteClass G57 := by decide

-- E?D_  (n=6, m=3)
abbrev G58 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(1, 5), (2, 5), (3, 4)]
example : GraphCalc.order G58 = 6 := by decide
example : GraphCalc.size G58 = 3 := by decide
example : SimpleGraph.minDegree G58 = 0 := by decide
example : SimpleGraph.maxDegree G58 = 2 := by decide
example : GraphCalc.indepNum G58 = 4 := by decide
example : GraphCalc.cliqueNum G58 = 2 := by decide
example : GraphCalc.dominationNumber G58 = 3 := by decide
example : GraphCalc.independentDominationNumber G58 = 3 := by decide
example : GraphCalc.slaterNumber G58 = 3 := by decide
example : GraphCalc.annihilationNumber G58 = 4 := by decide
example : GraphCalc.zeroForcingNumber G58 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G58 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G58 := by decide
example : GraphCalc.vertexCoverNumber G58 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G58 = 5 := by decide
example : GraphCalc.romanDominationNumber G58 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G58 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G58 := by decide
example : ¬ GraphCalc.IsTreeClass G58 := by decide
example : GraphCalc.IsClawFreeClass G58 := by decide
example : GraphCalc.IsCographClass G58 := by decide
example : ¬ GraphCalc.IsRegularClass G58 := by decide
example : ¬ GraphCalc.IsCubicClass G58 := by decide
example : GraphCalc.IsSubcubicClass G58 := by decide
example : ¬ GraphCalc.IsEulerianClass G58 := by decide
example : GraphCalc.IsTriangleFreeClass G58 := by decide
example : GraphCalc.IsK4FreeClass G58 := by decide
example : GraphCalc.IsNontrivialClass G58 := by decide
example : GraphCalc.IsBipartiteClass G58 := by decide

-- EK?G  (n=6, m=3)
abbrev G59 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (1, 2), (4, 5)]
example : GraphCalc.order G59 = 6 := by decide
example : GraphCalc.size G59 = 3 := by decide
example : SimpleGraph.minDegree G59 = 1 := by decide
example : SimpleGraph.maxDegree G59 = 1 := by decide
example : GraphCalc.indepNum G59 = 3 := by decide
example : GraphCalc.cliqueNum G59 = 2 := by decide
example : GraphCalc.dominationNumber G59 = 3 := by decide
example : GraphCalc.independentDominationNumber G59 = 3 := by decide
example : GraphCalc.slaterNumber G59 = 3 := by decide
example : GraphCalc.annihilationNumber G59 = 3 := by decide
example : GraphCalc.zeroForcingNumber G59 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G59 = 6 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G59 := by decide
example : GraphCalc.vertexCoverNumber G59 = 3 := by decide
example : GraphCalc.totalDominationNumber G59 = 6 := by decide
example : GraphCalc.edgeCoverNumber G59 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G59 = 6 := by decide
example : GraphCalc.romanDominationNumber G59 = 6 := by decide
example : GraphCalc.doubleRomanDominationNumber G59 = 9 := by decide
example : ¬ GraphCalc.IsConnectedClass G59 := by decide
example : ¬ GraphCalc.IsTreeClass G59 := by decide
example : GraphCalc.IsClawFreeClass G59 := by decide
example : GraphCalc.IsCographClass G59 := by decide
example : GraphCalc.IsRegularClass G59 := by decide
example : ¬ GraphCalc.IsCubicClass G59 := by decide
example : GraphCalc.IsSubcubicClass G59 := by decide
example : ¬ GraphCalc.IsEulerianClass G59 := by decide
example : GraphCalc.IsTriangleFreeClass G59 := by decide
example : GraphCalc.IsK4FreeClass G59 := by decide
example : GraphCalc.IsNontrivialClass G59 := by decide
example : GraphCalc.IsBipartiteClass G59 := by decide

-- ECaG  (n=6, m=4)
abbrev G60 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5), (4, 5)]
example : GraphCalc.order G60 = 6 := by decide
example : GraphCalc.size G60 = 4 := by decide
example : SimpleGraph.minDegree G60 = 0 := by decide
example : SimpleGraph.maxDegree G60 = 3 := by decide
example : GraphCalc.indepNum G60 = 4 := by decide
example : GraphCalc.cliqueNum G60 = 3 := by decide
example : GraphCalc.dominationNumber G60 = 3 := by decide
example : GraphCalc.independentDominationNumber G60 = 3 := by decide
example : GraphCalc.slaterNumber G60 = 2 := by decide
example : GraphCalc.annihilationNumber G60 = 4 := by decide
example : GraphCalc.zeroForcingNumber G60 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G60 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G60 := by decide
example : GraphCalc.vertexCoverNumber G60 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G60 = 3 := by decide
example : GraphCalc.romanDominationNumber G60 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G60 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G60 := by decide
example : ¬ GraphCalc.IsTreeClass G60 := by decide
example : GraphCalc.IsClawFreeClass G60 := by decide
example : GraphCalc.IsCographClass G60 := by decide
example : ¬ GraphCalc.IsRegularClass G60 := by decide
example : ¬ GraphCalc.IsCubicClass G60 := by decide
example : GraphCalc.IsSubcubicClass G60 := by decide
example : ¬ GraphCalc.IsEulerianClass G60 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G60 := by decide
example : GraphCalc.IsK4FreeClass G60 := by decide
example : GraphCalc.IsNontrivialClass G60 := by decide
example : ¬ GraphCalc.IsBipartiteClass G60 := by decide

-- EC_W  (n=6, m=4)
abbrev G61 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (3, 5), (4, 5)]
example : GraphCalc.order G61 = 6 := by decide
example : GraphCalc.size G61 = 4 := by decide
example : SimpleGraph.minDegree G61 = 0 := by decide
example : SimpleGraph.maxDegree G61 = 2 := by decide
example : GraphCalc.indepNum G61 = 4 := by decide
example : GraphCalc.cliqueNum G61 = 2 := by decide
example : GraphCalc.dominationNumber G61 = 4 := by decide
example : GraphCalc.independentDominationNumber G61 = 4 := by decide
example : GraphCalc.slaterNumber G61 = 2 := by decide
example : GraphCalc.annihilationNumber G61 = 4 := by decide
example : GraphCalc.zeroForcingNumber G61 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G61 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G61 := by decide
example : GraphCalc.vertexCoverNumber G61 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G61 = 3 := by decide
example : GraphCalc.romanDominationNumber G61 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G61 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G61 := by decide
example : ¬ GraphCalc.IsTreeClass G61 := by decide
example : GraphCalc.IsClawFreeClass G61 := by decide
example : GraphCalc.IsCographClass G61 := by decide
example : ¬ GraphCalc.IsRegularClass G61 := by decide
example : ¬ GraphCalc.IsCubicClass G61 := by decide
example : GraphCalc.IsSubcubicClass G61 := by decide
example : ¬ GraphCalc.IsEulerianClass G61 := by decide
example : GraphCalc.IsTriangleFreeClass G61 := by decide
example : GraphCalc.IsK4FreeClass G61 := by decide
example : GraphCalc.IsNontrivialClass G61 := by decide
example : GraphCalc.IsBipartiteClass G61 := by decide

-- E?Bo  (n=6, m=4)
abbrev G62 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (1, 5), (2, 5), (3, 5)]
example : GraphCalc.order G62 = 6 := by decide
example : GraphCalc.size G62 = 4 := by decide
example : SimpleGraph.minDegree G62 = 0 := by decide
example : SimpleGraph.maxDegree G62 = 4 := by decide
example : GraphCalc.indepNum G62 = 5 := by decide
example : GraphCalc.cliqueNum G62 = 2 := by decide
example : GraphCalc.dominationNumber G62 = 2 := by decide
example : GraphCalc.independentDominationNumber G62 = 2 := by decide
example : GraphCalc.slaterNumber G62 = 2 := by decide
example : GraphCalc.annihilationNumber G62 = 5 := by decide
example : GraphCalc.zeroForcingNumber G62 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G62 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G62 := by decide
example : GraphCalc.vertexCoverNumber G62 = 1 := by decide
example : GraphCalc.subTotalDominationNumber G62 = 3 := by decide
example : GraphCalc.romanDominationNumber G62 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G62 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G62 := by decide
example : ¬ GraphCalc.IsTreeClass G62 := by decide
example : ¬ GraphCalc.IsClawFreeClass G62 := by decide
example : GraphCalc.IsCographClass G62 := by decide
example : ¬ GraphCalc.IsRegularClass G62 := by decide
example : ¬ GraphCalc.IsCubicClass G62 := by decide
example : ¬ GraphCalc.IsSubcubicClass G62 := by decide
example : ¬ GraphCalc.IsEulerianClass G62 := by decide
example : GraphCalc.IsTriangleFreeClass G62 := by decide
example : GraphCalc.IsK4FreeClass G62 := by decide
example : GraphCalc.IsNontrivialClass G62 := by decide
example : GraphCalc.IsBipartiteClass G62 := by decide

-- EBc?  (n=6, m=4)
abbrev G63 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G63 = 6 := by decide
example : GraphCalc.size G63 = 4 := by decide
example : SimpleGraph.minDegree G63 = 0 := by decide
example : SimpleGraph.maxDegree G63 = 3 := by decide
example : GraphCalc.indepNum G63 = 4 := by decide
example : GraphCalc.cliqueNum G63 = 2 := by decide
example : GraphCalc.dominationNumber G63 = 3 := by decide
example : GraphCalc.independentDominationNumber G63 = 3 := by decide
example : GraphCalc.slaterNumber G63 = 2 := by decide
example : GraphCalc.annihilationNumber G63 = 4 := by decide
example : GraphCalc.zeroForcingNumber G63 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G63 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G63 := by decide
example : GraphCalc.vertexCoverNumber G63 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G63 = 3 := by decide
example : GraphCalc.romanDominationNumber G63 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G63 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G63 := by decide
example : ¬ GraphCalc.IsTreeClass G63 := by decide
example : ¬ GraphCalc.IsClawFreeClass G63 := by decide
example : ¬ GraphCalc.IsCographClass G63 := by decide
example : ¬ GraphCalc.IsRegularClass G63 := by decide
example : ¬ GraphCalc.IsCubicClass G63 := by decide
example : GraphCalc.IsSubcubicClass G63 := by decide
example : ¬ GraphCalc.IsEulerianClass G63 := by decide
example : GraphCalc.IsTriangleFreeClass G63 := by decide
example : GraphCalc.IsK4FreeClass G63 := by decide
example : GraphCalc.IsNontrivialClass G63 := by decide
example : GraphCalc.IsBipartiteClass G63 := by decide

-- EY?O  (n=6, m=4)
abbrev G64 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 3), (3, 5)]
example : GraphCalc.order G64 = 6 := by decide
example : GraphCalc.size G64 = 4 := by decide
example : SimpleGraph.minDegree G64 = 0 := by decide
example : SimpleGraph.maxDegree G64 = 2 := by decide
example : GraphCalc.indepNum G64 = 4 := by decide
example : GraphCalc.cliqueNum G64 = 2 := by decide
example : GraphCalc.dominationNumber G64 = 3 := by decide
example : GraphCalc.independentDominationNumber G64 = 3 := by decide
example : GraphCalc.slaterNumber G64 = 2 := by decide
example : GraphCalc.annihilationNumber G64 = 4 := by decide
example : GraphCalc.zeroForcingNumber G64 = 2 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G64 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G64 := by decide
example : GraphCalc.vertexCoverNumber G64 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G64 = 3 := by decide
example : GraphCalc.romanDominationNumber G64 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G64 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G64 := by decide
example : ¬ GraphCalc.IsTreeClass G64 := by decide
example : GraphCalc.IsClawFreeClass G64 := by decide
example : ¬ GraphCalc.IsCographClass G64 := by decide
example : ¬ GraphCalc.IsRegularClass G64 := by decide
example : ¬ GraphCalc.IsCubicClass G64 := by decide
example : GraphCalc.IsSubcubicClass G64 := by decide
example : ¬ GraphCalc.IsEulerianClass G64 := by decide
example : GraphCalc.IsTriangleFreeClass G64 := by decide
example : GraphCalc.IsK4FreeClass G64 := by decide
example : GraphCalc.IsNontrivialClass G64 := by decide
example : GraphCalc.IsBipartiteClass G64 := by decide

-- EJA?  (n=6, m=4)
abbrev G65 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G65 = 6 := by decide
example : GraphCalc.size G65 = 4 := by decide
example : SimpleGraph.minDegree G65 = 0 := by decide
example : SimpleGraph.maxDegree G65 = 2 := by decide
example : GraphCalc.indepNum G65 = 3 := by decide
example : GraphCalc.cliqueNum G65 = 3 := by decide
example : GraphCalc.dominationNumber G65 = 3 := by decide
example : GraphCalc.independentDominationNumber G65 = 3 := by decide
example : GraphCalc.slaterNumber G65 = 2 := by decide
example : GraphCalc.annihilationNumber G65 = 4 := by decide
example : GraphCalc.zeroForcingNumber G65 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G65 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G65 := by decide
example : GraphCalc.vertexCoverNumber G65 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G65 = 3 := by decide
example : GraphCalc.romanDominationNumber G65 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G65 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G65 := by decide
example : ¬ GraphCalc.IsTreeClass G65 := by decide
example : GraphCalc.IsClawFreeClass G65 := by decide
example : GraphCalc.IsCographClass G65 := by decide
example : ¬ GraphCalc.IsRegularClass G65 := by decide
example : ¬ GraphCalc.IsCubicClass G65 := by decide
example : GraphCalc.IsSubcubicClass G65 := by decide
example : ¬ GraphCalc.IsEulerianClass G65 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G65 := by decide
example : GraphCalc.IsK4FreeClass G65 := by decide
example : GraphCalc.IsNontrivialClass G65 := by decide
example : ¬ GraphCalc.IsBipartiteClass G65 := by decide

-- EKa?  (n=6, m=4)
abbrev G66 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5), (1, 2)]
example : GraphCalc.order G66 = 6 := by decide
example : GraphCalc.size G66 = 4 := by decide
example : SimpleGraph.minDegree G66 = 1 := by decide
example : SimpleGraph.maxDegree G66 = 3 := by decide
example : GraphCalc.indepNum G66 = 4 := by decide
example : GraphCalc.cliqueNum G66 = 2 := by decide
example : GraphCalc.dominationNumber G66 = 2 := by decide
example : GraphCalc.independentDominationNumber G66 = 2 := by decide
example : GraphCalc.slaterNumber G66 = 2 := by decide
example : GraphCalc.annihilationNumber G66 = 4 := by decide
example : GraphCalc.zeroForcingNumber G66 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G66 = 5 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G66 := by decide
example : GraphCalc.vertexCoverNumber G66 = 2 := by decide
example : GraphCalc.totalDominationNumber G66 = 4 := by decide
example : GraphCalc.edgeCoverNumber G66 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G66 = 4 := by decide
example : GraphCalc.romanDominationNumber G66 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G66 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G66 := by decide
example : ¬ GraphCalc.IsTreeClass G66 := by decide
example : ¬ GraphCalc.IsClawFreeClass G66 := by decide
example : GraphCalc.IsCographClass G66 := by decide
example : ¬ GraphCalc.IsRegularClass G66 := by decide
example : ¬ GraphCalc.IsCubicClass G66 := by decide
example : GraphCalc.IsSubcubicClass G66 := by decide
example : ¬ GraphCalc.IsEulerianClass G66 := by decide
example : GraphCalc.IsTriangleFreeClass G66 := by decide
example : GraphCalc.IsK4FreeClass G66 := by decide
example : GraphCalc.IsNontrivialClass G66 := by decide
example : GraphCalc.IsBipartiteClass G66 := by decide

-- EGEG  (n=6, m=4)
abbrev G67 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (1, 2), (3, 4), (4, 5)]
example : GraphCalc.order G67 = 6 := by decide
example : GraphCalc.size G67 = 4 := by decide
example : SimpleGraph.minDegree G67 = 1 := by decide
example : SimpleGraph.maxDegree G67 = 2 := by decide
example : GraphCalc.indepNum G67 = 3 := by decide
example : GraphCalc.cliqueNum G67 = 2 := by decide
example : GraphCalc.dominationNumber G67 = 3 := by decide
example : GraphCalc.independentDominationNumber G67 = 3 := by decide
example : GraphCalc.slaterNumber G67 = 2 := by decide
example : GraphCalc.annihilationNumber G67 = 4 := by decide
example : GraphCalc.zeroForcingNumber G67 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G67 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G67 := by decide
example : GraphCalc.vertexCoverNumber G67 = 3 := by decide
example : GraphCalc.totalDominationNumber G67 = 4 := by decide
example : GraphCalc.edgeCoverNumber G67 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G67 = 4 := by decide
example : GraphCalc.romanDominationNumber G67 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G67 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G67 := by decide
example : ¬ GraphCalc.IsTreeClass G67 := by decide
example : GraphCalc.IsClawFreeClass G67 := by decide
example : ¬ GraphCalc.IsCographClass G67 := by decide
example : ¬ GraphCalc.IsRegularClass G67 := by decide
example : ¬ GraphCalc.IsCubicClass G67 := by decide
example : GraphCalc.IsSubcubicClass G67 := by decide
example : ¬ GraphCalc.IsEulerianClass G67 := by decide
example : GraphCalc.IsTriangleFreeClass G67 := by decide
example : GraphCalc.IsK4FreeClass G67 := by decide
example : GraphCalc.IsNontrivialClass G67 := by decide
example : GraphCalc.IsBipartiteClass G67 := by decide

-- EQ_O  (n=6, m=4)
abbrev G68 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 4), (1, 3), (3, 5)]
example : GraphCalc.order G68 = 6 := by decide
example : GraphCalc.size G68 = 4 := by decide
example : SimpleGraph.minDegree G68 = 1 := by decide
example : SimpleGraph.maxDegree G68 = 2 := by decide
example : GraphCalc.indepNum G68 = 4 := by decide
example : GraphCalc.cliqueNum G68 = 2 := by decide
example : GraphCalc.dominationNumber G68 = 2 := by decide
example : GraphCalc.independentDominationNumber G68 = 2 := by decide
example : GraphCalc.slaterNumber G68 = 2 := by decide
example : GraphCalc.annihilationNumber G68 = 4 := by decide
example : GraphCalc.zeroForcingNumber G68 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G68 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G68 := by decide
example : GraphCalc.vertexCoverNumber G68 = 2 := by decide
example : GraphCalc.totalDominationNumber G68 = 4 := by decide
example : GraphCalc.edgeCoverNumber G68 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G68 = 4 := by decide
example : GraphCalc.romanDominationNumber G68 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G68 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G68 := by decide
example : ¬ GraphCalc.IsTreeClass G68 := by decide
example : GraphCalc.IsClawFreeClass G68 := by decide
example : GraphCalc.IsCographClass G68 := by decide
example : ¬ GraphCalc.IsRegularClass G68 := by decide
example : ¬ GraphCalc.IsCubicClass G68 := by decide
example : GraphCalc.IsSubcubicClass G68 := by decide
example : ¬ GraphCalc.IsEulerianClass G68 := by decide
example : GraphCalc.IsTriangleFreeClass G68 := by decide
example : GraphCalc.IsK4FreeClass G68 := by decide
example : GraphCalc.IsNontrivialClass G68 := by decide
example : GraphCalc.IsBipartiteClass G68 := by decide

-- ECaW  (n=6, m=5)
abbrev G69 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5), (3, 5), (4, 5)]
example : GraphCalc.order G69 = 6 := by decide
example : GraphCalc.size G69 = 5 := by decide
example : SimpleGraph.minDegree G69 = 0 := by decide
example : SimpleGraph.maxDegree G69 = 3 := by decide
example : GraphCalc.indepNum G69 = 4 := by decide
example : GraphCalc.cliqueNum G69 = 3 := by decide
example : GraphCalc.dominationNumber G69 = 3 := by decide
example : GraphCalc.independentDominationNumber G69 = 3 := by decide
example : GraphCalc.slaterNumber G69 = 2 := by decide
example : GraphCalc.annihilationNumber G69 = 4 := by decide
example : GraphCalc.zeroForcingNumber G69 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G69 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G69 := by decide
example : GraphCalc.vertexCoverNumber G69 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G69 = 2 := by decide
example : GraphCalc.romanDominationNumber G69 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G69 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G69 := by decide
example : ¬ GraphCalc.IsTreeClass G69 := by decide
example : GraphCalc.IsClawFreeClass G69 := by decide
example : GraphCalc.IsCographClass G69 := by decide
example : ¬ GraphCalc.IsRegularClass G69 := by decide
example : ¬ GraphCalc.IsCubicClass G69 := by decide
example : GraphCalc.IsSubcubicClass G69 := by decide
example : ¬ GraphCalc.IsEulerianClass G69 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G69 := by decide
example : GraphCalc.IsK4FreeClass G69 := by decide
example : GraphCalc.IsNontrivialClass G69 := by decide
example : ¬ GraphCalc.IsBipartiteClass G69 := by decide

-- EBCW  (n=6, m=5)
abbrev G70 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G70 = 6 := by decide
example : GraphCalc.size G70 = 5 := by decide
example : SimpleGraph.minDegree G70 = 0 := by decide
example : SimpleGraph.maxDegree G70 = 4 := by decide
example : GraphCalc.indepNum G70 = 4 := by decide
example : GraphCalc.cliqueNum G70 = 3 := by decide
example : GraphCalc.dominationNumber G70 = 2 := by decide
example : GraphCalc.independentDominationNumber G70 = 2 := by decide
example : GraphCalc.slaterNumber G70 = 2 := by decide
example : GraphCalc.annihilationNumber G70 = 4 := by decide
example : GraphCalc.zeroForcingNumber G70 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G70 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G70 := by decide
example : GraphCalc.vertexCoverNumber G70 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G70 = 2 := by decide
example : GraphCalc.romanDominationNumber G70 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G70 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G70 := by decide
example : ¬ GraphCalc.IsTreeClass G70 := by decide
example : ¬ GraphCalc.IsClawFreeClass G70 := by decide
example : GraphCalc.IsCographClass G70 := by decide
example : ¬ GraphCalc.IsRegularClass G70 := by decide
example : ¬ GraphCalc.IsCubicClass G70 := by decide
example : ¬ GraphCalc.IsSubcubicClass G70 := by decide
example : ¬ GraphCalc.IsEulerianClass G70 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G70 := by decide
example : GraphCalc.IsK4FreeClass G70 := by decide
example : GraphCalc.IsNontrivialClass G70 := by decide
example : ¬ GraphCalc.IsBipartiteClass G70 := by decide

-- E@cW  (n=6, m=5)
abbrev G71 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (2, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G71 = 6 := by decide
example : GraphCalc.size G71 = 5 := by decide
example : SimpleGraph.minDegree G71 = 0 := by decide
example : SimpleGraph.maxDegree G71 = 3 := by decide
example : GraphCalc.indepNum G71 = 4 := by decide
example : GraphCalc.cliqueNum G71 = 3 := by decide
example : GraphCalc.dominationNumber G71 = 3 := by decide
example : GraphCalc.independentDominationNumber G71 = 3 := by decide
example : GraphCalc.slaterNumber G71 = 2 := by decide
example : GraphCalc.annihilationNumber G71 = 4 := by decide
example : GraphCalc.zeroForcingNumber G71 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G71 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G71 := by decide
example : GraphCalc.vertexCoverNumber G71 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G71 = 2 := by decide
example : GraphCalc.romanDominationNumber G71 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G71 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G71 := by decide
example : ¬ GraphCalc.IsTreeClass G71 := by decide
example : GraphCalc.IsClawFreeClass G71 := by decide
example : ¬ GraphCalc.IsCographClass G71 := by decide
example : ¬ GraphCalc.IsRegularClass G71 := by decide
example : ¬ GraphCalc.IsCubicClass G71 := by decide
example : GraphCalc.IsSubcubicClass G71 := by decide
example : ¬ GraphCalc.IsEulerianClass G71 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G71 := by decide
example : GraphCalc.IsK4FreeClass G71 := by decide
example : GraphCalc.IsNontrivialClass G71 := by decide
example : ¬ GraphCalc.IsBipartiteClass G71 := by decide

-- EJc?  (n=6, m=5)
abbrev G72 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 2), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G72 = 6 := by decide
example : GraphCalc.size G72 = 5 := by decide
example : SimpleGraph.minDegree G72 = 0 := by decide
example : SimpleGraph.maxDegree G72 = 3 := by decide
example : GraphCalc.indepNum G72 = 3 := by decide
example : GraphCalc.cliqueNum G72 = 3 := by decide
example : GraphCalc.dominationNumber G72 = 3 := by decide
example : GraphCalc.independentDominationNumber G72 = 3 := by decide
example : GraphCalc.slaterNumber G72 = 2 := by decide
example : GraphCalc.annihilationNumber G72 = 4 := by decide
example : GraphCalc.zeroForcingNumber G72 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G72 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G72 := by decide
example : GraphCalc.vertexCoverNumber G72 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G72 = 3 := by decide
example : GraphCalc.romanDominationNumber G72 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G72 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G72 := by decide
example : ¬ GraphCalc.IsTreeClass G72 := by decide
example : GraphCalc.IsClawFreeClass G72 := by decide
example : ¬ GraphCalc.IsCographClass G72 := by decide
example : ¬ GraphCalc.IsRegularClass G72 := by decide
example : ¬ GraphCalc.IsCubicClass G72 := by decide
example : GraphCalc.IsSubcubicClass G72 := by decide
example : ¬ GraphCalc.IsEulerianClass G72 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G72 := by decide
example : GraphCalc.IsK4FreeClass G72 := by decide
example : GraphCalc.IsNontrivialClass G72 := by decide
example : ¬ GraphCalc.IsBipartiteClass G72 := by decide

-- EHs?  (n=6, m=5)
abbrev G73 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
example : GraphCalc.order G73 = 6 := by decide
example : GraphCalc.size G73 = 5 := by decide
example : SimpleGraph.minDegree G73 = 0 := by decide
example : SimpleGraph.maxDegree G73 = 3 := by decide
example : GraphCalc.indepNum G73 = 4 := by decide
example : GraphCalc.cliqueNum G73 = 2 := by decide
example : GraphCalc.dominationNumber G73 = 3 := by decide
example : GraphCalc.independentDominationNumber G73 = 3 := by decide
example : GraphCalc.slaterNumber G73 = 2 := by decide
example : GraphCalc.annihilationNumber G73 = 4 := by decide
example : GraphCalc.zeroForcingNumber G73 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G73 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G73 := by decide
example : GraphCalc.vertexCoverNumber G73 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G73 = 3 := by decide
example : GraphCalc.romanDominationNumber G73 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G73 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G73 := by decide
example : ¬ GraphCalc.IsTreeClass G73 := by decide
example : ¬ GraphCalc.IsClawFreeClass G73 := by decide
example : ¬ GraphCalc.IsCographClass G73 := by decide
example : ¬ GraphCalc.IsRegularClass G73 := by decide
example : ¬ GraphCalc.IsCubicClass G73 := by decide
example : GraphCalc.IsSubcubicClass G73 := by decide
example : ¬ GraphCalc.IsEulerianClass G73 := by decide
example : GraphCalc.IsTriangleFreeClass G73 := by decide
example : GraphCalc.IsK4FreeClass G73 := by decide
example : GraphCalc.IsNontrivialClass G73 := by decide
example : GraphCalc.IsBipartiteClass G73 := by decide

-- Ehc?  (n=6, m=5)
abbrev G74 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)]
example : GraphCalc.order G74 = 6 := by decide
example : GraphCalc.size G74 = 5 := by decide
example : SimpleGraph.minDegree G74 = 0 := by decide
example : SimpleGraph.maxDegree G74 = 2 := by decide
example : GraphCalc.indepNum G74 = 3 := by decide
example : GraphCalc.cliqueNum G74 = 2 := by decide
example : GraphCalc.dominationNumber G74 = 3 := by decide
example : GraphCalc.independentDominationNumber G74 = 3 := by decide
example : GraphCalc.slaterNumber G74 = 2 := by decide
example : GraphCalc.annihilationNumber G74 = 3 := by decide
example : GraphCalc.zeroForcingNumber G74 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G74 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G74 := by decide
example : GraphCalc.vertexCoverNumber G74 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G74 = 3 := by decide
example : GraphCalc.romanDominationNumber G74 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G74 = 8 := by decide
example : ¬ GraphCalc.IsConnectedClass G74 := by decide
example : ¬ GraphCalc.IsTreeClass G74 := by decide
example : GraphCalc.IsClawFreeClass G74 := by decide
example : ¬ GraphCalc.IsCographClass G74 := by decide
example : ¬ GraphCalc.IsRegularClass G74 := by decide
example : ¬ GraphCalc.IsCubicClass G74 := by decide
example : GraphCalc.IsSubcubicClass G74 := by decide
example : ¬ GraphCalc.IsEulerianClass G74 := by decide
example : GraphCalc.IsTriangleFreeClass G74 := by decide
example : GraphCalc.IsK4FreeClass G74 := by decide
example : GraphCalc.IsNontrivialClass G74 := by decide
example : ¬ GraphCalc.IsBipartiteClass G74 := by decide

-- E?Bw  (n=6, m=5)
abbrev G75 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]
example : GraphCalc.order G75 = 6 := by decide
example : GraphCalc.size G75 = 5 := by decide
example : SimpleGraph.minDegree G75 = 1 := by decide
example : SimpleGraph.maxDegree G75 = 5 := by decide
example : GraphCalc.indepNum G75 = 5 := by decide
example : GraphCalc.cliqueNum G75 = 2 := by decide
example : GraphCalc.dominationNumber G75 = 1 := by decide
example : GraphCalc.independentDominationNumber G75 = 1 := by decide
example : GraphCalc.slaterNumber G75 = 1 := by decide
example : GraphCalc.annihilationNumber G75 = 5 := by decide
example : GraphCalc.zeroForcingNumber G75 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G75 = 5 := by decide
example : GraphCalc.connectedZeroForcingNumber G75 = 5 := by decide
example : GraphCalc.vertexCoverNumber G75 = 1 := by decide
example : GraphCalc.totalDominationNumber G75 = 2 := by decide
example : GraphCalc.edgeCoverNumber G75 = 5 := by decide
example : GraphCalc.subTotalDominationNumber G75 = 2 := by decide
example : GraphCalc.romanDominationNumber G75 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G75 = 3 := by decide
example : GraphCalc.radius G75 = 1 := by decide
example : GraphCalc.IsConnectedClass G75 := by decide
example : GraphCalc.IsTreeClass G75 := by decide
example : ¬ GraphCalc.IsClawFreeClass G75 := by decide
example : GraphCalc.IsCographClass G75 := by decide
example : ¬ GraphCalc.IsRegularClass G75 := by decide
example : ¬ GraphCalc.IsCubicClass G75 := by decide
example : ¬ GraphCalc.IsSubcubicClass G75 := by decide
example : ¬ GraphCalc.IsEulerianClass G75 := by decide
example : GraphCalc.IsTriangleFreeClass G75 := by decide
example : GraphCalc.IsK4FreeClass G75 := by decide
example : GraphCalc.IsNontrivialClass G75 := by decide
example : GraphCalc.IsBipartiteClass G75 := by decide

-- EhP?  (n=6, m=5)
abbrev G76 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (1, 2), (1, 4), (1, 5), (2, 3)]
example : GraphCalc.order G76 = 6 := by decide
example : GraphCalc.size G76 = 5 := by decide
example : SimpleGraph.minDegree G76 = 1 := by decide
example : SimpleGraph.maxDegree G76 = 4 := by decide
example : GraphCalc.indepNum G76 = 4 := by decide
example : GraphCalc.cliqueNum G76 = 2 := by decide
example : GraphCalc.dominationNumber G76 = 2 := by decide
example : GraphCalc.independentDominationNumber G76 = 2 := by decide
example : GraphCalc.slaterNumber G76 = 2 := by decide
example : GraphCalc.annihilationNumber G76 = 4 := by decide
example : GraphCalc.zeroForcingNumber G76 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G76 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G76 = 4 := by decide
example : GraphCalc.vertexCoverNumber G76 = 2 := by decide
example : GraphCalc.totalDominationNumber G76 = 2 := by decide
example : GraphCalc.edgeCoverNumber G76 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G76 = 2 := by decide
example : GraphCalc.romanDominationNumber G76 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G76 = 5 := by decide
example : GraphCalc.radius G76 = 2 := by decide
example : GraphCalc.IsConnectedClass G76 := by decide
example : GraphCalc.IsTreeClass G76 := by decide
example : ¬ GraphCalc.IsClawFreeClass G76 := by decide
example : ¬ GraphCalc.IsCographClass G76 := by decide
example : ¬ GraphCalc.IsRegularClass G76 := by decide
example : ¬ GraphCalc.IsCubicClass G76 := by decide
example : ¬ GraphCalc.IsSubcubicClass G76 := by decide
example : ¬ GraphCalc.IsEulerianClass G76 := by decide
example : GraphCalc.IsTriangleFreeClass G76 := by decide
example : GraphCalc.IsK4FreeClass G76 := by decide
example : GraphCalc.IsNontrivialClass G76 := by decide
example : GraphCalc.IsBipartiteClass G76 := by decide

-- EsCO  (n=6, m=5)
abbrev G77 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (3, 4), (3, 5)]
example : GraphCalc.order G77 = 6 := by decide
example : GraphCalc.size G77 = 5 := by decide
example : SimpleGraph.minDegree G77 = 1 := by decide
example : SimpleGraph.maxDegree G77 = 3 := by decide
example : GraphCalc.indepNum G77 = 4 := by decide
example : GraphCalc.cliqueNum G77 = 2 := by decide
example : GraphCalc.dominationNumber G77 = 2 := by decide
example : GraphCalc.independentDominationNumber G77 = 3 := by decide
example : GraphCalc.slaterNumber G77 = 2 := by decide
example : GraphCalc.annihilationNumber G77 = 4 := by decide
example : GraphCalc.zeroForcingNumber G77 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G77 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G77 = 4 := by decide
example : GraphCalc.vertexCoverNumber G77 = 2 := by decide
example : GraphCalc.totalDominationNumber G77 = 2 := by decide
example : GraphCalc.edgeCoverNumber G77 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G77 = 2 := by decide
example : GraphCalc.romanDominationNumber G77 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G77 = 6 := by decide
example : GraphCalc.radius G77 = 2 := by decide
example : GraphCalc.IsConnectedClass G77 := by decide
example : GraphCalc.IsTreeClass G77 := by decide
example : ¬ GraphCalc.IsClawFreeClass G77 := by decide
example : ¬ GraphCalc.IsCographClass G77 := by decide
example : ¬ GraphCalc.IsRegularClass G77 := by decide
example : ¬ GraphCalc.IsCubicClass G77 := by decide
example : GraphCalc.IsSubcubicClass G77 := by decide
example : ¬ GraphCalc.IsEulerianClass G77 := by decide
example : GraphCalc.IsTriangleFreeClass G77 := by decide
example : GraphCalc.IsK4FreeClass G77 := by decide
example : GraphCalc.IsNontrivialClass G77 := by decide
example : GraphCalc.IsBipartiteClass G77 := by decide

-- EiGO  (n=6, m=5)
abbrev G78 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (1, 2), (1, 3), (2, 4), (3, 5)]
example : GraphCalc.order G78 = 6 := by decide
example : GraphCalc.size G78 = 5 := by decide
example : SimpleGraph.minDegree G78 = 1 := by decide
example : SimpleGraph.maxDegree G78 = 3 := by decide
example : GraphCalc.indepNum G78 = 3 := by decide
example : GraphCalc.cliqueNum G78 = 2 := by decide
example : GraphCalc.dominationNumber G78 = 3 := by decide
example : GraphCalc.independentDominationNumber G78 = 3 := by decide
example : GraphCalc.slaterNumber G78 = 2 := by decide
example : GraphCalc.annihilationNumber G78 = 4 := by decide
example : GraphCalc.zeroForcingNumber G78 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G78 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G78 = 3 := by decide
example : GraphCalc.vertexCoverNumber G78 = 3 := by decide
example : GraphCalc.totalDominationNumber G78 = 3 := by decide
example : GraphCalc.edgeCoverNumber G78 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G78 = 3 := by decide
example : GraphCalc.romanDominationNumber G78 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G78 = 7 := by decide
example : GraphCalc.radius G78 = 2 := by decide
example : GraphCalc.IsConnectedClass G78 := by decide
example : GraphCalc.IsTreeClass G78 := by decide
example : ¬ GraphCalc.IsClawFreeClass G78 := by decide
example : ¬ GraphCalc.IsCographClass G78 := by decide
example : ¬ GraphCalc.IsRegularClass G78 := by decide
example : ¬ GraphCalc.IsCubicClass G78 := by decide
example : GraphCalc.IsSubcubicClass G78 := by decide
example : ¬ GraphCalc.IsEulerianClass G78 := by decide
example : GraphCalc.IsTriangleFreeClass G78 := by decide
example : GraphCalc.IsK4FreeClass G78 := by decide
example : GraphCalc.IsNontrivialClass G78 := by decide
example : GraphCalc.IsBipartiteClass G78 := by decide

-- EBe?  (n=6, m=5)
abbrev G79 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G79 = 6 := by decide
example : GraphCalc.size G79 = 5 := by decide
example : SimpleGraph.minDegree G79 = 1 := by decide
example : SimpleGraph.maxDegree G79 = 3 := by decide
example : GraphCalc.indepNum G79 = 4 := by decide
example : GraphCalc.cliqueNum G79 = 2 := by decide
example : GraphCalc.dominationNumber G79 = 2 := by decide
example : GraphCalc.independentDominationNumber G79 = 2 := by decide
example : GraphCalc.slaterNumber G79 = 2 := by decide
example : GraphCalc.annihilationNumber G79 = 4 := by decide
example : GraphCalc.zeroForcingNumber G79 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G79 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G79 = 3 := by decide
example : GraphCalc.vertexCoverNumber G79 = 2 := by decide
example : GraphCalc.totalDominationNumber G79 = 3 := by decide
example : GraphCalc.edgeCoverNumber G79 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G79 = 3 := by decide
example : GraphCalc.romanDominationNumber G79 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G79 = 6 := by decide
example : GraphCalc.radius G79 = 2 := by decide
example : GraphCalc.IsConnectedClass G79 := by decide
example : GraphCalc.IsTreeClass G79 := by decide
example : ¬ GraphCalc.IsClawFreeClass G79 := by decide
example : ¬ GraphCalc.IsCographClass G79 := by decide
example : ¬ GraphCalc.IsRegularClass G79 := by decide
example : ¬ GraphCalc.IsCubicClass G79 := by decide
example : GraphCalc.IsSubcubicClass G79 := by decide
example : ¬ GraphCalc.IsEulerianClass G79 := by decide
example : GraphCalc.IsTriangleFreeClass G79 := by decide
example : GraphCalc.IsK4FreeClass G79 := by decide
example : GraphCalc.IsNontrivialClass G79 := by decide
example : GraphCalc.IsBipartiteClass G79 := by decide

-- Ej?G  (n=6, m=5)
abbrev G80 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (1, 2), (1, 3), (2, 3), (4, 5)]
example : GraphCalc.order G80 = 6 := by decide
example : GraphCalc.size G80 = 5 := by decide
example : SimpleGraph.minDegree G80 = 1 := by decide
example : SimpleGraph.maxDegree G80 = 3 := by decide
example : GraphCalc.indepNum G80 = 3 := by decide
example : GraphCalc.cliqueNum G80 = 3 := by decide
example : GraphCalc.dominationNumber G80 = 2 := by decide
example : GraphCalc.independentDominationNumber G80 = 2 := by decide
example : GraphCalc.slaterNumber G80 = 2 := by decide
example : GraphCalc.annihilationNumber G80 = 4 := by decide
example : GraphCalc.zeroForcingNumber G80 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G80 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G80 := by decide
example : GraphCalc.vertexCoverNumber G80 = 3 := by decide
example : GraphCalc.totalDominationNumber G80 = 4 := by decide
example : GraphCalc.edgeCoverNumber G80 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G80 = 3 := by decide
example : GraphCalc.romanDominationNumber G80 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G80 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G80 := by decide
example : ¬ GraphCalc.IsTreeClass G80 := by decide
example : GraphCalc.IsClawFreeClass G80 := by decide
example : GraphCalc.IsCographClass G80 := by decide
example : ¬ GraphCalc.IsRegularClass G80 := by decide
example : ¬ GraphCalc.IsCubicClass G80 := by decide
example : GraphCalc.IsSubcubicClass G80 := by decide
example : ¬ GraphCalc.IsEulerianClass G80 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G80 := by decide
example : GraphCalc.IsK4FreeClass G80 := by decide
example : GraphCalc.IsNontrivialClass G80 := by decide
example : ¬ GraphCalc.IsBipartiteClass G80 := by decide

-- E`EG  (n=6, m=5)
abbrev G81 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 5), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G81 = 6 := by decide
example : GraphCalc.size G81 = 5 := by decide
example : SimpleGraph.minDegree G81 = 1 := by decide
example : SimpleGraph.maxDegree G81 = 2 := by decide
example : GraphCalc.indepNum G81 = 3 := by decide
example : GraphCalc.cliqueNum G81 = 2 := by decide
example : GraphCalc.dominationNumber G81 = 2 := by decide
example : GraphCalc.independentDominationNumber G81 = 2 := by decide
example : GraphCalc.slaterNumber G81 = 2 := by decide
example : GraphCalc.annihilationNumber G81 = 3 := by decide
example : GraphCalc.zeroForcingNumber G81 = 1 := by decide
example : GraphCalc.totalZeroForcingNumber G81 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G81 = 1 := by decide
example : GraphCalc.vertexCoverNumber G81 = 3 := by decide
example : GraphCalc.totalDominationNumber G81 = 4 := by decide
example : GraphCalc.edgeCoverNumber G81 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G81 = 3 := by decide
example : GraphCalc.romanDominationNumber G81 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G81 = 6 := by decide
example : GraphCalc.radius G81 = 3 := by decide
example : GraphCalc.IsConnectedClass G81 := by decide
example : GraphCalc.IsTreeClass G81 := by decide
example : GraphCalc.IsClawFreeClass G81 := by decide
example : ¬ GraphCalc.IsCographClass G81 := by decide
example : ¬ GraphCalc.IsRegularClass G81 := by decide
example : ¬ GraphCalc.IsCubicClass G81 := by decide
example : GraphCalc.IsSubcubicClass G81 := by decide
example : ¬ GraphCalc.IsEulerianClass G81 := by decide
example : GraphCalc.IsTriangleFreeClass G81 := by decide
example : GraphCalc.IsK4FreeClass G81 := by decide
example : GraphCalc.IsNontrivialClass G81 := by decide
example : GraphCalc.IsBipartiteClass G81 := by decide

-- ECd_  (n=6, m=5)
abbrev G82 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (1, 5), (2, 5), (3, 4)]
example : GraphCalc.order G82 = 6 := by decide
example : GraphCalc.size G82 = 5 := by decide
example : SimpleGraph.minDegree G82 = 1 := by decide
example : SimpleGraph.maxDegree G82 = 2 := by decide
example : GraphCalc.indepNum G82 = 3 := by decide
example : GraphCalc.cliqueNum G82 = 3 := by decide
example : GraphCalc.dominationNumber G82 = 2 := by decide
example : GraphCalc.independentDominationNumber G82 = 2 := by decide
example : GraphCalc.slaterNumber G82 = 2 := by decide
example : GraphCalc.annihilationNumber G82 = 3 := by decide
example : GraphCalc.zeroForcingNumber G82 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G82 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G82 := by decide
example : GraphCalc.vertexCoverNumber G82 = 3 := by decide
example : GraphCalc.totalDominationNumber G82 = 4 := by decide
example : GraphCalc.edgeCoverNumber G82 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G82 = 3 := by decide
example : GraphCalc.romanDominationNumber G82 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G82 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G82 := by decide
example : ¬ GraphCalc.IsTreeClass G82 := by decide
example : GraphCalc.IsClawFreeClass G82 := by decide
example : GraphCalc.IsCographClass G82 := by decide
example : ¬ GraphCalc.IsRegularClass G82 := by decide
example : ¬ GraphCalc.IsCubicClass G82 := by decide
example : GraphCalc.IsSubcubicClass G82 := by decide
example : ¬ GraphCalc.IsEulerianClass G82 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G82 := by decide
example : GraphCalc.IsK4FreeClass G82 := by decide
example : GraphCalc.IsNontrivialClass G82 := by decide
example : ¬ GraphCalc.IsBipartiteClass G82 := by decide

-- EK_W  (n=6, m=5)
abbrev G83 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (1, 2), (3, 5), (4, 5)]
example : GraphCalc.order G83 = 6 := by decide
example : GraphCalc.size G83 = 5 := by decide
example : SimpleGraph.minDegree G83 = 1 := by decide
example : SimpleGraph.maxDegree G83 = 2 := by decide
example : GraphCalc.indepNum G83 = 3 := by decide
example : GraphCalc.cliqueNum G83 = 2 := by decide
example : GraphCalc.dominationNumber G83 = 3 := by decide
example : GraphCalc.independentDominationNumber G83 = 3 := by decide
example : GraphCalc.slaterNumber G83 = 2 := by decide
example : GraphCalc.annihilationNumber G83 = 3 := by decide
example : GraphCalc.zeroForcingNumber G83 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G83 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G83 := by decide
example : GraphCalc.vertexCoverNumber G83 = 3 := by decide
example : GraphCalc.totalDominationNumber G83 = 4 := by decide
example : GraphCalc.edgeCoverNumber G83 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G83 = 3 := by decide
example : GraphCalc.romanDominationNumber G83 = 5 := by decide
example : GraphCalc.doubleRomanDominationNumber G83 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G83 := by decide
example : ¬ GraphCalc.IsTreeClass G83 := by decide
example : GraphCalc.IsClawFreeClass G83 := by decide
example : GraphCalc.IsCographClass G83 := by decide
example : ¬ GraphCalc.IsRegularClass G83 := by decide
example : ¬ GraphCalc.IsCubicClass G83 := by decide
example : GraphCalc.IsSubcubicClass G83 := by decide
example : ¬ GraphCalc.IsEulerianClass G83 := by decide
example : GraphCalc.IsTriangleFreeClass G83 := by decide
example : GraphCalc.IsK4FreeClass G83 := by decide
example : GraphCalc.IsNontrivialClass G83 := by decide
example : GraphCalc.IsBipartiteClass G83 := by decide

-- ECeW  (n=6, m=6)
abbrev G84 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G84 = 6 := by decide
example : GraphCalc.size G84 = 6 := by decide
example : SimpleGraph.minDegree G84 = 0 := by decide
example : SimpleGraph.maxDegree G84 = 3 := by decide
example : GraphCalc.indepNum G84 = 3 := by decide
example : GraphCalc.cliqueNum G84 = 4 := by decide
example : GraphCalc.dominationNumber G84 = 3 := by decide
example : GraphCalc.independentDominationNumber G84 = 3 := by decide
example : GraphCalc.slaterNumber G84 = 2 := by decide
example : GraphCalc.annihilationNumber G84 = 4 := by decide
example : GraphCalc.zeroForcingNumber G84 = 5 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G84 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G84 := by decide
example : GraphCalc.vertexCoverNumber G84 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G84 = 2 := by decide
example : GraphCalc.romanDominationNumber G84 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G84 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G84 := by decide
example : ¬ GraphCalc.IsTreeClass G84 := by decide
example : GraphCalc.IsClawFreeClass G84 := by decide
example : GraphCalc.IsCographClass G84 := by decide
example : ¬ GraphCalc.IsRegularClass G84 := by decide
example : ¬ GraphCalc.IsCubicClass G84 := by decide
example : GraphCalc.IsSubcubicClass G84 := by decide
example : ¬ GraphCalc.IsEulerianClass G84 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G84 := by decide
example : ¬ GraphCalc.IsK4FreeClass G84 := by decide
example : GraphCalc.IsNontrivialClass G84 := by decide
example : ¬ GraphCalc.IsBipartiteClass G84 := by decide

-- EB{?  (n=6, m=6)
abbrev G85 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G85 = 6 := by decide
example : GraphCalc.size G85 = 6 := by decide
example : SimpleGraph.minDegree G85 = 0 := by decide
example : SimpleGraph.maxDegree G85 = 4 := by decide
example : GraphCalc.indepNum G85 = 4 := by decide
example : GraphCalc.cliqueNum G85 = 3 := by decide
example : GraphCalc.dominationNumber G85 = 2 := by decide
example : GraphCalc.independentDominationNumber G85 = 2 := by decide
example : GraphCalc.slaterNumber G85 = 2 := by decide
example : GraphCalc.annihilationNumber G85 = 4 := by decide
example : GraphCalc.zeroForcingNumber G85 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G85 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G85 := by decide
example : GraphCalc.vertexCoverNumber G85 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G85 = 2 := by decide
example : GraphCalc.romanDominationNumber G85 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G85 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G85 := by decide
example : ¬ GraphCalc.IsTreeClass G85 := by decide
example : ¬ GraphCalc.IsClawFreeClass G85 := by decide
example : GraphCalc.IsCographClass G85 := by decide
example : ¬ GraphCalc.IsRegularClass G85 := by decide
example : ¬ GraphCalc.IsCubicClass G85 := by decide
example : ¬ GraphCalc.IsSubcubicClass G85 := by decide
example : ¬ GraphCalc.IsEulerianClass G85 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G85 := by decide
example : GraphCalc.IsK4FreeClass G85 := by decide
example : GraphCalc.IsNontrivialClass G85 := by decide
example : ¬ GraphCalc.IsBipartiteClass G85 := by decide

-- EJw?  (n=6, m=6)
abbrev G86 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G86 = 6 := by decide
example : GraphCalc.size G86 = 6 := by decide
example : SimpleGraph.minDegree G86 = 0 := by decide
example : SimpleGraph.maxDegree G86 = 3 := by decide
example : GraphCalc.indepNum G86 = 3 := by decide
example : GraphCalc.cliqueNum G86 = 3 := by decide
example : GraphCalc.dominationNumber G86 = 3 := by decide
example : GraphCalc.independentDominationNumber G86 = 3 := by decide
example : GraphCalc.slaterNumber G86 = 2 := by decide
example : GraphCalc.annihilationNumber G86 = 4 := by decide
example : GraphCalc.zeroForcingNumber G86 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G86 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G86 := by decide
example : GraphCalc.vertexCoverNumber G86 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G86 = 2 := by decide
example : GraphCalc.romanDominationNumber G86 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G86 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G86 := by decide
example : ¬ GraphCalc.IsTreeClass G86 := by decide
example : GraphCalc.IsClawFreeClass G86 := by decide
example : ¬ GraphCalc.IsCographClass G86 := by decide
example : ¬ GraphCalc.IsRegularClass G86 := by decide
example : ¬ GraphCalc.IsCubicClass G86 := by decide
example : GraphCalc.IsSubcubicClass G86 := by decide
example : ¬ GraphCalc.IsEulerianClass G86 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G86 := by decide
example : GraphCalc.IsK4FreeClass G86 := by decide
example : GraphCalc.IsNontrivialClass G86 := by decide
example : ¬ GraphCalc.IsBipartiteClass G86 := by decide

-- EOkW  (n=6, m=6)
abbrev G87 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 4), (2, 4), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G87 = 6 := by decide
example : GraphCalc.size G87 = 6 := by decide
example : SimpleGraph.minDegree G87 = 0 := by decide
example : SimpleGraph.maxDegree G87 = 4 := by decide
example : GraphCalc.indepNum G87 = 3 := by decide
example : GraphCalc.cliqueNum G87 = 3 := by decide
example : GraphCalc.dominationNumber G87 = 2 := by decide
example : GraphCalc.independentDominationNumber G87 = 2 := by decide
example : GraphCalc.slaterNumber G87 = 2 := by decide
example : GraphCalc.annihilationNumber G87 = 4 := by decide
example : GraphCalc.zeroForcingNumber G87 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G87 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G87 := by decide
example : GraphCalc.vertexCoverNumber G87 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G87 = 2 := by decide
example : GraphCalc.romanDominationNumber G87 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G87 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G87 := by decide
example : ¬ GraphCalc.IsTreeClass G87 := by decide
example : GraphCalc.IsClawFreeClass G87 := by decide
example : GraphCalc.IsCographClass G87 := by decide
example : ¬ GraphCalc.IsRegularClass G87 := by decide
example : ¬ GraphCalc.IsCubicClass G87 := by decide
example : ¬ GraphCalc.IsSubcubicClass G87 := by decide
example : ¬ GraphCalc.IsEulerianClass G87 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G87 := by decide
example : GraphCalc.IsK4FreeClass G87 := by decide
example : GraphCalc.IsNontrivialClass G87 := by decide
example : ¬ GraphCalc.IsBipartiteClass G87 := by decide

-- Elc?  (n=6, m=6)
abbrev G88 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4)]
example : GraphCalc.order G88 = 6 := by decide
example : GraphCalc.size G88 = 6 := by decide
example : SimpleGraph.minDegree G88 = 0 := by decide
example : SimpleGraph.maxDegree G88 = 3 := by decide
example : GraphCalc.indepNum G88 = 3 := by decide
example : GraphCalc.cliqueNum G88 = 3 := by decide
example : GraphCalc.dominationNumber G88 = 3 := by decide
example : GraphCalc.independentDominationNumber G88 = 3 := by decide
example : GraphCalc.slaterNumber G88 = 2 := by decide
example : GraphCalc.annihilationNumber G88 = 4 := by decide
example : GraphCalc.zeroForcingNumber G88 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G88 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G88 := by decide
example : GraphCalc.vertexCoverNumber G88 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G88 = 2 := by decide
example : GraphCalc.romanDominationNumber G88 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G88 = 7 := by decide
example : ¬ GraphCalc.IsConnectedClass G88 := by decide
example : ¬ GraphCalc.IsTreeClass G88 := by decide
example : GraphCalc.IsClawFreeClass G88 := by decide
example : ¬ GraphCalc.IsCographClass G88 := by decide
example : ¬ GraphCalc.IsRegularClass G88 := by decide
example : ¬ GraphCalc.IsCubicClass G88 := by decide
example : GraphCalc.IsSubcubicClass G88 := by decide
example : ¬ GraphCalc.IsEulerianClass G88 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G88 := by decide
example : GraphCalc.IsK4FreeClass G88 := by decide
example : GraphCalc.IsNontrivialClass G88 := by decide
example : ¬ GraphCalc.IsBipartiteClass G88 := by decide

-- ErW?  (n=6, m=6)
abbrev G89 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G89 = 6 := by decide
example : GraphCalc.size G89 = 6 := by decide
example : SimpleGraph.minDegree G89 = 0 := by decide
example : SimpleGraph.maxDegree G89 = 3 := by decide
example : GraphCalc.indepNum G89 = 4 := by decide
example : GraphCalc.cliqueNum G89 = 2 := by decide
example : GraphCalc.dominationNumber G89 = 3 := by decide
example : GraphCalc.independentDominationNumber G89 = 3 := by decide
example : GraphCalc.slaterNumber G89 = 2 := by decide
example : GraphCalc.annihilationNumber G89 = 4 := by decide
example : GraphCalc.zeroForcingNumber G89 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G89 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G89 := by decide
example : GraphCalc.vertexCoverNumber G89 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G89 = 2 := by decide
example : GraphCalc.romanDominationNumber G89 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G89 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G89 := by decide
example : ¬ GraphCalc.IsTreeClass G89 := by decide
example : ¬ GraphCalc.IsClawFreeClass G89 := by decide
example : GraphCalc.IsCographClass G89 := by decide
example : ¬ GraphCalc.IsRegularClass G89 := by decide
example : ¬ GraphCalc.IsCubicClass G89 := by decide
example : GraphCalc.IsSubcubicClass G89 := by decide
example : ¬ GraphCalc.IsEulerianClass G89 := by decide
example : GraphCalc.IsTriangleFreeClass G89 := by decide
example : GraphCalc.IsK4FreeClass G89 := by decide
example : GraphCalc.IsNontrivialClass G89 := by decide
example : GraphCalc.IsBipartiteClass G89 := by decide

-- E?Fw  (n=6, m=6)
abbrev G90 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 5), (1, 5), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G90 = 6 := by decide
example : GraphCalc.size G90 = 6 := by decide
example : SimpleGraph.minDegree G90 = 1 := by decide
example : SimpleGraph.maxDegree G90 = 5 := by decide
example : GraphCalc.indepNum G90 = 4 := by decide
example : GraphCalc.cliqueNum G90 = 3 := by decide
example : GraphCalc.dominationNumber G90 = 1 := by decide
example : GraphCalc.independentDominationNumber G90 = 1 := by decide
example : GraphCalc.slaterNumber G90 = 1 := by decide
example : GraphCalc.annihilationNumber G90 = 4 := by decide
example : GraphCalc.zeroForcingNumber G90 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G90 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G90 = 4 := by decide
example : GraphCalc.vertexCoverNumber G90 = 2 := by decide
example : GraphCalc.totalDominationNumber G90 = 2 := by decide
example : GraphCalc.edgeCoverNumber G90 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G90 = 2 := by decide
example : GraphCalc.romanDominationNumber G90 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G90 = 3 := by decide
example : GraphCalc.radius G90 = 1 := by decide
example : GraphCalc.IsConnectedClass G90 := by decide
example : ¬ GraphCalc.IsTreeClass G90 := by decide
example : ¬ GraphCalc.IsClawFreeClass G90 := by decide
example : GraphCalc.IsCographClass G90 := by decide
example : ¬ GraphCalc.IsRegularClass G90 := by decide
example : ¬ GraphCalc.IsCubicClass G90 := by decide
example : ¬ GraphCalc.IsSubcubicClass G90 := by decide
example : ¬ GraphCalc.IsEulerianClass G90 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G90 := by decide
example : GraphCalc.IsK4FreeClass G90 := by decide
example : GraphCalc.IsNontrivialClass G90 := by decide
example : ¬ GraphCalc.IsBipartiteClass G90 := by decide

-- EC{O  (n=6, m=6)
abbrev G91 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (3, 5)]
example : GraphCalc.order G91 = 6 := by decide
example : GraphCalc.size G91 = 6 := by decide
example : SimpleGraph.minDegree G91 = 1 := by decide
example : SimpleGraph.maxDegree G91 = 4 := by decide
example : GraphCalc.indepNum G91 = 4 := by decide
example : GraphCalc.cliqueNum G91 = 3 := by decide
example : GraphCalc.dominationNumber G91 = 2 := by decide
example : GraphCalc.independentDominationNumber G91 = 2 := by decide
example : GraphCalc.slaterNumber G91 = 2 := by decide
example : GraphCalc.annihilationNumber G91 = 4 := by decide
example : GraphCalc.zeroForcingNumber G91 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G91 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G91 = 3 := by decide
example : GraphCalc.vertexCoverNumber G91 = 2 := by decide
example : GraphCalc.totalDominationNumber G91 = 2 := by decide
example : GraphCalc.edgeCoverNumber G91 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G91 = 2 := by decide
example : GraphCalc.romanDominationNumber G91 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G91 = 5 := by decide
example : GraphCalc.radius G91 = 2 := by decide
example : GraphCalc.IsConnectedClass G91 := by decide
example : ¬ GraphCalc.IsTreeClass G91 := by decide
example : ¬ GraphCalc.IsClawFreeClass G91 := by decide
example : ¬ GraphCalc.IsCographClass G91 := by decide
example : ¬ GraphCalc.IsRegularClass G91 := by decide
example : ¬ GraphCalc.IsCubicClass G91 := by decide
example : ¬ GraphCalc.IsSubcubicClass G91 := by decide
example : ¬ GraphCalc.IsEulerianClass G91 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G91 := by decide
example : GraphCalc.IsK4FreeClass G91 := by decide
example : GraphCalc.IsNontrivialClass G91 := by decide
example : ¬ GraphCalc.IsBipartiteClass G91 := by decide

-- E@dW  (n=6, m=6)
abbrev G92 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 5), (2, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G92 = 6 := by decide
example : GraphCalc.size G92 = 6 := by decide
example : SimpleGraph.minDegree G92 = 1 := by decide
example : SimpleGraph.maxDegree G92 = 3 := by decide
example : GraphCalc.indepNum G92 = 3 := by decide
example : GraphCalc.cliqueNum G92 = 3 := by decide
example : GraphCalc.dominationNumber G92 = 3 := by decide
example : GraphCalc.independentDominationNumber G92 = 3 := by decide
example : GraphCalc.slaterNumber G92 = 2 := by decide
example : GraphCalc.annihilationNumber G92 = 4 := by decide
example : GraphCalc.zeroForcingNumber G92 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G92 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G92 = 3 := by decide
example : GraphCalc.vertexCoverNumber G92 = 3 := by decide
example : GraphCalc.totalDominationNumber G92 = 3 := by decide
example : GraphCalc.edgeCoverNumber G92 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G92 = 2 := by decide
example : GraphCalc.romanDominationNumber G92 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G92 = 7 := by decide
example : GraphCalc.radius G92 = 2 := by decide
example : GraphCalc.IsConnectedClass G92 := by decide
example : ¬ GraphCalc.IsTreeClass G92 := by decide
example : GraphCalc.IsClawFreeClass G92 := by decide
example : ¬ GraphCalc.IsCographClass G92 := by decide
example : ¬ GraphCalc.IsRegularClass G92 := by decide
example : ¬ GraphCalc.IsCubicClass G92 := by decide
example : GraphCalc.IsSubcubicClass G92 := by decide
example : ¬ GraphCalc.IsEulerianClass G92 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G92 := by decide
example : GraphCalc.IsK4FreeClass G92 := by decide
example : GraphCalc.IsNontrivialClass G92 := by decide
example : ¬ GraphCalc.IsBipartiteClass G92 := by decide

-- EG}?  (n=6, m=6)
abbrev G93 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 2), (1, 4), (2, 4), (3, 4)]
example : GraphCalc.order G93 = 6 := by decide
example : GraphCalc.size G93 = 6 := by decide
example : SimpleGraph.minDegree G93 = 1 := by decide
example : SimpleGraph.maxDegree G93 = 4 := by decide
example : GraphCalc.indepNum G93 = 3 := by decide
example : GraphCalc.cliqueNum G93 = 3 := by decide
example : GraphCalc.dominationNumber G93 = 2 := by decide
example : GraphCalc.independentDominationNumber G93 = 2 := by decide
example : GraphCalc.slaterNumber G93 = 2 := by decide
example : GraphCalc.annihilationNumber G93 = 4 := by decide
example : GraphCalc.zeroForcingNumber G93 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G93 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G93 = 3 := by decide
example : GraphCalc.vertexCoverNumber G93 = 3 := by decide
example : GraphCalc.totalDominationNumber G93 = 2 := by decide
example : GraphCalc.edgeCoverNumber G93 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G93 = 2 := by decide
example : GraphCalc.romanDominationNumber G93 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G93 = 5 := by decide
example : GraphCalc.radius G93 = 2 := by decide
example : GraphCalc.IsConnectedClass G93 := by decide
example : ¬ GraphCalc.IsTreeClass G93 := by decide
example : ¬ GraphCalc.IsClawFreeClass G93 := by decide
example : ¬ GraphCalc.IsCographClass G93 := by decide
example : ¬ GraphCalc.IsRegularClass G93 := by decide
example : ¬ GraphCalc.IsCubicClass G93 := by decide
example : ¬ GraphCalc.IsSubcubicClass G93 := by decide
example : ¬ GraphCalc.IsEulerianClass G93 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G93 := by decide
example : GraphCalc.IsK4FreeClass G93 := by decide
example : GraphCalc.IsNontrivialClass G93 := by decide
example : ¬ GraphCalc.IsBipartiteClass G93 := by decide

-- E]a?  (n=6, m=6)
abbrev G94 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3)]
example : GraphCalc.order G94 = 6 := by decide
example : GraphCalc.size G94 = 6 := by decide
example : SimpleGraph.minDegree G94 = 1 := by decide
example : SimpleGraph.maxDegree G94 = 4 := by decide
example : GraphCalc.indepNum G94 = 4 := by decide
example : GraphCalc.cliqueNum G94 = 2 := by decide
example : GraphCalc.dominationNumber G94 = 2 := by decide
example : GraphCalc.independentDominationNumber G94 = 2 := by decide
example : GraphCalc.slaterNumber G94 = 2 := by decide
example : GraphCalc.annihilationNumber G94 = 4 := by decide
example : GraphCalc.zeroForcingNumber G94 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G94 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G94 = 3 := by decide
example : GraphCalc.vertexCoverNumber G94 = 2 := by decide
example : GraphCalc.totalDominationNumber G94 = 2 := by decide
example : GraphCalc.edgeCoverNumber G94 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G94 = 2 := by decide
example : GraphCalc.romanDominationNumber G94 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G94 = 5 := by decide
example : GraphCalc.radius G94 = 2 := by decide
example : GraphCalc.IsConnectedClass G94 := by decide
example : ¬ GraphCalc.IsTreeClass G94 := by decide
example : ¬ GraphCalc.IsClawFreeClass G94 := by decide
example : ¬ GraphCalc.IsCographClass G94 := by decide
example : ¬ GraphCalc.IsRegularClass G94 := by decide
example : ¬ GraphCalc.IsCubicClass G94 := by decide
example : ¬ GraphCalc.IsSubcubicClass G94 := by decide
example : ¬ GraphCalc.IsEulerianClass G94 := by decide
example : GraphCalc.IsTriangleFreeClass G94 := by decide
example : GraphCalc.IsK4FreeClass G94 := by decide
example : GraphCalc.IsNontrivialClass G94 := by decide
example : GraphCalc.IsBipartiteClass G94 := by decide

-- EYWO  (n=6, m=6)
abbrev G95 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 5)]
example : GraphCalc.order G95 = 6 := by decide
example : GraphCalc.size G95 = 6 := by decide
example : SimpleGraph.minDegree G95 = 1 := by decide
example : SimpleGraph.maxDegree G95 = 3 := by decide
example : GraphCalc.indepNum G95 = 3 := by decide
example : GraphCalc.cliqueNum G95 = 3 := by decide
example : GraphCalc.dominationNumber G95 = 2 := by decide
example : GraphCalc.independentDominationNumber G95 = 2 := by decide
example : GraphCalc.slaterNumber G95 = 2 := by decide
example : GraphCalc.annihilationNumber G95 = 4 := by decide
example : GraphCalc.zeroForcingNumber G95 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G95 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G95 = 2 := by decide
example : GraphCalc.vertexCoverNumber G95 = 3 := by decide
example : GraphCalc.totalDominationNumber G95 = 3 := by decide
example : GraphCalc.edgeCoverNumber G95 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G95 = 2 := by decide
example : GraphCalc.romanDominationNumber G95 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G95 = 6 := by decide
example : GraphCalc.radius G95 = 2 := by decide
example : GraphCalc.IsConnectedClass G95 := by decide
example : ¬ GraphCalc.IsTreeClass G95 := by decide
example : GraphCalc.IsClawFreeClass G95 := by decide
example : ¬ GraphCalc.IsCographClass G95 := by decide
example : ¬ GraphCalc.IsRegularClass G95 := by decide
example : ¬ GraphCalc.IsCubicClass G95 := by decide
example : GraphCalc.IsSubcubicClass G95 := by decide
example : ¬ GraphCalc.IsEulerianClass G95 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G95 := by decide
example : GraphCalc.IsK4FreeClass G95 := by decide
example : GraphCalc.IsNontrivialClass G95 := by decide
example : ¬ GraphCalc.IsBipartiteClass G95 := by decide

-- E]_O  (n=6, m=6)
abbrev G96 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (3, 5)]
example : GraphCalc.order G96 = 6 := by decide
example : GraphCalc.size G96 = 6 := by decide
example : SimpleGraph.minDegree G96 = 1 := by decide
example : SimpleGraph.maxDegree G96 = 3 := by decide
example : GraphCalc.indepNum G96 = 3 := by decide
example : GraphCalc.cliqueNum G96 = 2 := by decide
example : GraphCalc.dominationNumber G96 = 2 := by decide
example : GraphCalc.independentDominationNumber G96 = 3 := by decide
example : GraphCalc.slaterNumber G96 = 2 := by decide
example : GraphCalc.annihilationNumber G96 = 4 := by decide
example : GraphCalc.zeroForcingNumber G96 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G96 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G96 = 2 := by decide
example : GraphCalc.vertexCoverNumber G96 = 3 := by decide
example : GraphCalc.totalDominationNumber G96 = 2 := by decide
example : GraphCalc.edgeCoverNumber G96 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G96 = 2 := by decide
example : GraphCalc.romanDominationNumber G96 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G96 = 6 := by decide
example : GraphCalc.radius G96 = 2 := by decide
example : GraphCalc.IsConnectedClass G96 := by decide
example : ¬ GraphCalc.IsTreeClass G96 := by decide
example : ¬ GraphCalc.IsClawFreeClass G96 := by decide
example : ¬ GraphCalc.IsCographClass G96 := by decide
example : ¬ GraphCalc.IsRegularClass G96 := by decide
example : ¬ GraphCalc.IsCubicClass G96 := by decide
example : GraphCalc.IsSubcubicClass G96 := by decide
example : ¬ GraphCalc.IsEulerianClass G96 := by decide
example : GraphCalc.IsTriangleFreeClass G96 := by decide
example : GraphCalc.IsK4FreeClass G96 := by decide
example : GraphCalc.IsNontrivialClass G96 := by decide
example : GraphCalc.IsBipartiteClass G96 := by decide

-- EQKo  (n=6, m=6)
abbrev G97 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 3), (2, 4), (2, 5), (3, 4), (3, 5)]
example : GraphCalc.order G97 = 6 := by decide
example : GraphCalc.size G97 = 6 := by decide
example : SimpleGraph.minDegree G97 = 1 := by decide
example : SimpleGraph.maxDegree G97 = 3 := by decide
example : GraphCalc.indepNum G97 = 4 := by decide
example : GraphCalc.cliqueNum G97 = 2 := by decide
example : GraphCalc.dominationNumber G97 = 2 := by decide
example : GraphCalc.independentDominationNumber G97 = 2 := by decide
example : GraphCalc.slaterNumber G97 = 2 := by decide
example : GraphCalc.annihilationNumber G97 = 4 := by decide
example : GraphCalc.zeroForcingNumber G97 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G97 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G97 = 3 := by decide
example : GraphCalc.vertexCoverNumber G97 = 2 := by decide
example : GraphCalc.totalDominationNumber G97 = 3 := by decide
example : GraphCalc.edgeCoverNumber G97 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G97 = 2 := by decide
example : GraphCalc.romanDominationNumber G97 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G97 = 6 := by decide
example : GraphCalc.radius G97 = 2 := by decide
example : GraphCalc.IsConnectedClass G97 := by decide
example : ¬ GraphCalc.IsTreeClass G97 := by decide
example : ¬ GraphCalc.IsClawFreeClass G97 := by decide
example : ¬ GraphCalc.IsCographClass G97 := by decide
example : ¬ GraphCalc.IsRegularClass G97 := by decide
example : ¬ GraphCalc.IsCubicClass G97 := by decide
example : GraphCalc.IsSubcubicClass G97 := by decide
example : ¬ GraphCalc.IsEulerianClass G97 := by decide
example : GraphCalc.IsTriangleFreeClass G97 := by decide
example : GraphCalc.IsK4FreeClass G97 := by decide
example : GraphCalc.IsNontrivialClass G97 := by decide
example : GraphCalc.IsBipartiteClass G97 := by decide

-- EsCW  (n=6, m=6)
abbrev G98 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G98 = 6 := by decide
example : GraphCalc.size G98 = 6 := by decide
example : SimpleGraph.minDegree G98 = 1 := by decide
example : SimpleGraph.maxDegree G98 = 3 := by decide
example : GraphCalc.indepNum G98 = 3 := by decide
example : GraphCalc.cliqueNum G98 = 3 := by decide
example : GraphCalc.dominationNumber G98 = 2 := by decide
example : GraphCalc.independentDominationNumber G98 = 2 := by decide
example : GraphCalc.slaterNumber G98 = 2 := by decide
example : GraphCalc.annihilationNumber G98 = 4 := by decide
example : GraphCalc.zeroForcingNumber G98 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G98 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G98 = 4 := by decide
example : GraphCalc.vertexCoverNumber G98 = 3 := by decide
example : GraphCalc.totalDominationNumber G98 = 2 := by decide
example : GraphCalc.edgeCoverNumber G98 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G98 = 2 := by decide
example : GraphCalc.romanDominationNumber G98 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G98 = 6 := by decide
example : GraphCalc.radius G98 = 2 := by decide
example : GraphCalc.IsConnectedClass G98 := by decide
example : ¬ GraphCalc.IsTreeClass G98 := by decide
example : ¬ GraphCalc.IsClawFreeClass G98 := by decide
example : ¬ GraphCalc.IsCographClass G98 := by decide
example : ¬ GraphCalc.IsRegularClass G98 := by decide
example : ¬ GraphCalc.IsCubicClass G98 := by decide
example : GraphCalc.IsSubcubicClass G98 := by decide
example : ¬ GraphCalc.IsEulerianClass G98 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G98 := by decide
example : GraphCalc.IsK4FreeClass G98 := by decide
example : GraphCalc.IsNontrivialClass G98 := by decide
example : ¬ GraphCalc.IsBipartiteClass G98 := by decide

-- EKaW  (n=6, m=6)
abbrev G99 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 3), (0, 4), (0, 5), (1, 2), (3, 5), (4, 5)]
example : GraphCalc.order G99 = 6 := by decide
example : GraphCalc.size G99 = 6 := by decide
example : SimpleGraph.minDegree G99 = 1 := by decide
example : SimpleGraph.maxDegree G99 = 3 := by decide
example : GraphCalc.indepNum G99 = 3 := by decide
example : GraphCalc.cliqueNum G99 = 3 := by decide
example : GraphCalc.dominationNumber G99 = 2 := by decide
example : GraphCalc.independentDominationNumber G99 = 2 := by decide
example : GraphCalc.slaterNumber G99 = 2 := by decide
example : GraphCalc.annihilationNumber G99 = 4 := by decide
example : GraphCalc.zeroForcingNumber G99 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G99 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G99 := by decide
example : GraphCalc.vertexCoverNumber G99 = 3 := by decide
example : GraphCalc.totalDominationNumber G99 = 4 := by decide
example : GraphCalc.edgeCoverNumber G99 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G99 = 2 := by decide
example : GraphCalc.romanDominationNumber G99 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G99 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G99 := by decide
example : ¬ GraphCalc.IsTreeClass G99 := by decide
example : GraphCalc.IsClawFreeClass G99 := by decide
example : GraphCalc.IsCographClass G99 := by decide
example : ¬ GraphCalc.IsRegularClass G99 := by decide
example : ¬ GraphCalc.IsCubicClass G99 := by decide
example : GraphCalc.IsSubcubicClass G99 := by decide
example : ¬ GraphCalc.IsEulerianClass G99 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G99 := by decide
example : GraphCalc.IsK4FreeClass G99 := by decide
example : GraphCalc.IsNontrivialClass G99 := by decide
example : ¬ GraphCalc.IsBipartiteClass G99 := by decide

-- EJe?  (n=6, m=6)
abbrev G100 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 2), (1, 3), (2, 3), (3, 4)]
example : GraphCalc.order G100 = 6 := by decide
example : GraphCalc.size G100 = 6 := by decide
example : SimpleGraph.minDegree G100 = 1 := by decide
example : SimpleGraph.maxDegree G100 = 3 := by decide
example : GraphCalc.indepNum G100 = 3 := by decide
example : GraphCalc.cliqueNum G100 = 3 := by decide
example : GraphCalc.dominationNumber G100 = 2 := by decide
example : GraphCalc.independentDominationNumber G100 = 2 := by decide
example : GraphCalc.slaterNumber G100 = 2 := by decide
example : GraphCalc.annihilationNumber G100 = 3 := by decide
example : GraphCalc.zeroForcingNumber G100 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G100 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G100 = 2 := by decide
example : GraphCalc.vertexCoverNumber G100 = 3 := by decide
example : GraphCalc.totalDominationNumber G100 = 3 := by decide
example : GraphCalc.edgeCoverNumber G100 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G100 = 3 := by decide
example : GraphCalc.romanDominationNumber G100 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G100 = 6 := by decide
example : GraphCalc.radius G100 = 2 := by decide
example : GraphCalc.IsConnectedClass G100 := by decide
example : ¬ GraphCalc.IsTreeClass G100 := by decide
example : GraphCalc.IsClawFreeClass G100 := by decide
example : ¬ GraphCalc.IsCographClass G100 := by decide
example : ¬ GraphCalc.IsRegularClass G100 := by decide
example : ¬ GraphCalc.IsCubicClass G100 := by decide
example : GraphCalc.IsSubcubicClass G100 := by decide
example : ¬ GraphCalc.IsEulerianClass G100 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G100 := by decide
example : GraphCalc.IsK4FreeClass G100 := by decide
example : GraphCalc.IsNontrivialClass G100 := by decide
example : ¬ GraphCalc.IsBipartiteClass G100 := by decide

-- EBy?  (n=6, m=6)
abbrev G101 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G101 = 6 := by decide
example : GraphCalc.size G101 = 6 := by decide
example : SimpleGraph.minDegree G101 = 1 := by decide
example : SimpleGraph.maxDegree G101 = 3 := by decide
example : GraphCalc.indepNum G101 = 3 := by decide
example : GraphCalc.cliqueNum G101 = 2 := by decide
example : GraphCalc.dominationNumber G101 = 2 := by decide
example : GraphCalc.independentDominationNumber G101 = 2 := by decide
example : GraphCalc.slaterNumber G101 = 2 := by decide
example : GraphCalc.annihilationNumber G101 = 3 := by decide
example : GraphCalc.zeroForcingNumber G101 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G101 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G101 = 2 := by decide
example : GraphCalc.vertexCoverNumber G101 = 3 := by decide
example : GraphCalc.totalDominationNumber G101 = 3 := by decide
example : GraphCalc.edgeCoverNumber G101 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G101 = 3 := by decide
example : GraphCalc.romanDominationNumber G101 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G101 = 6 := by decide
example : GraphCalc.radius G101 = 2 := by decide
example : GraphCalc.IsConnectedClass G101 := by decide
example : ¬ GraphCalc.IsTreeClass G101 := by decide
example : ¬ GraphCalc.IsClawFreeClass G101 := by decide
example : ¬ GraphCalc.IsCographClass G101 := by decide
example : ¬ GraphCalc.IsRegularClass G101 := by decide
example : ¬ GraphCalc.IsCubicClass G101 := by decide
example : GraphCalc.IsSubcubicClass G101 := by decide
example : ¬ GraphCalc.IsEulerianClass G101 := by decide
example : GraphCalc.IsTriangleFreeClass G101 := by decide
example : GraphCalc.IsK4FreeClass G101 := by decide
example : GraphCalc.IsNontrivialClass G101 := by decide
example : GraphCalc.IsBipartiteClass G101 := by decide

-- Ehd?  (n=6, m=6)
abbrev G102 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (3, 4)]
example : GraphCalc.order G102 = 6 := by decide
example : GraphCalc.size G102 = 6 := by decide
example : SimpleGraph.minDegree G102 = 1 := by decide
example : SimpleGraph.maxDegree G102 = 3 := by decide
example : GraphCalc.indepNum G102 = 3 := by decide
example : GraphCalc.cliqueNum G102 = 2 := by decide
example : GraphCalc.dominationNumber G102 = 2 := by decide
example : GraphCalc.independentDominationNumber G102 = 2 := by decide
example : GraphCalc.slaterNumber G102 = 2 := by decide
example : GraphCalc.annihilationNumber G102 = 3 := by decide
example : GraphCalc.zeroForcingNumber G102 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G102 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G102 = 2 := by decide
example : GraphCalc.vertexCoverNumber G102 = 3 := by decide
example : GraphCalc.totalDominationNumber G102 = 3 := by decide
example : GraphCalc.edgeCoverNumber G102 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G102 = 3 := by decide
example : GraphCalc.romanDominationNumber G102 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G102 = 6 := by decide
example : GraphCalc.radius G102 = 2 := by decide
example : GraphCalc.IsConnectedClass G102 := by decide
example : ¬ GraphCalc.IsTreeClass G102 := by decide
example : ¬ GraphCalc.IsClawFreeClass G102 := by decide
example : ¬ GraphCalc.IsCographClass G102 := by decide
example : ¬ GraphCalc.IsRegularClass G102 := by decide
example : ¬ GraphCalc.IsCubicClass G102 := by decide
example : GraphCalc.IsSubcubicClass G102 := by decide
example : ¬ GraphCalc.IsEulerianClass G102 := by decide
example : GraphCalc.IsTriangleFreeClass G102 := by decide
example : GraphCalc.IsK4FreeClass G102 := by decide
example : GraphCalc.IsNontrivialClass G102 := by decide
example : ¬ GraphCalc.IsBipartiteClass G102 := by decide

-- EhEG  (n=6, m=6)
abbrev G103 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G103 = 6 := by decide
example : GraphCalc.size G103 = 6 := by decide
example : SimpleGraph.minDegree G103 = 2 := by decide
example : SimpleGraph.maxDegree G103 = 2 := by decide
example : GraphCalc.indepNum G103 = 3 := by decide
example : GraphCalc.cliqueNum G103 = 2 := by decide
example : GraphCalc.dominationNumber G103 = 2 := by decide
example : GraphCalc.independentDominationNumber G103 = 2 := by decide
example : GraphCalc.slaterNumber G103 = 2 := by decide
example : GraphCalc.annihilationNumber G103 = 3 := by decide
example : GraphCalc.zeroForcingNumber G103 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G103 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G103 = 2 := by decide
example : GraphCalc.vertexCoverNumber G103 = 3 := by decide
example : GraphCalc.totalDominationNumber G103 = 4 := by decide
example : GraphCalc.edgeCoverNumber G103 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G103 = 3 := by decide
example : GraphCalc.romanDominationNumber G103 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G103 = 6 := by decide
example : GraphCalc.radius G103 = 3 := by decide
example : GraphCalc.IsConnectedClass G103 := by decide
example : ¬ GraphCalc.IsTreeClass G103 := by decide
example : GraphCalc.IsClawFreeClass G103 := by decide
example : ¬ GraphCalc.IsCographClass G103 := by decide
example : GraphCalc.IsRegularClass G103 := by decide
example : ¬ GraphCalc.IsCubicClass G103 := by decide
example : GraphCalc.IsSubcubicClass G103 := by decide
example : GraphCalc.IsEulerianClass G103 := by decide
example : GraphCalc.IsTriangleFreeClass G103 := by decide
example : GraphCalc.IsK4FreeClass G103 := by decide
example : GraphCalc.IsNontrivialClass G103 := by decide
example : GraphCalc.IsBipartiteClass G103 := by decide

-- EJaG  (n=6, m=6)
abbrev G104 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 2), (1, 3), (2, 3), (4, 5)]
example : GraphCalc.order G104 = 6 := by decide
example : GraphCalc.size G104 = 6 := by decide
example : SimpleGraph.minDegree G104 = 2 := by decide
example : SimpleGraph.maxDegree G104 = 2 := by decide
example : GraphCalc.indepNum G104 = 2 := by decide
example : GraphCalc.cliqueNum G104 = 3 := by decide
example : GraphCalc.dominationNumber G104 = 2 := by decide
example : GraphCalc.independentDominationNumber G104 = 2 := by decide
example : GraphCalc.slaterNumber G104 = 2 := by decide
example : GraphCalc.annihilationNumber G104 = 3 := by decide
example : GraphCalc.zeroForcingNumber G104 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G104 = 4 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G104 := by decide
example : GraphCalc.vertexCoverNumber G104 = 4 := by decide
example : GraphCalc.totalDominationNumber G104 = 4 := by decide
example : GraphCalc.edgeCoverNumber G104 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G104 = 3 := by decide
example : GraphCalc.romanDominationNumber G104 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G104 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G104 := by decide
example : ¬ GraphCalc.IsTreeClass G104 := by decide
example : GraphCalc.IsClawFreeClass G104 := by decide
example : GraphCalc.IsCographClass G104 := by decide
example : GraphCalc.IsRegularClass G104 := by decide
example : ¬ GraphCalc.IsCubicClass G104 := by decide
example : GraphCalc.IsSubcubicClass G104 := by decide
example : ¬ GraphCalc.IsEulerianClass G104 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G104 := by decide
example : GraphCalc.IsK4FreeClass G104 := by decide
example : GraphCalc.IsNontrivialClass G104 := by decide
example : ¬ GraphCalc.IsBipartiteClass G104 := by decide

-- E~A?  (n=6, m=7)
abbrev G105 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G105 = 6 := by decide
example : GraphCalc.size G105 = 7 := by decide
example : SimpleGraph.minDegree G105 = 0 := by decide
example : SimpleGraph.maxDegree G105 = 4 := by decide
example : GraphCalc.indepNum G105 = 3 := by decide
example : GraphCalc.cliqueNum G105 = 4 := by decide
example : GraphCalc.dominationNumber G105 = 2 := by decide
example : GraphCalc.independentDominationNumber G105 = 2 := by decide
example : GraphCalc.slaterNumber G105 = 2 := by decide
example : GraphCalc.annihilationNumber G105 = 4 := by decide
example : GraphCalc.zeroForcingNumber G105 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G105 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G105 := by decide
example : GraphCalc.vertexCoverNumber G105 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G105 = 2 := by decide
example : GraphCalc.romanDominationNumber G105 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G105 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G105 := by decide
example : ¬ GraphCalc.IsTreeClass G105 := by decide
example : GraphCalc.IsClawFreeClass G105 := by decide
example : GraphCalc.IsCographClass G105 := by decide
example : ¬ GraphCalc.IsRegularClass G105 := by decide
example : ¬ GraphCalc.IsCubicClass G105 := by decide
example : ¬ GraphCalc.IsSubcubicClass G105 := by decide
example : ¬ GraphCalc.IsEulerianClass G105 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G105 := by decide
example : ¬ GraphCalc.IsK4FreeClass G105 := by decide
example : GraphCalc.IsNontrivialClass G105 := by decide
example : ¬ GraphCalc.IsBipartiteClass G105 := by decide

-- EzW?  (n=6, m=7)
abbrev G106 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G106 = 6 := by decide
example : GraphCalc.size G106 = 7 := by decide
example : SimpleGraph.minDegree G106 = 0 := by decide
example : SimpleGraph.maxDegree G106 = 4 := by decide
example : GraphCalc.indepNum G106 = 4 := by decide
example : GraphCalc.cliqueNum G106 = 3 := by decide
example : GraphCalc.dominationNumber G106 = 2 := by decide
example : GraphCalc.independentDominationNumber G106 = 2 := by decide
example : GraphCalc.slaterNumber G106 = 2 := by decide
example : GraphCalc.annihilationNumber G106 = 4 := by decide
example : GraphCalc.zeroForcingNumber G106 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G106 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G106 := by decide
example : GraphCalc.vertexCoverNumber G106 = 2 := by decide
example : GraphCalc.subTotalDominationNumber G106 = 2 := by decide
example : GraphCalc.romanDominationNumber G106 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G106 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G106 := by decide
example : ¬ GraphCalc.IsTreeClass G106 := by decide
example : ¬ GraphCalc.IsClawFreeClass G106 := by decide
example : GraphCalc.IsCographClass G106 := by decide
example : ¬ GraphCalc.IsRegularClass G106 := by decide
example : ¬ GraphCalc.IsCubicClass G106 := by decide
example : ¬ GraphCalc.IsSubcubicClass G106 := by decide
example : ¬ GraphCalc.IsEulerianClass G106 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G106 := by decide
example : GraphCalc.IsK4FreeClass G106 := by decide
example : GraphCalc.IsNontrivialClass G106 := by decide
example : ¬ GraphCalc.IsBipartiteClass G106 := by decide

-- Ejs?  (n=6, m=7)
abbrev G107 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
example : GraphCalc.order G107 = 6 := by decide
example : GraphCalc.size G107 = 7 := by decide
example : SimpleGraph.minDegree G107 = 0 := by decide
example : SimpleGraph.maxDegree G107 = 4 := by decide
example : GraphCalc.indepNum G107 = 3 := by decide
example : GraphCalc.cliqueNum G107 = 3 := by decide
example : GraphCalc.dominationNumber G107 = 2 := by decide
example : GraphCalc.independentDominationNumber G107 = 2 := by decide
example : GraphCalc.slaterNumber G107 = 2 := by decide
example : GraphCalc.annihilationNumber G107 = 4 := by decide
example : GraphCalc.zeroForcingNumber G107 = 3 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G107 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G107 := by decide
example : GraphCalc.vertexCoverNumber G107 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G107 = 2 := by decide
example : GraphCalc.romanDominationNumber G107 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G107 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G107 := by decide
example : ¬ GraphCalc.IsTreeClass G107 := by decide
example : GraphCalc.IsClawFreeClass G107 := by decide
example : ¬ GraphCalc.IsCographClass G107 := by decide
example : ¬ GraphCalc.IsRegularClass G107 := by decide
example : ¬ GraphCalc.IsCubicClass G107 := by decide
example : ¬ GraphCalc.IsSubcubicClass G107 := by decide
example : ¬ GraphCalc.IsEulerianClass G107 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G107 := by decide
example : GraphCalc.IsK4FreeClass G107 := by decide
example : GraphCalc.IsNontrivialClass G107 := by decide
example : ¬ GraphCalc.IsBipartiteClass G107 := by decide

-- Ev@_  (n=6, m=7)
abbrev G108 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 3), (1, 5), (2, 3), (2, 5)]
example : GraphCalc.order G108 = 6 := by decide
example : GraphCalc.size G108 = 7 := by decide
example : SimpleGraph.minDegree G108 = 0 := by decide
example : SimpleGraph.maxDegree G108 = 3 := by decide
example : GraphCalc.indepNum G108 = 3 := by decide
example : GraphCalc.cliqueNum G108 = 3 := by decide
example : GraphCalc.dominationNumber G108 = 3 := by decide
example : GraphCalc.independentDominationNumber G108 = 3 := by decide
example : GraphCalc.slaterNumber G108 = 2 := by decide
example : GraphCalc.annihilationNumber G108 = 3 := by decide
example : GraphCalc.zeroForcingNumber G108 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G108 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G108 := by decide
example : GraphCalc.vertexCoverNumber G108 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G108 = 2 := by decide
example : GraphCalc.romanDominationNumber G108 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G108 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G108 := by decide
example : ¬ GraphCalc.IsTreeClass G108 := by decide
example : GraphCalc.IsClawFreeClass G108 := by decide
example : GraphCalc.IsCographClass G108 := by decide
example : ¬ GraphCalc.IsRegularClass G108 := by decide
example : ¬ GraphCalc.IsCubicClass G108 := by decide
example : GraphCalc.IsSubcubicClass G108 := by decide
example : ¬ GraphCalc.IsEulerianClass G108 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G108 := by decide
example : GraphCalc.IsK4FreeClass G108 := by decide
example : GraphCalc.IsNontrivialClass G108 := by decide
example : ¬ GraphCalc.IsBipartiteClass G108 := by decide

-- EB{G  (n=6, m=7)
abbrev G109 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G109 = 6 := by decide
example : GraphCalc.size G109 = 7 := by decide
example : SimpleGraph.minDegree G109 = 1 := by decide
example : SimpleGraph.maxDegree G109 = 5 := by decide
example : GraphCalc.indepNum G109 = 4 := by decide
example : GraphCalc.cliqueNum G109 = 3 := by decide
example : GraphCalc.dominationNumber G109 = 1 := by decide
example : GraphCalc.independentDominationNumber G109 = 1 := by decide
example : GraphCalc.slaterNumber G109 = 1 := by decide
example : GraphCalc.annihilationNumber G109 = 4 := by decide
example : GraphCalc.zeroForcingNumber G109 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G109 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G109 = 3 := by decide
example : GraphCalc.vertexCoverNumber G109 = 2 := by decide
example : GraphCalc.totalDominationNumber G109 = 2 := by decide
example : GraphCalc.edgeCoverNumber G109 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G109 = 2 := by decide
example : GraphCalc.romanDominationNumber G109 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G109 = 3 := by decide
example : GraphCalc.radius G109 = 1 := by decide
example : GraphCalc.IsConnectedClass G109 := by decide
example : ¬ GraphCalc.IsTreeClass G109 := by decide
example : ¬ GraphCalc.IsClawFreeClass G109 := by decide
example : GraphCalc.IsCographClass G109 := by decide
example : ¬ GraphCalc.IsRegularClass G109 := by decide
example : ¬ GraphCalc.IsCubicClass G109 := by decide
example : ¬ GraphCalc.IsSubcubicClass G109 := by decide
example : ¬ GraphCalc.IsEulerianClass G109 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G109 := by decide
example : GraphCalc.IsK4FreeClass G109 := by decide
example : GraphCalc.IsNontrivialClass G109 := by decide
example : ¬ GraphCalc.IsBipartiteClass G109 := by decide

-- EhX_  (n=6, m=7)
abbrev G110 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)]
example : GraphCalc.order G110 = 6 := by decide
example : GraphCalc.size G110 = 7 := by decide
example : SimpleGraph.minDegree G110 = 1 := by decide
example : SimpleGraph.maxDegree G110 = 4 := by decide
example : GraphCalc.indepNum G110 = 4 := by decide
example : GraphCalc.cliqueNum G110 = 3 := by decide
example : GraphCalc.dominationNumber G110 = 2 := by decide
example : GraphCalc.independentDominationNumber G110 = 2 := by decide
example : GraphCalc.slaterNumber G110 = 2 := by decide
example : GraphCalc.annihilationNumber G110 = 4 := by decide
example : GraphCalc.zeroForcingNumber G110 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G110 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G110 = 3 := by decide
example : GraphCalc.vertexCoverNumber G110 = 2 := by decide
example : GraphCalc.totalDominationNumber G110 = 2 := by decide
example : GraphCalc.edgeCoverNumber G110 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G110 = 2 := by decide
example : GraphCalc.romanDominationNumber G110 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G110 = 5 := by decide
example : GraphCalc.radius G110 = 2 := by decide
example : GraphCalc.IsConnectedClass G110 := by decide
example : ¬ GraphCalc.IsTreeClass G110 := by decide
example : ¬ GraphCalc.IsClawFreeClass G110 := by decide
example : ¬ GraphCalc.IsCographClass G110 := by decide
example : ¬ GraphCalc.IsRegularClass G110 := by decide
example : ¬ GraphCalc.IsCubicClass G110 := by decide
example : ¬ GraphCalc.IsSubcubicClass G110 := by decide
example : ¬ GraphCalc.IsEulerianClass G110 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G110 := by decide
example : GraphCalc.IsK4FreeClass G110 := by decide
example : GraphCalc.IsNontrivialClass G110 := by decide
example : ¬ GraphCalc.IsBipartiteClass G110 := by decide

-- E^_O  (n=6, m=7)
abbrev G111 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (3, 5)]
example : GraphCalc.order G111 = 6 := by decide
example : GraphCalc.size G111 = 7 := by decide
example : SimpleGraph.minDegree G111 = 1 := by decide
example : SimpleGraph.maxDegree G111 = 4 := by decide
example : GraphCalc.indepNum G111 = 3 := by decide
example : GraphCalc.cliqueNum G111 = 3 := by decide
example : GraphCalc.dominationNumber G111 = 2 := by decide
example : GraphCalc.independentDominationNumber G111 = 2 := by decide
example : GraphCalc.slaterNumber G111 = 2 := by decide
example : GraphCalc.annihilationNumber G111 = 4 := by decide
example : GraphCalc.zeroForcingNumber G111 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G111 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G111 = 2 := by decide
example : GraphCalc.vertexCoverNumber G111 = 3 := by decide
example : GraphCalc.totalDominationNumber G111 = 2 := by decide
example : GraphCalc.edgeCoverNumber G111 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G111 = 2 := by decide
example : GraphCalc.romanDominationNumber G111 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G111 = 5 := by decide
example : GraphCalc.radius G111 = 2 := by decide
example : GraphCalc.IsConnectedClass G111 := by decide
example : ¬ GraphCalc.IsTreeClass G111 := by decide
example : ¬ GraphCalc.IsClawFreeClass G111 := by decide
example : ¬ GraphCalc.IsCographClass G111 := by decide
example : ¬ GraphCalc.IsRegularClass G111 := by decide
example : ¬ GraphCalc.IsCubicClass G111 := by decide
example : ¬ GraphCalc.IsSubcubicClass G111 := by decide
example : ¬ GraphCalc.IsEulerianClass G111 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G111 := by decide
example : GraphCalc.IsK4FreeClass G111 := by decide
example : GraphCalc.IsNontrivialClass G111 := by decide
example : ¬ GraphCalc.IsBipartiteClass G111 := by decide

-- EJwG  (n=6, m=7)
abbrev G112 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (4, 5)]
example : GraphCalc.order G112 = 6 := by decide
example : GraphCalc.size G112 = 7 := by decide
example : SimpleGraph.minDegree G112 = 1 := by decide
example : SimpleGraph.maxDegree G112 = 4 := by decide
example : GraphCalc.indepNum G112 = 3 := by decide
example : GraphCalc.cliqueNum G112 = 3 := by decide
example : GraphCalc.dominationNumber G112 = 2 := by decide
example : GraphCalc.independentDominationNumber G112 = 2 := by decide
example : GraphCalc.slaterNumber G112 = 2 := by decide
example : GraphCalc.annihilationNumber G112 = 4 := by decide
example : GraphCalc.zeroForcingNumber G112 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G112 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G112 = 4 := by decide
example : GraphCalc.vertexCoverNumber G112 = 3 := by decide
example : GraphCalc.totalDominationNumber G112 = 2 := by decide
example : GraphCalc.edgeCoverNumber G112 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G112 = 2 := by decide
example : GraphCalc.romanDominationNumber G112 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G112 = 5 := by decide
example : GraphCalc.radius G112 = 2 := by decide
example : GraphCalc.IsConnectedClass G112 := by decide
example : ¬ GraphCalc.IsTreeClass G112 := by decide
example : ¬ GraphCalc.IsClawFreeClass G112 := by decide
example : ¬ GraphCalc.IsCographClass G112 := by decide
example : ¬ GraphCalc.IsRegularClass G112 := by decide
example : ¬ GraphCalc.IsCubicClass G112 := by decide
example : ¬ GraphCalc.IsSubcubicClass G112 := by decide
example : ¬ GraphCalc.IsEulerianClass G112 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G112 := by decide
example : GraphCalc.IsK4FreeClass G112 := by decide
example : GraphCalc.IsNontrivialClass G112 := by decide
example : ¬ GraphCalc.IsBipartiteClass G112 := by decide

-- E`Xg  (n=6, m=7)
abbrev G113 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (4, 5)]
example : GraphCalc.order G113 = 6 := by decide
example : GraphCalc.size G113 = 7 := by decide
example : SimpleGraph.minDegree G113 = 1 := by decide
example : SimpleGraph.maxDegree G113 = 3 := by decide
example : GraphCalc.indepNum G113 = 3 := by decide
example : GraphCalc.cliqueNum G113 = 3 := by decide
example : GraphCalc.dominationNumber G113 = 2 := by decide
example : GraphCalc.independentDominationNumber G113 = 2 := by decide
example : GraphCalc.slaterNumber G113 = 2 := by decide
example : GraphCalc.annihilationNumber G113 = 3 := by decide
example : GraphCalc.zeroForcingNumber G113 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G113 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G113 = 3 := by decide
example : GraphCalc.vertexCoverNumber G113 = 3 := by decide
example : GraphCalc.totalDominationNumber G113 = 3 := by decide
example : GraphCalc.edgeCoverNumber G113 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G113 = 2 := by decide
example : GraphCalc.romanDominationNumber G113 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G113 = 6 := by decide
example : GraphCalc.radius G113 = 2 := by decide
example : GraphCalc.IsConnectedClass G113 := by decide
example : ¬ GraphCalc.IsTreeClass G113 := by decide
example : GraphCalc.IsClawFreeClass G113 := by decide
example : ¬ GraphCalc.IsCographClass G113 := by decide
example : ¬ GraphCalc.IsRegularClass G113 := by decide
example : ¬ GraphCalc.IsCubicClass G113 := by decide
example : GraphCalc.IsSubcubicClass G113 := by decide
example : ¬ GraphCalc.IsEulerianClass G113 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G113 := by decide
example : GraphCalc.IsK4FreeClass G113 := by decide
example : GraphCalc.IsNontrivialClass G113 := by decide
example : ¬ GraphCalc.IsBipartiteClass G113 := by decide

-- E~?G  (n=6, m=7)
abbrev G114 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (4, 5)]
example : GraphCalc.order G114 = 6 := by decide
example : GraphCalc.size G114 = 7 := by decide
example : SimpleGraph.minDegree G114 = 1 := by decide
example : SimpleGraph.maxDegree G114 = 3 := by decide
example : GraphCalc.indepNum G114 = 2 := by decide
example : GraphCalc.cliqueNum G114 = 4 := by decide
example : GraphCalc.dominationNumber G114 = 2 := by decide
example : GraphCalc.independentDominationNumber G114 = 2 := by decide
example : GraphCalc.slaterNumber G114 = 2 := by decide
example : GraphCalc.annihilationNumber G114 = 3 := by decide
example : GraphCalc.zeroForcingNumber G114 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G114 = 5 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G114 := by decide
example : GraphCalc.vertexCoverNumber G114 = 4 := by decide
example : GraphCalc.totalDominationNumber G114 = 4 := by decide
example : GraphCalc.edgeCoverNumber G114 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G114 = 2 := by decide
example : GraphCalc.romanDominationNumber G114 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G114 = 6 := by decide
example : ¬ GraphCalc.IsConnectedClass G114 := by decide
example : ¬ GraphCalc.IsTreeClass G114 := by decide
example : GraphCalc.IsClawFreeClass G114 := by decide
example : GraphCalc.IsCographClass G114 := by decide
example : ¬ GraphCalc.IsRegularClass G114 := by decide
example : ¬ GraphCalc.IsCubicClass G114 := by decide
example : GraphCalc.IsSubcubicClass G114 := by decide
example : ¬ GraphCalc.IsEulerianClass G114 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G114 := by decide
example : ¬ GraphCalc.IsK4FreeClass G114 := by decide
example : GraphCalc.IsNontrivialClass G114 := by decide
example : ¬ GraphCalc.IsBipartiteClass G114 := by decide

-- EtaG  (n=6, m=7)
abbrev G115 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (2, 3), (4, 5)]
example : GraphCalc.order G115 = 6 := by decide
example : GraphCalc.size G115 = 7 := by decide
example : SimpleGraph.minDegree G115 = 1 := by decide
example : SimpleGraph.maxDegree G115 = 5 := by decide
example : GraphCalc.indepNum G115 = 3 := by decide
example : GraphCalc.cliqueNum G115 = 3 := by decide
example : GraphCalc.dominationNumber G115 = 1 := by decide
example : GraphCalc.independentDominationNumber G115 = 1 := by decide
example : GraphCalc.slaterNumber G115 = 1 := by decide
example : GraphCalc.annihilationNumber G115 = 4 := by decide
example : GraphCalc.zeroForcingNumber G115 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G115 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G115 = 3 := by decide
example : GraphCalc.vertexCoverNumber G115 = 3 := by decide
example : GraphCalc.totalDominationNumber G115 = 2 := by decide
example : GraphCalc.edgeCoverNumber G115 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G115 = 2 := by decide
example : GraphCalc.romanDominationNumber G115 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G115 = 3 := by decide
example : GraphCalc.radius G115 = 1 := by decide
example : GraphCalc.IsConnectedClass G115 := by decide
example : ¬ GraphCalc.IsTreeClass G115 := by decide
example : ¬ GraphCalc.IsClawFreeClass G115 := by decide
example : GraphCalc.IsCographClass G115 := by decide
example : ¬ GraphCalc.IsRegularClass G115 := by decide
example : ¬ GraphCalc.IsCubicClass G115 := by decide
example : ¬ GraphCalc.IsSubcubicClass G115 := by decide
example : ¬ GraphCalc.IsEulerianClass G115 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G115 := by decide
example : GraphCalc.IsK4FreeClass G115 := by decide
example : GraphCalc.IsNontrivialClass G115 := by decide
example : ¬ GraphCalc.IsBipartiteClass G115 := by decide

-- Eht?  (n=6, m=7)
abbrev G116 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 4), (1, 5), (2, 3), (3, 4)]
example : GraphCalc.order G116 = 6 := by decide
example : GraphCalc.size G116 = 7 := by decide
example : SimpleGraph.minDegree G116 = 1 := by decide
example : SimpleGraph.maxDegree G116 = 4 := by decide
example : GraphCalc.indepNum G116 = 3 := by decide
example : GraphCalc.cliqueNum G116 = 3 := by decide
example : GraphCalc.dominationNumber G116 = 2 := by decide
example : GraphCalc.independentDominationNumber G116 = 2 := by decide
example : GraphCalc.slaterNumber G116 = 2 := by decide
example : GraphCalc.annihilationNumber G116 = 4 := by decide
example : GraphCalc.zeroForcingNumber G116 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G116 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G116 = 2 := by decide
example : GraphCalc.vertexCoverNumber G116 = 3 := by decide
example : GraphCalc.totalDominationNumber G116 = 2 := by decide
example : GraphCalc.edgeCoverNumber G116 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G116 = 2 := by decide
example : GraphCalc.romanDominationNumber G116 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G116 = 5 := by decide
example : GraphCalc.radius G116 = 2 := by decide
example : GraphCalc.IsConnectedClass G116 := by decide
example : ¬ GraphCalc.IsTreeClass G116 := by decide
example : ¬ GraphCalc.IsClawFreeClass G116 := by decide
example : ¬ GraphCalc.IsCographClass G116 := by decide
example : ¬ GraphCalc.IsRegularClass G116 := by decide
example : ¬ GraphCalc.IsCubicClass G116 := by decide
example : ¬ GraphCalc.IsSubcubicClass G116 := by decide
example : ¬ GraphCalc.IsEulerianClass G116 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G116 := by decide
example : GraphCalc.IsK4FreeClass G116 := by decide
example : GraphCalc.IsNontrivialClass G116 := by decide
example : ¬ GraphCalc.IsBipartiteClass G116 := by decide

-- EtoO  (n=6, m=7)
abbrev G117 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3), (3, 5)]
example : GraphCalc.order G117 = 6 := by decide
example : GraphCalc.size G117 = 7 := by decide
example : SimpleGraph.minDegree G117 = 1 := by decide
example : SimpleGraph.maxDegree G117 = 4 := by decide
example : GraphCalc.indepNum G117 = 3 := by decide
example : GraphCalc.cliqueNum G117 = 3 := by decide
example : GraphCalc.dominationNumber G117 = 2 := by decide
example : GraphCalc.independentDominationNumber G117 = 2 := by decide
example : GraphCalc.slaterNumber G117 = 2 := by decide
example : GraphCalc.annihilationNumber G117 = 4 := by decide
example : GraphCalc.zeroForcingNumber G117 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G117 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G117 = 3 := by decide
example : GraphCalc.vertexCoverNumber G117 = 3 := by decide
example : GraphCalc.totalDominationNumber G117 = 2 := by decide
example : GraphCalc.edgeCoverNumber G117 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G117 = 2 := by decide
example : GraphCalc.romanDominationNumber G117 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G117 = 5 := by decide
example : GraphCalc.radius G117 = 2 := by decide
example : GraphCalc.IsConnectedClass G117 := by decide
example : ¬ GraphCalc.IsTreeClass G117 := by decide
example : GraphCalc.IsClawFreeClass G117 := by decide
example : ¬ GraphCalc.IsCographClass G117 := by decide
example : ¬ GraphCalc.IsRegularClass G117 := by decide
example : ¬ GraphCalc.IsCubicClass G117 := by decide
example : ¬ GraphCalc.IsSubcubicClass G117 := by decide
example : ¬ GraphCalc.IsEulerianClass G117 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G117 := by decide
example : GraphCalc.IsK4FreeClass G117 := by decide
example : GraphCalc.IsNontrivialClass G117 := by decide
example : ¬ GraphCalc.IsBipartiteClass G117 := by decide

-- EB}?  (n=6, m=7)
abbrev G118 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G118 = 6 := by decide
example : GraphCalc.size G118 = 7 := by decide
example : SimpleGraph.minDegree G118 = 1 := by decide
example : SimpleGraph.maxDegree G118 = 4 := by decide
example : GraphCalc.indepNum G118 = 3 := by decide
example : GraphCalc.cliqueNum G118 = 3 := by decide
example : GraphCalc.dominationNumber G118 = 2 := by decide
example : GraphCalc.independentDominationNumber G118 = 2 := by decide
example : GraphCalc.slaterNumber G118 = 2 := by decide
example : GraphCalc.annihilationNumber G118 = 4 := by decide
example : GraphCalc.zeroForcingNumber G118 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G118 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G118 = 2 := by decide
example : GraphCalc.vertexCoverNumber G118 = 3 := by decide
example : GraphCalc.totalDominationNumber G118 = 2 := by decide
example : GraphCalc.edgeCoverNumber G118 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G118 = 2 := by decide
example : GraphCalc.romanDominationNumber G118 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G118 = 5 := by decide
example : GraphCalc.radius G118 = 2 := by decide
example : GraphCalc.IsConnectedClass G118 := by decide
example : ¬ GraphCalc.IsTreeClass G118 := by decide
example : ¬ GraphCalc.IsClawFreeClass G118 := by decide
example : ¬ GraphCalc.IsCographClass G118 := by decide
example : ¬ GraphCalc.IsRegularClass G118 := by decide
example : ¬ GraphCalc.IsCubicClass G118 := by decide
example : ¬ GraphCalc.IsSubcubicClass G118 := by decide
example : ¬ GraphCalc.IsEulerianClass G118 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G118 := by decide
example : GraphCalc.IsK4FreeClass G118 := by decide
example : GraphCalc.IsNontrivialClass G118 := by decide
example : ¬ GraphCalc.IsBipartiteClass G118 := by decide

-- EXSg  (n=6, m=7)
abbrev G119 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 4), (2, 3), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G119 = 6 := by decide
example : GraphCalc.size G119 = 7 := by decide
example : SimpleGraph.minDegree G119 = 1 := by decide
example : SimpleGraph.maxDegree G119 = 4 := by decide
example : GraphCalc.indepNum G119 = 4 := by decide
example : GraphCalc.cliqueNum G119 = 2 := by decide
example : GraphCalc.dominationNumber G119 = 2 := by decide
example : GraphCalc.independentDominationNumber G119 = 2 := by decide
example : GraphCalc.slaterNumber G119 = 2 := by decide
example : GraphCalc.annihilationNumber G119 = 4 := by decide
example : GraphCalc.zeroForcingNumber G119 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G119 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G119 = 3 := by decide
example : GraphCalc.vertexCoverNumber G119 = 2 := by decide
example : GraphCalc.totalDominationNumber G119 = 2 := by decide
example : GraphCalc.edgeCoverNumber G119 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G119 = 2 := by decide
example : GraphCalc.romanDominationNumber G119 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G119 = 5 := by decide
example : GraphCalc.radius G119 = 2 := by decide
example : GraphCalc.IsConnectedClass G119 := by decide
example : ¬ GraphCalc.IsTreeClass G119 := by decide
example : ¬ GraphCalc.IsClawFreeClass G119 := by decide
example : ¬ GraphCalc.IsCographClass G119 := by decide
example : ¬ GraphCalc.IsRegularClass G119 := by decide
example : ¬ GraphCalc.IsCubicClass G119 := by decide
example : ¬ GraphCalc.IsSubcubicClass G119 := by decide
example : ¬ GraphCalc.IsEulerianClass G119 := by decide
example : GraphCalc.IsTriangleFreeClass G119 := by decide
example : GraphCalc.IsK4FreeClass G119 := by decide
example : GraphCalc.IsNontrivialClass G119 := by decide
example : GraphCalc.IsBipartiteClass G119 := by decide

-- Eld?  (n=6, m=7)
abbrev G120 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 5), (2, 3), (3, 4)]
example : GraphCalc.order G120 = 6 := by decide
example : GraphCalc.size G120 = 7 := by decide
example : SimpleGraph.minDegree G120 = 1 := by decide
example : SimpleGraph.maxDegree G120 = 3 := by decide
example : GraphCalc.indepNum G120 = 3 := by decide
example : GraphCalc.cliqueNum G120 = 3 := by decide
example : GraphCalc.dominationNumber G120 = 2 := by decide
example : GraphCalc.independentDominationNumber G120 = 2 := by decide
example : GraphCalc.slaterNumber G120 = 2 := by decide
example : GraphCalc.annihilationNumber G120 = 3 := by decide
example : GraphCalc.zeroForcingNumber G120 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G120 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G120 = 2 := by decide
example : GraphCalc.vertexCoverNumber G120 = 3 := by decide
example : GraphCalc.totalDominationNumber G120 = 2 := by decide
example : GraphCalc.edgeCoverNumber G120 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G120 = 2 := by decide
example : GraphCalc.romanDominationNumber G120 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G120 = 6 := by decide
example : GraphCalc.radius G120 = 2 := by decide
example : GraphCalc.IsConnectedClass G120 := by decide
example : ¬ GraphCalc.IsTreeClass G120 := by decide
example : ¬ GraphCalc.IsClawFreeClass G120 := by decide
example : ¬ GraphCalc.IsCographClass G120 := by decide
example : ¬ GraphCalc.IsRegularClass G120 := by decide
example : ¬ GraphCalc.IsCubicClass G120 := by decide
example : GraphCalc.IsSubcubicClass G120 := by decide
example : ¬ GraphCalc.IsEulerianClass G120 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G120 := by decide
example : GraphCalc.IsK4FreeClass G120 := by decide
example : GraphCalc.IsNontrivialClass G120 := by decide
example : ¬ GraphCalc.IsBipartiteClass G120 := by decide

-- EJy?  (n=6, m=7)
abbrev G121 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
example : GraphCalc.order G121 = 6 := by decide
example : GraphCalc.size G121 = 7 := by decide
example : SimpleGraph.minDegree G121 = 1 := by decide
example : SimpleGraph.maxDegree G121 = 3 := by decide
example : GraphCalc.indepNum G121 = 3 := by decide
example : GraphCalc.cliqueNum G121 = 3 := by decide
example : GraphCalc.dominationNumber G121 = 2 := by decide
example : GraphCalc.independentDominationNumber G121 = 2 := by decide
example : GraphCalc.slaterNumber G121 = 2 := by decide
example : GraphCalc.annihilationNumber G121 = 3 := by decide
example : GraphCalc.zeroForcingNumber G121 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G121 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G121 = 2 := by decide
example : GraphCalc.vertexCoverNumber G121 = 3 := by decide
example : GraphCalc.totalDominationNumber G121 = 3 := by decide
example : GraphCalc.edgeCoverNumber G121 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G121 = 2 := by decide
example : GraphCalc.romanDominationNumber G121 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G121 = 6 := by decide
example : GraphCalc.radius G121 = 2 := by decide
example : GraphCalc.IsConnectedClass G121 := by decide
example : ¬ GraphCalc.IsTreeClass G121 := by decide
example : GraphCalc.IsClawFreeClass G121 := by decide
example : ¬ GraphCalc.IsCographClass G121 := by decide
example : ¬ GraphCalc.IsRegularClass G121 := by decide
example : ¬ GraphCalc.IsCubicClass G121 := by decide
example : GraphCalc.IsSubcubicClass G121 := by decide
example : ¬ GraphCalc.IsEulerianClass G121 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G121 := by decide
example : GraphCalc.IsK4FreeClass G121 := by decide
example : GraphCalc.IsNontrivialClass G121 := by decide
example : ¬ GraphCalc.IsBipartiteClass G121 := by decide

-- Exd?  (n=6, m=7)
abbrev G122 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (1, 2), (1, 5), (2, 3), (3, 4)]
example : GraphCalc.order G122 = 6 := by decide
example : GraphCalc.size G122 = 7 := by decide
example : SimpleGraph.minDegree G122 = 1 := by decide
example : SimpleGraph.maxDegree G122 = 3 := by decide
example : GraphCalc.indepNum G122 = 3 := by decide
example : GraphCalc.cliqueNum G122 = 3 := by decide
example : GraphCalc.dominationNumber G122 = 2 := by decide
example : GraphCalc.independentDominationNumber G122 = 2 := by decide
example : GraphCalc.slaterNumber G122 = 2 := by decide
example : GraphCalc.annihilationNumber G122 = 3 := by decide
example : GraphCalc.zeroForcingNumber G122 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G122 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G122 = 2 := by decide
example : GraphCalc.vertexCoverNumber G122 = 3 := by decide
example : GraphCalc.totalDominationNumber G122 = 3 := by decide
example : GraphCalc.edgeCoverNumber G122 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G122 = 2 := by decide
example : GraphCalc.romanDominationNumber G122 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G122 = 6 := by decide
example : GraphCalc.radius G122 = 2 := by decide
example : GraphCalc.IsConnectedClass G122 := by decide
example : ¬ GraphCalc.IsTreeClass G122 := by decide
example : GraphCalc.IsClawFreeClass G122 := by decide
example : ¬ GraphCalc.IsCographClass G122 := by decide
example : ¬ GraphCalc.IsRegularClass G122 := by decide
example : ¬ GraphCalc.IsCubicClass G122 := by decide
example : GraphCalc.IsSubcubicClass G122 := by decide
example : ¬ GraphCalc.IsEulerianClass G122 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G122 := by decide
example : GraphCalc.IsK4FreeClass G122 := by decide
example : GraphCalc.IsNontrivialClass G122 := by decide
example : ¬ GraphCalc.IsBipartiteClass G122 := by decide

-- EYOw  (n=6, m=7)
abbrev G123 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)]
example : GraphCalc.order G123 = 6 := by decide
example : GraphCalc.size G123 = 7 := by decide
example : SimpleGraph.minDegree G123 = 1 := by decide
example : SimpleGraph.maxDegree G123 = 3 := by decide
example : GraphCalc.indepNum G123 = 3 := by decide
example : GraphCalc.cliqueNum G123 = 2 := by decide
example : GraphCalc.dominationNumber G123 = 2 := by decide
example : GraphCalc.independentDominationNumber G123 = 3 := by decide
example : GraphCalc.slaterNumber G123 = 2 := by decide
example : GraphCalc.annihilationNumber G123 = 3 := by decide
example : GraphCalc.zeroForcingNumber G123 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G123 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G123 = 3 := by decide
example : GraphCalc.vertexCoverNumber G123 = 3 := by decide
example : GraphCalc.totalDominationNumber G123 = 2 := by decide
example : GraphCalc.edgeCoverNumber G123 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G123 = 2 := by decide
example : GraphCalc.romanDominationNumber G123 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G123 = 6 := by decide
example : GraphCalc.radius G123 = 2 := by decide
example : GraphCalc.IsConnectedClass G123 := by decide
example : ¬ GraphCalc.IsTreeClass G123 := by decide
example : ¬ GraphCalc.IsClawFreeClass G123 := by decide
example : ¬ GraphCalc.IsCographClass G123 := by decide
example : ¬ GraphCalc.IsRegularClass G123 := by decide
example : ¬ GraphCalc.IsCubicClass G123 := by decide
example : GraphCalc.IsSubcubicClass G123 := by decide
example : ¬ GraphCalc.IsEulerianClass G123 := by decide
example : GraphCalc.IsTriangleFreeClass G123 := by decide
example : GraphCalc.IsK4FreeClass G123 := by decide
example : GraphCalc.IsNontrivialClass G123 := by decide
example : GraphCalc.IsBipartiteClass G123 := by decide

-- ERUO  (n=6, m=7)
abbrev G124 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 5), (1, 3), (1, 4), (2, 3), (3, 4), (3, 5)]
example : GraphCalc.order G124 = 6 := by decide
example : GraphCalc.size G124 = 7 := by decide
example : SimpleGraph.minDegree G124 = 2 := by decide
example : SimpleGraph.maxDegree G124 = 4 := by decide
example : GraphCalc.indepNum G124 = 3 := by decide
example : GraphCalc.cliqueNum G124 = 3 := by decide
example : GraphCalc.dominationNumber G124 = 2 := by decide
example : GraphCalc.independentDominationNumber G124 = 2 := by decide
example : GraphCalc.slaterNumber G124 = 2 := by decide
example : GraphCalc.annihilationNumber G124 = 3 := by decide
example : GraphCalc.zeroForcingNumber G124 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G124 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G124 = 3 := by decide
example : GraphCalc.vertexCoverNumber G124 = 3 := by decide
example : GraphCalc.totalDominationNumber G124 = 2 := by decide
example : GraphCalc.edgeCoverNumber G124 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G124 = 2 := by decide
example : GraphCalc.romanDominationNumber G124 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G124 = 5 := by decide
example : GraphCalc.radius G124 = 2 := by decide
example : GraphCalc.IsConnectedClass G124 := by decide
example : ¬ GraphCalc.IsTreeClass G124 := by decide
example : ¬ GraphCalc.IsClawFreeClass G124 := by decide
example : ¬ GraphCalc.IsCographClass G124 := by decide
example : ¬ GraphCalc.IsRegularClass G124 := by decide
example : ¬ GraphCalc.IsCubicClass G124 := by decide
example : ¬ GraphCalc.IsSubcubicClass G124 := by decide
example : GraphCalc.IsEulerianClass G124 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G124 := by decide
example : GraphCalc.IsK4FreeClass G124 := by decide
example : GraphCalc.IsNontrivialClass G124 := by decide
example : ¬ GraphCalc.IsBipartiteClass G124 := by decide

-- EZEG  (n=6, m=7)
abbrev G125 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 5), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G125 = 6 := by decide
example : GraphCalc.size G125 = 7 := by decide
example : SimpleGraph.minDegree G125 = 2 := by decide
example : SimpleGraph.maxDegree G125 = 3 := by decide
example : GraphCalc.indepNum G125 = 3 := by decide
example : GraphCalc.cliqueNum G125 = 3 := by decide
example : GraphCalc.dominationNumber G125 = 2 := by decide
example : GraphCalc.independentDominationNumber G125 = 2 := by decide
example : GraphCalc.slaterNumber G125 = 2 := by decide
example : GraphCalc.annihilationNumber G125 = 3 := by decide
example : GraphCalc.zeroForcingNumber G125 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G125 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G125 = 2 := by decide
example : GraphCalc.vertexCoverNumber G125 = 3 := by decide
example : GraphCalc.totalDominationNumber G125 = 3 := by decide
example : GraphCalc.edgeCoverNumber G125 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G125 = 2 := by decide
example : GraphCalc.romanDominationNumber G125 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G125 = 6 := by decide
example : GraphCalc.radius G125 = 2 := by decide
example : GraphCalc.IsConnectedClass G125 := by decide
example : ¬ GraphCalc.IsTreeClass G125 := by decide
example : GraphCalc.IsClawFreeClass G125 := by decide
example : ¬ GraphCalc.IsCographClass G125 := by decide
example : ¬ GraphCalc.IsRegularClass G125 := by decide
example : ¬ GraphCalc.IsCubicClass G125 := by decide
example : GraphCalc.IsSubcubicClass G125 := by decide
example : ¬ GraphCalc.IsEulerianClass G125 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G125 := by decide
example : GraphCalc.IsK4FreeClass G125 := by decide
example : GraphCalc.IsNontrivialClass G125 := by decide
example : ¬ GraphCalc.IsBipartiteClass G125 := by decide

-- ElEG  (n=6, m=7)
abbrev G126 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G126 = 6 := by decide
example : GraphCalc.size G126 = 7 := by decide
example : SimpleGraph.minDegree G126 = 2 := by decide
example : SimpleGraph.maxDegree G126 = 3 := by decide
example : GraphCalc.indepNum G126 = 3 := by decide
example : GraphCalc.cliqueNum G126 = 2 := by decide
example : GraphCalc.dominationNumber G126 = 2 := by decide
example : GraphCalc.independentDominationNumber G126 = 2 := by decide
example : GraphCalc.slaterNumber G126 = 2 := by decide
example : GraphCalc.annihilationNumber G126 = 3 := by decide
example : GraphCalc.zeroForcingNumber G126 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G126 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G126 = 2 := by decide
example : GraphCalc.vertexCoverNumber G126 = 3 := by decide
example : GraphCalc.totalDominationNumber G126 = 2 := by decide
example : GraphCalc.edgeCoverNumber G126 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G126 = 2 := by decide
example : GraphCalc.romanDominationNumber G126 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G126 = 6 := by decide
example : GraphCalc.radius G126 = 2 := by decide
example : GraphCalc.IsConnectedClass G126 := by decide
example : ¬ GraphCalc.IsTreeClass G126 := by decide
example : ¬ GraphCalc.IsClawFreeClass G126 := by decide
example : ¬ GraphCalc.IsCographClass G126 := by decide
example : ¬ GraphCalc.IsRegularClass G126 := by decide
example : ¬ GraphCalc.IsCubicClass G126 := by decide
example : GraphCalc.IsSubcubicClass G126 := by decide
example : ¬ GraphCalc.IsEulerianClass G126 := by decide
example : GraphCalc.IsTriangleFreeClass G126 := by decide
example : GraphCalc.IsK4FreeClass G126 := by decide
example : GraphCalc.IsNontrivialClass G126 := by decide
example : GraphCalc.IsBipartiteClass G126 := by decide

-- EheO  (n=6, m=7)
abbrev G127 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 4), (3, 5)]
example : GraphCalc.order G127 = 6 := by decide
example : GraphCalc.size G127 = 7 := by decide
example : SimpleGraph.minDegree G127 = 2 := by decide
example : SimpleGraph.maxDegree G127 = 3 := by decide
example : GraphCalc.indepNum G127 = 3 := by decide
example : GraphCalc.cliqueNum G127 = 2 := by decide
example : GraphCalc.dominationNumber G127 = 2 := by decide
example : GraphCalc.independentDominationNumber G127 = 2 := by decide
example : GraphCalc.slaterNumber G127 = 2 := by decide
example : GraphCalc.annihilationNumber G127 = 3 := by decide
example : GraphCalc.zeroForcingNumber G127 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G127 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G127 = 3 := by decide
example : GraphCalc.vertexCoverNumber G127 = 3 := by decide
example : GraphCalc.totalDominationNumber G127 = 3 := by decide
example : GraphCalc.edgeCoverNumber G127 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G127 = 2 := by decide
example : GraphCalc.romanDominationNumber G127 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G127 = 6 := by decide
example : GraphCalc.radius G127 = 2 := by decide
example : GraphCalc.IsConnectedClass G127 := by decide
example : ¬ GraphCalc.IsTreeClass G127 := by decide
example : ¬ GraphCalc.IsClawFreeClass G127 := by decide
example : ¬ GraphCalc.IsCographClass G127 := by decide
example : ¬ GraphCalc.IsRegularClass G127 := by decide
example : ¬ GraphCalc.IsCubicClass G127 := by decide
example : GraphCalc.IsSubcubicClass G127 := by decide
example : ¬ GraphCalc.IsEulerianClass G127 := by decide
example : GraphCalc.IsTriangleFreeClass G127 := by decide
example : GraphCalc.IsK4FreeClass G127 := by decide
example : GraphCalc.IsNontrivialClass G127 := by decide
example : ¬ GraphCalc.IsBipartiteClass G127 := by decide

-- E{CW  (n=6, m=7)
abbrev G128 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G128 = 6 := by decide
example : GraphCalc.size G128 = 7 := by decide
example : SimpleGraph.minDegree G128 = 2 := by decide
example : SimpleGraph.maxDegree G128 = 3 := by decide
example : GraphCalc.indepNum G128 = 2 := by decide
example : GraphCalc.cliqueNum G128 = 3 := by decide
example : GraphCalc.dominationNumber G128 = 2 := by decide
example : GraphCalc.independentDominationNumber G128 = 2 := by decide
example : GraphCalc.slaterNumber G128 = 2 := by decide
example : GraphCalc.annihilationNumber G128 = 3 := by decide
example : GraphCalc.zeroForcingNumber G128 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G128 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G128 = 4 := by decide
example : GraphCalc.vertexCoverNumber G128 = 4 := by decide
example : GraphCalc.totalDominationNumber G128 = 2 := by decide
example : GraphCalc.edgeCoverNumber G128 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G128 = 2 := by decide
example : GraphCalc.romanDominationNumber G128 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G128 = 6 := by decide
example : GraphCalc.radius G128 = 2 := by decide
example : GraphCalc.IsConnectedClass G128 := by decide
example : ¬ GraphCalc.IsTreeClass G128 := by decide
example : GraphCalc.IsClawFreeClass G128 := by decide
example : ¬ GraphCalc.IsCographClass G128 := by decide
example : ¬ GraphCalc.IsRegularClass G128 := by decide
example : ¬ GraphCalc.IsCubicClass G128 := by decide
example : GraphCalc.IsSubcubicClass G128 := by decide
example : ¬ GraphCalc.IsEulerianClass G128 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G128 := by decide
example : GraphCalc.IsK4FreeClass G128 := by decide
example : GraphCalc.IsNontrivialClass G128 := by decide
example : ¬ GraphCalc.IsBipartiteClass G128 := by decide

-- E~@_  (n=6, m=8)
abbrev G129 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 5), (2, 3), (2, 5)]
example : GraphCalc.order G129 = 6 := by decide
example : GraphCalc.size G129 = 8 := by decide
example : SimpleGraph.minDegree G129 = 0 := by decide
example : SimpleGraph.maxDegree G129 = 4 := by decide
example : GraphCalc.indepNum G129 = 3 := by decide
example : GraphCalc.cliqueNum G129 = 4 := by decide
example : GraphCalc.dominationNumber G129 = 2 := by decide
example : GraphCalc.independentDominationNumber G129 = 2 := by decide
example : GraphCalc.slaterNumber G129 = 2 := by decide
example : GraphCalc.annihilationNumber G129 = 4 := by decide
example : GraphCalc.zeroForcingNumber G129 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G129 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G129 := by decide
example : GraphCalc.vertexCoverNumber G129 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G129 = 2 := by decide
example : GraphCalc.romanDominationNumber G129 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G129 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G129 := by decide
example : ¬ GraphCalc.IsTreeClass G129 := by decide
example : GraphCalc.IsClawFreeClass G129 := by decide
example : GraphCalc.IsCographClass G129 := by decide
example : ¬ GraphCalc.IsRegularClass G129 := by decide
example : ¬ GraphCalc.IsCubicClass G129 := by decide
example : ¬ GraphCalc.IsSubcubicClass G129 := by decide
example : ¬ GraphCalc.IsEulerianClass G129 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G129 := by decide
example : ¬ GraphCalc.IsK4FreeClass G129 := by decide
example : GraphCalc.IsNontrivialClass G129 := by decide
example : ¬ GraphCalc.IsBipartiteClass G129 := by decide

-- El{?  (n=6, m=8)
abbrev G130 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G130 = 6 := by decide
example : GraphCalc.size G130 = 8 := by decide
example : SimpleGraph.minDegree G130 = 0 := by decide
example : SimpleGraph.maxDegree G130 = 4 := by decide
example : GraphCalc.indepNum G130 = 3 := by decide
example : GraphCalc.cliqueNum G130 = 3 := by decide
example : GraphCalc.dominationNumber G130 = 2 := by decide
example : GraphCalc.independentDominationNumber G130 = 2 := by decide
example : GraphCalc.slaterNumber G130 = 2 := by decide
example : GraphCalc.annihilationNumber G130 = 3 := by decide
example : GraphCalc.zeroForcingNumber G130 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G130 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G130 := by decide
example : GraphCalc.vertexCoverNumber G130 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G130 = 2 := by decide
example : GraphCalc.romanDominationNumber G130 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G130 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G130 := by decide
example : ¬ GraphCalc.IsTreeClass G130 := by decide
example : GraphCalc.IsClawFreeClass G130 := by decide
example : GraphCalc.IsCographClass G130 := by decide
example : ¬ GraphCalc.IsRegularClass G130 := by decide
example : ¬ GraphCalc.IsCubicClass G130 := by decide
example : ¬ GraphCalc.IsSubcubicClass G130 := by decide
example : ¬ GraphCalc.IsEulerianClass G130 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G130 := by decide
example : GraphCalc.IsK4FreeClass G130 := by decide
example : GraphCalc.IsNontrivialClass G130 := by decide
example : ¬ GraphCalc.IsBipartiteClass G130 := by decide

-- E~a?  (n=6, m=8)
abbrev G131 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (2, 3)]
example : GraphCalc.order G131 = 6 := by decide
example : GraphCalc.size G131 = 8 := by decide
example : SimpleGraph.minDegree G131 = 1 := by decide
example : SimpleGraph.maxDegree G131 = 5 := by decide
example : GraphCalc.indepNum G131 = 3 := by decide
example : GraphCalc.cliqueNum G131 = 4 := by decide
example : GraphCalc.dominationNumber G131 = 1 := by decide
example : GraphCalc.independentDominationNumber G131 = 1 := by decide
example : GraphCalc.slaterNumber G131 = 1 := by decide
example : GraphCalc.annihilationNumber G131 = 4 := by decide
example : GraphCalc.zeroForcingNumber G131 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G131 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G131 = 4 := by decide
example : GraphCalc.vertexCoverNumber G131 = 3 := by decide
example : GraphCalc.totalDominationNumber G131 = 2 := by decide
example : GraphCalc.edgeCoverNumber G131 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G131 = 2 := by decide
example : GraphCalc.romanDominationNumber G131 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G131 = 3 := by decide
example : GraphCalc.radius G131 = 1 := by decide
example : GraphCalc.IsConnectedClass G131 := by decide
example : ¬ GraphCalc.IsTreeClass G131 := by decide
example : ¬ GraphCalc.IsClawFreeClass G131 := by decide
example : GraphCalc.IsCographClass G131 := by decide
example : ¬ GraphCalc.IsRegularClass G131 := by decide
example : ¬ GraphCalc.IsCubicClass G131 := by decide
example : ¬ GraphCalc.IsSubcubicClass G131 := by decide
example : ¬ GraphCalc.IsEulerianClass G131 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G131 := by decide
example : ¬ GraphCalc.IsK4FreeClass G131 := by decide
example : GraphCalc.IsNontrivialClass G131 := by decide
example : ¬ GraphCalc.IsBipartiteClass G131 := by decide

-- E~_O  (n=6, m=8)
abbrev G132 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (3, 5)]
example : GraphCalc.order G132 = 6 := by decide
example : GraphCalc.size G132 = 8 := by decide
example : SimpleGraph.minDegree G132 = 1 := by decide
example : SimpleGraph.maxDegree G132 = 4 := by decide
example : GraphCalc.indepNum G132 = 3 := by decide
example : GraphCalc.cliqueNum G132 = 4 := by decide
example : GraphCalc.dominationNumber G132 = 2 := by decide
example : GraphCalc.independentDominationNumber G132 = 2 := by decide
example : GraphCalc.slaterNumber G132 = 2 := by decide
example : GraphCalc.annihilationNumber G132 = 4 := by decide
example : GraphCalc.zeroForcingNumber G132 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G132 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G132 = 3 := by decide
example : GraphCalc.vertexCoverNumber G132 = 3 := by decide
example : GraphCalc.totalDominationNumber G132 = 2 := by decide
example : GraphCalc.edgeCoverNumber G132 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G132 = 2 := by decide
example : GraphCalc.romanDominationNumber G132 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G132 = 5 := by decide
example : GraphCalc.radius G132 = 2 := by decide
example : GraphCalc.IsConnectedClass G132 := by decide
example : ¬ GraphCalc.IsTreeClass G132 := by decide
example : GraphCalc.IsClawFreeClass G132 := by decide
example : ¬ GraphCalc.IsCographClass G132 := by decide
example : ¬ GraphCalc.IsRegularClass G132 := by decide
example : ¬ GraphCalc.IsCubicClass G132 := by decide
example : ¬ GraphCalc.IsSubcubicClass G132 := by decide
example : ¬ GraphCalc.IsEulerianClass G132 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G132 := by decide
example : ¬ GraphCalc.IsK4FreeClass G132 := by decide
example : GraphCalc.IsNontrivialClass G132 := by decide
example : ¬ GraphCalc.IsBipartiteClass G132 := by decide

-- EzW_  (n=6, m=8)
abbrev G133 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (2, 5)]
example : GraphCalc.order G133 = 6 := by decide
example : GraphCalc.size G133 = 8 := by decide
example : SimpleGraph.minDegree G133 = 1 := by decide
example : SimpleGraph.maxDegree G133 = 5 := by decide
example : GraphCalc.indepNum G133 = 4 := by decide
example : GraphCalc.cliqueNum G133 = 3 := by decide
example : GraphCalc.dominationNumber G133 = 1 := by decide
example : GraphCalc.independentDominationNumber G133 = 1 := by decide
example : GraphCalc.slaterNumber G133 = 1 := by decide
example : GraphCalc.annihilationNumber G133 = 4 := by decide
example : GraphCalc.zeroForcingNumber G133 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G133 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G133 = 3 := by decide
example : GraphCalc.vertexCoverNumber G133 = 2 := by decide
example : GraphCalc.totalDominationNumber G133 = 2 := by decide
example : GraphCalc.edgeCoverNumber G133 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G133 = 2 := by decide
example : GraphCalc.romanDominationNumber G133 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G133 = 3 := by decide
example : GraphCalc.radius G133 = 1 := by decide
example : GraphCalc.IsConnectedClass G133 := by decide
example : ¬ GraphCalc.IsTreeClass G133 := by decide
example : ¬ GraphCalc.IsClawFreeClass G133 := by decide
example : GraphCalc.IsCographClass G133 := by decide
example : ¬ GraphCalc.IsRegularClass G133 := by decide
example : ¬ GraphCalc.IsCubicClass G133 := by decide
example : ¬ GraphCalc.IsSubcubicClass G133 := by decide
example : ¬ GraphCalc.IsEulerianClass G133 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G133 := by decide
example : GraphCalc.IsK4FreeClass G133 := by decide
example : GraphCalc.IsNontrivialClass G133 := by decide
example : ¬ GraphCalc.IsBipartiteClass G133 := by decide

-- Ejt?  (n=6, m=8)
abbrev G134 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (3, 4)]
example : GraphCalc.order G134 = 6 := by decide
example : GraphCalc.size G134 = 8 := by decide
example : SimpleGraph.minDegree G134 = 1 := by decide
example : SimpleGraph.maxDegree G134 = 5 := by decide
example : GraphCalc.indepNum G134 = 3 := by decide
example : GraphCalc.cliqueNum G134 = 3 := by decide
example : GraphCalc.dominationNumber G134 = 1 := by decide
example : GraphCalc.independentDominationNumber G134 = 1 := by decide
example : GraphCalc.slaterNumber G134 = 1 := by decide
example : GraphCalc.annihilationNumber G134 = 4 := by decide
example : GraphCalc.zeroForcingNumber G134 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G134 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G134 = 2 := by decide
example : GraphCalc.vertexCoverNumber G134 = 3 := by decide
example : GraphCalc.totalDominationNumber G134 = 2 := by decide
example : GraphCalc.edgeCoverNumber G134 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G134 = 2 := by decide
example : GraphCalc.romanDominationNumber G134 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G134 = 3 := by decide
example : GraphCalc.radius G134 = 1 := by decide
example : GraphCalc.IsConnectedClass G134 := by decide
example : ¬ GraphCalc.IsTreeClass G134 := by decide
example : ¬ GraphCalc.IsClawFreeClass G134 := by decide
example : ¬ GraphCalc.IsCographClass G134 := by decide
example : ¬ GraphCalc.IsRegularClass G134 := by decide
example : ¬ GraphCalc.IsCubicClass G134 := by decide
example : ¬ GraphCalc.IsSubcubicClass G134 := by decide
example : ¬ GraphCalc.IsEulerianClass G134 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G134 := by decide
example : GraphCalc.IsK4FreeClass G134 := by decide
example : GraphCalc.IsNontrivialClass G134 := by decide
example : ¬ GraphCalc.IsBipartiteClass G134 := by decide

-- EjsG  (n=6, m=8)
abbrev G135 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G135 = 6 := by decide
example : GraphCalc.size G135 = 8 := by decide
example : SimpleGraph.minDegree G135 = 1 := by decide
example : SimpleGraph.maxDegree G135 = 4 := by decide
example : GraphCalc.indepNum G135 = 3 := by decide
example : GraphCalc.cliqueNum G135 = 3 := by decide
example : GraphCalc.dominationNumber G135 = 2 := by decide
example : GraphCalc.independentDominationNumber G135 = 2 := by decide
example : GraphCalc.slaterNumber G135 = 2 := by decide
example : GraphCalc.annihilationNumber G135 = 4 := by decide
example : GraphCalc.zeroForcingNumber G135 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G135 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G135 = 2 := by decide
example : GraphCalc.vertexCoverNumber G135 = 3 := by decide
example : GraphCalc.totalDominationNumber G135 = 2 := by decide
example : GraphCalc.edgeCoverNumber G135 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G135 = 2 := by decide
example : GraphCalc.romanDominationNumber G135 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G135 = 5 := by decide
example : GraphCalc.radius G135 = 2 := by decide
example : GraphCalc.IsConnectedClass G135 := by decide
example : ¬ GraphCalc.IsTreeClass G135 := by decide
example : ¬ GraphCalc.IsClawFreeClass G135 := by decide
example : ¬ GraphCalc.IsCographClass G135 := by decide
example : ¬ GraphCalc.IsRegularClass G135 := by decide
example : ¬ GraphCalc.IsCubicClass G135 := by decide
example : ¬ GraphCalc.IsSubcubicClass G135 := by decide
example : ¬ GraphCalc.IsEulerianClass G135 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G135 := by decide
example : GraphCalc.IsK4FreeClass G135 := by decide
example : GraphCalc.IsNontrivialClass G135 := by decide
example : ¬ GraphCalc.IsBipartiteClass G135 := by decide

-- Ez`_  (n=6, m=8)
abbrev G136 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 5), (2, 3), (2, 5)]
example : GraphCalc.order G136 = 6 := by decide
example : GraphCalc.size G136 = 8 := by decide
example : SimpleGraph.minDegree G136 = 1 := by decide
example : SimpleGraph.maxDegree G136 = 4 := by decide
example : GraphCalc.indepNum G136 = 3 := by decide
example : GraphCalc.cliqueNum G136 = 3 := by decide
example : GraphCalc.dominationNumber G136 = 2 := by decide
example : GraphCalc.independentDominationNumber G136 = 2 := by decide
example : GraphCalc.slaterNumber G136 = 2 := by decide
example : GraphCalc.annihilationNumber G136 = 4 := by decide
example : GraphCalc.zeroForcingNumber G136 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G136 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G136 = 3 := by decide
example : GraphCalc.vertexCoverNumber G136 = 3 := by decide
example : GraphCalc.totalDominationNumber G136 = 2 := by decide
example : GraphCalc.edgeCoverNumber G136 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G136 = 2 := by decide
example : GraphCalc.romanDominationNumber G136 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G136 = 5 := by decide
example : GraphCalc.radius G136 = 2 := by decide
example : GraphCalc.IsConnectedClass G136 := by decide
example : ¬ GraphCalc.IsTreeClass G136 := by decide
example : ¬ GraphCalc.IsClawFreeClass G136 := by decide
example : ¬ GraphCalc.IsCographClass G136 := by decide
example : ¬ GraphCalc.IsRegularClass G136 := by decide
example : ¬ GraphCalc.IsCubicClass G136 := by decide
example : ¬ GraphCalc.IsSubcubicClass G136 := by decide
example : ¬ GraphCalc.IsEulerianClass G136 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G136 := by decide
example : GraphCalc.IsK4FreeClass G136 := by decide
example : GraphCalc.IsNontrivialClass G136 := by decide
example : ¬ GraphCalc.IsBipartiteClass G136 := by decide

-- Eju?  (n=6, m=8)
abbrev G137 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
example : GraphCalc.order G137 = 6 := by decide
example : GraphCalc.size G137 = 8 := by decide
example : SimpleGraph.minDegree G137 = 1 := by decide
example : SimpleGraph.maxDegree G137 = 4 := by decide
example : GraphCalc.indepNum G137 = 3 := by decide
example : GraphCalc.cliqueNum G137 = 3 := by decide
example : GraphCalc.dominationNumber G137 = 2 := by decide
example : GraphCalc.independentDominationNumber G137 = 2 := by decide
example : GraphCalc.slaterNumber G137 = 2 := by decide
example : GraphCalc.annihilationNumber G137 = 3 := by decide
example : GraphCalc.zeroForcingNumber G137 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G137 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G137 = 2 := by decide
example : GraphCalc.vertexCoverNumber G137 = 3 := by decide
example : GraphCalc.totalDominationNumber G137 = 2 := by decide
example : GraphCalc.edgeCoverNumber G137 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G137 = 2 := by decide
example : GraphCalc.romanDominationNumber G137 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G137 = 5 := by decide
example : GraphCalc.radius G137 = 2 := by decide
example : GraphCalc.IsConnectedClass G137 := by decide
example : ¬ GraphCalc.IsTreeClass G137 := by decide
example : GraphCalc.IsClawFreeClass G137 := by decide
example : ¬ GraphCalc.IsCographClass G137 := by decide
example : ¬ GraphCalc.IsRegularClass G137 := by decide
example : ¬ GraphCalc.IsCubicClass G137 := by decide
example : ¬ GraphCalc.IsSubcubicClass G137 := by decide
example : ¬ GraphCalc.IsEulerianClass G137 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G137 := by decide
example : GraphCalc.IsK4FreeClass G137 := by decide
example : GraphCalc.IsNontrivialClass G137 := by decide
example : ¬ GraphCalc.IsBipartiteClass G137 := by decide

-- Ev`_  (n=6, m=8)
abbrev G138 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (1, 5), (2, 3), (2, 5)]
example : GraphCalc.order G138 = 6 := by decide
example : GraphCalc.size G138 = 8 := by decide
example : SimpleGraph.minDegree G138 = 1 := by decide
example : SimpleGraph.maxDegree G138 = 4 := by decide
example : GraphCalc.indepNum G138 = 3 := by decide
example : GraphCalc.cliqueNum G138 = 3 := by decide
example : GraphCalc.dominationNumber G138 = 2 := by decide
example : GraphCalc.independentDominationNumber G138 = 2 := by decide
example : GraphCalc.slaterNumber G138 = 2 := by decide
example : GraphCalc.annihilationNumber G138 = 3 := by decide
example : GraphCalc.zeroForcingNumber G138 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G138 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G138 = 3 := by decide
example : GraphCalc.vertexCoverNumber G138 = 3 := by decide
example : GraphCalc.totalDominationNumber G138 = 2 := by decide
example : GraphCalc.edgeCoverNumber G138 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G138 = 2 := by decide
example : GraphCalc.romanDominationNumber G138 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G138 = 5 := by decide
example : GraphCalc.radius G138 = 2 := by decide
example : GraphCalc.IsConnectedClass G138 := by decide
example : ¬ GraphCalc.IsTreeClass G138 := by decide
example : ¬ GraphCalc.IsClawFreeClass G138 := by decide
example : ¬ GraphCalc.IsCographClass G138 := by decide
example : ¬ GraphCalc.IsRegularClass G138 := by decide
example : ¬ GraphCalc.IsCubicClass G138 := by decide
example : ¬ GraphCalc.IsSubcubicClass G138 := by decide
example : ¬ GraphCalc.IsEulerianClass G138 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G138 := by decide
example : GraphCalc.IsK4FreeClass G138 := by decide
example : GraphCalc.IsNontrivialClass G138 := by decide
example : ¬ GraphCalc.IsBipartiteClass G138 := by decide

-- EXSw  (n=6, m=8)
abbrev G139 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G139 = 6 := by decide
example : GraphCalc.size G139 = 8 := by decide
example : SimpleGraph.minDegree G139 = 1 := by decide
example : SimpleGraph.maxDegree G139 = 4 := by decide
example : GraphCalc.indepNum G139 = 3 := by decide
example : GraphCalc.cliqueNum G139 = 3 := by decide
example : GraphCalc.dominationNumber G139 = 2 := by decide
example : GraphCalc.independentDominationNumber G139 = 2 := by decide
example : GraphCalc.slaterNumber G139 = 2 := by decide
example : GraphCalc.annihilationNumber G139 = 3 := by decide
example : GraphCalc.zeroForcingNumber G139 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G139 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G139 = 3 := by decide
example : GraphCalc.vertexCoverNumber G139 = 3 := by decide
example : GraphCalc.totalDominationNumber G139 = 2 := by decide
example : GraphCalc.edgeCoverNumber G139 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G139 = 2 := by decide
example : GraphCalc.romanDominationNumber G139 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G139 = 5 := by decide
example : GraphCalc.radius G139 = 2 := by decide
example : GraphCalc.IsConnectedClass G139 := by decide
example : ¬ GraphCalc.IsTreeClass G139 := by decide
example : ¬ GraphCalc.IsClawFreeClass G139 := by decide
example : ¬ GraphCalc.IsCographClass G139 := by decide
example : ¬ GraphCalc.IsRegularClass G139 := by decide
example : ¬ GraphCalc.IsCubicClass G139 := by decide
example : ¬ GraphCalc.IsSubcubicClass G139 := by decide
example : ¬ GraphCalc.IsEulerianClass G139 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G139 := by decide
example : GraphCalc.IsK4FreeClass G139 := by decide
example : GraphCalc.IsNontrivialClass G139 := by decide
example : ¬ GraphCalc.IsBipartiteClass G139 := by decide

-- E~AG  (n=6, m=8)
abbrev G140 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (2, 3), (4, 5)]
example : GraphCalc.order G140 = 6 := by decide
example : GraphCalc.size G140 = 8 := by decide
example : SimpleGraph.minDegree G140 = 1 := by decide
example : SimpleGraph.maxDegree G140 = 4 := by decide
example : GraphCalc.indepNum G140 = 2 := by decide
example : GraphCalc.cliqueNum G140 = 4 := by decide
example : GraphCalc.dominationNumber G140 = 2 := by decide
example : GraphCalc.independentDominationNumber G140 = 2 := by decide
example : GraphCalc.slaterNumber G140 = 2 := by decide
example : GraphCalc.annihilationNumber G140 = 3 := by decide
example : GraphCalc.zeroForcingNumber G140 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G140 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G140 = 3 := by decide
example : GraphCalc.vertexCoverNumber G140 = 4 := by decide
example : GraphCalc.totalDominationNumber G140 = 2 := by decide
example : GraphCalc.edgeCoverNumber G140 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G140 = 2 := by decide
example : GraphCalc.romanDominationNumber G140 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G140 = 5 := by decide
example : GraphCalc.radius G140 = 2 := by decide
example : GraphCalc.IsConnectedClass G140 := by decide
example : ¬ GraphCalc.IsTreeClass G140 := by decide
example : GraphCalc.IsClawFreeClass G140 := by decide
example : ¬ GraphCalc.IsCographClass G140 := by decide
example : ¬ GraphCalc.IsRegularClass G140 := by decide
example : ¬ GraphCalc.IsCubicClass G140 := by decide
example : ¬ GraphCalc.IsSubcubicClass G140 := by decide
example : ¬ GraphCalc.IsEulerianClass G140 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G140 := by decide
example : ¬ GraphCalc.IsK4FreeClass G140 := by decide
example : GraphCalc.IsNontrivialClass G140 := by decide
example : ¬ GraphCalc.IsBipartiteClass G140 := by decide

-- Er`o  (n=6, m=8)
abbrev G141 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 5), (3, 5)]
example : GraphCalc.order G141 = 6 := by decide
example : GraphCalc.size G141 = 8 := by decide
example : SimpleGraph.minDegree G141 = 1 := by decide
example : SimpleGraph.maxDegree G141 = 3 := by decide
example : GraphCalc.indepNum G141 = 3 := by decide
example : GraphCalc.cliqueNum G141 = 3 := by decide
example : GraphCalc.dominationNumber G141 = 2 := by decide
example : GraphCalc.independentDominationNumber G141 = 2 := by decide
example : GraphCalc.slaterNumber G141 = 2 := by decide
example : GraphCalc.annihilationNumber G141 = 3 := by decide
example : GraphCalc.zeroForcingNumber G141 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G141 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G141 = 3 := by decide
example : GraphCalc.vertexCoverNumber G141 = 3 := by decide
example : GraphCalc.totalDominationNumber G141 = 2 := by decide
example : GraphCalc.edgeCoverNumber G141 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G141 = 2 := by decide
example : GraphCalc.romanDominationNumber G141 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G141 = 6 := by decide
example : GraphCalc.radius G141 = 2 := by decide
example : GraphCalc.IsConnectedClass G141 := by decide
example : ¬ GraphCalc.IsTreeClass G141 := by decide
example : ¬ GraphCalc.IsClawFreeClass G141 := by decide
example : ¬ GraphCalc.IsCographClass G141 := by decide
example : ¬ GraphCalc.IsRegularClass G141 := by decide
example : ¬ GraphCalc.IsCubicClass G141 := by decide
example : GraphCalc.IsSubcubicClass G141 := by decide
example : ¬ GraphCalc.IsEulerianClass G141 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G141 := by decide
example : GraphCalc.IsK4FreeClass G141 := by decide
example : GraphCalc.IsNontrivialClass G141 := by decide
example : ¬ GraphCalc.IsBipartiteClass G141 := by decide

-- EB}G  (n=6, m=8)
abbrev G142 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G142 = 6 := by decide
example : GraphCalc.size G142 = 8 := by decide
example : SimpleGraph.minDegree G142 = 2 := by decide
example : SimpleGraph.maxDegree G142 = 5 := by decide
example : GraphCalc.indepNum G142 = 3 := by decide
example : GraphCalc.cliqueNum G142 = 3 := by decide
example : GraphCalc.dominationNumber G142 = 1 := by decide
example : GraphCalc.independentDominationNumber G142 = 1 := by decide
example : GraphCalc.slaterNumber G142 = 1 := by decide
example : GraphCalc.annihilationNumber G142 = 4 := by decide
example : GraphCalc.zeroForcingNumber G142 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G142 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G142 = 3 := by decide
example : GraphCalc.vertexCoverNumber G142 = 3 := by decide
example : GraphCalc.totalDominationNumber G142 = 2 := by decide
example : GraphCalc.edgeCoverNumber G142 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G142 = 2 := by decide
example : GraphCalc.romanDominationNumber G142 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G142 = 3 := by decide
example : GraphCalc.radius G142 = 1 := by decide
example : GraphCalc.IsConnectedClass G142 := by decide
example : ¬ GraphCalc.IsTreeClass G142 := by decide
example : ¬ GraphCalc.IsClawFreeClass G142 := by decide
example : GraphCalc.IsCographClass G142 := by decide
example : ¬ GraphCalc.IsRegularClass G142 := by decide
example : ¬ GraphCalc.IsCubicClass G142 := by decide
example : ¬ GraphCalc.IsSubcubicClass G142 := by decide
example : ¬ GraphCalc.IsEulerianClass G142 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G142 := by decide
example : GraphCalc.IsK4FreeClass G142 := by decide
example : GraphCalc.IsNontrivialClass G142 := by decide
example : ¬ GraphCalc.IsBipartiteClass G142 := by decide

-- Exe_  (n=6, m=8)
abbrev G143 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G143 = 6 := by decide
example : GraphCalc.size G143 = 8 := by decide
example : SimpleGraph.minDegree G143 = 2 := by decide
example : SimpleGraph.maxDegree G143 = 4 := by decide
example : GraphCalc.indepNum G143 = 3 := by decide
example : GraphCalc.cliqueNum G143 = 3 := by decide
example : GraphCalc.dominationNumber G143 = 2 := by decide
example : GraphCalc.independentDominationNumber G143 = 2 := by decide
example : GraphCalc.slaterNumber G143 = 2 := by decide
example : GraphCalc.annihilationNumber G143 = 4 := by decide
example : GraphCalc.zeroForcingNumber G143 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G143 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G143 = 3 := by decide
example : GraphCalc.vertexCoverNumber G143 = 3 := by decide
example : GraphCalc.totalDominationNumber G143 = 2 := by decide
example : GraphCalc.edgeCoverNumber G143 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G143 = 2 := by decide
example : GraphCalc.romanDominationNumber G143 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G143 = 5 := by decide
example : GraphCalc.radius G143 = 2 := by decide
example : GraphCalc.IsConnectedClass G143 := by decide
example : ¬ GraphCalc.IsTreeClass G143 := by decide
example : ¬ GraphCalc.IsClawFreeClass G143 := by decide
example : ¬ GraphCalc.IsCographClass G143 := by decide
example : ¬ GraphCalc.IsRegularClass G143 := by decide
example : ¬ GraphCalc.IsCubicClass G143 := by decide
example : ¬ GraphCalc.IsSubcubicClass G143 := by decide
example : GraphCalc.IsEulerianClass G143 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G143 := by decide
example : GraphCalc.IsK4FreeClass G143 := by decide
example : GraphCalc.IsNontrivialClass G143 := by decide
example : ¬ GraphCalc.IsBipartiteClass G143 := by decide

-- E?~o  (n=6, m=8)
abbrev G144 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)]
example : GraphCalc.order G144 = 6 := by decide
example : GraphCalc.size G144 = 8 := by decide
example : SimpleGraph.minDegree G144 = 2 := by decide
example : SimpleGraph.maxDegree G144 = 4 := by decide
example : GraphCalc.indepNum G144 = 4 := by decide
example : GraphCalc.cliqueNum G144 = 2 := by decide
example : GraphCalc.dominationNumber G144 = 2 := by decide
example : GraphCalc.independentDominationNumber G144 = 2 := by decide
example : GraphCalc.slaterNumber G144 = 2 := by decide
example : GraphCalc.annihilationNumber G144 = 4 := by decide
example : GraphCalc.zeroForcingNumber G144 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G144 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G144 = 4 := by decide
example : GraphCalc.vertexCoverNumber G144 = 2 := by decide
example : GraphCalc.totalDominationNumber G144 = 2 := by decide
example : GraphCalc.edgeCoverNumber G144 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G144 = 2 := by decide
example : GraphCalc.romanDominationNumber G144 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G144 = 4 := by decide
example : GraphCalc.radius G144 = 2 := by decide
example : GraphCalc.IsConnectedClass G144 := by decide
example : ¬ GraphCalc.IsTreeClass G144 := by decide
example : ¬ GraphCalc.IsClawFreeClass G144 := by decide
example : GraphCalc.IsCographClass G144 := by decide
example : ¬ GraphCalc.IsRegularClass G144 := by decide
example : ¬ GraphCalc.IsCubicClass G144 := by decide
example : ¬ GraphCalc.IsSubcubicClass G144 := by decide
example : GraphCalc.IsEulerianClass G144 := by decide
example : GraphCalc.IsTriangleFreeClass G144 := by decide
example : GraphCalc.IsK4FreeClass G144 := by decide
example : GraphCalc.IsNontrivialClass G144 := by decide
example : GraphCalc.IsBipartiteClass G144 := by decide

-- EhMg  (n=6, m=8)
abbrev G145 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 5), (1, 2), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G145 = 6 := by decide
example : GraphCalc.size G145 = 8 := by decide
example : SimpleGraph.minDegree G145 = 2 := by decide
example : SimpleGraph.maxDegree G145 = 4 := by decide
example : GraphCalc.indepNum G145 = 3 := by decide
example : GraphCalc.cliqueNum G145 = 3 := by decide
example : GraphCalc.dominationNumber G145 = 2 := by decide
example : GraphCalc.independentDominationNumber G145 = 2 := by decide
example : GraphCalc.slaterNumber G145 = 2 := by decide
example : GraphCalc.annihilationNumber G145 = 3 := by decide
example : GraphCalc.zeroForcingNumber G145 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G145 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G145 = 2 := by decide
example : GraphCalc.vertexCoverNumber G145 = 3 := by decide
example : GraphCalc.totalDominationNumber G145 = 2 := by decide
example : GraphCalc.edgeCoverNumber G145 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G145 = 2 := by decide
example : GraphCalc.romanDominationNumber G145 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G145 = 5 := by decide
example : GraphCalc.radius G145 = 2 := by decide
example : GraphCalc.IsConnectedClass G145 := by decide
example : ¬ GraphCalc.IsTreeClass G145 := by decide
example : ¬ GraphCalc.IsClawFreeClass G145 := by decide
example : ¬ GraphCalc.IsCographClass G145 := by decide
example : ¬ GraphCalc.IsRegularClass G145 := by decide
example : ¬ GraphCalc.IsCubicClass G145 := by decide
example : ¬ GraphCalc.IsSubcubicClass G145 := by decide
example : ¬ GraphCalc.IsEulerianClass G145 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G145 := by decide
example : GraphCalc.IsK4FreeClass G145 := by decide
example : GraphCalc.IsNontrivialClass G145 := by decide
example : ¬ GraphCalc.IsBipartiteClass G145 := by decide

-- EyUG  (n=6, m=8)
abbrev G146 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (3, 4), (4, 5)]
example : GraphCalc.order G146 = 6 := by decide
example : GraphCalc.size G146 = 8 := by decide
example : SimpleGraph.minDegree G146 = 2 := by decide
example : SimpleGraph.maxDegree G146 = 4 := by decide
example : GraphCalc.indepNum G146 = 3 := by decide
example : GraphCalc.cliqueNum G146 = 3 := by decide
example : GraphCalc.dominationNumber G146 = 2 := by decide
example : GraphCalc.independentDominationNumber G146 = 2 := by decide
example : GraphCalc.slaterNumber G146 = 2 := by decide
example : GraphCalc.annihilationNumber G146 = 3 := by decide
example : GraphCalc.zeroForcingNumber G146 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G146 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G146 = 2 := by decide
example : GraphCalc.vertexCoverNumber G146 = 3 := by decide
example : GraphCalc.totalDominationNumber G146 = 2 := by decide
example : GraphCalc.edgeCoverNumber G146 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G146 = 2 := by decide
example : GraphCalc.romanDominationNumber G146 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G146 = 5 := by decide
example : GraphCalc.radius G146 = 2 := by decide
example : GraphCalc.IsConnectedClass G146 := by decide
example : ¬ GraphCalc.IsTreeClass G146 := by decide
example : GraphCalc.IsClawFreeClass G146 := by decide
example : ¬ GraphCalc.IsCographClass G146 := by decide
example : ¬ GraphCalc.IsRegularClass G146 := by decide
example : ¬ GraphCalc.IsCubicClass G146 := by decide
example : ¬ GraphCalc.IsSubcubicClass G146 := by decide
example : ¬ GraphCalc.IsEulerianClass G146 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G146 := by decide
example : GraphCalc.IsK4FreeClass G146 := by decide
example : GraphCalc.IsNontrivialClass G146 := by decide
example : ¬ GraphCalc.IsBipartiteClass G146 := by decide

-- Ele_  (n=6, m=8)
abbrev G147 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G147 = 6 := by decide
example : GraphCalc.size G147 = 8 := by decide
example : SimpleGraph.minDegree G147 = 2 := by decide
example : SimpleGraph.maxDegree G147 = 4 := by decide
example : GraphCalc.indepNum G147 = 3 := by decide
example : GraphCalc.cliqueNum G147 = 3 := by decide
example : GraphCalc.dominationNumber G147 = 2 := by decide
example : GraphCalc.independentDominationNumber G147 = 2 := by decide
example : GraphCalc.slaterNumber G147 = 2 := by decide
example : GraphCalc.annihilationNumber G147 = 3 := by decide
example : GraphCalc.zeroForcingNumber G147 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G147 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G147 = 3 := by decide
example : GraphCalc.vertexCoverNumber G147 = 3 := by decide
example : GraphCalc.totalDominationNumber G147 = 2 := by decide
example : GraphCalc.edgeCoverNumber G147 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G147 = 2 := by decide
example : GraphCalc.romanDominationNumber G147 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G147 = 5 := by decide
example : GraphCalc.radius G147 = 2 := by decide
example : GraphCalc.IsConnectedClass G147 := by decide
example : ¬ GraphCalc.IsTreeClass G147 := by decide
example : ¬ GraphCalc.IsClawFreeClass G147 := by decide
example : ¬ GraphCalc.IsCographClass G147 := by decide
example : ¬ GraphCalc.IsRegularClass G147 := by decide
example : ¬ GraphCalc.IsCubicClass G147 := by decide
example : ¬ GraphCalc.IsSubcubicClass G147 := by decide
example : ¬ GraphCalc.IsEulerianClass G147 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G147 := by decide
example : GraphCalc.IsK4FreeClass G147 := by decide
example : GraphCalc.IsNontrivialClass G147 := by decide
example : ¬ GraphCalc.IsBipartiteClass G147 := by decide

-- EJyG  (n=6, m=8)
abbrev G148 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (4, 5)]
example : GraphCalc.order G148 = 6 := by decide
example : GraphCalc.size G148 = 8 := by decide
example : SimpleGraph.minDegree G148 = 2 := by decide
example : SimpleGraph.maxDegree G148 = 4 := by decide
example : GraphCalc.indepNum G148 = 2 := by decide
example : GraphCalc.cliqueNum G148 = 3 := by decide
example : GraphCalc.dominationNumber G148 = 2 := by decide
example : GraphCalc.independentDominationNumber G148 = 2 := by decide
example : GraphCalc.slaterNumber G148 = 2 := by decide
example : GraphCalc.annihilationNumber G148 = 3 := by decide
example : GraphCalc.zeroForcingNumber G148 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G148 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G148 = 3 := by decide
example : GraphCalc.vertexCoverNumber G148 = 4 := by decide
example : GraphCalc.totalDominationNumber G148 = 2 := by decide
example : GraphCalc.edgeCoverNumber G148 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G148 = 2 := by decide
example : GraphCalc.romanDominationNumber G148 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G148 = 5 := by decide
example : GraphCalc.radius G148 = 2 := by decide
example : GraphCalc.IsConnectedClass G148 := by decide
example : ¬ GraphCalc.IsTreeClass G148 := by decide
example : GraphCalc.IsClawFreeClass G148 := by decide
example : ¬ GraphCalc.IsCographClass G148 := by decide
example : ¬ GraphCalc.IsRegularClass G148 := by decide
example : ¬ GraphCalc.IsCubicClass G148 := by decide
example : ¬ GraphCalc.IsSubcubicClass G148 := by decide
example : ¬ GraphCalc.IsEulerianClass G148 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G148 := by decide
example : GraphCalc.IsK4FreeClass G148 := by decide
example : GraphCalc.IsNontrivialClass G148 := by decide
example : ¬ GraphCalc.IsBipartiteClass G148 := by decide

-- EhdW  (n=6, m=8)
abbrev G149 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G149 = 6 := by decide
example : GraphCalc.size G149 = 8 := by decide
example : SimpleGraph.minDegree G149 = 2 := by decide
example : SimpleGraph.maxDegree G149 = 3 := by decide
example : GraphCalc.indepNum G149 = 3 := by decide
example : GraphCalc.cliqueNum G149 = 3 := by decide
example : GraphCalc.dominationNumber G149 = 2 := by decide
example : GraphCalc.independentDominationNumber G149 = 2 := by decide
example : GraphCalc.slaterNumber G149 = 2 := by decide
example : GraphCalc.annihilationNumber G149 = 3 := by decide
example : GraphCalc.zeroForcingNumber G149 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G149 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G149 = 3 := by decide
example : GraphCalc.vertexCoverNumber G149 = 3 := by decide
example : GraphCalc.totalDominationNumber G149 = 2 := by decide
example : GraphCalc.edgeCoverNumber G149 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G149 = 2 := by decide
example : GraphCalc.romanDominationNumber G149 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G149 = 6 := by decide
example : GraphCalc.radius G149 = 2 := by decide
example : GraphCalc.IsConnectedClass G149 := by decide
example : ¬ GraphCalc.IsTreeClass G149 := by decide
example : ¬ GraphCalc.IsClawFreeClass G149 := by decide
example : ¬ GraphCalc.IsCographClass G149 := by decide
example : ¬ GraphCalc.IsRegularClass G149 := by decide
example : ¬ GraphCalc.IsCubicClass G149 := by decide
example : GraphCalc.IsSubcubicClass G149 := by decide
example : ¬ GraphCalc.IsEulerianClass G149 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G149 := by decide
example : GraphCalc.IsK4FreeClass G149 := by decide
example : GraphCalc.IsNontrivialClass G149 := by decide
example : ¬ GraphCalc.IsBipartiteClass G149 := by decide

-- EhNG  (n=6, m=8)
abbrev G150 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 5), (1, 2), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G150 = 6 := by decide
example : GraphCalc.size G150 = 8 := by decide
example : SimpleGraph.minDegree G150 = 2 := by decide
example : SimpleGraph.maxDegree G150 = 3 := by decide
example : GraphCalc.indepNum G150 = 2 := by decide
example : GraphCalc.cliqueNum G150 = 3 := by decide
example : GraphCalc.dominationNumber G150 = 2 := by decide
example : GraphCalc.independentDominationNumber G150 = 2 := by decide
example : GraphCalc.slaterNumber G150 = 2 := by decide
example : GraphCalc.annihilationNumber G150 = 3 := by decide
example : GraphCalc.zeroForcingNumber G150 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G150 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G150 = 2 := by decide
example : GraphCalc.vertexCoverNumber G150 = 4 := by decide
example : GraphCalc.totalDominationNumber G150 = 2 := by decide
example : GraphCalc.edgeCoverNumber G150 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G150 = 2 := by decide
example : GraphCalc.romanDominationNumber G150 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G150 = 6 := by decide
example : GraphCalc.radius G150 = 2 := by decide
example : GraphCalc.IsConnectedClass G150 := by decide
example : ¬ GraphCalc.IsTreeClass G150 := by decide
example : GraphCalc.IsClawFreeClass G150 := by decide
example : ¬ GraphCalc.IsCographClass G150 := by decide
example : ¬ GraphCalc.IsRegularClass G150 := by decide
example : ¬ GraphCalc.IsCubicClass G150 := by decide
example : GraphCalc.IsSubcubicClass G150 := by decide
example : ¬ GraphCalc.IsEulerianClass G150 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G150 := by decide
example : GraphCalc.IsK4FreeClass G150 := by decide
example : GraphCalc.IsNontrivialClass G150 := by decide
example : ¬ GraphCalc.IsBipartiteClass G150 := by decide

-- Ehf_  (n=6, m=8)
abbrev G151 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G151 = 6 := by decide
example : GraphCalc.size G151 = 8 := by decide
example : SimpleGraph.minDegree G151 = 2 := by decide
example : SimpleGraph.maxDegree G151 = 3 := by decide
example : GraphCalc.indepNum G151 = 2 := by decide
example : GraphCalc.cliqueNum G151 = 3 := by decide
example : GraphCalc.dominationNumber G151 = 2 := by decide
example : GraphCalc.independentDominationNumber G151 = 2 := by decide
example : GraphCalc.slaterNumber G151 = 2 := by decide
example : GraphCalc.annihilationNumber G151 = 3 := by decide
example : GraphCalc.zeroForcingNumber G151 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G151 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G151 = 3 := by decide
example : GraphCalc.vertexCoverNumber G151 = 4 := by decide
example : GraphCalc.totalDominationNumber G151 = 3 := by decide
example : GraphCalc.edgeCoverNumber G151 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G151 = 2 := by decide
example : GraphCalc.romanDominationNumber G151 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G151 = 6 := by decide
example : GraphCalc.radius G151 = 2 := by decide
example : GraphCalc.IsConnectedClass G151 := by decide
example : ¬ GraphCalc.IsTreeClass G151 := by decide
example : GraphCalc.IsClawFreeClass G151 := by decide
example : ¬ GraphCalc.IsCographClass G151 := by decide
example : ¬ GraphCalc.IsRegularClass G151 := by decide
example : ¬ GraphCalc.IsCubicClass G151 := by decide
example : GraphCalc.IsSubcubicClass G151 := by decide
example : ¬ GraphCalc.IsEulerianClass G151 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G151 := by decide
example : GraphCalc.IsK4FreeClass G151 := by decide
example : GraphCalc.IsNontrivialClass G151 := by decide
example : ¬ GraphCalc.IsBipartiteClass G151 := by decide

-- EhUg  (n=6, m=8)
abbrev G152 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 5), (1, 2), (1, 4), (2, 3), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G152 = 6 := by decide
example : GraphCalc.size G152 = 8 := by decide
example : SimpleGraph.minDegree G152 = 2 := by decide
example : SimpleGraph.maxDegree G152 = 3 := by decide
example : GraphCalc.indepNum G152 = 3 := by decide
example : GraphCalc.cliqueNum G152 = 2 := by decide
example : GraphCalc.dominationNumber G152 = 2 := by decide
example : GraphCalc.independentDominationNumber G152 = 2 := by decide
example : GraphCalc.slaterNumber G152 = 2 := by decide
example : GraphCalc.annihilationNumber G152 = 3 := by decide
example : GraphCalc.zeroForcingNumber G152 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G152 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G152 = 3 := by decide
example : GraphCalc.vertexCoverNumber G152 = 3 := by decide
example : GraphCalc.totalDominationNumber G152 = 2 := by decide
example : GraphCalc.edgeCoverNumber G152 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G152 = 2 := by decide
example : GraphCalc.romanDominationNumber G152 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G152 = 6 := by decide
example : GraphCalc.radius G152 = 2 := by decide
example : GraphCalc.IsConnectedClass G152 := by decide
example : ¬ GraphCalc.IsTreeClass G152 := by decide
example : ¬ GraphCalc.IsClawFreeClass G152 := by decide
example : ¬ GraphCalc.IsCographClass G152 := by decide
example : ¬ GraphCalc.IsRegularClass G152 := by decide
example : ¬ GraphCalc.IsCubicClass G152 := by decide
example : GraphCalc.IsSubcubicClass G152 := by decide
example : ¬ GraphCalc.IsEulerianClass G152 := by decide
example : GraphCalc.IsTriangleFreeClass G152 := by decide
example : GraphCalc.IsK4FreeClass G152 := by decide
example : GraphCalc.IsNontrivialClass G152 := by decide
example : GraphCalc.IsBipartiteClass G152 := by decide

-- En{?  (n=6, m=9)
abbrev G153 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G153 = 6 := by decide
example : GraphCalc.size G153 = 9 := by decide
example : SimpleGraph.minDegree G153 = 0 := by decide
example : SimpleGraph.maxDegree G153 = 4 := by decide
example : GraphCalc.indepNum G153 = 3 := by decide
example : GraphCalc.cliqueNum G153 = 4 := by decide
example : GraphCalc.dominationNumber G153 = 2 := by decide
example : GraphCalc.independentDominationNumber G153 = 2 := by decide
example : GraphCalc.slaterNumber G153 = 2 := by decide
example : GraphCalc.annihilationNumber G153 = 3 := by decide
example : GraphCalc.zeroForcingNumber G153 = 4 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G153 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G153 := by decide
example : GraphCalc.vertexCoverNumber G153 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G153 = 2 := by decide
example : GraphCalc.romanDominationNumber G153 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G153 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G153 := by decide
example : ¬ GraphCalc.IsTreeClass G153 := by decide
example : GraphCalc.IsClawFreeClass G153 := by decide
example : GraphCalc.IsCographClass G153 := by decide
example : ¬ GraphCalc.IsRegularClass G153 := by decide
example : ¬ GraphCalc.IsCubicClass G153 := by decide
example : ¬ GraphCalc.IsSubcubicClass G153 := by decide
example : ¬ GraphCalc.IsEulerianClass G153 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G153 := by decide
example : ¬ GraphCalc.IsK4FreeClass G153 := by decide
example : GraphCalc.IsNontrivialClass G153 := by decide
example : ¬ GraphCalc.IsBipartiteClass G153 := by decide

-- E~H_  (n=6, m=9)
abbrev G154 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (2, 5)]
example : GraphCalc.order G154 = 6 := by decide
example : GraphCalc.size G154 = 9 := by decide
example : SimpleGraph.minDegree G154 = 1 := by decide
example : SimpleGraph.maxDegree G154 = 5 := by decide
example : GraphCalc.indepNum G154 = 3 := by decide
example : GraphCalc.cliqueNum G154 = 4 := by decide
example : GraphCalc.dominationNumber G154 = 1 := by decide
example : GraphCalc.independentDominationNumber G154 = 1 := by decide
example : GraphCalc.slaterNumber G154 = 1 := by decide
example : GraphCalc.annihilationNumber G154 = 4 := by decide
example : GraphCalc.zeroForcingNumber G154 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G154 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G154 = 3 := by decide
example : GraphCalc.vertexCoverNumber G154 = 3 := by decide
example : GraphCalc.totalDominationNumber G154 = 2 := by decide
example : GraphCalc.edgeCoverNumber G154 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G154 = 2 := by decide
example : GraphCalc.romanDominationNumber G154 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G154 = 3 := by decide
example : GraphCalc.radius G154 = 1 := by decide
example : GraphCalc.IsConnectedClass G154 := by decide
example : ¬ GraphCalc.IsTreeClass G154 := by decide
example : ¬ GraphCalc.IsClawFreeClass G154 := by decide
example : GraphCalc.IsCographClass G154 := by decide
example : ¬ GraphCalc.IsRegularClass G154 := by decide
example : ¬ GraphCalc.IsCubicClass G154 := by decide
example : ¬ GraphCalc.IsSubcubicClass G154 := by decide
example : ¬ GraphCalc.IsEulerianClass G154 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G154 := by decide
example : ¬ GraphCalc.IsK4FreeClass G154 := by decide
example : GraphCalc.IsNontrivialClass G154 := by decide
example : ¬ GraphCalc.IsBipartiteClass G154 := by decide

-- E~`_  (n=6, m=9)
abbrev G155 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 5), (2, 3), (2, 5)]
example : GraphCalc.order G155 = 6 := by decide
example : GraphCalc.size G155 = 9 := by decide
example : SimpleGraph.minDegree G155 = 1 := by decide
example : SimpleGraph.maxDegree G155 = 4 := by decide
example : GraphCalc.indepNum G155 = 3 := by decide
example : GraphCalc.cliqueNum G155 = 4 := by decide
example : GraphCalc.dominationNumber G155 = 2 := by decide
example : GraphCalc.independentDominationNumber G155 = 2 := by decide
example : GraphCalc.slaterNumber G155 = 2 := by decide
example : GraphCalc.annihilationNumber G155 = 3 := by decide
example : GraphCalc.zeroForcingNumber G155 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G155 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G155 = 3 := by decide
example : GraphCalc.vertexCoverNumber G155 = 3 := by decide
example : GraphCalc.totalDominationNumber G155 = 2 := by decide
example : GraphCalc.edgeCoverNumber G155 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G155 = 2 := by decide
example : GraphCalc.romanDominationNumber G155 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G155 = 5 := by decide
example : GraphCalc.radius G155 = 2 := by decide
example : GraphCalc.IsConnectedClass G155 := by decide
example : ¬ GraphCalc.IsTreeClass G155 := by decide
example : GraphCalc.IsClawFreeClass G155 := by decide
example : ¬ GraphCalc.IsCographClass G155 := by decide
example : ¬ GraphCalc.IsRegularClass G155 := by decide
example : ¬ GraphCalc.IsCubicClass G155 := by decide
example : ¬ GraphCalc.IsSubcubicClass G155 := by decide
example : ¬ GraphCalc.IsEulerianClass G155 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G155 := by decide
example : ¬ GraphCalc.IsK4FreeClass G155 := by decide
example : GraphCalc.IsNontrivialClass G155 := by decide
example : ¬ GraphCalc.IsBipartiteClass G155 := by decide

-- El{G  (n=6, m=9)
abbrev G156 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G156 = 6 := by decide
example : GraphCalc.size G156 = 9 := by decide
example : SimpleGraph.minDegree G156 = 1 := by decide
example : SimpleGraph.maxDegree G156 = 5 := by decide
example : GraphCalc.indepNum G156 = 3 := by decide
example : GraphCalc.cliqueNum G156 = 3 := by decide
example : GraphCalc.dominationNumber G156 = 1 := by decide
example : GraphCalc.independentDominationNumber G156 = 1 := by decide
example : GraphCalc.slaterNumber G156 = 1 := by decide
example : GraphCalc.annihilationNumber G156 = 3 := by decide
example : GraphCalc.zeroForcingNumber G156 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G156 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G156 = 3 := by decide
example : GraphCalc.vertexCoverNumber G156 = 3 := by decide
example : GraphCalc.totalDominationNumber G156 = 2 := by decide
example : GraphCalc.edgeCoverNumber G156 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G156 = 2 := by decide
example : GraphCalc.romanDominationNumber G156 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G156 = 3 := by decide
example : GraphCalc.radius G156 = 1 := by decide
example : GraphCalc.IsConnectedClass G156 := by decide
example : ¬ GraphCalc.IsTreeClass G156 := by decide
example : ¬ GraphCalc.IsClawFreeClass G156 := by decide
example : GraphCalc.IsCographClass G156 := by decide
example : ¬ GraphCalc.IsRegularClass G156 := by decide
example : ¬ GraphCalc.IsCubicClass G156 := by decide
example : ¬ GraphCalc.IsSubcubicClass G156 := by decide
example : ¬ GraphCalc.IsEulerianClass G156 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G156 := by decide
example : GraphCalc.IsK4FreeClass G156 := by decide
example : GraphCalc.IsNontrivialClass G156 := by decide
example : ¬ GraphCalc.IsBipartiteClass G156 := by decide

-- EZSw  (n=6, m=9)
abbrev G157 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G157 = 6 := by decide
example : GraphCalc.size G157 = 9 := by decide
example : SimpleGraph.minDegree G157 = 1 := by decide
example : SimpleGraph.maxDegree G157 = 4 := by decide
example : GraphCalc.indepNum G157 = 3 := by decide
example : GraphCalc.cliqueNum G157 = 3 := by decide
example : GraphCalc.dominationNumber G157 = 2 := by decide
example : GraphCalc.independentDominationNumber G157 = 2 := by decide
example : GraphCalc.slaterNumber G157 = 2 := by decide
example : GraphCalc.annihilationNumber G157 = 3 := by decide
example : GraphCalc.zeroForcingNumber G157 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G157 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G157 = 3 := by decide
example : GraphCalc.vertexCoverNumber G157 = 3 := by decide
example : GraphCalc.totalDominationNumber G157 = 2 := by decide
example : GraphCalc.edgeCoverNumber G157 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G157 = 2 := by decide
example : GraphCalc.romanDominationNumber G157 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G157 = 5 := by decide
example : GraphCalc.radius G157 = 2 := by decide
example : GraphCalc.IsConnectedClass G157 := by decide
example : ¬ GraphCalc.IsTreeClass G157 := by decide
example : ¬ GraphCalc.IsClawFreeClass G157 := by decide
example : ¬ GraphCalc.IsCographClass G157 := by decide
example : ¬ GraphCalc.IsRegularClass G157 := by decide
example : ¬ GraphCalc.IsCubicClass G157 := by decide
example : ¬ GraphCalc.IsSubcubicClass G157 := by decide
example : ¬ GraphCalc.IsEulerianClass G157 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G157 := by decide
example : GraphCalc.IsK4FreeClass G157 := by decide
example : GraphCalc.IsNontrivialClass G157 := by decide
example : ¬ GraphCalc.IsBipartiteClass G157 := by decide

-- E~@g  (n=6, m=9)
abbrev G158 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 5), (2, 3), (2, 5), (4, 5)]
example : GraphCalc.order G158 = 6 := by decide
example : GraphCalc.size G158 = 9 := by decide
example : SimpleGraph.minDegree G158 = 1 := by decide
example : SimpleGraph.maxDegree G158 = 4 := by decide
example : GraphCalc.indepNum G158 = 2 := by decide
example : GraphCalc.cliqueNum G158 = 4 := by decide
example : GraphCalc.dominationNumber G158 = 2 := by decide
example : GraphCalc.independentDominationNumber G158 = 2 := by decide
example : GraphCalc.slaterNumber G158 = 2 := by decide
example : GraphCalc.annihilationNumber G158 = 3 := by decide
example : GraphCalc.zeroForcingNumber G158 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G158 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G158 = 3 := by decide
example : GraphCalc.vertexCoverNumber G158 = 4 := by decide
example : GraphCalc.totalDominationNumber G158 = 2 := by decide
example : GraphCalc.edgeCoverNumber G158 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G158 = 2 := by decide
example : GraphCalc.romanDominationNumber G158 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G158 = 5 := by decide
example : GraphCalc.radius G158 = 2 := by decide
example : GraphCalc.IsConnectedClass G158 := by decide
example : ¬ GraphCalc.IsTreeClass G158 := by decide
example : GraphCalc.IsClawFreeClass G158 := by decide
example : ¬ GraphCalc.IsCographClass G158 := by decide
example : ¬ GraphCalc.IsRegularClass G158 := by decide
example : ¬ GraphCalc.IsCubicClass G158 := by decide
example : ¬ GraphCalc.IsSubcubicClass G158 := by decide
example : ¬ GraphCalc.IsEulerianClass G158 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G158 := by decide
example : ¬ GraphCalc.IsK4FreeClass G158 := by decide
example : GraphCalc.IsNontrivialClass G158 := by decide
example : ¬ GraphCalc.IsBipartiteClass G158 := by decide

-- E?~w  (n=6, m=9)
abbrev G159 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G159 = 6 := by decide
example : GraphCalc.size G159 = 9 := by decide
example : SimpleGraph.minDegree G159 = 2 := by decide
example : SimpleGraph.maxDegree G159 = 5 := by decide
example : GraphCalc.indepNum G159 = 4 := by decide
example : GraphCalc.cliqueNum G159 = 3 := by decide
example : GraphCalc.dominationNumber G159 = 1 := by decide
example : GraphCalc.independentDominationNumber G159 = 1 := by decide
example : GraphCalc.slaterNumber G159 = 1 := by decide
example : GraphCalc.annihilationNumber G159 = 4 := by decide
example : GraphCalc.zeroForcingNumber G159 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G159 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G159 = 4 := by decide
example : GraphCalc.vertexCoverNumber G159 = 2 := by decide
example : GraphCalc.totalDominationNumber G159 = 2 := by decide
example : GraphCalc.edgeCoverNumber G159 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G159 = 2 := by decide
example : GraphCalc.romanDominationNumber G159 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G159 = 3 := by decide
example : GraphCalc.radius G159 = 1 := by decide
example : GraphCalc.IsConnectedClass G159 := by decide
example : ¬ GraphCalc.IsTreeClass G159 := by decide
example : ¬ GraphCalc.IsClawFreeClass G159 := by decide
example : GraphCalc.IsCographClass G159 := by decide
example : ¬ GraphCalc.IsRegularClass G159 := by decide
example : ¬ GraphCalc.IsCubicClass G159 := by decide
example : ¬ GraphCalc.IsSubcubicClass G159 := by decide
example : ¬ GraphCalc.IsEulerianClass G159 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G159 := by decide
example : GraphCalc.IsK4FreeClass G159 := by decide
example : GraphCalc.IsNontrivialClass G159 := by decide
example : ¬ GraphCalc.IsBipartiteClass G159 := by decide

-- E|e_  (n=6, m=9)
abbrev G160 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G160 = 6 := by decide
example : GraphCalc.size G160 = 9 := by decide
example : SimpleGraph.minDegree G160 = 2 := by decide
example : SimpleGraph.maxDegree G160 = 5 := by decide
example : GraphCalc.indepNum G160 = 3 := by decide
example : GraphCalc.cliqueNum G160 = 3 := by decide
example : GraphCalc.dominationNumber G160 = 1 := by decide
example : GraphCalc.independentDominationNumber G160 = 1 := by decide
example : GraphCalc.slaterNumber G160 = 1 := by decide
example : GraphCalc.annihilationNumber G160 = 4 := by decide
example : GraphCalc.zeroForcingNumber G160 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G160 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G160 = 3 := by decide
example : GraphCalc.vertexCoverNumber G160 = 3 := by decide
example : GraphCalc.totalDominationNumber G160 = 2 := by decide
example : GraphCalc.edgeCoverNumber G160 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G160 = 2 := by decide
example : GraphCalc.romanDominationNumber G160 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G160 = 3 := by decide
example : GraphCalc.radius G160 = 1 := by decide
example : GraphCalc.IsConnectedClass G160 := by decide
example : ¬ GraphCalc.IsTreeClass G160 := by decide
example : ¬ GraphCalc.IsClawFreeClass G160 := by decide
example : ¬ GraphCalc.IsCographClass G160 := by decide
example : ¬ GraphCalc.IsRegularClass G160 := by decide
example : ¬ GraphCalc.IsCubicClass G160 := by decide
example : ¬ GraphCalc.IsSubcubicClass G160 := by decide
example : ¬ GraphCalc.IsEulerianClass G160 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G160 := by decide
example : GraphCalc.IsK4FreeClass G160 := by decide
example : GraphCalc.IsNontrivialClass G160 := by decide
example : ¬ GraphCalc.IsBipartiteClass G160 := by decide

-- EyuG  (n=6, m=9)
abbrev G161 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (3, 4), (4, 5)]
example : GraphCalc.order G161 = 6 := by decide
example : GraphCalc.size G161 = 9 := by decide
example : SimpleGraph.minDegree G161 = 2 := by decide
example : SimpleGraph.maxDegree G161 = 4 := by decide
example : GraphCalc.indepNum G161 = 3 := by decide
example : GraphCalc.cliqueNum G161 = 3 := by decide
example : GraphCalc.dominationNumber G161 = 2 := by decide
example : GraphCalc.independentDominationNumber G161 = 2 := by decide
example : GraphCalc.slaterNumber G161 = 2 := by decide
example : GraphCalc.annihilationNumber G161 = 3 := by decide
example : GraphCalc.zeroForcingNumber G161 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G161 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G161 = 3 := by decide
example : GraphCalc.vertexCoverNumber G161 = 3 := by decide
example : GraphCalc.totalDominationNumber G161 = 2 := by decide
example : GraphCalc.edgeCoverNumber G161 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G161 = 2 := by decide
example : GraphCalc.romanDominationNumber G161 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G161 = 5 := by decide
example : GraphCalc.radius G161 = 2 := by decide
example : GraphCalc.IsConnectedClass G161 := by decide
example : ¬ GraphCalc.IsTreeClass G161 := by decide
example : GraphCalc.IsClawFreeClass G161 := by decide
example : ¬ GraphCalc.IsCographClass G161 := by decide
example : ¬ GraphCalc.IsRegularClass G161 := by decide
example : ¬ GraphCalc.IsCubicClass G161 := by decide
example : ¬ GraphCalc.IsSubcubicClass G161 := by decide
example : GraphCalc.IsEulerianClass G161 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G161 := by decide
example : GraphCalc.IsK4FreeClass G161 := by decide
example : GraphCalc.IsNontrivialClass G161 := by decide
example : ¬ GraphCalc.IsBipartiteClass G161 := by decide

-- EyVG  (n=6, m=9)
abbrev G162 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (3, 4), (4, 5)]
example : GraphCalc.order G162 = 6 := by decide
example : GraphCalc.size G162 = 9 := by decide
example : SimpleGraph.minDegree G162 = 2 := by decide
example : SimpleGraph.maxDegree G162 = 5 := by decide
example : GraphCalc.indepNum G162 = 3 := by decide
example : GraphCalc.cliqueNum G162 = 3 := by decide
example : GraphCalc.dominationNumber G162 = 1 := by decide
example : GraphCalc.independentDominationNumber G162 = 1 := by decide
example : GraphCalc.slaterNumber G162 = 1 := by decide
example : GraphCalc.annihilationNumber G162 = 3 := by decide
example : GraphCalc.zeroForcingNumber G162 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G162 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G162 = 2 := by decide
example : GraphCalc.vertexCoverNumber G162 = 3 := by decide
example : GraphCalc.totalDominationNumber G162 = 2 := by decide
example : GraphCalc.edgeCoverNumber G162 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G162 = 2 := by decide
example : GraphCalc.romanDominationNumber G162 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G162 = 3 := by decide
example : GraphCalc.radius G162 = 1 := by decide
example : GraphCalc.IsConnectedClass G162 := by decide
example : ¬ GraphCalc.IsTreeClass G162 := by decide
example : ¬ GraphCalc.IsClawFreeClass G162 := by decide
example : ¬ GraphCalc.IsCographClass G162 := by decide
example : ¬ GraphCalc.IsRegularClass G162 := by decide
example : ¬ GraphCalc.IsCubicClass G162 := by decide
example : ¬ GraphCalc.IsSubcubicClass G162 := by decide
example : ¬ GraphCalc.IsEulerianClass G162 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G162 := by decide
example : GraphCalc.IsK4FreeClass G162 := by decide
example : GraphCalc.IsNontrivialClass G162 := by decide
example : ¬ GraphCalc.IsBipartiteClass G162 := by decide

-- E~aG  (n=6, m=9)
abbrev G163 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (2, 3), (4, 5)]
example : GraphCalc.order G163 = 6 := by decide
example : GraphCalc.size G163 = 9 := by decide
example : SimpleGraph.minDegree G163 = 2 := by decide
example : SimpleGraph.maxDegree G163 = 5 := by decide
example : GraphCalc.indepNum G163 = 2 := by decide
example : GraphCalc.cliqueNum G163 = 4 := by decide
example : GraphCalc.dominationNumber G163 = 1 := by decide
example : GraphCalc.independentDominationNumber G163 = 1 := by decide
example : GraphCalc.slaterNumber G163 = 1 := by decide
example : GraphCalc.annihilationNumber G163 = 3 := by decide
example : GraphCalc.zeroForcingNumber G163 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G163 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G163 = 4 := by decide
example : GraphCalc.vertexCoverNumber G163 = 4 := by decide
example : GraphCalc.totalDominationNumber G163 = 2 := by decide
example : GraphCalc.edgeCoverNumber G163 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G163 = 2 := by decide
example : GraphCalc.romanDominationNumber G163 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G163 = 3 := by decide
example : GraphCalc.radius G163 = 1 := by decide
example : GraphCalc.IsConnectedClass G163 := by decide
example : ¬ GraphCalc.IsTreeClass G163 := by decide
example : GraphCalc.IsClawFreeClass G163 := by decide
example : GraphCalc.IsCographClass G163 := by decide
example : ¬ GraphCalc.IsRegularClass G163 := by decide
example : ¬ GraphCalc.IsCubicClass G163 := by decide
example : ¬ GraphCalc.IsSubcubicClass G163 := by decide
example : ¬ GraphCalc.IsEulerianClass G163 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G163 := by decide
example : ¬ GraphCalc.IsK4FreeClass G163 := by decide
example : GraphCalc.IsNontrivialClass G163 := by decide
example : ¬ GraphCalc.IsBipartiteClass G163 := by decide

-- ElfO  (n=6, m=9)
abbrev G164 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (3, 4), (3, 5)]
example : GraphCalc.order G164 = 6 := by decide
example : GraphCalc.size G164 = 9 := by decide
example : SimpleGraph.minDegree G164 = 2 := by decide
example : SimpleGraph.maxDegree G164 = 4 := by decide
example : GraphCalc.indepNum G164 = 3 := by decide
example : GraphCalc.cliqueNum G164 = 3 := by decide
example : GraphCalc.dominationNumber G164 = 2 := by decide
example : GraphCalc.independentDominationNumber G164 = 2 := by decide
example : GraphCalc.slaterNumber G164 = 2 := by decide
example : GraphCalc.annihilationNumber G164 = 3 := by decide
example : GraphCalc.zeroForcingNumber G164 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G164 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G164 = 3 := by decide
example : GraphCalc.vertexCoverNumber G164 = 3 := by decide
example : GraphCalc.totalDominationNumber G164 = 2 := by decide
example : GraphCalc.edgeCoverNumber G164 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G164 = 2 := by decide
example : GraphCalc.romanDominationNumber G164 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G164 = 5 := by decide
example : GraphCalc.radius G164 = 2 := by decide
example : GraphCalc.IsConnectedClass G164 := by decide
example : ¬ GraphCalc.IsTreeClass G164 := by decide
example : ¬ GraphCalc.IsClawFreeClass G164 := by decide
example : ¬ GraphCalc.IsCographClass G164 := by decide
example : ¬ GraphCalc.IsRegularClass G164 := by decide
example : ¬ GraphCalc.IsCubicClass G164 := by decide
example : ¬ GraphCalc.IsSubcubicClass G164 := by decide
example : ¬ GraphCalc.IsEulerianClass G164 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G164 := by decide
example : GraphCalc.IsK4FreeClass G164 := by decide
example : GraphCalc.IsNontrivialClass G164 := by decide
example : ¬ GraphCalc.IsBipartiteClass G164 := by decide

-- E^eG  (n=6, m=9)
abbrev G165 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G165 = 6 := by decide
example : GraphCalc.size G165 = 9 := by decide
example : SimpleGraph.minDegree G165 = 2 := by decide
example : SimpleGraph.maxDegree G165 = 4 := by decide
example : GraphCalc.indepNum G165 = 2 := by decide
example : GraphCalc.cliqueNum G165 = 3 := by decide
example : GraphCalc.dominationNumber G165 = 2 := by decide
example : GraphCalc.independentDominationNumber G165 = 2 := by decide
example : GraphCalc.slaterNumber G165 = 2 := by decide
example : GraphCalc.annihilationNumber G165 = 3 := by decide
example : GraphCalc.zeroForcingNumber G165 = 2 := by decide
example : GraphCalc.totalZeroForcingNumber G165 = 2 := by decide
example : GraphCalc.connectedZeroForcingNumber G165 = 2 := by decide
example : GraphCalc.vertexCoverNumber G165 = 4 := by decide
example : GraphCalc.totalDominationNumber G165 = 2 := by decide
example : GraphCalc.edgeCoverNumber G165 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G165 = 2 := by decide
example : GraphCalc.romanDominationNumber G165 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G165 = 5 := by decide
example : GraphCalc.radius G165 = 2 := by decide
example : GraphCalc.IsConnectedClass G165 := by decide
example : ¬ GraphCalc.IsTreeClass G165 := by decide
example : GraphCalc.IsClawFreeClass G165 := by decide
example : ¬ GraphCalc.IsCographClass G165 := by decide
example : ¬ GraphCalc.IsRegularClass G165 := by decide
example : ¬ GraphCalc.IsCubicClass G165 := by decide
example : ¬ GraphCalc.IsSubcubicClass G165 := by decide
example : ¬ GraphCalc.IsEulerianClass G165 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G165 := by decide
example : GraphCalc.IsK4FreeClass G165 := by decide
example : GraphCalc.IsNontrivialClass G165 := by decide
example : ¬ GraphCalc.IsBipartiteClass G165 := by decide

-- E^MG  (n=6, m=9)
abbrev G166 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G166 = 6 := by decide
example : GraphCalc.size G166 = 9 := by decide
example : SimpleGraph.minDegree G166 = 2 := by decide
example : SimpleGraph.maxDegree G166 = 4 := by decide
example : GraphCalc.indepNum G166 = 3 := by decide
example : GraphCalc.cliqueNum G166 = 3 := by decide
example : GraphCalc.dominationNumber G166 = 2 := by decide
example : GraphCalc.independentDominationNumber G166 = 2 := by decide
example : GraphCalc.slaterNumber G166 = 2 := by decide
example : GraphCalc.annihilationNumber G166 = 3 := by decide
example : GraphCalc.zeroForcingNumber G166 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G166 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G166 = 3 := by decide
example : GraphCalc.vertexCoverNumber G166 = 3 := by decide
example : GraphCalc.totalDominationNumber G166 = 2 := by decide
example : GraphCalc.edgeCoverNumber G166 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G166 = 2 := by decide
example : GraphCalc.romanDominationNumber G166 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G166 = 5 := by decide
example : GraphCalc.radius G166 = 2 := by decide
example : GraphCalc.IsConnectedClass G166 := by decide
example : ¬ GraphCalc.IsTreeClass G166 := by decide
example : ¬ GraphCalc.IsClawFreeClass G166 := by decide
example : ¬ GraphCalc.IsCographClass G166 := by decide
example : ¬ GraphCalc.IsRegularClass G166 := by decide
example : ¬ GraphCalc.IsCubicClass G166 := by decide
example : ¬ GraphCalc.IsSubcubicClass G166 := by decide
example : ¬ GraphCalc.IsEulerianClass G166 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G166 := by decide
example : GraphCalc.IsK4FreeClass G166 := by decide
example : GraphCalc.IsNontrivialClass G166 := by decide
example : ¬ GraphCalc.IsBipartiteClass G166 := by decide

-- Exf_  (n=6, m=9)
abbrev G167 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G167 = 6 := by decide
example : GraphCalc.size G167 = 9 := by decide
example : SimpleGraph.minDegree G167 = 2 := by decide
example : SimpleGraph.maxDegree G167 = 4 := by decide
example : GraphCalc.indepNum G167 = 2 := by decide
example : GraphCalc.cliqueNum G167 = 4 := by decide
example : GraphCalc.dominationNumber G167 = 2 := by decide
example : GraphCalc.independentDominationNumber G167 = 2 := by decide
example : GraphCalc.slaterNumber G167 = 2 := by decide
example : GraphCalc.annihilationNumber G167 = 3 := by decide
example : GraphCalc.zeroForcingNumber G167 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G167 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G167 = 3 := by decide
example : GraphCalc.vertexCoverNumber G167 = 4 := by decide
example : GraphCalc.totalDominationNumber G167 = 2 := by decide
example : GraphCalc.edgeCoverNumber G167 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G167 = 2 := by decide
example : GraphCalc.romanDominationNumber G167 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G167 = 5 := by decide
example : GraphCalc.radius G167 = 2 := by decide
example : GraphCalc.IsConnectedClass G167 := by decide
example : ¬ GraphCalc.IsTreeClass G167 := by decide
example : GraphCalc.IsClawFreeClass G167 := by decide
example : ¬ GraphCalc.IsCographClass G167 := by decide
example : ¬ GraphCalc.IsRegularClass G167 := by decide
example : ¬ GraphCalc.IsCubicClass G167 := by decide
example : ¬ GraphCalc.IsSubcubicClass G167 := by decide
example : ¬ GraphCalc.IsEulerianClass G167 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G167 := by decide
example : ¬ GraphCalc.IsK4FreeClass G167 := by decide
example : GraphCalc.IsNontrivialClass G167 := by decide
example : ¬ GraphCalc.IsBipartiteClass G167 := by decide

-- EO~o  (n=6, m=9)
abbrev G168 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)]
example : GraphCalc.order G168 = 6 := by decide
example : GraphCalc.size G168 = 9 := by decide
example : SimpleGraph.minDegree G168 = 2 := by decide
example : SimpleGraph.maxDegree G168 = 4 := by decide
example : GraphCalc.indepNum G168 = 3 := by decide
example : GraphCalc.cliqueNum G168 = 3 := by decide
example : GraphCalc.dominationNumber G168 = 2 := by decide
example : GraphCalc.independentDominationNumber G168 = 2 := by decide
example : GraphCalc.slaterNumber G168 = 2 := by decide
example : GraphCalc.annihilationNumber G168 = 3 := by decide
example : GraphCalc.zeroForcingNumber G168 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G168 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G168 = 3 := by decide
example : GraphCalc.vertexCoverNumber G168 = 3 := by decide
example : GraphCalc.totalDominationNumber G168 = 2 := by decide
example : GraphCalc.edgeCoverNumber G168 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G168 = 2 := by decide
example : GraphCalc.romanDominationNumber G168 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G168 = 4 := by decide
example : GraphCalc.radius G168 = 2 := by decide
example : GraphCalc.IsConnectedClass G168 := by decide
example : ¬ GraphCalc.IsTreeClass G168 := by decide
example : ¬ GraphCalc.IsClawFreeClass G168 := by decide
example : GraphCalc.IsCographClass G168 := by decide
example : ¬ GraphCalc.IsRegularClass G168 := by decide
example : ¬ GraphCalc.IsCubicClass G168 := by decide
example : ¬ GraphCalc.IsSubcubicClass G168 := by decide
example : ¬ GraphCalc.IsEulerianClass G168 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G168 := by decide
example : GraphCalc.IsK4FreeClass G168 := by decide
example : GraphCalc.IsNontrivialClass G168 := by decide
example : ¬ GraphCalc.IsBipartiteClass G168 := by decide

-- Ehew  (n=6, m=9)
abbrev G169 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G169 = 6 := by decide
example : GraphCalc.size G169 = 9 := by decide
example : SimpleGraph.minDegree G169 = 2 := by decide
example : SimpleGraph.maxDegree G169 = 4 := by decide
example : GraphCalc.indepNum G169 = 2 := by decide
example : GraphCalc.cliqueNum G169 = 3 := by decide
example : GraphCalc.dominationNumber G169 = 2 := by decide
example : GraphCalc.independentDominationNumber G169 = 2 := by decide
example : GraphCalc.slaterNumber G169 = 2 := by decide
example : GraphCalc.annihilationNumber G169 = 3 := by decide
example : GraphCalc.zeroForcingNumber G169 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G169 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G169 = 3 := by decide
example : GraphCalc.vertexCoverNumber G169 = 4 := by decide
example : GraphCalc.totalDominationNumber G169 = 2 := by decide
example : GraphCalc.edgeCoverNumber G169 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G169 = 2 := by decide
example : GraphCalc.romanDominationNumber G169 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G169 = 5 := by decide
example : GraphCalc.radius G169 = 2 := by decide
example : GraphCalc.IsConnectedClass G169 := by decide
example : ¬ GraphCalc.IsTreeClass G169 := by decide
example : GraphCalc.IsClawFreeClass G169 := by decide
example : ¬ GraphCalc.IsCographClass G169 := by decide
example : ¬ GraphCalc.IsRegularClass G169 := by decide
example : ¬ GraphCalc.IsCubicClass G169 := by decide
example : ¬ GraphCalc.IsSubcubicClass G169 := by decide
example : ¬ GraphCalc.IsEulerianClass G169 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G169 := by decide
example : GraphCalc.IsK4FreeClass G169 := by decide
example : GraphCalc.IsNontrivialClass G169 := by decide
example : ¬ GraphCalc.IsBipartiteClass G169 := by decide

-- Elf_  (n=6, m=9)
abbrev G170 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G170 = 6 := by decide
example : GraphCalc.size G170 = 9 := by decide
example : SimpleGraph.minDegree G170 = 2 := by decide
example : SimpleGraph.maxDegree G170 = 4 := by decide
example : GraphCalc.indepNum G170 = 2 := by decide
example : GraphCalc.cliqueNum G170 = 3 := by decide
example : GraphCalc.dominationNumber G170 = 2 := by decide
example : GraphCalc.independentDominationNumber G170 = 2 := by decide
example : GraphCalc.slaterNumber G170 = 2 := by decide
example : GraphCalc.annihilationNumber G170 = 3 := by decide
example : GraphCalc.zeroForcingNumber G170 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G170 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G170 = 3 := by decide
example : GraphCalc.vertexCoverNumber G170 = 4 := by decide
example : GraphCalc.totalDominationNumber G170 = 2 := by decide
example : GraphCalc.edgeCoverNumber G170 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G170 = 2 := by decide
example : GraphCalc.romanDominationNumber G170 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G170 = 5 := by decide
example : GraphCalc.radius G170 = 2 := by decide
example : GraphCalc.IsConnectedClass G170 := by decide
example : ¬ GraphCalc.IsTreeClass G170 := by decide
example : GraphCalc.IsClawFreeClass G170 := by decide
example : ¬ GraphCalc.IsCographClass G170 := by decide
example : ¬ GraphCalc.IsRegularClass G170 := by decide
example : ¬ GraphCalc.IsCubicClass G170 := by decide
example : ¬ GraphCalc.IsSubcubicClass G170 := by decide
example : ¬ GraphCalc.IsEulerianClass G170 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G170 := by decide
example : GraphCalc.IsK4FreeClass G170 := by decide
example : GraphCalc.IsNontrivialClass G170 := by decide
example : ¬ GraphCalc.IsBipartiteClass G170 := by decide

-- ElMg  (n=6, m=9)
abbrev G171 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 5), (1, 2), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G171 = 6 := by decide
example : GraphCalc.size G171 = 9 := by decide
example : SimpleGraph.minDegree G171 = 2 := by decide
example : SimpleGraph.maxDegree G171 = 4 := by decide
example : GraphCalc.indepNum G171 = 3 := by decide
example : GraphCalc.cliqueNum G171 = 3 := by decide
example : GraphCalc.dominationNumber G171 = 2 := by decide
example : GraphCalc.independentDominationNumber G171 = 2 := by decide
example : GraphCalc.slaterNumber G171 = 2 := by decide
example : GraphCalc.annihilationNumber G171 = 3 := by decide
example : GraphCalc.zeroForcingNumber G171 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G171 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G171 = 3 := by decide
example : GraphCalc.vertexCoverNumber G171 = 3 := by decide
example : GraphCalc.totalDominationNumber G171 = 2 := by decide
example : GraphCalc.edgeCoverNumber G171 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G171 = 2 := by decide
example : GraphCalc.romanDominationNumber G171 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G171 = 5 := by decide
example : GraphCalc.radius G171 = 2 := by decide
example : GraphCalc.IsConnectedClass G171 := by decide
example : ¬ GraphCalc.IsTreeClass G171 := by decide
example : ¬ GraphCalc.IsClawFreeClass G171 := by decide
example : ¬ GraphCalc.IsCographClass G171 := by decide
example : ¬ GraphCalc.IsRegularClass G171 := by decide
example : ¬ GraphCalc.IsCubicClass G171 := by decide
example : ¬ GraphCalc.IsSubcubicClass G171 := by decide
example : ¬ GraphCalc.IsEulerianClass G171 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G171 := by decide
example : GraphCalc.IsK4FreeClass G171 := by decide
example : GraphCalc.IsNontrivialClass G171 := by decide
example : ¬ GraphCalc.IsBipartiteClass G171 := by decide

-- EtTg  (n=6, m=9)
abbrev G172 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G172 = 6 := by decide
example : GraphCalc.size G172 = 9 := by decide
example : SimpleGraph.minDegree G172 = 3 := by decide
example : SimpleGraph.maxDegree G172 = 3 := by decide
example : GraphCalc.indepNum G172 = 2 := by decide
example : GraphCalc.cliqueNum G172 = 3 := by decide
example : GraphCalc.dominationNumber G172 = 2 := by decide
example : GraphCalc.independentDominationNumber G172 = 2 := by decide
example : GraphCalc.slaterNumber G172 = 2 := by decide
example : GraphCalc.annihilationNumber G172 = 3 := by decide
example : GraphCalc.zeroForcingNumber G172 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G172 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G172 = 3 := by decide
example : GraphCalc.vertexCoverNumber G172 = 4 := by decide
example : GraphCalc.totalDominationNumber G172 = 2 := by decide
example : GraphCalc.edgeCoverNumber G172 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G172 = 2 := by decide
example : GraphCalc.romanDominationNumber G172 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G172 = 6 := by decide
example : GraphCalc.radius G172 = 2 := by decide
example : GraphCalc.IsConnectedClass G172 := by decide
example : ¬ GraphCalc.IsTreeClass G172 := by decide
example : GraphCalc.IsClawFreeClass G172 := by decide
example : ¬ GraphCalc.IsCographClass G172 := by decide
example : GraphCalc.IsRegularClass G172 := by decide
example : GraphCalc.IsCubicClass G172 := by decide
example : GraphCalc.IsSubcubicClass G172 := by decide
example : ¬ GraphCalc.IsEulerianClass G172 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G172 := by decide
example : GraphCalc.IsK4FreeClass G172 := by decide
example : GraphCalc.IsNontrivialClass G172 := by decide
example : ¬ GraphCalc.IsBipartiteClass G172 := by decide

-- ElUg  (n=6, m=9)
abbrev G173 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 5), (1, 2), (1, 4), (2, 3), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G173 = 6 := by decide
example : GraphCalc.size G173 = 9 := by decide
example : SimpleGraph.minDegree G173 = 3 := by decide
example : SimpleGraph.maxDegree G173 = 3 := by decide
example : GraphCalc.indepNum G173 = 3 := by decide
example : GraphCalc.cliqueNum G173 = 2 := by decide
example : GraphCalc.dominationNumber G173 = 2 := by decide
example : GraphCalc.independentDominationNumber G173 = 3 := by decide
example : GraphCalc.slaterNumber G173 = 2 := by decide
example : GraphCalc.annihilationNumber G173 = 3 := by decide
example : GraphCalc.zeroForcingNumber G173 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G173 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G173 = 4 := by decide
example : GraphCalc.vertexCoverNumber G173 = 3 := by decide
example : GraphCalc.totalDominationNumber G173 = 2 := by decide
example : GraphCalc.edgeCoverNumber G173 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G173 = 2 := by decide
example : GraphCalc.romanDominationNumber G173 = 4 := by decide
example : GraphCalc.doubleRomanDominationNumber G173 = 6 := by decide
example : GraphCalc.radius G173 = 2 := by decide
example : GraphCalc.IsConnectedClass G173 := by decide
example : ¬ GraphCalc.IsTreeClass G173 := by decide
example : ¬ GraphCalc.IsClawFreeClass G173 := by decide
example : GraphCalc.IsCographClass G173 := by decide
example : GraphCalc.IsRegularClass G173 := by decide
example : GraphCalc.IsCubicClass G173 := by decide
example : GraphCalc.IsSubcubicClass G173 := by decide
example : ¬ GraphCalc.IsEulerianClass G173 := by decide
example : GraphCalc.IsTriangleFreeClass G173 := by decide
example : GraphCalc.IsK4FreeClass G173 := by decide
example : GraphCalc.IsNontrivialClass G173 := by decide
example : GraphCalc.IsBipartiteClass G173 := by decide

-- E~{?  (n=6, m=10)
abbrev G174 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G174 = 6 := by decide
example : GraphCalc.size G174 = 10 := by decide
example : SimpleGraph.minDegree G174 = 0 := by decide
example : SimpleGraph.maxDegree G174 = 4 := by decide
example : GraphCalc.indepNum G174 = 2 := by decide
example : GraphCalc.cliqueNum G174 = 5 := by decide
example : GraphCalc.dominationNumber G174 = 2 := by decide
example : GraphCalc.independentDominationNumber G174 = 2 := by decide
example : GraphCalc.slaterNumber G174 = 2 := by decide
example : GraphCalc.annihilationNumber G174 = 3 := by decide
example : GraphCalc.zeroForcingNumber G174 = 5 := by decide
example : ¬ GraphCalc.HasTotalZeroForcingNumber G174 := by decide
example : ¬ GraphCalc.HasConnectedZeroForcingNumber G174 := by decide
example : GraphCalc.vertexCoverNumber G174 = 4 := by decide
example : GraphCalc.subTotalDominationNumber G174 = 2 := by decide
example : GraphCalc.romanDominationNumber G174 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G174 = 5 := by decide
example : ¬ GraphCalc.IsConnectedClass G174 := by decide
example : ¬ GraphCalc.IsTreeClass G174 := by decide
example : GraphCalc.IsClawFreeClass G174 := by decide
example : GraphCalc.IsCographClass G174 := by decide
example : ¬ GraphCalc.IsRegularClass G174 := by decide
example : ¬ GraphCalc.IsCubicClass G174 := by decide
example : ¬ GraphCalc.IsSubcubicClass G174 := by decide
example : ¬ GraphCalc.IsEulerianClass G174 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G174 := by decide
example : ¬ GraphCalc.IsK4FreeClass G174 := by decide
example : GraphCalc.IsNontrivialClass G174 := by decide
example : ¬ GraphCalc.IsBipartiteClass G174 := by decide

-- En{G  (n=6, m=10)
abbrev G175 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G175 = 6 := by decide
example : GraphCalc.size G175 = 10 := by decide
example : SimpleGraph.minDegree G175 = 1 := by decide
example : SimpleGraph.maxDegree G175 = 5 := by decide
example : GraphCalc.indepNum G175 = 3 := by decide
example : GraphCalc.cliqueNum G175 = 4 := by decide
example : GraphCalc.dominationNumber G175 = 1 := by decide
example : GraphCalc.independentDominationNumber G175 = 1 := by decide
example : GraphCalc.slaterNumber G175 = 1 := by decide
example : GraphCalc.annihilationNumber G175 = 3 := by decide
example : GraphCalc.zeroForcingNumber G175 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G175 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G175 = 3 := by decide
example : GraphCalc.vertexCoverNumber G175 = 3 := by decide
example : GraphCalc.totalDominationNumber G175 = 2 := by decide
example : GraphCalc.edgeCoverNumber G175 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G175 = 2 := by decide
example : GraphCalc.romanDominationNumber G175 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G175 = 3 := by decide
example : GraphCalc.radius G175 = 1 := by decide
example : GraphCalc.IsConnectedClass G175 := by decide
example : ¬ GraphCalc.IsTreeClass G175 := by decide
example : ¬ GraphCalc.IsClawFreeClass G175 := by decide
example : GraphCalc.IsCographClass G175 := by decide
example : ¬ GraphCalc.IsRegularClass G175 := by decide
example : ¬ GraphCalc.IsCubicClass G175 := by decide
example : ¬ GraphCalc.IsSubcubicClass G175 := by decide
example : ¬ GraphCalc.IsEulerianClass G175 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G175 := by decide
example : ¬ GraphCalc.IsK4FreeClass G175 := by decide
example : GraphCalc.IsNontrivialClass G175 := by decide
example : ¬ GraphCalc.IsBipartiteClass G175 := by decide

-- En}?  (n=6, m=10)
abbrev G176 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G176 = 6 := by decide
example : GraphCalc.size G176 = 10 := by decide
example : SimpleGraph.minDegree G176 = 1 := by decide
example : SimpleGraph.maxDegree G176 = 4 := by decide
example : GraphCalc.indepNum G176 = 2 := by decide
example : GraphCalc.cliqueNum G176 = 4 := by decide
example : GraphCalc.dominationNumber G176 = 2 := by decide
example : GraphCalc.independentDominationNumber G176 = 2 := by decide
example : GraphCalc.slaterNumber G176 = 2 := by decide
example : GraphCalc.annihilationNumber G176 = 3 := by decide
example : GraphCalc.zeroForcingNumber G176 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G176 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G176 = 3 := by decide
example : GraphCalc.vertexCoverNumber G176 = 4 := by decide
example : GraphCalc.totalDominationNumber G176 = 2 := by decide
example : GraphCalc.edgeCoverNumber G176 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G176 = 2 := by decide
example : GraphCalc.romanDominationNumber G176 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G176 = 5 := by decide
example : GraphCalc.radius G176 = 2 := by decide
example : GraphCalc.IsConnectedClass G176 := by decide
example : ¬ GraphCalc.IsTreeClass G176 := by decide
example : GraphCalc.IsClawFreeClass G176 := by decide
example : ¬ GraphCalc.IsCographClass G176 := by decide
example : ¬ GraphCalc.IsRegularClass G176 := by decide
example : ¬ GraphCalc.IsCubicClass G176 := by decide
example : ¬ GraphCalc.IsSubcubicClass G176 := by decide
example : ¬ GraphCalc.IsEulerianClass G176 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G176 := by decide
example : ¬ GraphCalc.IsK4FreeClass G176 := by decide
example : GraphCalc.IsNontrivialClass G176 := by decide
example : ¬ GraphCalc.IsBipartiteClass G176 := by decide

-- E_~w  (n=6, m=10)
abbrev G177 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G177 = 6 := by decide
example : GraphCalc.size G177 = 10 := by decide
example : SimpleGraph.minDegree G177 = 2 := by decide
example : SimpleGraph.maxDegree G177 = 5 := by decide
example : GraphCalc.indepNum G177 = 3 := by decide
example : GraphCalc.cliqueNum G177 = 4 := by decide
example : GraphCalc.dominationNumber G177 = 1 := by decide
example : GraphCalc.independentDominationNumber G177 = 1 := by decide
example : GraphCalc.slaterNumber G177 = 1 := by decide
example : GraphCalc.annihilationNumber G177 = 4 := by decide
example : GraphCalc.zeroForcingNumber G177 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G177 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G177 = 3 := by decide
example : GraphCalc.vertexCoverNumber G177 = 3 := by decide
example : GraphCalc.totalDominationNumber G177 = 2 := by decide
example : GraphCalc.edgeCoverNumber G177 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G177 = 2 := by decide
example : GraphCalc.romanDominationNumber G177 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G177 = 3 := by decide
example : GraphCalc.radius G177 = 1 := by decide
example : GraphCalc.IsConnectedClass G177 := by decide
example : ¬ GraphCalc.IsTreeClass G177 := by decide
example : ¬ GraphCalc.IsClawFreeClass G177 := by decide
example : GraphCalc.IsCographClass G177 := by decide
example : ¬ GraphCalc.IsRegularClass G177 := by decide
example : ¬ GraphCalc.IsCubicClass G177 := by decide
example : ¬ GraphCalc.IsSubcubicClass G177 := by decide
example : ¬ GraphCalc.IsEulerianClass G177 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G177 := by decide
example : ¬ GraphCalc.IsK4FreeClass G177 := by decide
example : GraphCalc.IsNontrivialClass G177 := by decide
example : ¬ GraphCalc.IsBipartiteClass G177 := by decide

-- EjtW  (n=6, m=10)
abbrev G178 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G178 = 6 := by decide
example : GraphCalc.size G178 = 10 := by decide
example : SimpleGraph.minDegree G178 = 2 := by decide
example : SimpleGraph.maxDegree G178 = 5 := by decide
example : GraphCalc.indepNum G178 = 3 := by decide
example : GraphCalc.cliqueNum G178 = 4 := by decide
example : GraphCalc.dominationNumber G178 = 1 := by decide
example : GraphCalc.independentDominationNumber G178 = 1 := by decide
example : GraphCalc.slaterNumber G178 = 1 := by decide
example : GraphCalc.annihilationNumber G178 = 3 := by decide
example : GraphCalc.zeroForcingNumber G178 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G178 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G178 = 3 := by decide
example : GraphCalc.vertexCoverNumber G178 = 3 := by decide
example : GraphCalc.totalDominationNumber G178 = 2 := by decide
example : GraphCalc.edgeCoverNumber G178 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G178 = 2 := by decide
example : GraphCalc.romanDominationNumber G178 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G178 = 3 := by decide
example : GraphCalc.radius G178 = 1 := by decide
example : GraphCalc.IsConnectedClass G178 := by decide
example : ¬ GraphCalc.IsTreeClass G178 := by decide
example : ¬ GraphCalc.IsClawFreeClass G178 := by decide
example : ¬ GraphCalc.IsCographClass G178 := by decide
example : ¬ GraphCalc.IsRegularClass G178 := by decide
example : ¬ GraphCalc.IsCubicClass G178 := by decide
example : ¬ GraphCalc.IsSubcubicClass G178 := by decide
example : ¬ GraphCalc.IsEulerianClass G178 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G178 := by decide
example : ¬ GraphCalc.IsK4FreeClass G178 := by decide
example : GraphCalc.IsNontrivialClass G178 := by decide
example : ¬ GraphCalc.IsBipartiteClass G178 := by decide

-- E^mG  (n=6, m=10)
abbrev G179 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G179 = 6 := by decide
example : GraphCalc.size G179 = 10 := by decide
example : SimpleGraph.minDegree G179 = 2 := by decide
example : SimpleGraph.maxDegree G179 = 4 := by decide
example : GraphCalc.indepNum G179 = 2 := by decide
example : GraphCalc.cliqueNum G179 = 4 := by decide
example : GraphCalc.dominationNumber G179 = 2 := by decide
example : GraphCalc.independentDominationNumber G179 = 2 := by decide
example : GraphCalc.slaterNumber G179 = 2 := by decide
example : GraphCalc.annihilationNumber G179 = 3 := by decide
example : GraphCalc.zeroForcingNumber G179 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G179 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G179 = 3 := by decide
example : GraphCalc.vertexCoverNumber G179 = 4 := by decide
example : GraphCalc.totalDominationNumber G179 = 2 := by decide
example : GraphCalc.edgeCoverNumber G179 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G179 = 2 := by decide
example : GraphCalc.romanDominationNumber G179 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G179 = 5 := by decide
example : GraphCalc.radius G179 = 2 := by decide
example : GraphCalc.IsConnectedClass G179 := by decide
example : ¬ GraphCalc.IsTreeClass G179 := by decide
example : GraphCalc.IsClawFreeClass G179 := by decide
example : ¬ GraphCalc.IsCographClass G179 := by decide
example : ¬ GraphCalc.IsRegularClass G179 := by decide
example : ¬ GraphCalc.IsCubicClass G179 := by decide
example : ¬ GraphCalc.IsSubcubicClass G179 := by decide
example : GraphCalc.IsEulerianClass G179 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G179 := by decide
example : ¬ GraphCalc.IsK4FreeClass G179 := by decide
example : GraphCalc.IsNontrivialClass G179 := by decide
example : ¬ GraphCalc.IsBipartiteClass G179 := by decide

-- E^Mg  (n=6, m=10)
abbrev G180 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G180 = 6 := by decide
example : GraphCalc.size G180 = 10 := by decide
example : SimpleGraph.minDegree G180 = 2 := by decide
example : SimpleGraph.maxDegree G180 = 5 := by decide
example : GraphCalc.indepNum G180 = 3 := by decide
example : GraphCalc.cliqueNum G180 = 3 := by decide
example : GraphCalc.dominationNumber G180 = 1 := by decide
example : GraphCalc.independentDominationNumber G180 = 1 := by decide
example : GraphCalc.slaterNumber G180 = 1 := by decide
example : GraphCalc.annihilationNumber G180 = 3 := by decide
example : GraphCalc.zeroForcingNumber G180 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G180 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G180 = 3 := by decide
example : GraphCalc.vertexCoverNumber G180 = 3 := by decide
example : GraphCalc.totalDominationNumber G180 = 2 := by decide
example : GraphCalc.edgeCoverNumber G180 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G180 = 2 := by decide
example : GraphCalc.romanDominationNumber G180 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G180 = 3 := by decide
example : GraphCalc.radius G180 = 1 := by decide
example : GraphCalc.IsConnectedClass G180 := by decide
example : ¬ GraphCalc.IsTreeClass G180 := by decide
example : ¬ GraphCalc.IsClawFreeClass G180 := by decide
example : ¬ GraphCalc.IsCographClass G180 := by decide
example : ¬ GraphCalc.IsRegularClass G180 := by decide
example : ¬ GraphCalc.IsCubicClass G180 := by decide
example : ¬ GraphCalc.IsSubcubicClass G180 := by decide
example : ¬ GraphCalc.IsEulerianClass G180 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G180 := by decide
example : GraphCalc.IsK4FreeClass G180 := by decide
example : GraphCalc.IsNontrivialClass G180 := by decide
example : ¬ GraphCalc.IsBipartiteClass G180 := by decide

-- EjvG  (n=6, m=10)
abbrev G181 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (3, 4), (4, 5)]
example : GraphCalc.order G181 = 6 := by decide
example : GraphCalc.size G181 = 10 := by decide
example : SimpleGraph.minDegree G181 = 2 := by decide
example : SimpleGraph.maxDegree G181 = 5 := by decide
example : GraphCalc.indepNum G181 = 2 := by decide
example : GraphCalc.cliqueNum G181 = 4 := by decide
example : GraphCalc.dominationNumber G181 = 1 := by decide
example : GraphCalc.independentDominationNumber G181 = 1 := by decide
example : GraphCalc.slaterNumber G181 = 1 := by decide
example : GraphCalc.annihilationNumber G181 = 3 := by decide
example : GraphCalc.zeroForcingNumber G181 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G181 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G181 = 3 := by decide
example : GraphCalc.vertexCoverNumber G181 = 4 := by decide
example : GraphCalc.totalDominationNumber G181 = 2 := by decide
example : GraphCalc.edgeCoverNumber G181 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G181 = 2 := by decide
example : GraphCalc.romanDominationNumber G181 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G181 = 3 := by decide
example : GraphCalc.radius G181 = 1 := by decide
example : GraphCalc.IsConnectedClass G181 := by decide
example : ¬ GraphCalc.IsTreeClass G181 := by decide
example : GraphCalc.IsClawFreeClass G181 := by decide
example : ¬ GraphCalc.IsCographClass G181 := by decide
example : ¬ GraphCalc.IsRegularClass G181 := by decide
example : ¬ GraphCalc.IsCubicClass G181 := by decide
example : ¬ GraphCalc.IsSubcubicClass G181 := by decide
example : ¬ GraphCalc.IsEulerianClass G181 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G181 := by decide
example : ¬ GraphCalc.IsK4FreeClass G181 := by decide
example : GraphCalc.IsNontrivialClass G181 := by decide
example : ¬ GraphCalc.IsBipartiteClass G181 := by decide

-- Elfo  (n=6, m=10)
abbrev G182 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5)]
example : GraphCalc.order G182 = 6 := by decide
example : GraphCalc.size G182 = 10 := by decide
example : SimpleGraph.minDegree G182 = 2 := by decide
example : SimpleGraph.maxDegree G182 = 4 := by decide
example : GraphCalc.indepNum G182 = 2 := by decide
example : GraphCalc.cliqueNum G182 = 3 := by decide
example : GraphCalc.dominationNumber G182 = 2 := by decide
example : GraphCalc.independentDominationNumber G182 = 2 := by decide
example : GraphCalc.slaterNumber G182 = 2 := by decide
example : GraphCalc.annihilationNumber G182 = 3 := by decide
example : GraphCalc.zeroForcingNumber G182 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G182 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G182 = 3 := by decide
example : GraphCalc.vertexCoverNumber G182 = 4 := by decide
example : GraphCalc.totalDominationNumber G182 = 2 := by decide
example : GraphCalc.edgeCoverNumber G182 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G182 = 2 := by decide
example : GraphCalc.romanDominationNumber G182 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G182 = 5 := by decide
example : GraphCalc.radius G182 = 2 := by decide
example : GraphCalc.IsConnectedClass G182 := by decide
example : ¬ GraphCalc.IsTreeClass G182 := by decide
example : GraphCalc.IsClawFreeClass G182 := by decide
example : ¬ GraphCalc.IsCographClass G182 := by decide
example : ¬ GraphCalc.IsRegularClass G182 := by decide
example : ¬ GraphCalc.IsCubicClass G182 := by decide
example : ¬ GraphCalc.IsSubcubicClass G182 := by decide
example : ¬ GraphCalc.IsEulerianClass G182 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G182 := by decide
example : GraphCalc.IsK4FreeClass G182 := by decide
example : GraphCalc.IsNontrivialClass G182 := by decide
example : ¬ GraphCalc.IsBipartiteClass G182 := by decide

-- Exv_  (n=6, m=10)
abbrev G183 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4)]
example : GraphCalc.order G183 = 6 := by decide
example : GraphCalc.size G183 = 10 := by decide
example : SimpleGraph.minDegree G183 = 2 := by decide
example : SimpleGraph.maxDegree G183 = 4 := by decide
example : GraphCalc.indepNum G183 = 2 := by decide
example : GraphCalc.cliqueNum G183 = 4 := by decide
example : GraphCalc.dominationNumber G183 = 2 := by decide
example : GraphCalc.independentDominationNumber G183 = 2 := by decide
example : GraphCalc.slaterNumber G183 = 2 := by decide
example : GraphCalc.annihilationNumber G183 = 3 := by decide
example : GraphCalc.zeroForcingNumber G183 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G183 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G183 = 3 := by decide
example : GraphCalc.vertexCoverNumber G183 = 4 := by decide
example : GraphCalc.totalDominationNumber G183 = 2 := by decide
example : GraphCalc.edgeCoverNumber G183 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G183 = 2 := by decide
example : GraphCalc.romanDominationNumber G183 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G183 = 5 := by decide
example : GraphCalc.radius G183 = 2 := by decide
example : GraphCalc.IsConnectedClass G183 := by decide
example : ¬ GraphCalc.IsTreeClass G183 := by decide
example : GraphCalc.IsClawFreeClass G183 := by decide
example : ¬ GraphCalc.IsCographClass G183 := by decide
example : ¬ GraphCalc.IsRegularClass G183 := by decide
example : ¬ GraphCalc.IsCubicClass G183 := by decide
example : ¬ GraphCalc.IsSubcubicClass G183 := by decide
example : ¬ GraphCalc.IsEulerianClass G183 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G183 := by decide
example : ¬ GraphCalc.IsK4FreeClass G183 := by decide
example : GraphCalc.IsNontrivialClass G183 := by decide
example : ¬ GraphCalc.IsBipartiteClass G183 := by decide

-- ErXw  (n=6, m=10)
abbrev G184 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5)]
example : GraphCalc.order G184 = 6 := by decide
example : GraphCalc.size G184 = 10 := by decide
example : SimpleGraph.minDegree G184 = 2 := by decide
example : SimpleGraph.maxDegree G184 = 4 := by decide
example : GraphCalc.indepNum G184 = 3 := by decide
example : GraphCalc.cliqueNum G184 = 3 := by decide
example : GraphCalc.dominationNumber G184 = 2 := by decide
example : GraphCalc.independentDominationNumber G184 = 2 := by decide
example : GraphCalc.slaterNumber G184 = 2 := by decide
example : GraphCalc.annihilationNumber G184 = 3 := by decide
example : GraphCalc.zeroForcingNumber G184 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G184 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G184 = 3 := by decide
example : GraphCalc.vertexCoverNumber G184 = 3 := by decide
example : GraphCalc.totalDominationNumber G184 = 2 := by decide
example : GraphCalc.edgeCoverNumber G184 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G184 = 2 := by decide
example : GraphCalc.romanDominationNumber G184 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G184 = 4 := by decide
example : GraphCalc.radius G184 = 2 := by decide
example : GraphCalc.IsConnectedClass G184 := by decide
example : ¬ GraphCalc.IsTreeClass G184 := by decide
example : ¬ GraphCalc.IsClawFreeClass G184 := by decide
example : GraphCalc.IsCographClass G184 := by decide
example : ¬ GraphCalc.IsRegularClass G184 := by decide
example : ¬ GraphCalc.IsCubicClass G184 := by decide
example : ¬ GraphCalc.IsSubcubicClass G184 := by decide
example : ¬ GraphCalc.IsEulerianClass G184 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G184 := by decide
example : GraphCalc.IsK4FreeClass G184 := by decide
example : GraphCalc.IsNontrivialClass G184 := by decide
example : ¬ GraphCalc.IsBipartiteClass G184 := by decide

-- Ehfw  (n=6, m=10)
abbrev G185 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 4), (0, 5), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G185 = 6 := by decide
example : GraphCalc.size G185 = 10 := by decide
example : SimpleGraph.minDegree G185 = 3 := by decide
example : SimpleGraph.maxDegree G185 = 5 := by decide
example : GraphCalc.indepNum G185 = 2 := by decide
example : GraphCalc.cliqueNum G185 = 3 := by decide
example : GraphCalc.dominationNumber G185 = 1 := by decide
example : GraphCalc.independentDominationNumber G185 = 1 := by decide
example : GraphCalc.slaterNumber G185 = 1 := by decide
example : GraphCalc.annihilationNumber G185 = 3 := by decide
example : GraphCalc.zeroForcingNumber G185 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G185 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G185 = 3 := by decide
example : GraphCalc.vertexCoverNumber G185 = 4 := by decide
example : GraphCalc.totalDominationNumber G185 = 2 := by decide
example : GraphCalc.edgeCoverNumber G185 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G185 = 2 := by decide
example : GraphCalc.romanDominationNumber G185 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G185 = 3 := by decide
example : GraphCalc.radius G185 = 1 := by decide
example : GraphCalc.IsConnectedClass G185 := by decide
example : ¬ GraphCalc.IsTreeClass G185 := by decide
example : GraphCalc.IsClawFreeClass G185 := by decide
example : ¬ GraphCalc.IsCographClass G185 := by decide
example : ¬ GraphCalc.IsRegularClass G185 := by decide
example : ¬ GraphCalc.IsCubicClass G185 := by decide
example : ¬ GraphCalc.IsSubcubicClass G185 := by decide
example : ¬ GraphCalc.IsEulerianClass G185 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G185 := by decide
example : GraphCalc.IsK4FreeClass G185 := by decide
example : GraphCalc.IsNontrivialClass G185 := by decide
example : ¬ GraphCalc.IsBipartiteClass G185 := by decide

-- EzNG  (n=6, m=10)
abbrev G186 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G186 = 6 := by decide
example : GraphCalc.size G186 = 10 := by decide
example : SimpleGraph.minDegree G186 = 3 := by decide
example : SimpleGraph.maxDegree G186 = 4 := by decide
example : GraphCalc.indepNum G186 = 2 := by decide
example : GraphCalc.cliqueNum G186 = 3 := by decide
example : GraphCalc.dominationNumber G186 = 2 := by decide
example : GraphCalc.independentDominationNumber G186 = 2 := by decide
example : GraphCalc.slaterNumber G186 = 2 := by decide
example : GraphCalc.annihilationNumber G186 = 3 := by decide
example : GraphCalc.zeroForcingNumber G186 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G186 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G186 = 3 := by decide
example : GraphCalc.vertexCoverNumber G186 = 4 := by decide
example : GraphCalc.totalDominationNumber G186 = 2 := by decide
example : GraphCalc.edgeCoverNumber G186 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G186 = 2 := by decide
example : GraphCalc.romanDominationNumber G186 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G186 = 5 := by decide
example : GraphCalc.radius G186 = 2 := by decide
example : GraphCalc.IsConnectedClass G186 := by decide
example : ¬ GraphCalc.IsTreeClass G186 := by decide
example : GraphCalc.IsClawFreeClass G186 := by decide
example : ¬ GraphCalc.IsCographClass G186 := by decide
example : ¬ GraphCalc.IsRegularClass G186 := by decide
example : ¬ GraphCalc.IsCubicClass G186 := by decide
example : ¬ GraphCalc.IsSubcubicClass G186 := by decide
example : ¬ GraphCalc.IsEulerianClass G186 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G186 := by decide
example : GraphCalc.IsK4FreeClass G186 := by decide
example : GraphCalc.IsNontrivialClass G186 := by decide
example : ¬ GraphCalc.IsBipartiteClass G186 := by decide

-- E^NG  (n=6, m=10)
abbrev G187 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G187 = 6 := by decide
example : GraphCalc.size G187 = 10 := by decide
example : SimpleGraph.minDegree G187 = 3 := by decide
example : SimpleGraph.maxDegree G187 = 4 := by decide
example : GraphCalc.indepNum G187 = 3 := by decide
example : GraphCalc.cliqueNum G187 = 3 := by decide
example : GraphCalc.dominationNumber G187 = 2 := by decide
example : GraphCalc.independentDominationNumber G187 = 2 := by decide
example : GraphCalc.slaterNumber G187 = 2 := by decide
example : GraphCalc.annihilationNumber G187 = 3 := by decide
example : GraphCalc.zeroForcingNumber G187 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G187 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G187 = 4 := by decide
example : GraphCalc.vertexCoverNumber G187 = 3 := by decide
example : GraphCalc.totalDominationNumber G187 = 2 := by decide
example : GraphCalc.edgeCoverNumber G187 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G187 = 2 := by decide
example : GraphCalc.romanDominationNumber G187 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G187 = 5 := by decide
example : GraphCalc.radius G187 = 2 := by decide
example : GraphCalc.IsConnectedClass G187 := by decide
example : ¬ GraphCalc.IsTreeClass G187 := by decide
example : ¬ GraphCalc.IsClawFreeClass G187 := by decide
example : GraphCalc.IsCographClass G187 := by decide
example : ¬ GraphCalc.IsRegularClass G187 := by decide
example : ¬ GraphCalc.IsCubicClass G187 := by decide
example : ¬ GraphCalc.IsSubcubicClass G187 := by decide
example : ¬ GraphCalc.IsEulerianClass G187 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G187 := by decide
example : GraphCalc.IsK4FreeClass G187 := by decide
example : GraphCalc.IsNontrivialClass G187 := by decide
example : ¬ GraphCalc.IsBipartiteClass G187 := by decide

-- EyUw  (n=6, m=10)
abbrev G188 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G188 = 6 := by decide
example : GraphCalc.size G188 = 10 := by decide
example : SimpleGraph.minDegree G188 = 3 := by decide
example : SimpleGraph.maxDegree G188 = 4 := by decide
example : GraphCalc.indepNum G188 = 2 := by decide
example : GraphCalc.cliqueNum G188 = 3 := by decide
example : GraphCalc.dominationNumber G188 = 2 := by decide
example : GraphCalc.independentDominationNumber G188 = 2 := by decide
example : GraphCalc.slaterNumber G188 = 2 := by decide
example : GraphCalc.annihilationNumber G188 = 3 := by decide
example : GraphCalc.zeroForcingNumber G188 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G188 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G188 = 4 := by decide
example : GraphCalc.vertexCoverNumber G188 = 4 := by decide
example : GraphCalc.totalDominationNumber G188 = 2 := by decide
example : GraphCalc.edgeCoverNumber G188 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G188 = 2 := by decide
example : GraphCalc.romanDominationNumber G188 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G188 = 4 := by decide
example : GraphCalc.radius G188 = 2 := by decide
example : GraphCalc.IsConnectedClass G188 := by decide
example : ¬ GraphCalc.IsTreeClass G188 := by decide
example : GraphCalc.IsClawFreeClass G188 := by decide
example : GraphCalc.IsCographClass G188 := by decide
example : ¬ GraphCalc.IsRegularClass G188 := by decide
example : ¬ GraphCalc.IsCubicClass G188 := by decide
example : ¬ GraphCalc.IsSubcubicClass G188 := by decide
example : ¬ GraphCalc.IsEulerianClass G188 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G188 := by decide
example : GraphCalc.IsK4FreeClass G188 := by decide
example : GraphCalc.IsNontrivialClass G188 := by decide
example : ¬ GraphCalc.IsBipartiteClass G188 := by decide

-- E~|?  (n=6, m=11)
abbrev G189 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4)]
example : GraphCalc.order G189 = 6 := by decide
example : GraphCalc.size G189 = 11 := by decide
example : SimpleGraph.minDegree G189 = 1 := by decide
example : SimpleGraph.maxDegree G189 = 5 := by decide
example : GraphCalc.indepNum G189 = 2 := by decide
example : GraphCalc.cliqueNum G189 = 5 := by decide
example : GraphCalc.dominationNumber G189 = 1 := by decide
example : GraphCalc.independentDominationNumber G189 = 1 := by decide
example : GraphCalc.slaterNumber G189 = 1 := by decide
example : GraphCalc.annihilationNumber G189 = 3 := by decide
example : GraphCalc.zeroForcingNumber G189 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G189 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G189 = 4 := by decide
example : GraphCalc.vertexCoverNumber G189 = 4 := by decide
example : GraphCalc.totalDominationNumber G189 = 2 := by decide
example : GraphCalc.edgeCoverNumber G189 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G189 = 2 := by decide
example : GraphCalc.romanDominationNumber G189 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G189 = 3 := by decide
example : GraphCalc.radius G189 = 1 := by decide
example : GraphCalc.IsConnectedClass G189 := by decide
example : ¬ GraphCalc.IsTreeClass G189 := by decide
example : GraphCalc.IsClawFreeClass G189 := by decide
example : GraphCalc.IsCographClass G189 := by decide
example : ¬ GraphCalc.IsRegularClass G189 := by decide
example : ¬ GraphCalc.IsCubicClass G189 := by decide
example : ¬ GraphCalc.IsSubcubicClass G189 := by decide
example : ¬ GraphCalc.IsEulerianClass G189 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G189 := by decide
example : ¬ GraphCalc.IsK4FreeClass G189 := by decide
example : GraphCalc.IsNontrivialClass G189 := by decide
example : ¬ GraphCalc.IsBipartiteClass G189 := by decide

-- E~Xo  (n=6, m=11)
abbrev G190 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5)]
example : GraphCalc.order G190 = 6 := by decide
example : GraphCalc.size G190 = 11 := by decide
example : SimpleGraph.minDegree G190 = 2 := by decide
example : SimpleGraph.maxDegree G190 = 5 := by decide
example : GraphCalc.indepNum G190 = 3 := by decide
example : GraphCalc.cliqueNum G190 = 4 := by decide
example : GraphCalc.dominationNumber G190 = 1 := by decide
example : GraphCalc.independentDominationNumber G190 = 1 := by decide
example : GraphCalc.slaterNumber G190 = 1 := by decide
example : GraphCalc.annihilationNumber G190 = 3 := by decide
example : GraphCalc.zeroForcingNumber G190 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G190 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G190 = 3 := by decide
example : GraphCalc.vertexCoverNumber G190 = 3 := by decide
example : GraphCalc.totalDominationNumber G190 = 2 := by decide
example : GraphCalc.edgeCoverNumber G190 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G190 = 2 := by decide
example : GraphCalc.romanDominationNumber G190 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G190 = 3 := by decide
example : GraphCalc.radius G190 = 1 := by decide
example : GraphCalc.IsConnectedClass G190 := by decide
example : ¬ GraphCalc.IsTreeClass G190 := by decide
example : ¬ GraphCalc.IsClawFreeClass G190 := by decide
example : GraphCalc.IsCographClass G190 := by decide
example : ¬ GraphCalc.IsRegularClass G190 := by decide
example : ¬ GraphCalc.IsCubicClass G190 := by decide
example : ¬ GraphCalc.IsSubcubicClass G190 := by decide
example : ¬ GraphCalc.IsEulerianClass G190 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G190 := by decide
example : ¬ GraphCalc.IsK4FreeClass G190 := by decide
example : GraphCalc.IsNontrivialClass G190 := by decide
example : ¬ GraphCalc.IsBipartiteClass G190 := by decide

-- En}G  (n=6, m=11)
abbrev G191 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G191 = 6 := by decide
example : GraphCalc.size G191 = 11 := by decide
example : SimpleGraph.minDegree G191 = 2 := by decide
example : SimpleGraph.maxDegree G191 = 5 := by decide
example : GraphCalc.indepNum G191 = 2 := by decide
example : GraphCalc.cliqueNum G191 = 4 := by decide
example : GraphCalc.dominationNumber G191 = 1 := by decide
example : GraphCalc.independentDominationNumber G191 = 1 := by decide
example : GraphCalc.slaterNumber G191 = 1 := by decide
example : GraphCalc.annihilationNumber G191 = 3 := by decide
example : GraphCalc.zeroForcingNumber G191 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G191 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G191 = 3 := by decide
example : GraphCalc.vertexCoverNumber G191 = 4 := by decide
example : GraphCalc.totalDominationNumber G191 = 2 := by decide
example : GraphCalc.edgeCoverNumber G191 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G191 = 2 := by decide
example : GraphCalc.romanDominationNumber G191 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G191 = 3 := by decide
example : GraphCalc.radius G191 = 1 := by decide
example : GraphCalc.IsConnectedClass G191 := by decide
example : ¬ GraphCalc.IsTreeClass G191 := by decide
example : GraphCalc.IsClawFreeClass G191 := by decide
example : ¬ GraphCalc.IsCographClass G191 := by decide
example : ¬ GraphCalc.IsRegularClass G191 := by decide
example : ¬ GraphCalc.IsCubicClass G191 := by decide
example : ¬ GraphCalc.IsSubcubicClass G191 := by decide
example : ¬ GraphCalc.IsEulerianClass G191 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G191 := by decide
example : ¬ GraphCalc.IsK4FreeClass G191 := by decide
example : GraphCalc.IsNontrivialClass G191 := by decide
example : ¬ GraphCalc.IsBipartiteClass G191 := by decide

-- E~wW  (n=6, m=11)
abbrev G192 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 5)]
example : GraphCalc.order G192 = 6 := by decide
example : GraphCalc.size G192 = 11 := by decide
example : SimpleGraph.minDegree G192 = 2 := by decide
example : SimpleGraph.maxDegree G192 = 4 := by decide
example : GraphCalc.indepNum G192 = 2 := by decide
example : GraphCalc.cliqueNum G192 = 4 := by decide
example : GraphCalc.dominationNumber G192 = 2 := by decide
example : GraphCalc.independentDominationNumber G192 = 2 := by decide
example : GraphCalc.slaterNumber G192 = 2 := by decide
example : GraphCalc.annihilationNumber G192 = 3 := by decide
example : GraphCalc.zeroForcingNumber G192 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G192 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G192 = 4 := by decide
example : GraphCalc.vertexCoverNumber G192 = 4 := by decide
example : GraphCalc.totalDominationNumber G192 = 2 := by decide
example : GraphCalc.edgeCoverNumber G192 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G192 = 2 := by decide
example : GraphCalc.romanDominationNumber G192 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G192 = 4 := by decide
example : GraphCalc.radius G192 = 2 := by decide
example : GraphCalc.IsConnectedClass G192 := by decide
example : ¬ GraphCalc.IsTreeClass G192 := by decide
example : GraphCalc.IsClawFreeClass G192 := by decide
example : GraphCalc.IsCographClass G192 := by decide
example : ¬ GraphCalc.IsRegularClass G192 := by decide
example : ¬ GraphCalc.IsCubicClass G192 := by decide
example : ¬ GraphCalc.IsSubcubicClass G192 := by decide
example : GraphCalc.IsEulerianClass G192 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G192 := by decide
example : ¬ GraphCalc.IsK4FreeClass G192 := by decide
example : GraphCalc.IsNontrivialClass G192 := by decide
example : ¬ GraphCalc.IsBipartiteClass G192 := by decide

-- EyVw  (n=6, m=11)
abbrev G193 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G193 = 6 := by decide
example : GraphCalc.size G193 = 11 := by decide
example : SimpleGraph.minDegree G193 = 3 := by decide
example : SimpleGraph.maxDegree G193 = 5 := by decide
example : GraphCalc.indepNum G193 = 2 := by decide
example : GraphCalc.cliqueNum G193 = 4 := by decide
example : GraphCalc.dominationNumber G193 = 1 := by decide
example : GraphCalc.independentDominationNumber G193 = 1 := by decide
example : GraphCalc.slaterNumber G193 = 1 := by decide
example : GraphCalc.annihilationNumber G193 = 3 := by decide
example : GraphCalc.zeroForcingNumber G193 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G193 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G193 = 4 := by decide
example : GraphCalc.vertexCoverNumber G193 = 4 := by decide
example : GraphCalc.totalDominationNumber G193 = 2 := by decide
example : GraphCalc.edgeCoverNumber G193 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G193 = 2 := by decide
example : GraphCalc.romanDominationNumber G193 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G193 = 3 := by decide
example : GraphCalc.radius G193 = 1 := by decide
example : GraphCalc.IsConnectedClass G193 := by decide
example : ¬ GraphCalc.IsTreeClass G193 := by decide
example : GraphCalc.IsClawFreeClass G193 := by decide
example : GraphCalc.IsCographClass G193 := by decide
example : ¬ GraphCalc.IsRegularClass G193 := by decide
example : ¬ GraphCalc.IsCubicClass G193 := by decide
example : ¬ GraphCalc.IsSubcubicClass G193 := by decide
example : ¬ GraphCalc.IsEulerianClass G193 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G193 := by decide
example : ¬ GraphCalc.IsK4FreeClass G193 := by decide
example : GraphCalc.IsNontrivialClass G193 := by decide
example : ¬ GraphCalc.IsBipartiteClass G193 := by decide

-- ER~g  (n=6, m=11)
abbrev G194 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 2), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G194 = 6 := by decide
example : GraphCalc.size G194 = 11 := by decide
example : SimpleGraph.minDegree G194 = 3 := by decide
example : SimpleGraph.maxDegree G194 = 5 := by decide
example : GraphCalc.indepNum G194 = 2 := by decide
example : GraphCalc.cliqueNum G194 = 4 := by decide
example : GraphCalc.dominationNumber G194 = 1 := by decide
example : GraphCalc.independentDominationNumber G194 = 1 := by decide
example : GraphCalc.slaterNumber G194 = 1 := by decide
example : GraphCalc.annihilationNumber G194 = 3 := by decide
example : GraphCalc.zeroForcingNumber G194 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G194 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G194 = 3 := by decide
example : GraphCalc.vertexCoverNumber G194 = 4 := by decide
example : GraphCalc.totalDominationNumber G194 = 2 := by decide
example : GraphCalc.edgeCoverNumber G194 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G194 = 2 := by decide
example : GraphCalc.romanDominationNumber G194 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G194 = 3 := by decide
example : GraphCalc.radius G194 = 1 := by decide
example : GraphCalc.IsConnectedClass G194 := by decide
example : ¬ GraphCalc.IsTreeClass G194 := by decide
example : GraphCalc.IsClawFreeClass G194 := by decide
example : ¬ GraphCalc.IsCographClass G194 := by decide
example : ¬ GraphCalc.IsRegularClass G194 := by decide
example : ¬ GraphCalc.IsCubicClass G194 := by decide
example : ¬ GraphCalc.IsSubcubicClass G194 := by decide
example : ¬ GraphCalc.IsEulerianClass G194 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G194 := by decide
example : ¬ GraphCalc.IsK4FreeClass G194 := by decide
example : GraphCalc.IsNontrivialClass G194 := by decide
example : ¬ GraphCalc.IsBipartiteClass G194 := by decide

-- E}^G  (n=6, m=11)
abbrev G195 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G195 = 6 := by decide
example : GraphCalc.size G195 = 11 := by decide
example : SimpleGraph.minDegree G195 = 3 := by decide
example : SimpleGraph.maxDegree G195 = 5 := by decide
example : GraphCalc.indepNum G195 = 3 := by decide
example : GraphCalc.cliqueNum G195 = 3 := by decide
example : GraphCalc.dominationNumber G195 = 1 := by decide
example : GraphCalc.independentDominationNumber G195 = 1 := by decide
example : GraphCalc.slaterNumber G195 = 1 := by decide
example : GraphCalc.annihilationNumber G195 = 3 := by decide
example : GraphCalc.zeroForcingNumber G195 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G195 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G195 = 4 := by decide
example : GraphCalc.vertexCoverNumber G195 = 3 := by decide
example : GraphCalc.totalDominationNumber G195 = 2 := by decide
example : GraphCalc.edgeCoverNumber G195 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G195 = 2 := by decide
example : GraphCalc.romanDominationNumber G195 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G195 = 3 := by decide
example : GraphCalc.radius G195 = 1 := by decide
example : GraphCalc.IsConnectedClass G195 := by decide
example : ¬ GraphCalc.IsTreeClass G195 := by decide
example : ¬ GraphCalc.IsClawFreeClass G195 := by decide
example : GraphCalc.IsCographClass G195 := by decide
example : ¬ GraphCalc.IsRegularClass G195 := by decide
example : ¬ GraphCalc.IsCubicClass G195 := by decide
example : ¬ GraphCalc.IsSubcubicClass G195 := by decide
example : ¬ GraphCalc.IsEulerianClass G195 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G195 := by decide
example : GraphCalc.IsK4FreeClass G195 := by decide
example : GraphCalc.IsNontrivialClass G195 := by decide
example : ¬ GraphCalc.IsBipartiteClass G195 := by decide

-- Ep~o  (n=6, m=11)
abbrev G196 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5)]
example : GraphCalc.order G196 = 6 := by decide
example : GraphCalc.size G196 = 11 := by decide
example : SimpleGraph.minDegree G196 = 3 := by decide
example : SimpleGraph.maxDegree G196 = 4 := by decide
example : GraphCalc.indepNum G196 = 2 := by decide
example : GraphCalc.cliqueNum G196 = 3 := by decide
example : GraphCalc.dominationNumber G196 = 2 := by decide
example : GraphCalc.independentDominationNumber G196 = 2 := by decide
example : GraphCalc.slaterNumber G196 = 2 := by decide
example : GraphCalc.annihilationNumber G196 = 3 := by decide
example : GraphCalc.zeroForcingNumber G196 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G196 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G196 = 3 := by decide
example : GraphCalc.vertexCoverNumber G196 = 4 := by decide
example : GraphCalc.totalDominationNumber G196 = 2 := by decide
example : GraphCalc.edgeCoverNumber G196 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G196 = 2 := by decide
example : GraphCalc.romanDominationNumber G196 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G196 = 4 := by decide
example : GraphCalc.radius G196 = 2 := by decide
example : GraphCalc.IsConnectedClass G196 := by decide
example : ¬ GraphCalc.IsTreeClass G196 := by decide
example : GraphCalc.IsClawFreeClass G196 := by decide
example : ¬ GraphCalc.IsCographClass G196 := by decide
example : ¬ GraphCalc.IsRegularClass G196 := by decide
example : ¬ GraphCalc.IsCubicClass G196 := by decide
example : ¬ GraphCalc.IsSubcubicClass G196 := by decide
example : ¬ GraphCalc.IsEulerianClass G196 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G196 := by decide
example : GraphCalc.IsK4FreeClass G196 := by decide
example : GraphCalc.IsNontrivialClass G196 := by decide
example : ¬ GraphCalc.IsBipartiteClass G196 := by decide

-- El^g  (n=6, m=11)
abbrev G197 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 3), (0, 5), (1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
example : GraphCalc.order G197 = 6 := by decide
example : GraphCalc.size G197 = 11 := by decide
example : SimpleGraph.minDegree G197 = 3 := by decide
example : SimpleGraph.maxDegree G197 = 4 := by decide
example : GraphCalc.indepNum G197 = 2 := by decide
example : GraphCalc.cliqueNum G197 = 4 := by decide
example : GraphCalc.dominationNumber G197 = 2 := by decide
example : GraphCalc.independentDominationNumber G197 = 2 := by decide
example : GraphCalc.slaterNumber G197 = 2 := by decide
example : GraphCalc.annihilationNumber G197 = 3 := by decide
example : GraphCalc.zeroForcingNumber G197 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G197 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G197 = 4 := by decide
example : GraphCalc.vertexCoverNumber G197 = 4 := by decide
example : GraphCalc.totalDominationNumber G197 = 2 := by decide
example : GraphCalc.edgeCoverNumber G197 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G197 = 2 := by decide
example : GraphCalc.romanDominationNumber G197 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G197 = 5 := by decide
example : GraphCalc.radius G197 = 2 := by decide
example : GraphCalc.IsConnectedClass G197 := by decide
example : ¬ GraphCalc.IsTreeClass G197 := by decide
example : GraphCalc.IsClawFreeClass G197 := by decide
example : GraphCalc.IsCographClass G197 := by decide
example : ¬ GraphCalc.IsRegularClass G197 := by decide
example : ¬ GraphCalc.IsCubicClass G197 := by decide
example : ¬ GraphCalc.IsSubcubicClass G197 := by decide
example : ¬ GraphCalc.IsEulerianClass G197 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G197 := by decide
example : ¬ GraphCalc.IsK4FreeClass G197 := by decide
example : GraphCalc.IsNontrivialClass G197 := by decide
example : ¬ GraphCalc.IsBipartiteClass G197 := by decide

-- E~{W  (n=6, m=12)
abbrev G198 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G198 = 6 := by decide
example : GraphCalc.size G198 = 12 := by decide
example : SimpleGraph.minDegree G198 = 2 := by decide
example : SimpleGraph.maxDegree G198 = 5 := by decide
example : GraphCalc.indepNum G198 = 2 := by decide
example : GraphCalc.cliqueNum G198 = 5 := by decide
example : GraphCalc.dominationNumber G198 = 1 := by decide
example : GraphCalc.independentDominationNumber G198 = 1 := by decide
example : GraphCalc.slaterNumber G198 = 1 := by decide
example : GraphCalc.annihilationNumber G198 = 3 := by decide
example : GraphCalc.zeroForcingNumber G198 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G198 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G198 = 4 := by decide
example : GraphCalc.vertexCoverNumber G198 = 4 := by decide
example : GraphCalc.totalDominationNumber G198 = 2 := by decide
example : GraphCalc.edgeCoverNumber G198 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G198 = 2 := by decide
example : GraphCalc.romanDominationNumber G198 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G198 = 3 := by decide
example : GraphCalc.radius G198 = 1 := by decide
example : GraphCalc.IsConnectedClass G198 := by decide
example : ¬ GraphCalc.IsTreeClass G198 := by decide
example : GraphCalc.IsClawFreeClass G198 := by decide
example : GraphCalc.IsCographClass G198 := by decide
example : ¬ GraphCalc.IsRegularClass G198 := by decide
example : ¬ GraphCalc.IsCubicClass G198 := by decide
example : ¬ GraphCalc.IsSubcubicClass G198 := by decide
example : ¬ GraphCalc.IsEulerianClass G198 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G198 := by decide
example : ¬ GraphCalc.IsK4FreeClass G198 := by decide
example : GraphCalc.IsNontrivialClass G198 := by decide
example : ¬ GraphCalc.IsBipartiteClass G198 := by decide

-- E~z_  (n=6, m=12)
abbrev G199 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)]
example : GraphCalc.order G199 = 6 := by decide
example : GraphCalc.size G199 = 12 := by decide
example : SimpleGraph.minDegree G199 = 3 := by decide
example : SimpleGraph.maxDegree G199 = 5 := by decide
example : GraphCalc.indepNum G199 = 3 := by decide
example : GraphCalc.cliqueNum G199 = 4 := by decide
example : GraphCalc.dominationNumber G199 = 1 := by decide
example : GraphCalc.independentDominationNumber G199 = 1 := by decide
example : GraphCalc.slaterNumber G199 = 1 := by decide
example : GraphCalc.annihilationNumber G199 = 3 := by decide
example : GraphCalc.zeroForcingNumber G199 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G199 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G199 = 4 := by decide
example : GraphCalc.vertexCoverNumber G199 = 3 := by decide
example : GraphCalc.totalDominationNumber G199 = 2 := by decide
example : GraphCalc.edgeCoverNumber G199 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G199 = 2 := by decide
example : GraphCalc.romanDominationNumber G199 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G199 = 3 := by decide
example : GraphCalc.radius G199 = 1 := by decide
example : GraphCalc.IsConnectedClass G199 := by decide
example : ¬ GraphCalc.IsTreeClass G199 := by decide
example : ¬ GraphCalc.IsClawFreeClass G199 := by decide
example : GraphCalc.IsCographClass G199 := by decide
example : ¬ GraphCalc.IsRegularClass G199 := by decide
example : ¬ GraphCalc.IsCubicClass G199 := by decide
example : ¬ GraphCalc.IsSubcubicClass G199 := by decide
example : ¬ GraphCalc.IsEulerianClass G199 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G199 := by decide
example : ¬ GraphCalc.IsK4FreeClass G199 := by decide
example : GraphCalc.IsNontrivialClass G199 := by decide
example : ¬ GraphCalc.IsBipartiteClass G199 := by decide

-- Ep~w  (n=6, m=12)
abbrev G200 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G200 = 6 := by decide
example : GraphCalc.size G200 = 12 := by decide
example : SimpleGraph.minDegree G200 = 3 := by decide
example : SimpleGraph.maxDegree G200 = 5 := by decide
example : GraphCalc.indepNum G200 = 2 := by decide
example : GraphCalc.cliqueNum G200 = 4 := by decide
example : GraphCalc.dominationNumber G200 = 1 := by decide
example : GraphCalc.independentDominationNumber G200 = 1 := by decide
example : GraphCalc.slaterNumber G200 = 1 := by decide
example : GraphCalc.annihilationNumber G200 = 3 := by decide
example : GraphCalc.zeroForcingNumber G200 = 3 := by decide
example : GraphCalc.totalZeroForcingNumber G200 = 3 := by decide
example : GraphCalc.connectedZeroForcingNumber G200 = 3 := by decide
example : GraphCalc.vertexCoverNumber G200 = 4 := by decide
example : GraphCalc.totalDominationNumber G200 = 2 := by decide
example : GraphCalc.edgeCoverNumber G200 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G200 = 2 := by decide
example : GraphCalc.romanDominationNumber G200 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G200 = 3 := by decide
example : GraphCalc.radius G200 = 1 := by decide
example : GraphCalc.IsConnectedClass G200 := by decide
example : ¬ GraphCalc.IsTreeClass G200 := by decide
example : GraphCalc.IsClawFreeClass G200 := by decide
example : ¬ GraphCalc.IsCographClass G200 := by decide
example : ¬ GraphCalc.IsRegularClass G200 := by decide
example : ¬ GraphCalc.IsCubicClass G200 := by decide
example : ¬ GraphCalc.IsSubcubicClass G200 := by decide
example : ¬ GraphCalc.IsEulerianClass G200 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G200 := by decide
example : ¬ GraphCalc.IsK4FreeClass G200 := by decide
example : GraphCalc.IsNontrivialClass G200 := by decide
example : ¬ GraphCalc.IsBipartiteClass G200 := by decide

-- E~^G  (n=6, m=12)
abbrev G201 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G201 = 6 := by decide
example : GraphCalc.size G201 = 12 := by decide
example : SimpleGraph.minDegree G201 = 3 := by decide
example : SimpleGraph.maxDegree G201 = 5 := by decide
example : GraphCalc.indepNum G201 = 2 := by decide
example : GraphCalc.cliqueNum G201 = 4 := by decide
example : GraphCalc.dominationNumber G201 = 1 := by decide
example : GraphCalc.independentDominationNumber G201 = 1 := by decide
example : GraphCalc.slaterNumber G201 = 1 := by decide
example : GraphCalc.annihilationNumber G201 = 3 := by decide
example : GraphCalc.zeroForcingNumber G201 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G201 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G201 = 4 := by decide
example : GraphCalc.vertexCoverNumber G201 = 4 := by decide
example : GraphCalc.totalDominationNumber G201 = 2 := by decide
example : GraphCalc.edgeCoverNumber G201 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G201 = 2 := by decide
example : GraphCalc.romanDominationNumber G201 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G201 = 3 := by decide
example : GraphCalc.radius G201 = 1 := by decide
example : GraphCalc.IsConnectedClass G201 := by decide
example : ¬ GraphCalc.IsTreeClass G201 := by decide
example : GraphCalc.IsClawFreeClass G201 := by decide
example : GraphCalc.IsCographClass G201 := by decide
example : ¬ GraphCalc.IsRegularClass G201 := by decide
example : ¬ GraphCalc.IsCubicClass G201 := by decide
example : ¬ GraphCalc.IsSubcubicClass G201 := by decide
example : ¬ GraphCalc.IsEulerianClass G201 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G201 := by decide
example : ¬ GraphCalc.IsK4FreeClass G201 := by decide
example : GraphCalc.IsNontrivialClass G201 := by decide
example : ¬ GraphCalc.IsBipartiteClass G201 := by decide

-- EznW  (n=6, m=12)
abbrev G202 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G202 = 6 := by decide
example : GraphCalc.size G202 = 12 := by decide
example : SimpleGraph.minDegree G202 = 4 := by decide
example : SimpleGraph.maxDegree G202 = 4 := by decide
example : GraphCalc.indepNum G202 = 2 := by decide
example : GraphCalc.cliqueNum G202 = 3 := by decide
example : GraphCalc.dominationNumber G202 = 2 := by decide
example : GraphCalc.independentDominationNumber G202 = 2 := by decide
example : GraphCalc.slaterNumber G202 = 2 := by decide
example : GraphCalc.annihilationNumber G202 = 3 := by decide
example : GraphCalc.zeroForcingNumber G202 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G202 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G202 = 4 := by decide
example : GraphCalc.vertexCoverNumber G202 = 4 := by decide
example : GraphCalc.totalDominationNumber G202 = 2 := by decide
example : GraphCalc.edgeCoverNumber G202 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G202 = 2 := by decide
example : GraphCalc.romanDominationNumber G202 = 3 := by decide
example : GraphCalc.doubleRomanDominationNumber G202 = 4 := by decide
example : GraphCalc.radius G202 = 2 := by decide
example : GraphCalc.IsConnectedClass G202 := by decide
example : ¬ GraphCalc.IsTreeClass G202 := by decide
example : GraphCalc.IsClawFreeClass G202 := by decide
example : GraphCalc.IsCographClass G202 := by decide
example : GraphCalc.IsRegularClass G202 := by decide
example : ¬ GraphCalc.IsCubicClass G202 := by decide
example : ¬ GraphCalc.IsSubcubicClass G202 := by decide
example : GraphCalc.IsEulerianClass G202 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G202 := by decide
example : GraphCalc.IsK4FreeClass G202 := by decide
example : GraphCalc.IsNontrivialClass G202 := by decide
example : ¬ GraphCalc.IsBipartiteClass G202 := by decide

-- E~~G  (n=6, m=13)
abbrev G203 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5)]
example : GraphCalc.order G203 = 6 := by decide
example : GraphCalc.size G203 = 13 := by decide
example : SimpleGraph.minDegree G203 = 3 := by decide
example : SimpleGraph.maxDegree G203 = 5 := by decide
example : GraphCalc.indepNum G203 = 2 := by decide
example : GraphCalc.cliqueNum G203 = 5 := by decide
example : GraphCalc.dominationNumber G203 = 1 := by decide
example : GraphCalc.independentDominationNumber G203 = 1 := by decide
example : GraphCalc.slaterNumber G203 = 1 := by decide
example : GraphCalc.annihilationNumber G203 = 3 := by decide
example : GraphCalc.zeroForcingNumber G203 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G203 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G203 = 4 := by decide
example : GraphCalc.vertexCoverNumber G203 = 4 := by decide
example : GraphCalc.totalDominationNumber G203 = 2 := by decide
example : GraphCalc.edgeCoverNumber G203 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G203 = 2 := by decide
example : GraphCalc.romanDominationNumber G203 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G203 = 3 := by decide
example : GraphCalc.radius G203 = 1 := by decide
example : GraphCalc.IsConnectedClass G203 := by decide
example : ¬ GraphCalc.IsTreeClass G203 := by decide
example : GraphCalc.IsClawFreeClass G203 := by decide
example : GraphCalc.IsCographClass G203 := by decide
example : ¬ GraphCalc.IsRegularClass G203 := by decide
example : ¬ GraphCalc.IsCubicClass G203 := by decide
example : ¬ GraphCalc.IsSubcubicClass G203 := by decide
example : ¬ GraphCalc.IsEulerianClass G203 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G203 := by decide
example : ¬ GraphCalc.IsK4FreeClass G203 := by decide
example : GraphCalc.IsNontrivialClass G203 := by decide
example : ¬ GraphCalc.IsBipartiteClass G203 := by decide

-- E~nW  (n=6, m=13)
abbrev G204 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G204 = 6 := by decide
example : GraphCalc.size G204 = 13 := by decide
example : SimpleGraph.minDegree G204 = 4 := by decide
example : SimpleGraph.maxDegree G204 = 5 := by decide
example : GraphCalc.indepNum G204 = 2 := by decide
example : GraphCalc.cliqueNum G204 = 4 := by decide
example : GraphCalc.dominationNumber G204 = 1 := by decide
example : GraphCalc.independentDominationNumber G204 = 1 := by decide
example : GraphCalc.slaterNumber G204 = 1 := by decide
example : GraphCalc.annihilationNumber G204 = 3 := by decide
example : GraphCalc.zeroForcingNumber G204 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G204 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G204 = 4 := by decide
example : GraphCalc.vertexCoverNumber G204 = 4 := by decide
example : GraphCalc.totalDominationNumber G204 = 2 := by decide
example : GraphCalc.edgeCoverNumber G204 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G204 = 2 := by decide
example : GraphCalc.romanDominationNumber G204 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G204 = 3 := by decide
example : GraphCalc.radius G204 = 1 := by decide
example : GraphCalc.IsConnectedClass G204 := by decide
example : ¬ GraphCalc.IsTreeClass G204 := by decide
example : GraphCalc.IsClawFreeClass G204 := by decide
example : GraphCalc.IsCographClass G204 := by decide
example : ¬ GraphCalc.IsRegularClass G204 := by decide
example : ¬ GraphCalc.IsCubicClass G204 := by decide
example : ¬ GraphCalc.IsSubcubicClass G204 := by decide
example : ¬ GraphCalc.IsEulerianClass G204 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G204 := by decide
example : ¬ GraphCalc.IsK4FreeClass G204 := by decide
example : GraphCalc.IsNontrivialClass G204 := by decide
example : ¬ GraphCalc.IsBipartiteClass G204 := by decide

-- Ez~w  (n=6, m=14)
abbrev G205 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G205 = 6 := by decide
example : GraphCalc.size G205 = 14 := by decide
example : SimpleGraph.minDegree G205 = 4 := by decide
example : SimpleGraph.maxDegree G205 = 5 := by decide
example : GraphCalc.indepNum G205 = 2 := by decide
example : GraphCalc.cliqueNum G205 = 5 := by decide
example : GraphCalc.dominationNumber G205 = 1 := by decide
example : GraphCalc.independentDominationNumber G205 = 1 := by decide
example : GraphCalc.slaterNumber G205 = 1 := by decide
example : GraphCalc.annihilationNumber G205 = 3 := by decide
example : GraphCalc.zeroForcingNumber G205 = 4 := by decide
example : GraphCalc.totalZeroForcingNumber G205 = 4 := by decide
example : GraphCalc.connectedZeroForcingNumber G205 = 4 := by decide
example : GraphCalc.vertexCoverNumber G205 = 4 := by decide
example : GraphCalc.totalDominationNumber G205 = 2 := by decide
example : GraphCalc.edgeCoverNumber G205 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G205 = 2 := by decide
example : GraphCalc.romanDominationNumber G205 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G205 = 3 := by decide
example : GraphCalc.radius G205 = 1 := by decide
example : GraphCalc.IsConnectedClass G205 := by decide
example : ¬ GraphCalc.IsTreeClass G205 := by decide
example : GraphCalc.IsClawFreeClass G205 := by decide
example : GraphCalc.IsCographClass G205 := by decide
example : ¬ GraphCalc.IsRegularClass G205 := by decide
example : ¬ GraphCalc.IsCubicClass G205 := by decide
example : ¬ GraphCalc.IsSubcubicClass G205 := by decide
example : ¬ GraphCalc.IsEulerianClass G205 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G205 := by decide
example : ¬ GraphCalc.IsK4FreeClass G205 := by decide
example : GraphCalc.IsNontrivialClass G205 := by decide
example : ¬ GraphCalc.IsBipartiteClass G205 := by decide

-- E~~w  (n=6, m=15)
abbrev G206 : SimpleGraph (Fin 6) := GraphCalc.ofEdges 6 [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
example : GraphCalc.order G206 = 6 := by decide
example : GraphCalc.size G206 = 15 := by decide
example : SimpleGraph.minDegree G206 = 5 := by decide
example : SimpleGraph.maxDegree G206 = 5 := by decide
example : GraphCalc.indepNum G206 = 1 := by decide
example : GraphCalc.cliqueNum G206 = 6 := by decide
example : GraphCalc.dominationNumber G206 = 1 := by decide
example : GraphCalc.independentDominationNumber G206 = 1 := by decide
example : GraphCalc.slaterNumber G206 = 1 := by decide
example : GraphCalc.annihilationNumber G206 = 3 := by decide
example : GraphCalc.zeroForcingNumber G206 = 5 := by decide
example : GraphCalc.totalZeroForcingNumber G206 = 5 := by decide
example : GraphCalc.connectedZeroForcingNumber G206 = 5 := by decide
example : GraphCalc.vertexCoverNumber G206 = 5 := by decide
example : GraphCalc.totalDominationNumber G206 = 2 := by decide
example : GraphCalc.edgeCoverNumber G206 = 3 := by decide
example : GraphCalc.subTotalDominationNumber G206 = 2 := by decide
example : GraphCalc.romanDominationNumber G206 = 2 := by decide
example : GraphCalc.doubleRomanDominationNumber G206 = 3 := by decide
example : GraphCalc.radius G206 = 1 := by decide
example : GraphCalc.IsConnectedClass G206 := by decide
example : ¬ GraphCalc.IsTreeClass G206 := by decide
example : GraphCalc.IsClawFreeClass G206 := by decide
example : GraphCalc.IsCographClass G206 := by decide
example : GraphCalc.IsRegularClass G206 := by decide
example : ¬ GraphCalc.IsCubicClass G206 := by decide
example : ¬ GraphCalc.IsSubcubicClass G206 := by decide
example : ¬ GraphCalc.IsEulerianClass G206 := by decide
example : ¬ GraphCalc.IsTriangleFreeClass G206 := by decide
example : ¬ GraphCalc.IsK4FreeClass G206 := by decide
example : GraphCalc.IsNontrivialClass G206 := by decide
example : ¬ GraphCalc.IsBipartiteClass G206 := by decide

