#!/usr/bin/env python
from utils import *
import glob

def grade_result_mail(filebase,pars):
	# Mail the grade result file to instructor
	mailtext='''\
	Hi %s,\n
	Please check the grading results for %s exam %s.\n
	I have put the exam questions and scantrons in your mailbox.\n
	Thanks,
	%s'''%(pars.instructor.split()[1],pars.course,pars.examnum,myname)
	subject='%s exam %s grading results'%(pars.course,pars.examnum)
	mailto=instructor_email(pars.instructor)
	CC=instructor_email('Francisco')
	BC=myemail
	attaches=[filebase+'.txt',filebase+'.gra',filebase+'.ans']
	send_email(mailtext,subject,mailto, cc=CC, bcc=BC, attach=attaches)

def glob_one_file(toglob):
	# get *.dsa file
	dsafiles=glob.glob(toglob)
	if len(dsafiles)==0: raise IOError("%s not found."%toglob)
	elif len(dsafiles)>1: raise IOError("%s more than one file found."%toglob)
	else:
		dsafile=dsafiles[0]
		return dsafile

if __name__=='__main__':
	pars=load_pars()
	workpath, fileprefix=file_names(pars)
	GradingFilePrefix=fileprefix[3:]
	filebase=workpath+GradingFilePrefix
	args=sys.argv

	if len(args)==2:
		dsa_toglob=workpath+'*.dsa'
		sanfile=filebase+'.san'

		zipfiles=glob.glob(workpath+'*.zip')
		if len(zipfiles)>1: raise IOError("More than one .zip file found.")

		# unzip and check san file
		elif len(zipfiles)==1: # one .zip file found

			# unzip downloaded zip file
			zipfile=zipfiles[0]
			unzipcmd='unzip '+workpath+'*.zip -d '+workpath
			os.system(unzipcmd); print(unzipcmd)
			rmzipcmd='rm '+workpath+'*.zip'	
			os.system(rmzipcmd); print(rmzipcmd)

			# get dsa file
			dsafile=glob_one_file(dsa_toglob)

			# copy dsa file to san file
			shutil.copy(dsafile,sanfile)
			print('Copied %s to %s.'%(dsafile,sanfile))

			# check san file
			os.system('vim %s'%sanfile)
			print('Checked '+sanfile)

		# have checked san file, do grading
		else: # no zip file found (zip file removed)

			# copy que file
			prequefile=workpath+fileprefix+'.que'
			quefile=filebase+'.que'
			shutil.copy(prequefile,quefile)
			print('Copied %s to %s.'%(prequefile,quefile))

			# copy ans file
			preansfile=workpath+fileprefix+'.ans'
			ansfile=filebase+'.ans'
			shutil.copy(preansfile,ansfile)
			print('Copied %s to %s.'%(preansfile,ansfile))

			# run texam on quefile
			run_texam(quefile,pars.num_exam,mode='GRADE')

			# move tex file to txt file
			texfile=filebase+'.tex'
			txtfile=filebase+'.txt'
			os.rename(texfile,txtfile)
			print('Moved %s to %s.'%(texfile,txtfile))

			# modify txtfile, remove tex content
			with open(txtfile,'r') as ftxt: txtbody = ftxt.read()
			txtbody = txtbody[txtbody.find('1REC'):]
			with open(txtfile,'w') as ftxt: ftxt.write(txtbody)
			print('Modified '+txtfile)
	
			# check gra file
			grafile=filebase+'.gra'
			os.system('vim %s'%grafile)
			print('Checked '+grafile)

	elif len(args)==3:
		if 'email'.startswith(args[2]): grade_result_mail(filebase,pars)
		else: raise ValueError('Cannot recognize argument "%s"'%args[2])
