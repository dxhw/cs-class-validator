#lang forge/froglet

//setup generics
abstract sig Boolean {}
one sig True extends Boolean {}

abstract sig Degree {
    numCourses: one Int
}

abstract sig Intermediate {}
one sig FoundationsI, MathematicsI, SystemsI extends Intermediate {}

abstract sig PathwayName {}
one sig AiMlP, DesignP, SoftwareP, DataP, SecurityP, ComputationalBiologyP, VisualComputingP, 
        ComputingArchitectureP, TheoryP, SystemsP extends PathwayName {}

abstract sig PathwayCourseType {}
one sig CoreT, RelatedT, IntermediateT extends PathwayCourseType {}

abstract sig Department {}
one sig CSCI, MATH extends Department {}

sig Course {
    // prereq: pfunc Int -> Course, // c.prereq[0] = some course
    prereq: lone Course,
    dept: one Department,
    finishIntro: lone Boolean, //19 or 200?
    intermediateType: lone Intermediate, 
    pathway: pfunc PathwayName -> PathwayCourseType,
    upperDiv: lone Boolean, //1000+?
    artsy: lone Boolean, //arts hums social sci

    // we probablyyyyy don't want this? It lets us do gimmicky things with counting
    degree: one Degree
}

//old req
sig oldDegreeSCB extends Degree { 
    calc: one Boolean,
    
    intro1: one Course, //can be any CS
    intro2: one Course, //0190 or 200

    inter1: one Course,
    inter2: one Course,
    inter3: one Course,
    inter4: one Course,
    inter5: one Course,

    pathway1: one PathwayRequirements,
    pathway2: one PathwayRequirements,

    upperLevel: one Course, //1000+ cs, not pathway
    elec1: one Course, //any
    elec2: one Course, //any
    elec3: one Course //any
}

sig PathwayRequirements {
    name: one PathwayName,
    core1: one Course,
    core2: lone Course,
    related1: lone Course,
    intermediate1: one Course,
    intermediate2: lone Course,
    intermediate3: lone Course
}

pred wellformed_course {
    all c: Course | {
        // TODO: need to figure out how to rewrite this since it isn't just going through
        // linked list, it is a function
        not reachable[c, c, prereq]

        // no course is both an intermediate and a core/related course for a pathway
        some c.intermediateType implies {
            all pn: PathwayName | {
                no c.pathway[pn] or c.pathway[pn] = IntermediateT
            }
        }
    }
}

pred finished_calc {
    all d: oldDegreeSCB | {
        some d.calc
    }
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
        some disj c1, c2, c3, c4, c5: Course | {       
            //all of these courses are in the degree
            d.inter1 = c1 and
            d.inter2 = c2 and
            d.inter3 = c3 and
            d.inter4 = c4 and
            d.inter5 = c5

            some c1.intermediateType
            some c2.intermediateType
            some c3.intermediateType
            some c4.intermediateType
            some c5.intermediateType

            //we only care that 3 of the courses are distributed across categories
            c1.intermediateType = FoundationsI
            c2.intermediateType = MathematicsI
            c3.intermediateType = SystemsI
        }  
    } 
}

pred distinct_pathways {
    all d: oldDegreeSCB | {
        //comparing pathways...
        //the two pathways are distinct
        d.pathway1.name != d.pathway2.name

        //the two pathways cannot share a core or related course
        d.pathway1.core1 != d.pathway2.core1
        d.pathway1.core1 != d.pathway2.core2
        d.pathway1.core1 != d.pathway2.related1

        d.pathway1.core2 != d.pathway2.core1
        d.pathway1.core2 != d.pathway2.core2
        d.pathway1.core2 != d.pathway2.related1

        d.pathway1.related1 != d.pathway2.core1
        d.pathway1.related1 != d.pathway2.core2
        d.pathway1.related1 != d.pathway2.related1
    }
}

pred all_pathways_valid {
    all p1: PathwayRequirements | {
        // all the pathway requirements fit their required buckets for the pathway name
        
        // Must have at least one core
        p1.core1.pathway[p1.name] = CoreT
        
        // Must have either a second core or a related
        some p1.core2 implies {
            p1.core2.pathway[p1.name] = CoreT
        } else {
            some p1.related1
            p1.related1.pathway[p1.name] = RelatedT
        }

        // Pathway Intermediates
        // all pathways have at least 1
        p1.intermediate1.pathway[p1.name] = IntermediateT
        // everything but architecture has 2+
        p1.name != ComputingArchitectureP implies {
            some p1.intermediate2
            p1.intermediate2.pathway[p1.name] = IntermediateT
        }
        // these ones have 3, the rest have 2
        (p1.name = ComputationalBiologyP or 
        p1.name = SoftwareP or 
        p1.name = SystemsP or 
        p1.name = VisualComputingP) implies {
            some p1.intermediate3
            p1.intermediate3.pathway[p1.name] = IntermediateT
        }

        //EVERYTHING is disjoint within the pathway
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

        //two of the courses in the pathway must be upper div and not intermediate
        #{c: Course | some c.upperDiv and (c = p1.core1 or c = p1.core2 or c = p1.related1)} >= 2

    }

}

pred valid_two_pathways {
    distinct_pathways
    all_pathways_valid
}

pred valid_upper_level {
    all d: oldDegreeSCB | {
        // the upper level is in neither of the pathways
        no d.upperLevel.pathway[d.pathway1.name]
        no d.upperLevel.pathway[d.pathway2.name]
        // 1000 or 2000-level CSCI
        some d.upperLevel.upperDiv
        d.upperLevel.dept = CSCI
    }
}

pred valid_electives {
    all d: oldDegreeSCB | some disj e1, e2, e3: Course |  {
        //("One may be an intermediate course not otherwise used as part of the concentration.
        // The others must be 1000-level")
        d.elec1 = e1
        d.elec2 = e2
        d.elec3 = e3

        // the electives cannot be anywhere else in the degree.
        all c1: Course |  (
            //[this is such an awful way to do this but it works?????????] 
            reachable[c1, d, intro1, intro2, inter1, inter2, inter3, inter4, inter5, upperLevel, 
                pathway1, pathway2, core1, core2, related1, intermediate1, intermediate2, intermediate3]
        ) implies {
            e1 != c1 and
            e2 != c1 and
            e3 != c1
        }

        some e1.upperDiv
        some e2.upperDiv
        // the last elective can be intermediate, so it doesn't need to be upper div

        // TODO: we need to check that none of the three electives are used anywhere else in the degree?
        // this makes sure they are all different, but not that they aren't in the rest of the degree
    }
}

pred wellformed_degree {
    finished_calc
    wellformed_course
    valid_intro_oSCB
    valid_intermediate
    valid_two_pathways
    valid_upper_level
    valid_electives

    // TODO: we can't actually write this but we need to 
    // all d: oldDegreeSCB | {
    //     #{c: Course | c in d} = 15
    // }

    // this is a gimmicky way to make it work because we are making it use exactly 15 courses
    all c: Course | some d: Degree | {
        c.degree = d
    }
    
    // the num courses thing is not actually doing anything at the moment


    // no more than 4 artsy
    #{c: Course | some c.artsy} <= 4

    //realistically there can't be more than 2 courses that finish the intro (it's just 190 and 200)
    #{c: Course | some c.finishIntro} <= 2

}

run {
    wellformed_degree
} for exactly 1 oldDegreeSCB, exactly 2 PathwayRequirements, exactly 12 Course
//TODO: what is the minimum number of courses that is still sat? nobody knows...
