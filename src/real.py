import shutil, os
def real_score(outtxt,qnumber,other_right_answer):
	'''
	Correct the graded score if there are two right answers
	INPUTS
	    outtxt [str]
	        The output *.txt (moved from *.tex) from texam grading program.
	    qnumber [int]
	        The number of the question (of the master proof) that has two
	        right answers.
	    other_right_answer [int]
	        The number of the other right answer for Question qnumber other
	        than the first answer.
	'''
	realtxt=os.path.dirname(outtxt)+'/real.txt'
	shutil.copy(outtxt,realtxt)
	with open(realtxt,'r') as f: txtbody = f.read()
	txtbody=txtbody[txtbody.find("1 STUDENT"):txtbody.find("SIGMA")].split('\n')[:-3]
	lines=txtbody[1::2]
	scores=[int(l[45:47]) for l in lines]
	answer=[int(l[49+qnumber]) for l in lines]
	for i in range(len(scores)):
		if answer[i]==other_right_answer: scores[i]+=1
	reals=['\n'+l[:45]+'%2d'%scores[i]+l[47:] for i,l in enumerate(lines)]
	reals.insert(0,txtbody[0])
	with open(realtxt,'w') as f: f.writelines(reals)

if __name__=='__main__':
	outtxt='/astro/depot/exam/SEw19/12052_2/se2b.txt'
	real_score(outtxt,3,4)
