# AJANVARAUS - appointment booking system

## Why?

AJANVARAUS booking system is being created specifically for a tool of study coordinators in the Sibelius Academy. I wanted to create a simple "no-nonsense" tool that works for creating booking calendars for study guidance sessions. These tools do exist already online, but none of them so far have exactly the features I would like them to have.

## Technologies

Ajanvaraus is built with Python3 and Flask, SQL with sqlite3, HTML with Jinja2 and a little hint of JavaScript. So far, no CSS styles have been added, but it will be a project for the future. Requirements for extra packages can be found in the requirements.txt file. (I'm sorry if there are packages that turned out not to be needed in the project!)

## Features

The main features of the booking system are user registration and login, creating booking calendars and sharing them with anyone who can book appointments without registration. The most important features of adding appointments to calendars is the possibility to define a deafult duration, when the form calculates the ending time automatically when the starting time is inserted. For the next appointment, the form also suggests that you want to start the appointment on the same minute as the previous one ends. 

It is also possible to edit and delete appointments and entire calendars.

## Future of the project

The next steps for improving the project are making sure all data is validated properly and errors are handled accordingly. 

New features I would like to add are (for example): 
- editing several appointment time frames on the same page
- changing username, password and e-mail
- appointments with several participants
- automatic e-mails for participants (when they have booked a meeting)
- for a logged-in user: list of booked appointments in other user's calendars, possibility to cancel and change them
- group e-mail from calendar creator to participants.

## Conclusion

This project was the first actual project I have ever created myself. I'm happy I was able to create a draft of something that in the real world would actually be useful. I have learned a lot during this process, especially about how to learn new skills in order to create new features in my project. I'm looking forward to continuing to improve this project and apply the knowledge I have acquired in many new projects in the future.