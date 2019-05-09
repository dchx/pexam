import os,sys,shutil,re
import numpy as np
from subprocess import Popen,PIPE
import PyPDF2 as pypdf

path='/depot/exam/'
myname='Do Not Reply'
myemail='do-not-reply@ufl.edu ('+myname+')'
myexamfolder='MyUserName_scratch/'

def load_pars():
	'''
	Load input parameters
	'''
	# identify input parameter file
	args=sys.argv
	defaultinfile=path+myexamfolder+"pars/input.py"
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

def send_email(mailtext, subject, mailto, mailfrom=myemail, cc='', bcc='', attach='', smtp='smtp.ufl.edu'):
	confirm=raw_input('Are you sure to send an email\nTo: %s\nCC: %s\nBC: %s\nSubject: %s\nContent:\n%s\nAttachments:%s\nSend? (yes/no) '%(mailto,cc,bcc,subject,mailtext,attach)).lower()

	additions = [cc, bcc, attach]
	padd = [' -c ', ' -b ', ' -a ']
	addparas = []
	for ia in range(len(additions)):
		if type(additions[ia]==list): additions[ia] = padd[ia].join(additions[ia])
		addparas.append(padd[ia]+additions[ia] if len(additions[ia])>0 else '')
	cc, bcc, attach = additions
	ccpara, bccpara, attachpara = addparas
	subjectpara = ' -s "'+subject+'"'
	mailfrompara = ' -r "'+mailfrom'"'
	smtppara = ' smtp='+smtp

	if 'yes'.startswith(confirm): os.system('echo "%s" | env MAILRC=/dev/null%s mailx -v%s%s%s%s%s %s'%\
	          (mailtext,smtppara,subjectpara,mailfrompara,ccpara,bccpara,attachpara,mailto))

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
	If one question doesn't have five answers, make it five by appending nonsense answers (NVA).
	input: qlines [list of str] the readed .q file stored by line, and should be in order [QQ,AA,(2),(3),(4),...] line by line

	Later added:
	 - add/remove periods (.) at the end of answers, as often asked by prof. lada
	 - make sure no duplicated answers
	 - make sure no empty answers
	 - make sure no duplicated question numbers
	 - make sure no more than 5 questions
	'''
	iques=[il for il in range(len(qlines)) if 'QQ' in qlines[il].strip()] # line index of questions
	qlinesout=[]
	for iiques in range(len(iques)): # index of question index list
		if iiques!=(len(iques)-1): answerslist=qlines[(iques[iiques]+1):iques[iiques+1]] # the body between two questions
		else: answerslist=qlines[(iques[iiques]+1):] # last question
		answerslist = [answer for answer in answerslist if len(answer.strip())>0] # clear empty answers

		# handle periods (.), empty answers, duplicated answers
		pureanswerslist=[]
		number_of_periods=0 # conunt period (.) at end of each answer as often asked by prof. lada
		for i,answer in enumerate(answerslist):
			pureanswer=re.split('\(\d\)',answer)[-1].strip()
			if pureanswer[-1]=='.': number_of_periods+=1 # conunt period (.) at end of each answer as often asked by prof. lada
			# in case of empty answers
			if pureanswer == '':
				pureanswer = 'NVA'
				answerslist[i] = answer.strip()+' NVA'
			pureanswerslist.append(pureanswer)
		# make sure no duplicated answers
		if len(np.unique(pureanswerslist))!=len(pureanswerslist): raise Exception("Question %d: found same answers."%(iiques+1))
		# add period (.) to sentence answers as often asked by prof. lada, plan B
		thequestion = qlines[iques[iiques]].strip()
		for i,answer in enumerate(answerslist):
			pureanswer=re.split('\(\d\)',answer)[-1].strip()
			if number_of_periods>=3 or thequestion[-1].isalpha() or (len(pureanswer.split())>4 and pureanswer[0].isupper() and not pureanswer.istitle()): 
			# more than 3 answers already have periods OR the question is not finished by a sentence OR (the answer has >4 words AND first word is capital AND is not title sentence)
				# all answers shold have a period
				if pureanswer[-1]!='.': answerslist[i] = answer.strip()+'.'
			else: # all answers shold NOT have period
				if pureanswer[-1]=='.': answerslist[i] = answer.strip().strip('.')

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

		# if less than 5 answers, add NVA answers
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
