from utils import *
import disabled
'''
Program to process exams.
'''

def proof_mail(pdffile,pars):
	''' email the grade result file to instructor'''
	mailtext='''\
	Hi %s,\n
	Please check the proof for %s exam %s.\n
	Thanks,
	%s'''%(pars.instructor.split()[1],pars.course,pars.examnum,myname)
	subject='%s exam %s proof'%(pars.course,pars.examnum)
	mailto=instructor_email(pars.instructor)
	CC=instructor_email('Francisco')
	BC=myemail
	attach=pdffile
	confirm=raw_input('Are you sure to send an email\nTo: %s\nCC: %s\nBC: %s\nSubject: %s\nContent:\n%s\nAttachment:%s\nSend? (yes/no) '%(mailto,CC,BC,subject,mailtext,attach)).lower()
	if 'yes'.startswith(confirm):
		os.system("echo '%s' | mailx -v -s '%s' -r %s -c %s -b %s -a %s %s"%(mailtext,subject,myemail,CC,BC,attach,mailto))

def modify_qfile(qfile):
	'''
	pre-process *.q file
	'''
	# sed operating
	os.system("sed -i 's/AA *(/AA S (/g' "+qfile) # insert 'S' if noappear, to all questions
	os.system("sed -i 's/AA *1 *(/AA S 1 (/g' "+qfile) # insert 'S' if noappear, to all questions
	#os.system("sed -i 's/AA *S *(/AA S 1 (/g' "+qfile) # insert correct answer '1' if noappear, to all questions

	# operating as single string
	with open(qfile,'r') as fq: qbody=fq.read().replace('\xef\xbb\xbf','')
	qbody=qbody.replace('\r','\n').replace('\\_','_').replace('_','\\_').replace('\t','') # \r -> \n; _ -> \_ ; \t -> ''; 
	qbody=qbody.replace('\\%','%').replace('%','\\%').replace('\\#','#').replace('#','\\#').replace('\\&','&').replace('&','\\&') # % -> \%; # -> \#; & -> \&
	qbody=qbody.replace(' S1 ',' S 1 ').replace(' 1 S ',' S 1 ').replace(' s1 ',' S 1 ').replace(' s 1 ',' S 1 ') #' S1 ' -> ' S 1 '; ' 1 S '->' S 1 '; ...
	qbody=qbody.replace('\n',' ').replace(' QQ','\n\nQQ').replace(' AA','\nAA').replace('  ',' ') # keep all QQ/AA/(n) in one line
	qbody=qbody.replace('\nA)','\n(1)').replace('\nB)','\n(2)').replace('\nC)','\n(3)').replace('\nD)','\n(4)').replace('\nE)','\n(5)') # A)B)C)D)E) -> (1)(2)(3)(4)(5)
	qbody=qbody.replace(' 1)','(1)').replace(' 2)','(2)').replace(' 3)','(3)').replace(' 4)','(4)').replace(' 5)','(5)') # 1)2)3)4)5) -> (1)(2)(3)(4)(5)
	qbody=qbody.replace('(1)',' (1) ').replace(' (2)','\n(2) ').replace(' (3)','\n(3) ').replace(' (4)','\n(4) ').replace(' (5)','\n(5) ') # (1)(2)(3)(4)(5) add space
	qbody=re.sub('"(.*?)"',"``\\1''",qbody) # "..." -> ``...''
	# recover \_ -> _ in $...$ maths
	for found in re.finditer('\$(.*?)\$',qbody):
		tosub=found.group().replace('\\_','_')
		qbody=qbody.replace(found.group(),tosub)
	
	# operating as list of lines
	qlines=qbody.split('\n')
	qlines=make5ques(qlines) # make sure one question has five answers by adding nonsense answers
	width=70
	for l in range(len(qlines)): qlines[l] = splitAline(qlines[l],width) # make sure lines within certain width
	qbody='\n'.join(qlines)
	
	numq=qbody.count('QQ')
	if qbody.count('AA')!=numq: raise ValueError("QQ and AA not same number.")
	numq=str(numq)

	with open(qfile,'w') as fq: fq.write(qbody)
	print 'Modified:',qfile
	return numq
	
def makehead(headfile,pars,numq):
	'''
	make head
	create *.hed
	'''
	specialcode=instructor2specialcode(pars.instructor)
	
	# 1st & 2nd page custom field 1
	CF1="\\centerline {\\bb DEPARTMENT OF ASTRONOMY}\n\\medskip\n\\noindent\n"
	CF1=CF1+"\\centerline {\\bb UNIVERSITY OF FLORIDA}\n\\medskip\n"
	CF1=CF1+"\\hbox to \\hsize{\\hbox to 1.3in{\\sans "+pars.course+"\\hfill}\n"
	CF1=CF1+"\\hfill {\\sans Exam \\# "+pars.examnum+"} - {\\br Test Form {\\bf "+pars.testform+"}} \\hfill\n"
	CF1=CF1+"\\hfill {\\sans Section {\\bf "+pars.section+"}}}\n"
	CF1=CF1+"\\hbox to \\hsize{\\hbox to 3.8in{\\sans "+pars.semester+", {\\bf "+pars.year+"} \\hfill}\n"
	CF1=CF1+"\\hfill {\\sans Periods: {\\bf "+pars.periods+"}}}\n"
	CF1=CF1+"\\hbox to \\hsize{\\hbox to 1.5in{\\sans "+pars.examdate+"\\hfill}\n"
	CF1=CF1+"\\hfill {\\sans Special Code {\\bf "+specialcode+"}} \\hfill\n"
	CF1=CF1+"\\hfill {\\sans "+pars.instructor+"}}\n"
	
	# 2nd page custorm field 2
	CF2_2="\\centerline{Your exam consists of "+numq+" questions and begins on the next page.}\n"
	CF2_2=CF2_2+"\\centerline{You may start as soon as you have carefully}\n" 
	CF2_2=CF2_2+"\\centerline{read and UNDERSTOOD the above instructions.}\n"
	CF2_2=CF2_2+"\\centerline{You have a total of "+pars.timelimit+" minutes.}\n\\hfill\n\\eject\n"
	
	page1body=open(pars.page1,'r').read()
	page2body=open(pars.page2,'r').read()
	outhead=CF1+page1body+CF1+page2body+CF2_2
	with open(headfile,'w') as fhead: fhead.write(outhead)
	print 'Created:',headfile

def modify_qufile(qufile,headfile):
	'''modify qu file add first and last lines'''
	with open(qufile,'r') as fqu: qubody=fqu.read()
	qubody='\\input '+headfile+'\n'+qubody+'\\EQ\n\\vfill\\eject\n\\evenpages\n\n' # make sure a blank line after \evenpages, or \evenpages can't work
	with open(qufile,'w') as fqu: fqu.write(qubody)
	print 'Modified:',qufile

def modify_texfile(texfile):
	# modify .tex file add first line
	with open(texfile,'r') as ftex: texbody=ftex.read()
	texbody='\\input '+path+myexamfolder+'pages/deflist.tex\n\\input '+path+myexamfolder+'pages/pdftexconfig.tex\n'+texbody
	with open(texfile,'w') as ftex: ftex.write(texbody)
	print 'Modified:',texfile

def process_exam(checkeven=True):
	pars=load_pars()
	workpath, fileprefix=file_names(pars)
	args=sys.argv

	if len(args)==2:
		quefile=workpath+fileprefix+'.que'
		if pars.mode=='PROOF' or (pars.mode=='EXAM' and not os.path.isfile(quefile)):
			# clear work folder
			os.system('rm -rf '+workpath+'*') 
			print 'Cleared folder:',workpath
			
			# copy qfile to *.q
			thisq=workpath+fileprefix+'.q' 
			shutil.copy(pars.qfile,thisq)
			print 'Copied',pars.qfile,'to',thisq
			
			# pre-process *.q file, calculate number of questions
			numq=modify_qfile(thisq)
			
			# run qq2tex.pl, input *.q and create *.qu
			qq2tex=path+myexamfolder+'src/qq2tex.pl'
			print 'Running',qq2tex,'on',thisq
			os.system('perl '+qq2tex+' '+thisq)
			qufile=workpath+fileprefix+'.qu'
			print 'Created:',qufile

			# create *.hed file
			headfile=workpath+fileprefix+'.hed'
			makehead(headfile,pars,numq)
			# modify qu file add first and last lines
			modify_qufile(qufile,headfile)
			
			# move *.qu to *.que
			os.rename(qufile,quefile)
			print 'Moved',qufile,'to',quefile

		# run texam on *.que, output *.tex, *.ans
		run_texam(quefile,pars.num_exam,mode=pars.mode)
		texfile=workpath+fileprefix+'.tex'
		ansfile=workpath+fileprefix+'.ans'
		
		# if proof: copy fileprefix.* to master.*
		if pars.mode=='PROOF':
			mastertex=workpath+'master.tex'
			shutil.copy(texfile,mastertex)
			print 'Copied',texfile,'to',mastertex
			texfile=mastertex
			shutil.copy(ansfile,workpath+'master.ans')
			print 'Copied',ansfile,'to',workpath+' master.ans'
			fileprefix='master'
		
		# modify .tex file add first line
		modify_texfile(texfile)
		
		# create pdf file
		pdffile=workpath+fileprefix+'.pdf'
		print 'Running pdftex on',texfile
		os.system('pdftex -output-directory '+workpath+' '+fileprefix+'.tex')
		print 'Created:',pdffile
		
		# check evenpage and extract pdf for disabled students
		if pars.mode=='EXAM': disabled.extract_disabled(pdffile,pars,checkeven=checkeven)

	elif len(args)==3:
		if 'email'.startswith(args[2]): proof_mail(workpath+'master.pdf',pars)
		else: raise ValueError('Cannot recognize argument "%s"'%args[2])

if __name__ == '__main__': process_exam(checkeven=True)
