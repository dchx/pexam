# 18sep2018: Chenxing working on converting qq2tex.pl to qq2tex.py

#!/perl -w
# JPO 5FEB00 code to convert simple QQ file to TEX QQ file
#     6FEB00 handle ** and // 
# but not yet **-> or **_ also we need to handle terminating * and )
#     8FEB00 limit line length to 80 cols
#			15FEB00 renamed qq2tex from qqfix
#		  			ignore (and do not output) header lines before first QQ!
#						put "S" for stacked up against { as {S
#			18FEB00 fixed format using bct/ect
#			28FEB00 fixed correct answer bug by eliminating space between { and number
#			(to do) store answers in strings for shuffle of correct to (1)

# debug variable that allows display of output lines on terminal
show=0	# 0=false, 1=true

open (QQFILE, qfile) || die "cannot open QQFILE: !"

# give output file the extension .qu for TeX format question file
outfile=fileprefix+'.qu'

open (QQOUTFILE, ">outfile") || die "cannot open QQOUTFILE: !"

lcnt=0 # count of lines ... may not be needed

# proof checking counts
QQcnt=AAcnt=0
AA1cnt=AA2cnt=AA3cnt=AA4cnt=AA5cnt=ERRcnt=0

# flags
QQmode=0  # 0= AA, 1=QQ

# start main loop, reading all input lines
while(<QQFILE>){
	lcnt++ # count lines
	line=_
	line=~s/\s+/\n/ # trim trailing whitespace
	# make sure answers parens at start/end of line have whitespace to left/right
	if index(line,"(",0)==0: line=" "+line
	if index(line,")",length(line)-2)!=-1: line=line[0:length(line)-1]+" \n"

	# handle QQ lines after 1st QQ line
	if QQmode==1: QQmode=2

	# handle QQ
	if (/^QQ/){
		line="\\QT{QQ \\bct"+line[2:]	# add TEX code
		QQcnt++
		QQmode=1 	# reading a QQ
		if (QQcnt != 1) {
			line="}\n"+line  # not 1st QQ so hang } on end of previous AA
			# now check to see if previous AA set had all 5 answers
			if (AA1cnt!=1 || AA2cnt!=1 ||AA3cnt!=1 || AA4cnt!=1 ||AA5cnt!=1){
				print "Error in question ",QQcnt-1,"\n" # flag errors
				print AA1cnt,AA2cnt,AA3cnt,AA4cnt,AA5cnt,"\n"
			 	ERRcnt++
			}
		AA1cnt=AA2cnt=AA3cnt=AA4cnt=AA5cnt=0 # reset for next AA
		}
	}

	# handle AA 
	# replace AA followed by "S" with "\ect}\n{S"  which terminates the QQ block and starts the answer block
	if (line=~s/^AA\s*S/\\ect}\n{S/) {
		AAcnt++ 
		QQmode=0
	}
	# replace AA (no "S" but with correct answer number"n") with "\ect}\n{n"  
	if (line=~s/^AA\s*(\d)/\\ect}\n{1/) {
		AAcnt++ 
		QQmode=0
		# now eliminate any blanks between { and correct answer number
	}
	# replace AA (no "S") with "\ect}\n{"  
	if (line=~s/^AA/\\ect}\n{/) {
		AAcnt++ 
		QQmode=0
		# now eliminate any blanks between { and correct answer number
	}

	# check for proper number of answers (will detect both missing and duplicated instances)
	start=-1
	while ((start=index(line," (1) ",start)) !=-1) {
		AA1cnt++
		start++
	}
	start=-1
	while ((start=index(line," (2) ",start)) !=-1) {
		AA2cnt++
		start++
	}
	start=-1
	while ((start=index(line," (3) ",start)) !=-1) {
		AA3cnt++
		start++
	}
	start=-1
	while ((start=index(line," (4) ",start)) !=-1) {
		AA4cnt++
		start++
	}
	start=-1
	while ((start=index(line," (5) ",start)) !=-1) {
		AA5cnt++
		start++
	}

	# handle super/sub scripts "**"
	start=length(line)
	while ((start=rindex(line,"**",start)) !=-1) {
	# ok ... ** found, work to right to whitespace
		if ((rws=index(line," ",start)) !=-1) {
			r="}\$"+line[rws:]
		}
		else {
			r="}\$ \n"
			rws=length(line)-1
		}
		# ok ... work to left to whitespace
		if ((lws=rindex(line," ",start)) !=-1) {
			l=line[0:lws+1]+"\$"
		}
		else {
			l="\$"
			lws=0
		}
		# now insert the replacement characters
		m=line[lws+1:start]+"\^\{"+line[start+2:rws]
		line=l+m+r
		start--
	}

	# handle super/sub scripts "//"
	start=length(line)
	while ((start=rindex(line,"//",start)) !=-1) {
	# ok ... // found, work to right to whitespace
		if ((rws=index(line," ",start)) !=-1) {
			r="}\$"+line[rws:]
		}
		else {
			r="}\$ \n"
			rws=length(line)-1
		}
		# ok ... work to left to whitespace
		if ((lws=rindex(line," ",start)) !=-1) {
			l=line[0:lws+1]+"\$"
		}
		else {
			l="\$"
			lws=0
		}
		# now insert the replacement characters
		m=line[lws+1:start]+"_\{"+line[start+2:rws]
		line=l+m+r
		start--
	}

	# OK ... finish up by printing this line
	# put ~ in front of QQ lines
	if (QQmode==2) { line="~"+line }
	# keep output line length <=80
	if (length(line) >80) {
		line=line[0:80]+" \\"+line[80:]  # tex will join lines
	}
	# 2/18/00	if ((length(line) != 1) && (QQcnt > 0)) {	
	# do not keep blank lines or lines before 1st QQ
	if (QQcnt > 0) {	# do not keep lines before 1st QQ
		if (show) { print line }
		print QQOUTFILE line
	}
} # end of main input loop

# now check to see if last AA set had all 5 answers
if (AA1cnt!=1 || AA2cnt!=1 ||AA3cnt!=1 || AA4cnt!=1 ||AA5cnt!=1){
	print "\nError in question ",QQcnt,": " # flag errors
	print AA1cnt,AA2cnt,AA3cnt,AA4cnt,AA5cnt,"\n"
 	ERRcnt++
}

# put brace at end of last QQ/AA pair
if (show) { print "}\n" }
print QQOUTFILE "}\n"

# print report
print "QQ: ",QQcnt," AA: ",AAcnt," errors: ",ERRcnt,"\n"

close (QQFILE)
close (QQOUTFILE)
