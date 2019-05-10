# pexam
Process exams: generate exam files, send exams to instructor/disability resource center, print exams, grade exams.

## Prerequisites

System programs: rm, env, sed, lpr, vim (optional), perl, texam, unzip, mailx, pdftex, python  
Python package: os, re, sys, glob, numpy, shutil, PyPDF2, subprocess

Note: texam is the core program to generate and grade the exams. It is usually installed in the departmental computers. If not, pexam has a copy in `src/`.

## Installation

In the departmental computers, pexam has a copy at 

    /depot/exam/common/pexam

You can use the code there or copy it to your preferred location, or download it from github:

    git clone https://github.com/dchx/pexam.git PexamPath

where `PexamPath` is the path you want pexam downloaded.

For basic setups, go to the pexam folder, open `src/utils.py` with any text editor, and you can find some variables defined at the top of the file. Do some modifications:

* `pexampath`: make it the path of pexam (`/depot/exam/common/pexam` or `PexamPath`)
* `myname`: change it to your name
* `myemail`: change it to your email address

Then, pexam is ready to use. If you want to run pexam anywhere, run

    export PATH="/depot/exam/common/pexam/src:$PATH"

or add this command to `~/.bashrc`. Certainly `/depot/exam/common/pexam/src` can be replaced by your `PexamPath/src`. This works if your `$SHELL` is bash, otherwise say if your `$SHELL` is csh/tcsh, run

    setenv PATH /depot/exam/common/pexam/src:$PATH

or add this command to `~/.cshrc`/`~/.tcshrc`.

## Generating Exam

You will receive an ASCII text file from the instructor, which is the question file. An example question file is at `qfiles/EXAM_EXAMPLE.txt` in pexam.

### Edit parameter file

The parameter file contains all the information we need about one exam. It is just python codes and pexam will execute it to load parameters. An example parameter file is at `pars/input.py` in pexam.

Notes on some of the parameters:

* `qfile`: the ASCII question file received from the instructor.
* `periods`: the [class meeting times](https://registrar.ufl.edu/courses/classtimes) for this course.
* `instructor`: better keep the prefix (Dr., Prof., ...) because the second word in this phrase will be in the greetings in the email you send to the instructor.
* `examnum`: the order of this exam in this semester for this course.
* `testform`: just follow `examnum` but in letters.
* `timelimit`: usually `'50'` for midterms and `'120'` for finals.
* `page1`/`page2`: the first and second pages of one printed exam. Different instructors may have different pages they want to use. Check their previous exams for the specific pages.
* `mode`: case insensitive;  
`'PROOF'` - generate the proof/master pdf file that has only one exam for checking.  
`'EXAM'` - generate the pdf file for real exams. It is one pdf file but with many exams concatenated.  
* `num_exam` - ask the instructor how many students are taking the exam, set `num_exam` ~3 more than this number.
* `num_disabled` - some of the students are going to take the exam at the [Disability Resource Center](https://disability.ufl.edu/) (DRC).

### Generate a proof

To generate a proof, set `mode` to `'PROOF'` in the parameter file and run

    process_exam.py TheParameterFile.py

where `TheParameterFile.py` is the parameter file we just edited. The command is given assuming `PexamPah/src` is set in `$PATH` during setup, otherwise you need to replace `process_exam.py` by `PexamPath/src/process_exam.py` or `python PexamPath/src/process_exam.py`.

It will generate a `master.pdf` file for you to check if everything is alright. The file is located in a specific folder for this specific exam where all the files related to this exam are saved. We call it the **"WorkPath"** hereafter.

### Email the proof to the instructor

After checking the proof, send the proof to the instructor for him/her to check. Just append `email` or simply `e` to the previous command.

    process_exam.py TheParameterFile.py email

pexam will print the email contents to the screen for you to check, and ask if you want go ahead and send the email. To confirm, type `yes`+ENTER or `y`+ENTER or simply ENTER. To cancel, type `no`+ENTER or `n`+ENTER or anything not the starting part of `yes`.

### Generate real exams

After the instructor checking and permitting to print the exam, we can generate the full exams. Now set `mode` to `'EXAM'` in the parameter file and run the same command.

    process_exam.py TheParameterFile.py

It will generate a pdf file in the WorkPath containing all the exams we need to print. The program will check if each exam in this pdf file has even pages (otherwise we cannot seperate them when they are printed), but it will take some time (though usually less than 1 minute). To disable this feature, go to the bottom of `src/process_exam.py` and set `checkeven=False`.

### Email some exams to DRC

If there are students taking the exam at DRC (`num_disabled` is not `'0'`), we need to send their exams to DRC and do not need to print them. In this case, `process_exam.py` will seperate the previously generated pdf exam file into two files, a `*_norm.pdf` file and a `*_disabled.pdf` file. We can use `src/disabled.py` to send the `*_disabled.pdf` file to DRC.

    disabled.py TheParameterFile.py

## Printing

If there are students taking the exam at DRC, just print the `*_norm.pdf` file. Otherwise, print the full exam pdf file.

### Alert

Before printing, send an email to everyone noticing the printer will be occupied for a while.

    printing.py a WorkPath/ThePdfFile.pdf

where `a` can be replaced by `alert` or `al`, `ale` etc. `ThePdfFile.pdf` is the pdf file you want to print. In the alerting process it is used to estimate the time needed for printing.

### Print

A few minutes after alerting, go check if the printer is alright and start printing.

    printing.py p WorkPath/ThePdfFile.pdf

where `p` can be replaced by `print` or `pr` etc. pexam will ask you for confirmation before printing.

### After printing

Put the printed exam in the cabinet. Send a message to the department and a message to the instructor saying the exam printed.

    printing.py c WorkPath/ThePdfFile.pdf

where `c` can be replaced by `complete` etc.

## Grading

After the students taken the exam, collect the scantrons, go to [Scanning Services](https://it.ufl.edu/services/scanning-services) and scan them up. It's better to provide a cover sheet to Scanning Services indicating the instructor name, department, your UFID (used for them to send you the scanning results), your email, course code, section, exam number, and the code **"PARKIN01"** which states the format of the scanning results we want to receive. An example cover sheet is in `pages/cover.docx`.

After the Scanning Services noticing you the scanning results are ready to download, go to [their website](https://scanning.at.ufl.edu) and download it to the **WorkPath**. It is a zip file. Then run `src/grading.py`.

    grading.py TheParameterFile.py

It will unzip the zip file and open the scanning results using vim. Check the results. Make sure there are no `*`s which means the scanning machine cannot recognize the answer. Make sure the questions 76-80 are filled in all scantrons, which is critical for the program to recognize which exam the scantron is answering.

If you are not familiar with vim, type `:q` or `:q!` to exit. You can either learn to use vim or use your preferred text editor by editting `src/grading.py` and replace all `vim`s (there are two) to your preferred editor.

After checking the scanning results, run the previous command again to grade.

    grading.py TheParameterFile.py

This time the grading result will be openned by vim for you to check. Make sure everyone has a score and there are no `-999`s which means the program connot match the scantron with the exams it generated.

### Email the grades to the instructor

After checking the grading result, put the exams and scantrons in the instructor's mailbox and send the grading results to the instructor by appending `email` or simply `e` to the previous command.

    grading.py TheParameterFile.py email

Then we have finished processing this exam.

## Other programs

* `src/real.py`

This program aims to correct the graded score when the instructor has mistakenly provided two right answers as choices in some question, but the system takes only one right answer. The basic logic of this code is to add one point to those who chose the other right answer that was not taken by the system. Before running the code, change `outtxt` in `real.py` to one of the grading results files named `*.txt`. Double check the code before running it because it depends heavily on content of the txt file. After running `real.py`, the corrected score will be saved at `WorkPath/real.txt`.
