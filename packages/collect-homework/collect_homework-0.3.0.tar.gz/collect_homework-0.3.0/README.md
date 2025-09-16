# manage your student's homework

## Description

assuming you have asked your students to create a repo on github to submit their homework,
this script will help you efficiently clone/pull/merge all the repos in a folder, and display a summary of the status of all the repos

## Installation

```bash
pip install collect-homework
```

## Initial setup

1. create a folder where you want to clone all the repos
1. create a file named `00.ids` in the folder  
   this file should contain the github ids of all the students, one id per line
1. at that point  
   ```bash
   collect-homework clone
   ```
   will clone all the repos in the folder
1. in order to pull all the repos in the folder  
   ```bash
   collect-homework pull
   ```
1. you get the gist of it; type
   ```bash
    collect-homework help
    ```
    to see all the available commands
1. of particular interest is the 
   ```bash
   collect-homework summary
   ```
   command, which will display a one-line summary of all repos in the folder
1. finally you can focus on one or several students by typing e.g. (this makes sense for most commands)
   ```bash
   collect-homework -s "JohnDoe JaneMartin" pull
   ```

## handling repo names

assuming you run this command in a folder e.g. `/Users/johndoe/python-homework`:

- then by default all the students are expected to have a repo named `python-homework`
- if this does not match your setup, you can specify the repo name in the `00.reponame` file  
  this one-line file should contain the name of all the repos, e.g. `python-homework-2024`
- and if a student does not comply with that name, you can specify the repo name in the `00.ids`
  file by writing `student/the-repo` instead of just `student`  
  (you can even put the complete github url instead if that's more convenient for you)
