
import sys
import os
import requests

if len(sys.argv) ==0:
	print "MCTS reports path not specified"
else:
	rel_reports_path = sys.argv[1]

abspath = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))

abs_reports_path = os.path.join(abspath, rel_reports_path)  

count_empty_files = 0
total = 0
failed = 0
existing = 0
uploaded = 0
for path, subdir, files in os.walk(abs_reports_path):
	for name in files:

		mcts_report = os.path.join(path, name)

		mcts_report_basename = os.path.basename(mcts_report)

		type= None
		if 'imm' in mcts_report_basename.lower() and 'inf' in mcts_report_basename.lower():
			type = 'IMM1'
		elif 'imm' in mcts_report_basename.lower() and 'child' in mcts_report_basename.lower():
			type = 'IMM2'
		elif 'anc' in mcts_report_basename.lower():
			type = 'ANC'


		print mcts_report
		print type

		if type:
			url = 'http://mcts-analytics.cloudapp.net/mctsdata/uploadandsave/'
			file = {'file': open(mcts_report, 'rb')}
			r = requests.post(url, files=file, data={'benef_type':type})
			print 'file: '+str(mcts_report)+' was parsed for category '+str(type)+' with status: '+str(r.status_code)
			total += 1
			if r.status_code == 500:
				failed += 1
			elif 'zero' in r.text:
				count_empty_files += 1  
			elif 'exists' in r.text:
				existing += 1
			elif 'successfully' in r.text:
				uploaded += 1
			
			r.close()
print "\nTotal: "+str(total)
print "\nZero: "+str(count_empty_files)
print "\nExisting: "+str(existing)
print "\nFailed: "+str(failed)
print "\nUploaded: "+str(uploaded)