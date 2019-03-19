import os,sys,shutil,re
import numpy as np
from subprocess import Popen,PIPE
import PyPDF2 as pypdf
path='/depot/exam/'
myemail='dcx@ufl.edu'
myname='Chenxing'

def load_pars():
# identify input parameter file
	args=sys.argv
	defaultinfile=path+"dcx_scratch/pars/input.py"
	if len(args)==1:
		infile=raw_input("Please enter input parameter file (Default: "+defaultinfile+"): ")
		if len(infile)==0: infile=defaultinfile
	elif len(args)==2 or len(args)==3: infile=args[1]
	else: raise ValueError("Too many input arguments.")
	
	# load input parameters
	class pars:
		execfile(infile)
		mode=mode.upper()
		num_disabled=int(num_disabled)
	return pars

def instructor2specialcode(instructor):
	'''
	Input instructor full name
	Return special code given instructor name.
	'''
	if 'Eikenberry' in instructor: return '01'
	elif 'Naibi' in instructor: return '02'
	elif 'Telesco' in instructor: return '03'
	elif 'Guzman' in instructor: return '04'
	elif 'Haywood' in instructor: return '05'
	elif 'Hamann' in instructor: return '06'
	elif 'Vicki' in instructor: return '07'
	elif 'Ata' in instructor: return '08'
	elif 'Jonathan' in instructor: return '09'
	elif 'Jian Ge' in instructor: return '10'
	elif 'Gustafson' in instructor: return '11'
	elif 'Lada' in instructor: return '12'
	elif 'NN' in instructor: return '13'
	elif 'Gonzalez' in instructor: return '14'
	elif 'Bandyopadhayay' in instructor: return '15'
	elif 'Reyes' in instructor: return '16'
	elif 'Dermott' in instructor: return '17'
	elif 'Barnes' in instructor: return '18'
	elif 'Lebo' in instructor: return '19'
	elif 'Dan Li' in instructor: return '20'
	else: raise ValueError("Cannot find instructor special code.")

def instructor_email(InstructorName):
	'''
	Input instructor firstname, return email
	'''
	if 'Naibi' in InstructorName: email='marinas@astro.ufl.edu'
	elif 'Anthony' in InstructorName: email='anthonyhg@astro.ufl.edu'
	elif 'Rafael' in InstructorName: email='guzman@astro.ufl.edu'
	elif 'Francisco' in InstructorName: email='freyes@astro.ufl.edu'
	elif ('Steve' in InstructorName) or ('Stephen' in InstructorName): email='eiken@astro.ufl.edu'
	elif 'Elizabeth' in InstructorName: email='elada@astro.ufl.edu'
	else: raise ValueError("Instructor %s email not defined"%InstructorName)
	return email

def semester_code(semester):
	if semester=='Fall': return 'f'
	elif semester=='Spring': return 'w'
	elif semester=='Summer': return 's'
	elif semester=='Summer A': return 'sa'
	elif semester=='Summer B': return 'sb'
	else: raise ValueError("Cannot identify input semester.")

def file_names(pars):
	'''
	create desired folders and return desired filenames
	 OUTPUT
	 - workpath: the path for processing this exam
	 - fileprefix: prefix for .q .qu .que .hed .tex etc files
	'''
	# instructor initials
	insnames=pars.instructor.split()
	if len(insnames)==3: initials=insnames[1][0]+insnames[2][0]
	else: raise ValueError("Instructor name must have title.") 
	# semester and year
	semyear=semester_code(pars.semester)+pars.year[-2:]
	
	# first folder
	folder1=initials.upper()+semyear+'/'
	if not os.path.isdir(path+folder1):
		os.mkdir(path+folder1) # instructor and semester year
		print 'Folder created:',path+folder1
	# second folder
	folder2=pars.section+'_'+pars.examnum+'/'
	workpath=path+folder1+folder2
	if not os.path.isdir(workpath):
		os.mkdir(workpath) # sectrion and exam
		print 'Folder created:',workpath
	# file prefix
	fileprefix=semyear+initials.lower()+pars.examnum+pars.testform.lower()
	return workpath, fileprefix

def splitAline(line,width):
	'''
	Given line [str] and width [int] to restrict one line, return line [str] with '\n' inserted to split
	'''
	width=int(width)
	restline=line
	linelist=[]
	while len(restline)>width:
		if restline[width]==' ' or restline[width-1]==' ':
			linelist.append(restline[:width].strip())
			restline=restline[width:].strip()
		else:
			subline=' '.join(restline[:width].split(' ')[:-1])
			linelist.append(subline.strip())
			restline=restline[len(subline):].strip()
	linelist.append(restline.strip())
	return '\n'.join(linelist)

def make5ques(qlines):
	'''
	if one question doesn't have five answers, make it five by appending nonsense answers (NVA).
	input: qlines [list of str] the readed .q file stored by line, and should be in order [QQ,AA,(2),(3),(4),...] line by line
	'''
	iques=[il for il in range(len(qlines)) if 'QQ' in qlines[il].strip()] # line index of questions
	qlinesout=[]
	for iiques in range(len(iques)): # index of question index list
		if iiques!=(len(iques)-1): answerslist=qlines[(iques[iiques]+1):iques[iiques+1]] # the body between two questions
		else: answerslist=qlines[(iques[iiques]+1):] # last question

		# make sure no duplicated answers
		pureanswerslist=[re.split('\(\d\)',answers)[-1].strip() for answers in answerslist]
		if len(np.unique(pureanswerslist))!=len(pureanswerslist): raise Exception("Question %d: found same answers."%(iiques+1))

		answerbody='\n'.join(answerslist) # answers list -> one string
		num_answer=len(re.findall('\(\d\)',answerbody))

		# make sure no duplicated question numbers
		if (num_answer==1 and not '(1)' in answerbody)\
		  or (num_answer==2 and not ('(1)' in answerbody and '(2)' in answerbody))\
		  or (num_answer==3 and not ('(1)' in answerbody and '(2)' in answerbody and '(3)' in answerbody))\
		  or (num_answer==4 and not ('(1)' in answerbody and '(2)' in answerbody and '(3)' in answerbody and '(4)' in answerbody))\
		  or (num_answer==5 and not ('(1)' in answerbody and '(2)' in answerbody and '(3)' in answerbody and '(4)' in answerbody and '(5)' in answerbody)):
			raise Exception("Question %d: answer numbers do not match."%(iiques+1))
		# make sure no more than 5 questions
		elif num_answer>5: raise Exception("Question %d: more than 5 answers."%(iiques+1))

		for iappend,num2append in enumerate(range(num_answer+1,6)): answerbody=answerbody+"\n(%d) NVA"%(num2append)
		qlinesout.append(qlines[iques[iiques]])
		for aline in answerbody.split('\n'): qlinesout.append(aline)
	return qlinesout

def run_texam(quefile,num_exam,mode='none'):
	# 6: run mode; 10: number of copies; 15: space between questions
	BasicInput='6 '+mode+'\n15 2\n'
	if mode=='PROOF': texam_input=BasicInput+'10 1\n\n' 
	elif mode=='EXAM': texam_input=BasicInput+'10 '+num_exam+'\n\n'
	elif mode=='GRADE': texam_input=BasicInput+'10 '+num_exam+'\n\n'
	else: raise ValueError("texam mode not recognized.")
	
	# run texam on *.que, output *.tex, *.ans
	print 'Running texam on',quefile
	p=Popen(['texam',quefile],stdin=PIPE,stdout=PIPE,stderr=PIPE)
	texamout=p.communicate(texam_input)
	if len(texamout[1])!=0: raise ValueError("texam input arguments error:\n"+texamout[0]+texamout[1]+"\n^^^texam input arguments error.\n")
	else: print texamout[0]
	for toremove in ['GTEMP.GRA','PHYSICS.FIL']:
		if os.path.isfile(toremove):
			os.remove(toremove)
			print 'Removed:',toremove
