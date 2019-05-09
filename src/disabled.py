from utils import *

def nPageDisabled_CheckEven(PdfFileReader,num_disabled):
	'''
	check if all exams have even pages
	'''
	num_page=PdfFileReader.getNumPages()
	num_exam_passed=0.
	num_page_thisexam=0
	print 'Checking each exam as even-paged...'
	for ipage in range(num_page):
		pagebody=PdfFileReader.getPage(ipage).extractText()
		if 'DEPARTMENTOFASTRONOMY\nUNIVERSITYOFFLORIDA' in pagebody:
			num_exam_passed+=0.5
			if num_exam_passed>num_disabled and (num_exam_passed-0.5)==num_disabled: num_disabled_page=ipage # record num_disabled_page
			if num_page_thisexam>2: # the starting page of each exam, except the first page
				if num_page_thisexam%2!=0: raise ValueError('Exam '+num_exam_passed+' has '+str(num_page_thisexam)+' pages, not even.') # check evenpage
				num_page_thisexam=1 # reset num_page_thisexam
			else: num_page_thisexam+=1
		else:
			num_page_thisexam+=1
	print 'Done.'
	print 'There are',num_exam_passed,'exams.'
	print 'In average',float(num_page)/num_exam_passed,'pages per exam.'
	print 'There are',num_disabled_page,'pages for disabled.'
	return num_page,num_disabled_page

def find_disabled_page(PdfFileReader,num_disabled):
	'''
	INPUT
	 PdfFileReader: PyPDF2.pdf.PdfFileReader
	RETURN
	 number of disabled page
	'''
	num_exam_passed=0.
	ipage = -1
	while num_exam_passed<=num_disabled:
		ipage+=1
		pagebody=PdfFileReader.getPage(ipage).extractText()
		if 'DEPARTMENTOFASTRONOMY\nUNIVERSITYOFFLORIDA' in pagebody: num_exam_passed+=0.5
	return ipage # which is num_disabled_page

def get_disabled_filename(pars):
	workpath, fileprefix=file_names(pars)
	outbase=workpath+pars.course+'_'+pars.section+'_'+pars.examnum
	disabledpdffile=outbase+'_disabled.pdf'
	normpdffile=outbase+'_norm.pdf'
	return disabledpdffile,normpdffile

def extract_disabled(pdffile,pars,checkeven=False):
	with open(pdffile,'rb') as fpdf:
		pdf=pypdf.PdfFileReader(fpdf)

		if checkeven: # checkeven and get page number
			num_page,num_disabled_page=nPageDisabled_CheckEven(pdf,pars.num_disabled)
		elif pars.num_disabled!=0: # get page number
			num_page=pdf.getNumPages()
			num_disabled_page=find_disabled_page(pdf,pars.num_disabled)

		if pars.num_disabled!=0: # do extraction
			disabledpdffile,normpdffile=get_disabled_filename(pars)

			# create exam for disabled students
			dwriter=pypdf.PdfFileWriter()
			for idis in range(num_disabled_page): dwriter.addPage(pdf.getPage(idis))
			with open(disabledpdffile,'wb') as fdisabled: dwriter.write(fdisabled)
			print 'Created:',disabledpdffile

			# create exam for normal students
			nwriter=pypdf.PdfFileWriter()
			for inorm in range(num_disabled_page,num_page): nwriter.addPage(pdf.getPage(inorm))
			with open(normpdffile,'wb') as fnorm: nwriter.write(fnorm)
			print 'Created:',normpdffile
			num_norm_page=num_page-num_disabled_page

def email_drc(pars):
	disabledpdffile,normpdffile=get_disabled_filename(pars)
	if pars.num_disabled > 1: toadd='''
	All the exams are integrated in one pdf file. Please print it once and separate the exams for different students.\n'''
	else: toadd=""
	mailtext='''\
	Hi,\n
	Please find the exam material for \n
	Course: %s
	Section: %s
	Instructor: %s
	Date of exam: %s
	Number of students with disability: %s\n
	Kindly tell the students to answer the exam in a scantron if possible.\n%s
	If you need any other information or document please let me know.\n
	Thanks,
	%s'''%(pars.course,pars.section,pars.instructor,pars.examdate,pars.num_disabled,toadd,myname)
	subject='%s section %s exam %s material'%(pars.course,pars.section,pars.examnum)
	mailto='testing@dso.ufl.edu'
	CCs=[instructor_email('Francisco'),instructor_email(pars.instructor)]
	BC=myemail
	attach=disabledpdffile
	send_email(mailtext,subject,mailto, cc=CCs, bcc=BC, attach=attach)

if __name__=='__main__':
	# email the exam to drc
	pars=load_pars()
	email_drc(pars)
