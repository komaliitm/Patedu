
import sys
import os
import requests

if len(sys.argv) ==0:
	print "MCTS reports path not specified"
else:
	rel_reports_path = sys.argv[1]

abspath = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))

abs_reports_path = os.path.join(abspath, rel_reports_path)  

for path, subdir, files in os.walk(abs_reports_path):
	for name in files:

		mcts_report = os.path.join(path, name)

		mcts_report_basename = os.path.basename(mcts_report)

		type= None
		if 'imm' in mcts_report_basename.lower() and 'infant' in mcts_report_basename.lower():
			type = 'IMM1'
		elif 'imm' in mcts_report_basename.lower() and 'child' in mcts_report_basename.lower():
			type = 'IMM2'
		elif 'anc' in mcts_report_basename.lower():
			type = 'ANC'


		print mcts_report
		print type

		if type:
			url = 'http://localhost:8000/mctsdata/uploadandsave/'
			file = {'file': open(mcts_report, 'rb')}
			r = requests.post(url, files=file, data={'benef_type':type})
			print 'file: '+str(mcts_report)+' was parsed for category '+str(type)+' with status: '+str(r.status_code)+' '+r.reason
			r.close()