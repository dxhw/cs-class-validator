#lang forge/froglet
/* froglet is the WRONG language for this model, since the degree model as written
* explicitly uses sets, but it's fun to have a challenge!
*/

// This option auto-populates the **FULLY AI GENERATED** Visualization script so it can be used
// this visualization is NOT the ground truth and should NOT be generally trusted, 
// it has NOT been human reviewed and it is just for convenience.
option run_sterling "vis.js"

//Set up generics
abstract sig Boolean {}
one sig True extends Boolean {}

//Set up model abstracts and labels
abstract sig Degree {}

abstract sig Intermediate {}
one sig FoundationsI, MathematicsI, SystemsI extends Intermediate {}

abstract sig PathwayName {}
one sig AiMlP, DesignP, SoftwareP, DataP, SecurityP, ComputationalBiologyP, VisualComputingP, 
        ComputingArchitectureP, TheoryP, SystemsP extends PathwayName {}

abstract sig PathwayCourseType {}
one sig CoreT, RelatedT, IntermediateT extends PathwayCourseType {}

sig Department {}
//the main issue for the model is CSCI/not CSCI
one sig CSCI extends Department {} 

//Set up model constructs
sig Course {
    // prereq: pfunc Int -> Course, // c.prereq[0] = some course
    prereq: lone Course, // this is not realistic, but this allows for reachability in a way that's useful
    dept: one Department, //CSCI, MATH, ...
    finishIntro: lone Boolean, //Tells us if this course is 0190 or 0200
    intermediateType: lone Intermediate, //Is this course an intermediate of some type?
    pathway: pfunc PathwayName -> PathwayCourseType, //Given some pathway, where does this course live in the pathway?
    upperDiv: lone Boolean, //Is this course 1000+?
    artsy: lone Boolean, //Is this course arts/humanities/social sciences?

    //This is circular but it lets us do gimmicky things with counting
    degree: one Degree
}

//List the courses in the old SCB requirements
lone sig oldDegreeSCB extends Degree { 
    calc: one Boolean, //Technically just a checkoff; this doesn't require a course
    
    intro1: one Course, //Can be any CS course! Usually 111/15/17, but with 19 as intro2 can be any
    intro2: one Course, //0190 or 0200, must complete the intro sequence.

    inter1: one Course, //Intermediate Foundations CS course
    inter2: one Course, //Intermediate Mathematics CS course
    inter3: one Course, //Intermediate Systems CS course
    inter4: one Course, //Any intermediate CS course
    inter5: one Course, //Any intermediate CS course

    pathway1: one PathwayRequirements, //Any pathway
    pathway2: one PathwayRequirements, //Any pathway

    upperLevel: one Course, //Any 1000+ CSCI course not in a pathway
    elec1: one Course, //Any course
    elec2: one Course, //Any upper-div course
    elec3: one Course //Any upper-div course
}

sig PathwayRequirements {
    name: one PathwayName, //Indicates what pathway this is
    core1: one Course, //Every pathway has at least 1 core course (no dept)
    coreOrRelated: one Course, // Every pathway requires a second course that is either core or "related"
    intermediate1: one Course, //Every pathway has at least 1 intermediate course (no dept)
    intermediate2: lone Course, //...and sometimes more!
    intermediate3: lone Course
}

pred wellformed_course {
    all c: Course | {
        //A course cannot be a prereq of itself
        not reachable[c, c, prereq]

        //No course is both an intermediate course and a core/related course for a pathway
        //so all intermediates are either not in a pathway or are an intermediate in a pathway
        some c.intermediateType implies {
            all pn: PathwayName | {
                no c.pathway[pn] or c.pathway[pn] = IntermediateT
            }
        }

        // if it is not an intermediate, it cannot fulfill an intermediate requirement
        no c.intermediateType implies {
            no pn: PathwayName | {
                c.pathway[pn] = IntermediateT
            }
        }

        //Finish intro is just 19/200 so:
        //Courses cannot finish the intro and be an intermediate
        //Courses cannot finish intro and be upper div
        //Courses that finish intro are CSCI
        //19 and 200 are never in a pathway
        some c.finishIntro implies {
            no c.intermediateType 
            no c.upperDiv
            c.dept = CSCI
            all pn: PathwayName | {
                no c.pathway[pn]
            }
        }
    }
}

//Calc requirement returns True
pred finished_calc {
    all d: oldDegreeSCB | {
        some d.calc
    }
}

pred valid_intro_oSCB {
    all d: oldDegreeSCB | {
        //Intro 1 and 2 are disjoint
        d.intro1 != d.intro2
        //Both are CSCI courses
        d.intro1.dept = CSCI
        d.intro2.dept = CSCI
        //Intro 2 is 0190 or 200 (finishing the intro seq)
        some d.intro2.finishIntro

        // intro courses can't be used for other purposes
        not reachable[d.intro1, d, inter1, inter2, inter3, inter4, inter5, elec1, elec2, elec3, upperLevel,
                pathway1, pathway2, core1, coreOrRelated, intermediate1, intermediate2, intermediate3]
        not reachable[d.intro2, d, inter1, inter2, inter3, inter4, inter5, elec1, elec2, elec3, upperLevel,
                pathway1, pathway2, core1, coreOrRelated, intermediate1, intermediate2, intermediate3]
    }
}

pred valid_intermediate {
    //For all degrees...
    all d: oldDegreeSCB | {
        //intermediate courses cannot be the same,
        some disj c1, c2, c3, c4, c5: Course | {       
            //all of these courses are in the degree,
            d.inter1 = c1 and
            d.inter2 = c2 and
            d.inter3 = c3 and
            d.inter4 = c4 and
            d.inter5 = c5

            //all of these courses are intermediates,
            some c1.intermediateType
            some c2.intermediateType
            some c3.intermediateType
            some c4.intermediateType
            some c5.intermediateType

            //3 of these courses are distributed across the categories.
            c1.intermediateType = FoundationsI
            c2.intermediateType = MathematicsI
            c3.intermediateType = SystemsI
        }  
    } 
}

pred distinct_pathways {
    all d: oldDegreeSCB | {
        //comparing pathways...
        //The two pathways are distinct,
        d.pathway1.name != d.pathway2.name

        //the two pathways cannot share a core or related course
        //(but no restrictions on intermediates!)
        d.pathway1.core1 != d.pathway2.core1
        d.pathway1.core1 != d.pathway2.coreOrRelated

        d.pathway1.coreOrRelated != d.pathway2.core1
        d.pathway1.coreOrRelated != d.pathway2.coreOrRelated
    }
}

pred all_pathways_valid {
    all p1: PathwayRequirements | {
        // All the pathway requirements fit their required buckets for the pathway name
        
        // Must have at least one core
        p1.core1.pathway[p1.name] = CoreT
        
        // Must have either a second core or a related
        ((p1.coreOrRelated.pathway[p1.name] = CoreT) or 
        (p1.coreOrRelated.pathway[p1.name] = RelatedT))

        // Pathway Intermediates
        // all pathways have at least 1
        p1.intermediate1.pathway[p1.name] = IntermediateT
        // everything but architecture has 2+
        p1.name = ComputingArchitectureP implies {
            no p1.intermediate2
        } else {
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
        } else {
            no p1.intermediate3
        }

        //EVERYTHING is disjoint within the pathway
        p1.core1 != p1.coreOrRelated
        p1.core1 != p1.intermediate1
        p1.core1 != p1.intermediate2
        p1.core1 != p1.intermediate3

        p1.coreOrRelated != p1.intermediate1
        p1.coreOrRelated != p1.intermediate2
        p1.coreOrRelated != p1.intermediate3

        p1.intermediate1 != p1.intermediate2
        p1.intermediate1 != p1.intermediate3

        some p1.intermediate2 implies p1.intermediate2 != p1.intermediate3
    }

}

//Roll pathway checks into one pred
pred valid_two_pathways {
    distinct_pathways
    all_pathways_valid
}

//("One additional 1000-level (or 2000-level) CSCI course that is 
//neither a core nor a related nor a grad course for the pathways")
pred valid_upper_level {
    all d: oldDegreeSCB | {
        // The upper level is in neither of the pathways
        no d.upperLevel.pathway[d.pathway1.name]
        no d.upperLevel.pathway[d.pathway2.name]
        // The course is 1000 or 2000-level CSCI
        some d.upperLevel.upperDiv
        d.upperLevel.dept = CSCI

        // The upper div cannot be anywhere else in the degree ("additional")
        not reachable[d.upperLevel, d, intro1, intro2, inter1, inter2, inter3, inter4, inter5, elec1, elec2, elec3, 
                pathway1, pathway2, core1, coreOrRelated, intermediate1, intermediate2, intermediate3]
    }
}

pred valid_electives {
    all d: oldDegreeSCB | some disj e1, e2, e3: Course |  {
        //("One may be an intermediate course not otherwise used as part of the concentration.
        // The others must be 1000-level")

        //These 3 courses are electives in the degree.
        d.elec1 = e1
        d.elec2 = e2
        d.elec3 = e3

        // The electives cannot be anywhere else in the degree.
        all c1: Course |  (
            //[this is such an awful way to do this but it works?????????] 
            reachable[c1, d, intro1, intro2, inter1, inter2, inter3, inter4, inter5, upperLevel, 
                pathway1, pathway2, core1, coreOrRelated, intermediate1, intermediate2, intermediate3]
        ) implies {
            e1 != c1 and
            e2 != c1 and
            e3 != c1
        }

        //Two of these courses must be upperDiv
        some e1.upperDiv
        some e2.upperDiv
        // the last elective can be intermediate, so it doesn't need to be upper div
    }
}

pred wellformed_degree {
    //Put all of the degree checks together
    finished_calc
    wellformed_course
    valid_intro_oSCB
    valid_intermediate
    valid_two_pathways
    valid_upper_level
    valid_electives

    // This is a gimmicky way to make sure we don't have free-floating courses
    all c: Course | some d: Degree | {
        c.degree = d
    }

    //No more than 4 artsy courses
    // we have an overflow error, so try to lessen it with the >= 0 bound
    (#{c: Course | some c.artsy} >= 0) and (#{c: Course | some c.artsy} <= 4)

    //There can't be more than 2 courses that finish the intro (it's just 190 and 200)
    (#{c: Course | some c.finishIntro} >= 0) and (#{c: Course | some c.finishIntro} <= 2)
}

run {
    wellformed_degree
} for exactly 1 oldDegreeSCB, exactly 15 Course
// You must have at least 15 courses:
//  2 intro, 5 intermediate, 4+ pathway (core + core/related X2, possible extra intermediates)
//  1 upper level, 3 electives
//  2 + 5 + 4 + 1 + 3 = 15
// running without specifying EXACTLY 15 (or a couple more) will take a LONG time
// note that the solver usually takes a bit of time (20+ seconds) to finish even in good conditions
