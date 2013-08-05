pyJournalLier
=============

A Day One (http://dayoneapp.com/) inspired and compatible journal editor/viewer powered by Python.
This app is actually a fork of the original pyDayOne (https://github.com/nitinthewiz/pyDayOne) by Nitin Khanna.

This application though could not replace the experience that the oriinal Day One app for the iOS and Mac OSX could provide.
Instead, we bring users of the app with a tool that could help them post, archive or make new entries on a Windows machine.

FAQ
===

For the users

**Q.** Why make this?

**Ans.** I myself have Day One for iOS (I have a iPad 2 BTW) and I'm frustrated that 
if I'm in a boring situation and I want to post my ideas (for just about anything) on a jorunal 
(much like what Jordan Mechner did when he made Prince of Persia). I'm surprised thought that 
somebody else have already made a solution for this on Windows. I knew that this would be a gem
that needed to be polished, so I scribbled down new code, adding new features to the app, and 
making little changes along the way.

Hence this app.

**Q.** What are the features of this app?

**Ans.** Well, here are certain features that I can highlight-
  - Make, edit and delete your entries
  - *NEW!* Star your entry!
  - *NEW!* Archive your journals!
  - MORE FEATURES SOON...

  So far though, I'm still making the editor side of this app, but by the time it's finished,
  there can be enough time to make the reader... if only I got time in my hands.
  
  Best of all, this is made free and open-source!

**Q.** Are there any bugs for this?

**Ans.** See Major Bugs


Requirements
============

Of course you need the Day One app but with the following done:
- Make sure that you have synced your Day One with Dropbox (https://www.dropbox.com/)
- Make sure you enable hashtagging (SETTINGS -> ADVANCED -> HASHTAGS) if you want to tag 

Note that this application is built in Python 2.7. You will need to have Python installed on
your computer to use. (As the original author said before, this still needs to be compiled into Windows.)

The following python modules need to be installed as well- 
1. pyGTK (http://www.pygtk.org/)
2. lxml (http://lxml.de/)
All can be downloaded from their specific websites.

How to Run this?
================

1. You can run it from command prompt/terminal with the command - "python pyJouralier_Editor.py"


Major Bugs - 
============

ORIGINAL:
1. Doesn't support many languages like Chinese (utf-8 encoding only)
