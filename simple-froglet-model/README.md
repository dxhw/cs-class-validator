# Curiosity Modeling 

---

1. Project Objective: What are you trying to model? Include a brief description that would give someone unfamiliar with the topic a basic understanding of your goal.

We are trying to model the Brown University CSCI undergraduate concentration requirements, specifically working to understand the constraints that are imposed 2020-2024 CS ScB (See: [The Brown CS Handbook](https://cs.brown.edu/degrees/undergrad/concentrating-in-cs/concentration-handbook/)). Our model works to validate an existing course plan and show other potential courses that could be added to the plan to generate a valid course plan. The new CSCI requirements recently changed and have only been solidified this academic year, which has led to some confusion among Junior and Senior concentrators about which version of the requirements is most optimal for them and most allows them to achieve their goals within the CS sequence, so we hope that our model will be a helpful tool for students working on planning their time at Brown.

The CSCI requirements have different requirement structures (both in the 2020 and 2024/2025 versions), and prerequisites that attach courses to each other. In particular, the 2020 version focused on a series of pathways, while the 2024/2025 version emphasizes course levels and categories that must be satisfied. Both of these represent an interesting modeling challenge to understand effective planning for students to undertake throughout the CS curriculum. We are focusing on the 2020 ScB requirements for this project, given that the pathway structure has greater complexity and is more familiar to us as upperclassmen concentrators. 

2. Model Design and Visualization: Give an overview of your model design choices, what checks or run statements you wrote, and what we should expect to see from an instance produced by the Sterling visualizer. How should we look at and interpret an instance created by your spec? Did you create a custom visualization, or did you use the default?

Our model represents a full 2020 CS ScB degree, representing the intersecting, mutually exclusive, and overlapping requirements that it has. The core of our model is the degree and and the courses. A degree is associated with some number of courses that might appear in various categories in the degree, such as courses in the intro sequence, intermediate courses, and electives. Each of these course categories have their own rules for what types of courses they may include and how they might intersect with other categories, which we model in our predicates. Each course also has an array of features that are used to verify whether it can belong in a certain category, such as what prerequisite courses it has, what department it is in, whether it is an upper division course, and where it exists in different degree pathways. We also include a large number of Pathway names, course types, departments, and intermediate course categories to fully represent the additional notational structures that effect how courses, pathways, and the degree may interact.

We intentionally did not include any representation of capstone courses in our model, as capstones are not in use for the 2025-2026 academic year. We also limited the prerequisite functionality for the courses, given that we do not have access to sets in froglet and that most CS and MATH courses only have one direct prerequisite. 

We include a series of checks in our predicates to align with the natural language descriptions of the [2020 ScB degree](https://cs.brown.edu/degrees/undergrad/concentrating-in-cs/concentration-requirements-2020/new-scb-requirements/). We include 1 run statement that shows a generic well-formed degree for 1 ScB degree and 15 Courses, which is the minimum number needed to successfully complete the degree. The Sterling visualizer presents an extremely large and interconnected web of atoms representing the courses, labels, truth values, and pathways within the degree. It's technically possible to use the default graph with these labels and connections, especially for a small example, but a complete degree will be largely unreadable. The table view provides a better overview to see how different elements and associations are laid out with each other. 

We provide a custom visualizer in our project that may assist with making sense of the courses and the information associated with each. This custom visualization is entirely AI generated and the code is unreviewed by us -- we provide it as a utility but do not view it as part of the project or the actual materials we are submitting. 

3. Signatures and Predicates: At a high level, what do each of your sigs and preds represent in the context of the model? Justify the purpose for their existence and how they fit together.

We used froglet as our Forge language for this project, which influenced our sig and predicate choices. 

For our sigs, we are using True as an extension of a Boolean, allowing the presence of True to indicate that a particular field is checked off within a course, pathway, or degree. This is especially useful for cases where something must be true about the course, pathway, or degree, but there may be no specific item that makes it true, such as a course being something that can complete the intro sequence. We include an abstract sig for the Degree, which we extend to oldDegreeSCB. OldDegreeSCB contains several fields for different courses that may slot into varying categories. It also contains two pathway fields for the pathway requirements, fulfilled by the PathwayRequirements sig. PathwayRequirements presents a further grouping of courses within its fields, some of which may be optional, depending on the pathway. For the Course sig, we have multiple fields as Boolean flags to indicate descriptive features about the course itself, as well as several fields to associate the courses' placement within a department, pathway, or intermediate course category. We include several labeling sigs for the intermediate course categories, pathway names, and pathway course types to better represent and distinguish the nuances and differences between these categories that may appear in a course plan. 

Most of our predicates are focused on constraining a category of courses in a particular manner, such that the group of course aligns with what is expected for the ScB. As an example, valid_electives may verify that the course used are not repeated in the degree and that some of the elective courses are upper division courses, which are the only restrictions given for courses that may be used in that category. We also verify that courses are wellformed on their own using the wellformed_course predicate, which verifies more generic features about courses, including avoiding circular prerequisites paths, mutual availability of certain fields for some course, and mutual exclusivity of other fields. We combine all of these predicates in wellformed_degree, overlapping the restrictions between course categories and what courses can possibly exist. This predicate also has some high-level checks for the degree as well, ensuring restrictions about the number of courses of certain types are enforced. Together, all of these predicates are used to build a generic degree that conforms to the CS ScB requirements. 

4. Testing: What tests did you write to test your model itself? What tests did you write to verify properties about your domain area? Feel free to give a high-level overview of this.

For the simpler predicates, we used a mix of positive examples, negative examples, and assertions to demonstrate and confirm basic features about what we expected. In particular, we referred back to the requirements given by the 2020 ScB and worked to assert for each category what features must be unsatisfiable for a valid degree and what features are necessarily required for each category to be successful. This allowed us to confirm certain beliefs about our domain area, particularly with some of the positive examples that pass our predicates. In practice, these assertions allow us to ensure that we didn't underconstrain our model by allowing negative examples and assertions and that we didn't overconstrain by disallowing positive ones. This allowed us to verify the model that we had created. For the more complex predicates, especially those involving the degree and pathways, we refrained from including examples to focus more attention on testing features of our model through positive and negative assertions. We include one example in wellformed_degree demonstrating a fully-modeled, real degree plan. This example ensures that the model is not overly constrained and can accurately represent the real world, alongside demonstrating the utility of the model to build potential instances of a degree plan. 

5. Documentation: Make sure your model and test files are well-documented. This will help in understanding the structure and logic of your project.

Documentation is included in-line for both the model and the tests. 

--- 

## LLM TASK:

We used Gemini 3 Pro for this task.

### PROMPT:
A student in Brown's CSCI 1710, a lightweight formal-methods course using Forge, is starting their midterm project. They have lots of freedom to explore a domain that's interesting to them, but are also looking for ways that their work on the project can support their goals in the course. Provide feedback on the following idea(s), given the following student profile. Keep the feedback fact-based, concise and natural. Remember that the student has not been using Forge for long, and can seek further advice from course staff. Feedback should focus on (1) helping to make the idea technically well-defined; (2) potential modeling pitfalls and places to seek advice; and (3) advice on potential, easily implemented, project enhancements tailored to the student's interests.  Do not provide Forge code or documentation.

PROJECT IDEA: A CSCI concentration requirements validator for a Brown University ScB degree. This may use either the "old requirements" (2020 requirements) or "new requirements" (2024/2025 requirements) available on the Brown CS handbook.

STUDENT PROFILE: The student working on this project is interested in creating tools that will be helpful for their friends to effectively manage their time at Brown. Given the recent changes to the degree requirements in CS, they want to help their friends to choose the requirements that are most suitable to their interests. They also have an interest in encouraging their friends who are less interested in attaining a CS degree that doing so is actually very easy at Brown, and trying to show them pathways that will work for them to achieve this degree with little hardship. The student is interested in working to write effective and clear descriptions of requirements that are more vaguely defined in the real world.
STUDENT PROFILE: 
The student working on this project is interested in creating tools that will be helpful for their friends to effectively manage their time at Brown. Given the recent changes to the degree requirements in CS, they want to help their friends to choose the requirements that are most suitable to their interests. They also have an interest in encouraging their friends who are less interested in attaining a CS degree that doing so is actually very easy at Brown, and trying to show them pathways that will work for them to achieve this degree with little hardship. The student is interested in working to write effective and clear descriptions of requirements that are more vaguely defined in the real world.


RESPONSE BELOW (TO FILE END)
--- 


This is a fantastic and highly practical application of formal methods. Degree requirement validation is essentially a constraint satisfaction problem, which Forge handles exceptionally well. Since you are dealing with a transition period between degree requirements (2020 vs. 2024/2025), your tool could provide genuine utility to your peers.

Here is feedback tailored to your profile and the scope of a CSCI 1710 midterm project.

### 1. Making the Idea Technically Well-Defined

To make this manageable within the timeframe, you need to move from "checking a degree" to "checking specific logic constraints."

* **Abstract the Course Catalog:** Do not try to model every single computer science course at Brown. This will lead to tedious data entry rather than interesting logic. Instead, define Signatures for course *types* or *categories* (e.g., `IntroSequence`, `MathRequirement`, `SystemsPathway`, `TheoryPathway`). You can instantiate specific atoms (like `CSCI0330`) only where strictly necessary to show prerequisite chains.
* **Modeling "Vagueness":** You mentioned an interest in writing clear descriptions of vague requirements. In Forge, this translates to defining predicates for edge cases. For example, how do you formally define a "Related Course"? Instead of a vague list, you could model it as a set of courses that possess specific properties (e.g., `isSTEM` and `level > 1000`).
* **The "State" of a Student:** Since you want to help friends manage their time, consider modeling the student's progress as a temporal trace (Semester 1 -> Semester 2 -> ...). This allows you to validate not just *if* they have the courses, but *if* the schedule is valid (e.g., checking that prerequisites are taken in previous semesters, not the current one).

### 2. Potential Modeling Pitfalls & Advice

* **The "Capstone" Trap:** The definition of a Capstone at Brown can be complex (it must be taken in the final year, often requires a specific grade or instructor permission).
* *Advice:* Start with a simplified definition (e.g., "Any 1000-level course marked as Capstone-eligible taken in semester 7 or 8"). Do not try to model the "instructor permission" aspect unless you create a specific field for it.


* **Over-Constraining:** A common mistake is writing constraints that are too tight, resulting in `unsat` (no solution) for valid schedules.
* *Advice:* Use `run` statements frequently with partial requirements to ensure your basic building blocks (like "Intro Sequence") work before you add the complex "Pathway" logic.


* **Handling "Or" Requirements:** Brown’s requirements often say "Math 100 OR Math 180."
* *Advice:* Be careful with how you model these choices. Ensure your logical `or` allows for the student to have taken *both* without breaking the model, or strictly *one*.



### 3. Tailored Project Enhancements

Given your interest in helping friends find "easy" paths and comparing degree versions, here are three specific enhancements:

* **The "Slacker's Optimizer" (finding easy paths):**
* You want to show friends that the degree can be achieved with "little hardship." You can assign an abstract "difficulty" or "workload" integer to different course types (e.g., `Systems` = 5, `Theory` = 3, `SocialChoice` = 1).
* Write a run statement that looks for a valid degree instance where the `sum` of the difficulty is below a certain threshold. This formally proves the existence of a "low hardship" ScB.


* **The "Requirement Comparator":**
* Since you are interested in the 2020 vs. 2024 changes, define two separate predicates: `validScB_2020` and `validScB_2024`.
* Run a check to find a schedule that satisfies `validScB_2020` but **fails** `validScB_2024`. This will immediately highlight to your friends exactly what courses they "lost" or "gained" access to with the new rules.


* **The "Pathway Shopper":**
* Instead of hardcoding a pathway, let the solver "choose" the pathway for the student. Define a predicate where the student has taken a set of random courses that they find interesting. Ask the solver: "Given these interests, does there exist *any* pathway completion that leads to a valid degree?" This supports your goal of helping friends choose requirements suitable to their interests.



**Next Step:** I can help you brainstorm how to abstract the "Pathway" requirements into a set of clean logical signatures to avoid hardcoding course numbers. Would you like to start there?
