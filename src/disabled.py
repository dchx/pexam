from utils import *

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
	return ipage

def extract_disabled(PdfFileReader,num_disabled_page):
	 num_page=PdfFileReader.getNumPages()

	# create exam for disabled students
	dwriter=pypdf.PdfFileWriter()
	for idis in range(num_disabled_page): dwriter.addPage(PdfFileReader.getPage(idis))
	disabledpdffile=outbase+'_disabled.pdf'
	with open(disabledpdffile,'wb') as fdisabled: dwriter.write(fdisabled)
	print 'Created:',disabledpdffile

	# create exam for normal students
	nwriter=pypdf.PdfFileWriter()
	for inorm in range(num_disabled_page,num_page): nwriter.addPage(PdfFileReader.getPage(inorm))
	normpdffile=outbase+'_norm.pdf'
	with open(normpdffile,'wb') as fnorm: nwriter.write(fnorm)
	print 'Created:',normpdffile
	num_norm_page=num_page-num_disabled_page


def email_drc(pars):
	mailtext='''\
	Hi,\n
	Please find the exam material for \n
	Course: %s
	Section: %s
	Instructor: %s
	Date of exam: %s
	Number of students with disability: %s\n
	Kindly tell the students to answer the exam in a scantron if possible.\n
	If you need any other information or document please let me know.\n
	Thanks,
	Chenxing'''%(pars.course,pars.section,pars.instructor,pars.examdate,pars.num_disabled)

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
	return num_disabled_page
