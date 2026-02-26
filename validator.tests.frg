#lang forge/froglet

open "validator.frg"

test suite for wellformed_course {

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

    //Minimal inputs for 2 courses
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

    //Two courses, where one is a prereq of the other
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
    //A course can't be a prereq of itself
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

    //2 courses can't be prereqs of each other
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

    //We can't have a cycle of prereqs
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

    //We can't have an intermediate course also be a core course
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

    //We can't have an intermediate course also be a related course
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

    //We can't have an intermediate course with no intermediate type
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

    //We can't have a course that finishes the intro and is also upper division
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

    //There's no course that finishes the intro and is an intermediate
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

    //There's no course that finishes the intro without being CSCI
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

    //There's no course that can finish the intro while being in a pathway
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
    //This predicate can run
    wc_sat: assert wellformed_course is sat
    //Courses can't be their own prereq
    wc_noSelfPrereq: assert {some c: Course | {
        c.prereq = c and wellformed_course}} is unsat
    //Courses can't be mutual prereqs
    wc_noCircularPrereq: assert {some disj c1, c2: Course | 
        c1.prereq = c2 and c2.prereq = c1 and wellformed_course} is unsat
    //Courses can't have themselves in their prereq mapping
    wc_noIndirectPrereq: assert {some disj c1, c2, c3: Course | 
        c1.prereq = c2 and c2.prereq = c3 and c3.prereq = c1 and wellformed_course} is unsat
    //Courses can't be core or related courses in pathway if intermediate course
    wc_noCoreOrRelatedIfIntermediate: assert {some c: Course | {
        some c.intermediateType  
        some pn: PathwayName | {
            c.pathway[pn] = CoreT or c.pathway[pn] = RelatedT
        }
        wellformed_course
    }} is unsat
    //Courses must be intermediate and in an intermediate pathway
    wc_notInIntermediatePathwayNotIntermediate: assert {some c: Course | {
        some pn: PathwayName | {
            c.pathway[pn] = IntermediateT and no c.intermediateType
        }
        wellformed_course
    }} is unsat
    //Only certain courses in very specific parameters get to finish the intro
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
    //We can put in a fully unrelated course into the degree and that is ok
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
    //No degree is valid
    example fc_noDegree is {finished_calc} for {
        Boolean = `T
        True = `T
        no Degree
    }
    //Finishing calc finishes calc
    example fc_finishTrue is {finished_calc} for {
        Boolean = `T
        True = `T
        Degree = `d

        `d.calc = `T
    }

    //assert
    //This pred works
    fc_sat: assert finished_calc is sat
    //Any degree with calc finished is enough
    fc_finishCalcTrueSuff: assert {some d: Degree | d.calc = True} is sufficient for finished_calc
    //Any degree is enough (because the sig requires finishing calc)
    fc_anyDegreeSuff: assert {some d: Degree | some d} is sufficient for finished_calc
    //Not finishing calc is impossible
    fc_finishCalcFalseUnsart: assert {some d: Degree | no d.calc and finished_calc} is unsat 
}

test suite for valid_intro_oSCB {
    //positive
    //This is valid for the empty case
    example vioSCB_noDegree is {valid_intro_oSCB} for {
        Boolean = `T
        True = `T
        no Degree
    }

    //[Please notice how long this test case is. This is unreasonable.]
    //We can have two generic intro courses that work
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

    //We can have two generic courses that work, these courses do not need to be wellformed
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
    //We can't have intro courses that aren't CSCI
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

    //We can't have intro courses that don't finish the intro sequence
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

    //We can't have only one course complete the intro
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

    //We can't have the intro courses appearing elsewhere in the degree
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
    //the predicate can run
    vioSCB_sat: assert valid_intro_oSCB is sat
    //there must be at least 2 courses
    vioSCB_unsatOneCourse: assert valid_intro_oSCB is unsat for exactly 1 Course
    //the courses must be in CSCI
    vioSCB_notWrongDept: assert {
        some disj c1, c2: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c2
            c1.dept != CSCI or c2.dept != CSCI
            valid_intro_oSCB
        }
    } is unsat
    //the courses must be distinct from each other
    vioSCB_notSameCourse: assert {
        some c1: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c1
            valid_intro_oSCB
        }
    } is unsat
    //the course must finish the intro
    vioSCB_notNotFinish: assert {
        some disj c1, c2: Course, d: Degree | {
            d.intro1 = c1
            d.intro2 = c2
            no c2.finishIntro or no c1.finishIntro
            valid_intro_oSCB
        }
    } is unsat
    //the courses can't be elsewhere in the degree
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
    //the pred must pass
    vi_sat: assert valid_intermediate is sat
    //the pred requires 5+ courses
    vi_not4OrFewerCourses: assert valid_intermediate is unsat for exactly 4 Course, 1 Degree
    //courses cannot overlap with each other
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
    //all of the intermediate courses have a intermediate type
    vi_necAllCoursesAreIntermediate: assert {
        all c: Course | some c.intermediateType
    } is necessary for valid_intermediate for exactly 5 Course, 1 Degree
    //the courses must be distributed across categories
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
    //none of the categories can be missing
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
    //the pred can run
    dp_sat: assert distinct_pathways is sat
    //there must be at least two pathways
    dp_notLessThanTwo: assert distinct_pathways is unsat for exactly 1 PathwayRequirements
    //the pathways must be distinct
    dp_notSamePathway: assert {
        some disj pr1, pr2: PathwayRequirements, pn: PathwayName, d: Degree | {
            d.pathway1 = pr1 and d.pathway2 = pr2
            pr1.name = pn
            pr2.name = pn
        } and
        distinct_pathways
    } is unsat
    //the pathways cannot have overlapping courses
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
    //the pred runs
    apv_sat: assert all_pathways_valid is sat
    //the core courses must have a core type
    apv_notCoreCourseNotCoreType: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.core1 = c and pr.name = pn
            c.pathway[pn] != CoreT
        } and 
        all_pathways_valid
    } is unsat
    //the core or related must be of that type
    apv_notCoreOrRelatedIsNotTyped: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.coreOrRelated = c and pr.name = pn
            c.pathway[pn] != CoreT and c.pathway[pn] != RelatedT
        } and
        all_pathways_valid
    } is unsat
    //the intermediate course must be of that type
    apv_noIntCourseHasNotIntType: assert {
        some c: Course, pr: PathwayRequirements, pn: PathwayName | {
            pr.intermediate1 = c and pr.name = pn
            c.pathway[pn] != IntermediateT
        } and 
        all_pathways_valid
    } is unsat
    //courses cannot repeat within the pathway
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
    //the pred runs
    vtp_sat: assert valid_two_pathways is sat
}

test suite for valid_upper_level {
    //the pred runs
    vul_sat: assert valid_upper_level is sat
    //the upper level course can't be in the pathway
    vul_notInPathway: assert {
        some d: Degree | {
            some d.upperLevel.pathway[d.pathway1.name] or
            some d.upperLevel.pathway[d.pathway1.name]
        } and 
        valid_upper_level 
    } is unsat
    //the upper level course must be CSCI
    vul_neccUpperLevelCSCI: assert {
        some d: Degree | {
            some d.upperLevel.upperDiv
            d.upperLevel.dept = CSCI 
        }
    } is necessary for valid_upper_level for exactly 1 Degree
    //the courses cannot overlap within the degree
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
    //the pred runs
    ve_sat: assert valid_electives is sat
    //there must be 3 distinct courses across the electives
    ve_necc3CourseInDegree: assert {
        some disj c1, c2, c3: Course, d: Degree | {
            d.elec1 = c1
            d.elec2 = c2
            d.elec3 = c3
        }
    } is necessary for valid_electives for exactly 1 Degree
    //the electives cannot overlap
    ve_noElecOverlap: assert {
        some d: Degree | {
            d.elec1 = d.elec2 or
            d.elec1 = d.elec3 or
            d.elec2 = d.elec3
        } and
        valid_electives
    } is unsat
    //two of the electives must be upper division
    ve_neccTwoUpperDiv: assert {
        some d: Degree | {
            some d.elec1.upperDiv
            some d.elec2.upperDiv
        }
    } is necessary for valid_electives for exactly 1 Degree
    //the courses cannot be elsewhere in the degree
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
    //the pred can run
    wd_sat: assert wellformed_degree is sat

    // wd_sat_complex: assert wellformed_degree is sat for exactly 1 Degree, 18 Course
    
    //there are not more than two courses that finish the intro 
    //(there's only 2 courses that ever do this)
    wd_notMoreThanTwoFinIntro: assert {
        #{c: Course | some c.finishIntro} > 2 and
        wellformed_degree
    } is unsat for exactly 1 Degree
    
    //there are not more than 4 artsy courses counted in the degree
    wd_notMoreThanFourArtsy: assert {
        #{c: Course | some c.artsy} > 4 and
        wellformed_degree
    } is unsat for exactly 1 Degree

    //this all works on a real completed degree path
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

