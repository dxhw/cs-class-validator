#lang forge/froglet

//setup generics
sig Boolean {}
sig True extends Boolean {}

sig Degree {
    numCourses: one Int
}

sig Course {
    prereq: pfunc Course -> Course
}

//old req

sig oldDegreeSCB extends Degree { 
    calc: one Boolean
    
    intro1: one Course //can be anything
    intro2: one Course //0190 or 200

    inter1: one Course
    inter2: one Course
    inter3: one Course
    inter4: one Course
    inter5: one Course

    pathway1: one Pathway
    pathway2: one Pathway

    upperDiv: one Course //1000+ cs, not pathway
    elec1: one Course //any
    elec2: one Course //any
    elec3: one Course //any

    // numIntroCourses: one Int
    // introCompleted: lone Boolean
    // numIntermediateCourses: one Int
    // intermediateCoursesCompleted: lone Boolean

}

sig Pathway {
    core1: one Course
    core2: lone Course
    related1: lone Course
    intermediate1: one Course
    intermediate2: lone Course
    intermediate3: lone Course
}
