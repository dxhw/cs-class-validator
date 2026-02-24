#lang forge/froglet

//setup generics
abstract abstract sig Boolean {}
sig True extends Boolean {}

sig Degree {
    numCourses: one Int
}

abstract sig Intermediate {}
one sig FoundationsI, MathematicsI, SystemsI extends Intermediate

abstract sig PathwayName {}
one sig AiMlP, DesignP, SoftwareP, DataP, SecurityP, ComputationalBiologyP, VisualComputingP, 
        ComputingArchitectureP, TheoryP, SystemsP extends PathwayName

abstract sig PathwayCourseType {}
one sig CoreT, RelatedT, IntermediateT extends PathwayCourseType

abstract sig Department {}
one sig CSCI, MATH extends Department {}

sig Course {
    prereq: pfunc Int -> Course // c.prereq[0] = some course
    dept: one Department
    finishIntro: lone Boolean //19 or 200?
    intermediateType: lone Intermediate 
    pathway: pfunc PathwayName -> PathwayCourseType
    upperDiv: lone Boolean //1000+?
    artsy: lone Boolean //arts hums social sci
}

//old req
sig oldDegreeSCB extends Degree { 
    calc: one Boolean
    
    intro1: one Course //can be any CS
    intro2: one Course //0190 or 200

    inter1: one Course
    inter2: one Course
    inter3: one Course
    inter4: one Course
    inter5: one Course

    pathway1: one PathwayRequirements
    pathway2: one PathwayRequirements

    upperLevel: one Course //1000+ cs, not pathway
    elec1: one Course //any
    elec2: one Course //any
    elec3: one Course //any
}

sig PathwayRequirements {
    name: one PathwayName
    core1: one Course
    core2: lone Course
    related1: lone Course
    intermediate1: one Course
    intermediate2: lone Course
    intermediate3: lone Course
}

pred wellformed_course {
    all c: Course | not reachable[c, c, prereq]
}

pred valid_intro_oSCB {
    all d: oldDegreeSCB | {
        //intro 1 and 2 are disj
        d.intro1 != d.intro2
        //both cs courses
        d.intro1.dept = CSCI
        d.intro2.dept = CSCI
        //intro 2 is 19 or 200 (finished intro seq)
        some d.intro2.finishIntro
    }
}

pred valid_intermediate {
    all d: oldDegreeSCB | {
        //these courses cannot be the same
        all disj c1, c2, c3, c4, c5 | (            
            //all of these courses are Intermediates
            d.inter1 = c1
            d.inter2 = c2
            d.inter3 = c3
            d.inter4 = c4
            d.inter5 = c5) implies {

            c1.intermediateType = Intermediate
            c2.intermediateType = Intermediate
            c3.intermediateType = Intermediate
            c4.intermediateType = Intermediate
            c5.intermediateType = Intermediate

            //these courses are disjoint
            all_inter_disj

            //we only care that 3 of the courses are distributed across categories
            c1.intermediateType = FoundationsI
            c2.intermediateType = MathematicsI
            c3.intermediateType = SystemsI
        }
    }
}

pred all_inter_disj {
    //for all degrees...
    all d: oldDegreeSCB | {
        //for all courses...
        all disj c1, c2, c3, c4, c5 | (   
            //such that all of these courses are intermediates   

            //TODO: these courses must be in the course      
            c1.intermediateType = Intermediate
            c2.intermediateType = Intermediate
            c3.intermediateType = Intermediate
            c4.intermediateType = Intermediate
            c5.intermediateType = Intermediate) implies {
                //[this is annoying BUT it works?]
                //none of these courses are the same.
                c1 != c2
                c1 != c3
                c1 != c4
                c1 != c5

                c2 != c3
                c2 != c4
                c2 != c5

                c3 != c4
                c3 != c5

                c4 != c5
            }
    }
}


pred valid_pathways {
    all d: oldDegreeSCB | {
        //comparing pathways...
        all disj p1, p2: PathwayRequirements | 
        (p1 = d.pathway1
        p2 = d.pathway2) implies {
            //the two pathways are distinct
            p1.name != p2.name

            //the two pathways cannot share a core or related course
            p1.core1 != p2.core1
            p1.core1 != p2.core2
            p1.core1 != p2.related1

            p1.core2 != p2.core1
            p1.core2 != p2.core2
            p1.core2 != p2.related1

            p1.related1 != p2.core1
            p1.related1 != p2.core2
            p1.related1 != p2.related1

        }

        //within a pathway...
        all p1: PathwayRequirements | {
            //EVERYTHING is disjoint within the pathway
            // ("The core and related courses used in one pathway may not overlap with those used in the other")
            p1.core1 != p1.core2
            p1.core1 != p1.related1
            p1.core1 != p1.intermediate1
            p1.core1 != p1.intermediate2
            p1.core1 != p1.intermediate3

            p1.core2 != p1.related1
            p1.core2 != p1.intermediate1
            p1.core2 != p1.intermediate2
            p1.core2 != p1.intermediate3

            p1.related1 != p1.intermediate1
            p1.related1 != p1.intermediate2
            p1.related1 != p1.intermediate3

            p1.intermediate1 != p1.intermediate2
            p1.intermediate1 != p1.intermediate3

            p1.intermediate2 != p1.intermediate3

            //at least 2 1000+ level CSCI in pathway
            // ("Each requires two 1000-level (or higher) CSCI courses")
            //there are some c2 courses
            some disj c1, c2: Course | (
                //such that these courses are in the pathway
                (c1 = p1.core1 or
                c1 = p1.core2 or
                c1 = p1.related1 or
                c1 = p1.intermediate1 or
                c1 = p1.intermediate2 or
                c1 = p1.intermediate3) and 
                (c2 = p1.core1 or
                c2 = p1.core2 or
                c2 = p1.related1 or
                c2 = p1.intermediate1 or
                c2 = p1.intermediate2 or
                c2 = p1.intermediate3)
            ) implies {
                //they are both upper div

                some c1.upperDiv
                some c2.upperDiv
                c1.dept = CSCI
                c2.dept = CSCI
            }
        }
    }
}

pred valid_upper_level {
    all d: oldDegreeSCB | {
        some p: PathwayRequirements, c: Course | 
        ((p = d.pathway1 or p = d.pathway2)
        (c = d.upperLevel)) implies {
            //("One additional 1000-level (or 2000-level) CSCI course")
            //this is actually upperDiv
            some c.upperDiv

            //and CSCI
            c.dept = CSCI

            //("hat is neither a core nor a related nor a grad course for the pathways")
            //this is NOT in the pathway
            c != p.core1
            c != p.core2
            c != p.related1
            c != p.intermediate1
            c != p.intermediate2
            c != p.intermediate3
        }
    }
}

pred valid_electives {
    all d: oldDegreeSCB | {
        some c1, c2, c3: Course | 
        (c1 = d.elec1
        c2 = d.elec2
        c3 = d.elec3) implies {
            //("One may be an intermediate course not otherwise used as part of the concentration.
            // The others must be 1000-level")

            //two must be upperdiv
            some c1.upperDiv
            some c2.upperDiv

            //TODO: if c3 is intermediate, then not in concentration? do we even model this
        }
    }
}


pred wellformed_degree {
    //TODO: all groups valid

    //TODO: no more than 4 artsy in concentration

}
