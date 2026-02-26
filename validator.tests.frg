#lang forge/froglet

open "validator.frg"

test suite for wellformed_course {

    // prereq: lone Course, // this is not realistic, but this allows for reachability in a way that's useful
    // dept: one Department, //CSCI, MATH, ...
    // finishIntro: lone Boolean, //Tells us if this course is 0190 or 0200
    // intermediateType: lone Intermediate, //Is this course an intermediate of some type?
    // pathway: pfunc PathwayName -> PathwayCourseType, //Given some pathway, where does this course live in the pathway?
    // upperDiv: lone Boolean, //Is this course 1000+?
    // artsy: lone Boolean, //Is this course arts/humanities/social sciences?

    // //This is circular but it lets us do gimmicky things with counting
    // degree: one Degree

    //positive
    //We can exist without courses
    example wc_NoCourse is {wellformed_course} for {
        no Course
    }

    //Minimal inputs for 1 course
    example wc_OneCourse is {wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
    }

    example wc_TwoCourse is {wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `MATH
        `c2.degree = `d
    }

    example wc_TwoCoursePrereq is {wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d
        `c1.prereq = `c2

        `c2.dept = `MATH
        `c2.degree = `d
    }

    //negative

    example wc_SelfPrereq is {not wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d
        `c1.prereq = `c1
    }

    example wc_CircularPrereq is {not wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d
        `c1.prereq = `c2

        `c2.dept = `MATH
        `c2.degree = `d
        `c2.prereq = `c1
    }


    example wc_IndirectSelfPrereq is {not wellformed_course} for { 
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI

        Course = `c1 + `c2 + `c3

        `c1.dept = `CSCI
        `c1.degree = `d
        `c1.prereq = `c2

        `c2.dept = `MATH
        `c2.degree = `d
        `c2.prereq = `c3

        `c3.dept = `CSCI
        `c3.degree = `d
        `c3.prereq = `c1
    }

    example wc_notInterAndCore is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.intermediateType = `FouI
        `c.pathway = `SyP -> `CorT
    }

    example wc_notInterAndRelated is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.intermediateType = `FouI
        `c.pathway = `SyP -> `RelT
    }

    example wc_notIntermediateNoIntType is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.pathway = `SyP -> `IntT
    }

    example wc_notFinishIntroUpperDiv is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.finishIntro = `T
        `c.upperDiv = `T
    }

    example wc_notFinishIntroIntermediate is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.finishIntro = `T
        `c.intermediateType = `FouI
    }

    example wc_notFinishIntroNotCS is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `MATH
        `c.degree = `d
        `c.finishIntro = `T
    }

    example wc_notFinishIntroNotPathway is {not wellformed_course} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI
        
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

        Course = `c

        `c.dept = `CSCI
        `c.degree = `d
        `c.finishIntro = `T
        `c.pathway = `AiP -> `CorT
    }

    //asserts
    wc_sat: assert wellformed_course is sat

    wc_noSelfPrereq: assert {some c: Course | {
        c.prereq = c and wellformed_course}} is unsat

    wc_noCircularPrereq: assert {some disj c1, c2: Course | 
        c1.prereq = c2 and c2.prereq = c1 and wellformed_course} is unsat

    wc_noIndirectPrereq: assert {some disj c1, c2, c3: Course | 
        c1.prereq = c2 and c2.prereq = c3 and c3.prereq = c1 and wellformed_course} is unsat

    wc_noCoreOrRelatedIfIntermediate: assert {some c: Course | {
        some c.intermediateType  
        some pn: PathwayName | {
            c.pathway[pn] = CoreT or c.pathway[pn] = RelatedT
        }
        wellformed_course
    }} is unsat

    wc_notInIntermediatePathwayNotIntermediate: assert {some c: Course | {
        some pn: PathwayName | {
            c.pathway[pn] = IntermediateT and no c.intermediateType
        }
        wellformed_course
    }} is unsat

    wc_finishIntroOnlyCertainCases: assert {some c: Course | {
        c.finishIntro = True 
        (some pn: PathwayName | {
            some c.pathway[pn]
        } or 
        some c.upperDiv or
        some c.intermediateType or
        c.dept != CSCI)
        wellformed_course
    }} is unsat

    wc_unrelatedCourseOK: assert {some c: Course, d: Degree | {
        no c.prereq
        c.dept != CSCI
        no c.finishIntro
        no c.intermediateType
        all pn: PathwayName | {
            no c.pathway[pn]
        }
        no c.upperDiv
        no c.artsy
        c.degree = d
    }} is sufficient for wellformed_course for 1 Course
}

test suite for finished_calc {
    //positive
    example fc_noDegree is {finished_calc} for {
        Boolean = `T
        True = `T
        no Degree
    }

    example fc_finishTrue is {finished_calc} for {
        Boolean = `T
        True = `T
        Degree = `d

        `d.calc = `T
    }

    //assert
    fc_sat: assert finished_calc is sat
    fc_finishCalcTrueSuff: assert {some d: Degree | d.calc = True} is sufficient for finished_calc
    fc_anyDegreeSuff: assert {some d: Degree | some d} is sufficient for finished_calc
    fc_finishCalcFalseUnsart: assert {some d: Degree | no d.calc and finished_calc} is unsat 
}

test suite for valid_intro_oSCB {
    //positive
    example vioSCB_noDegree is {valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        no Degree
    }

    //[Please notice how long this test case is. This is unreasonable.]
    example vioSCB_twoIntro is {valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI

        Course = `c1 + `c2 + `c3

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
        
        PathwayRequirements = `pr

        `pr.name = `AiP
        `pr.core1 = `c3
        `pr.coreOrRelated = `c3
        `pr.intermediate1 = `c3

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `CSCI
        `c2.degree = `d
        `c2.finishIntro = `T

        `c3.dept = `MATH
        `c3.degree = `d

        `d.intro1 = `c1
        `d.intro2 = `c2

        `d.inter1 = `c3
        `d.inter2 = `c3
        `d.inter3 = `c3
        `d.inter4 = `c3
        `d.inter5 = `c3

        `d.pathway1 = `pr
        `d.pathway2 = `pr

        `d.upperLevel = `c3
        `d.elec1 = `c3
        `d.elec2 = `c3
        `d.elec3 = `c3
    }

    example vioSCB_twoIntroNotWFCourse is {valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d

        Department = `CSCI + `MATH
        CSCI = `CSCI

        Course = `c1 + `c2 + `c3

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
        
        PathwayRequirements = `pr

        `pr.name = `AiP
        `pr.core1 = `c3
        `pr.coreOrRelated = `c3
        `pr.intermediate1 = `c3

        `c1.dept = `CSCI
        `c1.degree = `d
        `c1.prereq = `c1

        `c2.dept = `CSCI
        `c2.degree = `d
        `c2.finishIntro = `T

        `c3.dept = `MATH
        `c3.degree = `d

        `d.intro1 = `c1
        `d.intro2 = `c2

        `d.inter1 = `c3
        `d.inter2 = `c3
        `d.inter3 = `c3
        `d.inter4 = `c3
        `d.inter5 = `c3

        `d.pathway1 = `pr
        `d.pathway2 = `pr

        `d.upperLevel = `c3
        `d.elec1 = `c3
        `d.elec2 = `c3
        `d.elec3 = `c3
    }

    //negative
    example vioSCB_notCSCI is {not valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `MATH
        `c2.degree = `d
        `c2.finishIntro = `T

        `d.intro1 = `c1
        `d.intro2 = `c2
    }

    example vioSCB_notFinishIntro is {not valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `CSCI
        `c2.degree = `d

        `d.intro1 = `c1
        `d.intro2 = `c2
    }

    example vioSCB_notOneCourse is {not valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `CSCI
        `c2.degree = `d

        `d.intro1 = `c1
        `d.intro2 = `c1
    }

    example vioSCB_notDuplicatedInDegree is {not valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        Degree = `d
        Department = `CSCI + `MATH
        CSCI = `CSCI
        Course = `c1 + `c2

        `c1.dept = `CSCI
        `c1.degree = `d

        `c2.dept = `CSCI
        `c2.degree = `d

        `d.intro1 = `c1
        `d.intro2 = `c2

        `d.elec1 = `c1
    }

    //assert
    vioSCB_sat: assert valid_intro_oSCB is sat
    
    vioSCB_unsatOneCourse: assert valid_intro_oSCB is unsat for exactly 1 Course
    
    vioSCB_notWrongDept: assert {
        some disj c1, c2: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c2
            c1.dept != CSCI or c2.dept != CSCI
            valid_intro_oSCB
        }
    } is unsat

    vioSCB_notSameCourse: assert {
        some c1: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c1
            valid_intro_oSCB
        }
    } is unsat


    vioSCB_notNotFinish: assert {
        some disj c1, c2: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c2
            no c2.finishIntro or no c2.finishIntro
            valid_intro_oSCB
        }
    } is unsat

    vioSCB_notElsewhereInDeg: assert {
        some disj c1, c2: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c2

            some pr: PathwayRequirements | {
                (d.pathway1 = pr or d.pathway2 = pr)
                pr.core1 = c1 or
                pr.coreOrRelated = c1 or
                pr.intermediate1 = c1 or
                pr.intermediate2 = c1 or
                pr.intermediate3 = c1 or

                pr.core1 = c2 or
                pr.coreOrRelated = c2 or
                pr.intermediate1 = c2 or
                pr.intermediate2 = c2 or
                pr.intermediate3 = c2
            } or 
            
            (d.inter1 = c1 or 
            d.inter2  = c1 or 
            d.inter3 = c1 or 
            d.inter4 = c1 or 
            d.inter5 = c1 or 
            d.upperLevel = c1 or 
            d.elec1 = c1 or 
            d.elec2 = c1 or 
            d.elec3 = c1 or

            d.inter1 = c2 or 
            d.inter2  = c2 or 
            d.inter3 = c2 or 
            d.inter4 = c2 or 
            d.inter5 = c2 or 
            d.upperLevel = c2 or 
            d.elec1 = c2 or 
            d.elec2 = c2 or 
            d.elec3 = c2)

            valid_intro_oSCB
        }
    } is unsat
}

test suite for valid_intermediate {
    //assert because it is not worth writing those examples
    vi_sat: assert valid_intermediate is sat
    
    vi_not4OrFewerCourses: assert valid_intermediate is unsat for exactly 4 Course, 1 Degree
    
    vi_noOverlappingCourses: assert {
        some d: Degree | {
            d.inter1 = d.inter2 or
            d.inter1 = d.inter3 or 
            d.inter1 = d.inter4 or
            d.inter1 = d.inter5 or

            d.inter2 = d.inter3 or
            d.inter2 = d.inter4 or 
            d.inter2 = d.inter5 or

            d.inter3 = d.inter4 or
            d.inter3 = d.inter5 or

            d.inter4 = d.inter5

            valid_intermediate
        }
    } is unsat

    vi_necAllCoursesAreIntermediate: assert {
        all c: Course | some c.intermediateType
    } is necessary for valid_intermediate for exactly 5 Course, 1 Degree
    
    vi_necIntermediateCategoryDist: assert {
        some disj c1, c2, c3, c4, c5: Course, d: Degree | (
            d.inter1 = c1 and
            d.inter2 = c2 and
            d.inter3 = c3 and
            d.inter4 = c4 and
            d.inter5 = c5) implies {
            c1.intermediateType = FoundationsI
            c2.intermediateType = MathematicsI
            c3.intermediateType = SystemsI
        }
    } is necessary for valid_intermediate for exactly 5 Course, 1 Degree

    vi_notMissingIntermediateType: assert {
        some disj c1, c2, c3, c4, c5: Course, d: Degree | (
            d.inter1 = c1 and
            d.inter2 = c2 and
            d.inter3 = c3 and
            d.inter4 = c4 and
            d.inter5 = c5) implies {
                //not missing Foundation
                (c1.intermediateType != FoundationsI and 
                c2.intermediateType != FoundationsI and
                c3.intermediateType != FoundationsI and 
                c4.intermediateType != FoundationsI and
                c5.intermediateType != FoundationsI) or
                //not missing Mathematics
                (c1.intermediateType != MathematicsI and 
                c2.intermediateType != MathematicsI and
                c3.intermediateType != MathematicsI and 
                c4.intermediateType != MathematicsI and
                c5.intermediateType != MathematicsI) or
                //not missing Systems
                (c1.intermediateType != SystemsI and 
                c2.intermediateType != SystemsI and
                c3.intermediateType != SystemsI and 
                c4.intermediateType != SystemsI and
                c5.intermediateType != SystemsI)
        } and
        valid_intermediate
    } is unsat 
}

test suite for distinct_pathways {
    dp_sat: assert distinct_pathways is sat
    dp_notLessThanTwo: assert distinct_pathways is unsat for exactly 1 PathwayRequirements
    dp_notSamePathway: assert {
        some disj pr1, pr2: PathwayRequirements, pn: PathwayName, d: Degree | {
            d.pathway1 = pr1 and d.pathway2 = pr2
            pr1.name = pn
            pr2.name = pn
        } and
        distinct_pathways
    } is unsat
    dp_notOverlappingCR: assert {
        some disj c1: Course, d: Degree, pr1, pr2: PathwayRequirements | {
            d.pathway1 = pr1 and d.pathway2 = pr2
            (pr1.core1 = c1 and pr2.core1 = c1) or
            (pr1.core1 = c1 and pr2.coreOrRelated = c1) or
            (pr1.coreOrRelated = c1 and pr2.core1 = c1) or
            (pr1.coreOrRelated = c1 and pr2.coreOrRelated = c1)
        } and
        distinct_pathways
    } is unsat
}

test suite for all_pathways_valid {
    apv_sat: assert all_pathways_valid is sat

    apv_notCoreCourseNotCoreType: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.core1 = c and pr.name = pn
            c.pathway[pn] != CoreT
        } and 
        all_pathways_valid
    } is unsat

    apv_notCoreOrRelatedIsNotTyped: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.coreOrRelated = c and pr.name = pn
            c.pathway[pn] != CoreT and c.pathway[pn] != RelatedT
        } and
        all_pathways_valid
    } is unsat

    apv_noIntCourseHasNotIntType: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.intermediate1 = c and pr.name = pn
            c.pathway[pn] != IntermediateT
        } and 
        all_pathways_valid
    } is unsat

    //TODO: pathway specific asserts

    apv_noOverlapsInPathway: assert {
        some pr: PathwayRequirements | {
            pr.core1 = pr.coreOrRelated or 
            pr.core1 = pr.intermediate1 or
            pr.core1 = pr.intermediate2 or
            pr.core1 = pr.intermediate3 or 

            pr.coreOrRelated = pr.intermediate1 or
            pr.coreOrRelated = pr.intermediate2 or
            pr.coreOrRelated = pr.intermediate3 or

            pr.intermediate1 = pr.intermediate2 or
            pr.intermediate1 = pr.intermediate3 
        } and 
        all_pathways_valid
    } is unsat
}

test suite for valid_two_pathways {
    vtp_sat: assert valid_two_pathways is sat
}

test suite for valid_upper_level {
    vul_sat: assert valid_upper_level is sat
    
    vul_notInPathway: assert {
        some d: Degree | {
            some d.upperLevel.pathway[d.pathway1.name] or
            some d.upperLevel.pathway[d.pathway1.name]
        } and 
        valid_upper_level 
    } is unsat

    vul_neccUpperLevelCSCI: assert {
        some d: Degree | {
            some d.upperLevel.upperDiv
            d.upperLevel.dept = CSCI 
        }
    } is necessary for valid_upper_level for exactly 1 Degree

    vul_notOverlappingInDegree: assert {
        some d: Degree | {
            d.intro1 = d.upperLevel or
            d.intro2 = d.upperLevel or
            d.inter1 = d.upperLevel or
            d.inter2 = d.upperLevel or
            d.inter3 = d.upperLevel or
            d.inter4 = d.upperLevel or
            d.inter5 = d.upperLevel or
            d.elec1 = d.upperLevel or
            d.elec2 = d.upperLevel or
            d.elec3 = d.upperLevel
        } and 
        valid_upper_level
    } is unsat
}

test suite for valid_electives {
    ve_sat: assert valid_electives is sat
    
    ve_necc3CourseInDegree: assert {
        some disj c1, c2, c3: Course, d: Degree | {
            d.elec1 = c1
            d.elec2 = c2
            d.elec3 = c3
        }
    } is necessary for valid_electives for exactly 1 Degree

    ve_noElecOverlap: assert {
        some d: Degree | {
            d.elec1 = d.elec2 or
            d.elec1 = d.elec3 or
            d.elec2 = d.elec3
        } and
        valid_electives
    } is unsat

    ve_neccTwoUpperDiv: assert {
        some d: Degree | {
            some d.elec1.upperDiv
            some d.elec2.upperDiv
        }
    } is necessary for valid_electives for exactly 1 Degree

    ve_notElsewhereInDegree: assert {
        some c1: Course, d: Degree | {
            (d.elec1 = c1 or d.elec2 = c1 or d.elec3 = c1) and
            
            (some pr: PathwayRequirements | {
                (d.pathway1 = pr or d.pathway2 = pr)
                pr.core1 = c1 or
                pr.coreOrRelated = c1 or
                pr.intermediate1 = c1 or
                pr.intermediate2 = c1 or
                pr.intermediate3 = c1
            } or 
            
            (d.intro1 = c1 or
            d.intro2 = c1 or
            d.inter1 = c1 or 
            d.inter2  = c1 or 
            d.inter3 = c1 or 
            d.inter4 = c1 or 
            d.inter5 = c1 or 
            d.upperLevel = c1))
        } and 
        valid_electives
    } is unsat
}

test suite for wellformed_degree {
    wd_sat: assert wellformed_degree is sat

    // wd_sat_complex: assert wellformed_degree is sat for exactly 1 Degree, 18 Course
    
    wd_notMoreThanTwoFinIntro: assert {
        #{c: Course | some c.finishIntro} > 2 and
        wellformed_degree
    } is unsat for exactly 1 Degree
    
    wd_notMoreThanFourArtsy: assert {
        #{c: Course | some c.artsy} > 4 and
        wellformed_degree
    } is unsat for exactly 1 Degree

    example dorensActualDegree is {wellformed_degree} for {
        Boolean = `T
        True = `T
        Degree = `d
        oldDegreeSCB = `d

        // The visualization can't work if the atom name is the same as sig, so CS instead of CSCI
        Department = `CS + `CLPS + `APMA + `MATH
        CSCI = `CS

        Course = `CSCI0190 + `CLPS1850 + `CSCI0300 + `APMA1650 + `MATH0520 + `CSCI1805 + `CSCI1470 +
                `CSCI2952S + `CSCI1650 + `CSCI1970A + `MATH1000 + `CSCI0320 + `CSCI1970B + 
                `CSCI1270 + `CSCI1710

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
        
        `CSCI0190.dept = `CS
        `CSCI0190.finishIntro = `T

        `CLPS1850.dept = `CLPS
        `CLPS1850.pathway = `AiP -> `RelT

        `CSCI0300.dept = `CS
        `CSCI0300.prereq = `CSCI0190
        `CSCI0300.pathway = `SeP -> `IntT

        `APMA1650.dept = `APMA
        `APMA1650.pathway = `AiP -> `IntT + `SeP -> `IntT

        `MATH0520.dept = `MATH
        `MATH0520.pathway = `AiP -> `IntT

        `CSCI1805.dept = `CS
        `CSCI1805.pathway = `SeP -> `RelT

        `CSCI1470.dept = `CS
        `CSCI1470.pathway = `AiP -> `CorT
        `CSCI1470.prereq = `CSCI0190

        `CSCI2952S.dept = `CS
        no `CSCI2952S.pathway

        `CSCI1650.dept = `CS
        `CSCI1650.pathway = `SeP -> `CorT
        `CSCI1650.prereq = `CSCI0300

        `CSCI1970A.dept = `CS
        no `CSCI1970A.pathway

        `MATH1000.dept = `MATH
        no `MATH1000.pathway
        `MATH1000.prereq = `MATH0520

        `CSCI0320.dept = `CS
        no `CSCI0320.pathway
        `CSCI0320.prereq = `CSCI0190

        `CSCI1970B.dept = `CS
        no `CSCI1970B.pathway

        `CSCI1270.dept = `CS
        no `CSCI1270.pathway
        `CSCI1270.prereq = `CSCI0300

        `CSCI1710.dept = `CS
        `CSCI1710.pathway = `SeP -> `RelT
        `CSCI1710.prereq = `CSCI0190

        artsy = `CSCI2952S -> `T + `CSCI1805 -> `T
        upperDiv = `CLPS1850 -> `T + `CSCI1805 -> `T + `CSCI1470 -> `T +
                `CSCI2952S -> `T + `CSCI1650 -> `T + `CSCI1970A -> `T +
                `CSCI1970B -> `T + `CSCI1270 -> `T + `CSCI1710 -> `T      
        intermediateType = `CSCI0300 -> `SysI + `APMA1650 -> `MatI + `MATH0520 -> `MatI +
                             `MATH1000 -> `FouI + `CSCI0320 -> `SysI

        // This is the set of pathways that is actually true
        // If we put all of the other pathways into this example,
        // The model could actually tell me different "versions"
        // of my degree (i.e., with different pathways)
        // It will likely return something like this if not given those

        // PathwayRequirements = `AiPathway + `SecurityPathway

        // `AiPathway.name = `AiP
        // `AiPathway.core1 = `CSCI1470
        // `AiPathway.coreOrRelated = `CLPS1850
        // `AiPathway.intermediate1 = `APMA1650
        // `AiPathway.intermediate2 = `MATH0520

        // `SecurityPathway.name = `SeP
        // `SecurityPathway.core1 = `CSCI1650
        // `SecurityPathway.coreOrRelated = `CSCI1805
        // `SecurityPathway.intermediate1 = `APMA1650
        // `SecurityPathway.intermediate2 = `CSCI0300

        `d.calc = `T
    }
}

