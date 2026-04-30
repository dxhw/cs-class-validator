#lang forge/froglet

open "validator.frg"


test suite for wellformed_degree {
    example kathysActualDegree_withExtraCourse is {wellformed_degree} for {
        Boolean = `True
        True = `True
        Degree = `d
        oldDegreeSCB = `d

        `d.calc = `True
    

        // The visualization can't work if the atom name is the same as sig, so CS instead of CSCI
        Department = `CS + `APMA + `MATH + `CLPS
        CSCI = `CS

        Course = `CSCI0170 + `CSCI0200 + `CSCI0300 + `APMA1650 + `MATH0520 + `CSCI1952X + `CSCI1411 +
                `CSCI2952S + `CSCI1300 + `CSCI1970A + `CSCI0220 + `CSCI0320 + `CSCI1970B + 
                `CSCI1953A + `CSCI1710 + `Unknown1

        Intermediate = `FouI + `MatI + `SysI
        FoundationsI = `FouI
        MathematicsI = `MatI
        SystemsI = `SysI

        PathwayCourseType = `CorT + `RelT + `IntT
        CoreT = `CorT
        RelatedT = `RelT
        IntermediateT = `IntT

        PathwayName = `AiP + `DeP + `SoP + `DaP + `SeP + `CBP + `ViP + `CAP + `TruehP + `SyP
        AiMlP = `AiP 
        DesignP = `DeP
        SoftwareP = `SoP
        DataP = `DaP
        SecurityP = `SeP 
        ComputationalBiologyP = `CBP
        VisualComputingP = `ViP 
        ComputingArchitectureP = `CAP
        TheoryP = `TruehP 
        SystemsP = `SyP
        
        `CSCI0170.dept = `CS
        no `CSCI0170.pathway

        `d.intro1 = `CSCI0170
        
        `CSCI0200.dept = `CS
        no `CSCI0200.pathway
        `CSCI0200.finishIntro = `True

        `CSCI0300.dept = `CS
        `CSCI0300.pathway = `DaP -> `IntT + `DeP -> `IntT + `SeP -> `IntT + `SoP -> `IntT + `SyP -> `IntT + `ViP -> `IntT

        `APMA1650.dept = `APMA
        `APMA1650.pathway = `AiP -> `IntT + `CBP -> `IntT + `DaP -> `IntT + `DeP -> `IntT + `SeP -> `IntT + `TruehP -> `IntT

        `MATH0520.dept = `MATH
        `MATH0520.pathway = `AiP -> `IntT + `DaP -> `IntT + `TruehP -> `IntT + `ViP -> `IntT

        `CSCI1952X.dept = `CS
        no `CSCI1952X.pathway

        `CSCI1411.dept = `CS
        `CSCI1411.pathway = `AiP -> `CorT

        `CSCI2952S.dept = `CS
        no `CSCI2952S.pathway

        `CSCI1300.dept = `CS
        `CSCI1300.pathway = `DeP -> `CorT + `ViP -> `CorT

        `CSCI1970A.dept = `CS
        no `CSCI1970A.pathway

        `CSCI0220.dept = `CS
        `CSCI0220.pathway = `CBP -> `IntT + `SeP -> `IntT + `SoP -> `IntT + `SyP -> `IntT

        `CSCI0320.dept = `CS
        `CSCI0320.pathway = `DaP -> `IntT + `DeP -> `IntT + `SoP -> `IntT + `SyP -> `IntT + `ViP -> `IntT

        `CSCI1970B.dept = `CS
        no `CSCI1970B.pathway

        `CSCI1953A.dept = `CS
        `CSCI1953A.pathway = `DeP -> `RelT + `SeP -> `RelT

        `CSCI1710.dept = `CS
        `CSCI1710.pathway = `SeP -> `RelT + `SoP -> `CorT + `SyP -> `RelT + `TruehP -> `RelT

        artsy = `CSCI2952S -> `True + `CSCI1952X -> `True + `CSCI1953A -> `True
        
        upperDiv = `APMA1650 -> `True + `CSCI1952X -> `True + `CSCI1411 -> `True + `CSCI2952S -> `True + `CSCI1300 -> `True + `CSCI1970A -> `True + `CSCI1970B -> `True + `CSCI1953A -> `True + `CSCI1710 -> `True
        
        intermediateType = `CSCI0300 -> `SysI + `APMA1650 -> `MatI + `MATH0520 -> `MatI + `CSCI0220 -> `FouI + `CSCI0320 -> `SysI
    }
}