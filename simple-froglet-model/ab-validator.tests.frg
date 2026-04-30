#lang forge/froglet

open "ab-validator.frg"

test suite for wellformed_degree {
    // AI/ML, Architecture, Data, Design, Security, Visual

    example sashasDegree is {wellformed_degree_AB} for {
        Boolean = `T
        True = `T
        Degree = `d
        oldDegreeAB = `d

        `d.calc = `T

        // The visualization can't work if the atom name is the same as sig, so CS instead of CSCI
        Department = `CS + `APMA + `MATH + `ECON + `HIST + `POLS + `CLAS + `UNIV + `PHIL + `IAPA + `LANG + `CLPS
        CSCI = `CS

        Course = `ECON0110 + `MATH0100 + `LANG0710 + `POLS0110 +
                `ECON1110 + `IAPA1502 + `HIST0234 + `CLPS0220 +
                `ECON1620 + `ECON1210 + `ECON1050 + `CSCI0150 + `POLS1455 +
                `ECON1629 + `ECON1480 + `CSCI0200 + `CLAS1770 + `UNIV0123 +
                `ECON1710 + `APMA1650 + `MATH0540 + `CSCI1970A +
                `CSCI0300 + `CSCI1805 + `CSCI1970B + `PHIL1560 + `unknown1 + `unknown2

        Intermediate = `FouI + `MatI + `SysI
        FoundationsI = `FouI
        MathematicsI = `MatI
        SystemsI = `SysI

        PathwayCourseType = `CorT + `RelT + `IntT
        CoreT = `CorT
        RelatedT = `RelT
        IntermediateT = `IntT

        PathwayName = `AiP + `DeP + `SoP + `DaP + `SeP + `CBP + `ViP + `CAP + `ThP + `SyP
        AiMlP = `AiP 
        DesignP = `DeP
        SoftwareP = `SoP
        DataP = `DaP
        SecurityP = `SeP 
        ComputationalBiologyP = `CBP
        VisualComputingP = `ViP 
        ComputingArchitectureP = `CAP
        TheoryP = `ThP 
        SystemsP = `SyP

        // Courses to pathway mapping
        
        `ECON0110.dept = `ECON
        no `ECON0110.pathway
        
        `MATH0100.dept = `MATH
        no `MATH0100.pathway
        
        `LANG0710.dept = `LANG
        no `LANG0710.pathway
        
        `POLS0110.dept = `POLS
        no `POLS0110.pathway
        
        `ECON1110.dept = `ECON
        no `ECON1110.pathway
        
        `IAPA1502.dept = `IAPA
        no `IAPA1502.pathway
        
        `HIST0234.dept = `HIST
        no `HIST0234.pathway
        
        `CLPS0220.dept = `CLPS
        no `CLPS0220.pathway
        
        `ECON1620.dept = `ECON
        no `ECON1620.pathway
        
        `ECON1210.dept = `ECON
        no `ECON1210.pathway
        
        `ECON1050.dept = `ECON
        no `ECON1050.pathway
        
        `CSCI0150.dept = `CS
        no `CSCI0150.pathway
        
        `POLS1455.dept = `POLS
        no `POLS1455.pathway
        
        `ECON1629.dept = `ECON
        no `ECON1629.pathway
        
        `ECON1480.dept = `ECON
        no `ECON1480.pathway
        
        `CSCI0200.dept = `CS
        no `CSCI0200.pathway
        `CSCI0200.finishIntro = `T
        
        `CLAS1770.dept = `CLAS
        no `CLAS1770.pathway
        
        `UNIV0123.dept = `UNIV
        no `UNIV0123.pathway
        
        `ECON1710.dept = `ECON
        no `ECON1710.pathway
        
        `APMA1650.dept = `APMA
        `APMA1650.pathway = `AiP -> `IntT + `CBP -> `IntT + `DaP -> `IntT + `DeP -> `IntT + `SeP -> `IntT + `ThP -> `IntT
        
        `MATH0540.dept = `MATH
        `MATH0540.pathway = `AiP -> `IntT + `DaP -> `IntT + `ThP -> `IntT + `ViP -> `IntT
        
        `CSCI1970A.dept = `CS
        no `CSCI1970A.pathway
        
        `CSCI0300.dept = `CS
        `CSCI0300.pathway = `DaP -> `IntT + `DeP -> `IntT + `SeP -> `IntT + `SoP -> `IntT + `SyP -> `IntT + `ViP -> `IntT
        
        `CSCI1805.dept = `CS
        `CSCI1805.pathway = `SeP -> `RelT
        
        `CSCI1970B.dept = `CS
        no `CSCI1970B.pathway
        
        `PHIL1560.dept = `PHIL
        no `PHIL1560.pathway

        artsy = `CSCI1805 -> `T
        
        upperDiv = `ECON1110 -> `T + `IAPA1502 -> `T + `ECON1620 -> `T + `ECON1210 -> `T + `ECON1050 -> `T + `POLS1455 -> `T + `ECON1629 -> `T + `ECON1480 -> `T + `CLAS1770 -> `T + `ECON1710 -> `T + `APMA1650 -> `T + `CSCI1805 -> `T + `PHIL1560 -> `T + `unknown1 -> `T
        
        intermediateType = `CSCI0300 -> `SysI + `APMA1650 -> `MatI + `MATH0540 -> `MatI
    }
}