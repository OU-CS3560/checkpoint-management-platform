# A Manangement System

A system designed primarily for managing term project checkpoints
of CS3560 class that is offered at [Ohio University](https://www.ohio.edu/).

## Design

### Manual Tasks During First Week of Semester

- Create MS Team channels
- Create GitHub entire-class team
- Create GitHub project teams
- Create Repository for the term project team

### User Story - Import students' data from a LMS

1. Display the link to Blackboard API.
2. Have user visit the page, then copy and paste in the data.
3. Parse and store the data into the database.

The another method is too upload a CSV file from the `bb-utils` tool.

TODO(KC): Finalize the user story

### User Story - Team formation report

After team formation, these are the metrics we want to know.

- Who is not on a team? With a quick way to email them.
- How many team are there?
- Average team size / team size distribution
- Number of team by technology stack?
- Number of team by programming language?

TODO(KC): Finalize the user story

### User Story - Name lookup

Teaching assistant (TA) is grading the assignment and they want to check the student
GitHub username.

They then visit the student list view of the classroom. Using the search box they type
in part of the student name. The (client side) app use this to filter the list
of students by first name, last name, username and GitHub username.

The list of students that has the match is displayed with the links to quickly
visit their profiles.

### User Story - Check username's existent

Teaching assistant (TA) receive a list of GitHub usernames and Codewars usernames of the
students. They now want to check which username is not valid (e.g. no user profile on
respective website).

From the classroom page, TA can request the app to run the check of the username existent.
The client-side app talks to the backend and queue a task that check the usernames.

The result can be view in the tasks view.

### User Story - Clone all repositories from GitHub Classroom assignment

TA want to grade an assignment that is assigned via GitHub Classroom. They want to clone
all repositories to their computing device.

They visit the classroom page then click on one of the tools namely "Generate clone commands".
They fill in the prefix of the repository name. They app use the students' GitHub usernames
in its database, create a set of git-clone commands for the TA.

The TA can then run these commands to clone all repositories.

### User Story - Generate presentation order

TODO(KC): Finalize the user story

- Take into account what team did not present last checkpoint. These teams should be given
  an opportunity to present first.

### User Story - Mark student as presenting in a checkpoint presentation

TODO(KC): Finalize the user story

### User Story - Tacking student productivity during a checkpoint

TODO(KC): Finalize the user story

For each team (or maybe for all teams), show the commit frequency of the members.

### User Story - Updating scores on Blackboard

(This will be difficult)

TODO(KC): Finalize the user story

### User Story - MS Teams' channel creation

- User give a team information. The software automatically creates MS Teams channel with proper slug.
  The software creates team on GitHub Organization.
  
  Note that the current flow is to reuse a channel. Additional channels are then created once the
  existing channels are used up.
