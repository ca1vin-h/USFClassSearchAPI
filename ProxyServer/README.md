This software is written for a fastapi server to serve the USF schedule planner I am building. This program allows a user to request a course using the semester, subject, and course number. The server saves this information as a json file in case another user requests the same semester/subject/coursenum, then returns the json to the user requesting it.

An example of this server can be found at http://18.208.228.65:8080/docs#/default/get_course_get_course_get. Try it out by setting P_Semester to 202408, P_SUBJ to ENC, and P_NUM to 1101. Additional valid parameters can be found in /validFormData

NOTE: if you try out the API, please be sure to click the "Try it out" button before typing information into the fields. 
