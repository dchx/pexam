from utils import *

def print_time(num_page,time_per_page=6.9/2.):
	'''
	time_per_page: in seconds
	'''
	estsec=time_per_page*int(num_page)
	hh=int(np.floor(estsec/3600.))
	mm=int((estsec-hh*3600.)/60.)
	if hh==0: time='%d minutes'%mm
	elif hh==1: time='%d hour and %d minutes'%(hh,mm)
	else: time='%d hours and %d minutes'%(hh,mm)
	return time
	
def exam_print_mail(num_page):
	time=print_time(num_page)

	mailtext='''\
	Hi all,\n
	The "main" printer in the copy room will be printing an exam in about 10 minutes. It will take about %s for it to print.\n
	If anyone wants to use the printer please do it now. If you have something urgent coming up and you want me to hold off the printing, do let me know.\n
	Thanks,
	%s'''%(time,myname)

	subject='Printing exam on main'
	mailto='clas-astro@mail.ufl.edu'
	confirm=raw_input('Are you sure to send an email\nTo: %s\nSubject: %s\nContent:\n%s\nSend? (yes/no) '%(mailto,subject,mailtext)).lower()
	if 'yes'.startswith(confirm):
		os.system("echo '%s' | mailx -v -s '%s' -r %s %s"%(mailtext,subject,myemail,mailto))

def lprprint(pdffile):
	confirm=raw_input('Are you sure to print the file %s on the "main" printer? (yes/no)'%pdffile).lower()
	if 'yes'.startswith(confirm):
		os.system('lpr -P main -o sides=two-sided-long-edge %s'%pdffile)
		print 'Sent print command to main to print %s.'%pdffile

def get_pdf_info(pdffile):
	page1=pypdf.PdfFileReader(pdffile).getPage(0).extractText()
	# get instructor first name
	ins=page1.split('SpecialCode\n')[1].split('\n')[1]
	fname=re.findall('[A-Z][a-z]*',ins.split('.')[1])[0]
	# get exam name
	examname=page1.split('UNIVERSITYOFFLORIDA\n')[1].split('\n')[0]
	return fname,examname

def print_complete_mail(pdffile):
	# Mail saying printing is complete
	mailtext='''\
	Hi all,\n
	The printing job is completed.\n
	Thanks,
	%s'''%myname
	subject='Re: Printing exam on main'
	mailto='clas-astro@mail.ufl.edu'
	confirm=raw_input('Are you sure to send an email\nTo: %s\nSubject: %s\nContent:\n%s\nSend? (yes/no) '%(mailto,subject,mailtext)).lower()
	if 'yes'.startswith(confirm):
		os.system("echo '%s' | mailx -v -s '%s' -r %s %s"%(mailtext,subject,myemail,mailto))
		print 'Sent\nTo: %s\nSubject: %s\nContent:\n%s'%(mailto,subject,mailtext)

	# Mail saying exam in cabinet
	insname,examname=get_pdf_info(pdffile) # (InstructorName, ExamName)
	mailtext='''\
	Hi %s,\n
	The printed %s is in the cabinet now.\n
	Thanks,
	%s'''%(insname,examname,myname)
	subject='Exam printed'
	# set mailto address 
	mailto=instructor_email(insname)
	CC=instructor_email('Francisco')
	BC=myemail
	# send email
	confirm=raw_input('Are you sure to send an email\nTo: %s\nCC: %s\nBC: %s\nSubject: %s\nContent:\n%s\nSend? (yes/no) '%(mailto,CC,BC,subject,mailtext)).lower()
	if 'yes'.startswith(confirm):
		os.system("echo '%s' | mailx -v -s '%s' -r %s -c %s -b %s %s"%(mailtext,subject,myemail,CC,BC,mailto))

if __name__=='__main__':
	readme='''Usage:
	    python printing.py MODE FILE
	MODE:
	    alert,a - Email printing alart: printing in 10 minutes.
	    print,p - Do printing.
	    complete,c - Email that printing is complete.
	FILE:
	    the pdf file to print'''
	args=sys.argv
	if len(args)!=3: raise ValueError(readme)
	mode=sys.argv[1].lower()
	pfile=sys.argv[2]

	if 'alert'.startswith(mode): exam_print_mail(pypdf.PdfFileReader(pfile).getNumPages())
	elif 'print'.startswith(mode): lprprint(pfile)
	elif 'complete'.startswith(mode): print_complete_mail(pfile)
	else: raise ValueError(readme)
