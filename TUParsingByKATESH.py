#######################################################################################################################################
#Author: KATESH																														  #
#######################################################################################################################################
	
import xml.etree.cElementTree as ET
from datetime import date
import functools
##################################---TO REMOVE NAMESPACE---###################################

normname = lambda name:name[1:].split('}')[1] if name[0]=='{' else name

###########################################--- ----###########################################

###########################---RECURSIVELY PARSE XML FOR ANY TAG---###########################

def RecursiveParsing(root,r):
	if len(root)>0:	
		li={}
		for i in root:
			a = RecursiveParsing(i,r)
			li.update(a)
		if normname(root.tag)=="product":
			r[normname(root.tag)] = li
		else:
			return {normname(root.tag):li}
	else:	
		return {normname(root.tag):root.text}
	return r	

###########################################--- ---############################################

##############################---COMPUTE TU VARIABLES FROM XML---#############################

def PstDueRng(val):
	if val>=120:
		return '120+'
	elif val>=90:
		return '90+'
	elif val>=60:
		return '60+'
	elif val>=30:
		return '30+'
	else:
		return 'current'
	

def TUParsing(XmlName):
	tree = ET.parse(XmlName)
	root = tree.getroot()
	j=0
	ResultDictionary = {}	
	
	maxmonsch = 0
	psmcount = 0
	pflist = []
	psmc = []
	totrades = 0
	inddict = {}
	portdict = {}
	actype = {}
	mactype ={}
	numtrad1 = 0
	numtrad2 = 0
	numtrad3 = 0
	numtradind1 = {}
	numtradind2 = {}
	numtradind3 = {}
	numtradport1 = {}
	numtradport2 = {}
	numtradport3 = {}
	numtradaccnt1 = {}
	numtradaccnt2 = {}
	numtradaccnt3 = {}
	monloantaken = {}
	acctratindus = {}
	acctratport = {}
	maxhcred = 0
	maxcredlim = 0
	avgcre = 0
	avghighcre = 0
	NTRANGE = {}
	NTINTYPERANGE = {}
	PstDueRngVal = {}
	PstDueRngValPF = {}
	avgcrelimtype = {}
	avghighcretype = {}
	maxmonschind = {}
	maxmonschport = {}
	highaccntrattype = {}
	avgcreindus = {}
	avgcreport = {}
	avghighcreindus = {}
	avghighcreport = {}
	avgnumtrad = []
	avgnumnottrad = []
	numcon2 = 0
	numcon3 = 0
	maxconsnotp = 0
	maxconsp = 0
	
	tr = RecursiveParsing(root[2],{})
	yy,mm,dd = tr['transactionControl']['tracking']['transactionTimeStamp'][:10].split('-')
	d1 = date(int(yy),int(mm),int(dd))
	
	for i in tree.iter(tag='{http://www.transunion.com/namespace}trade'):
		totrades+=1			
		r=RecursiveParsing(i,{})
		industry = r['trade']['subscriber']['industryCode']
		portfolio = r['trade']['portfolioType']
		inddict[industry] = inddict[industry]+1 if industry in inddict else 1
		portdict[portfolio] = portdict[portfolio]+1 if portfolio in portdict else 1	
		if 'terms' in r['trade']:
			temp = r['trade']['terms']['scheduledMonthlyPayment']
			if 'account' in r['trade']:
				atype = r['trade']['account']['type']
				if atype in mactype:
					if temp>mactype[atype]:
						mactype[atype] = temp
				else:
					mactype[atype] = temp
			maxmonschind[industry] = temp if industry not in maxmonschind else maxmonschind[industry] if maxmonschind[industry]>temp else temp
			maxmonschport[portfolio] = temp if portfolio not in maxmonschport else maxmonschport[portfolio] if maxmonschport[portfolio]>temp else temp	
			if temp>int(maxmonsch):
				maxmonsch = temp
			if 'paymentFrequency' in r['trade']['terms']:
				pflist.append(r['trade']['terms']['paymentFrequency'])
			if 'paymentScheduleMonthCount' in r['trade']['terms']:
				countt = r['trade']['terms']['paymentScheduleMonthCount']
				if countt!='MIN':
					psmc.append(countt)
					if psmcount<countt:
						psmcount = countt
		if 'account' in r['trade']:
			atype = r['trade']['account']['type']
			actype[atype] = actype[atype]+1 if atype in actype else 1
			if 'creditLimit' in r['trade']:	
				credit = r['trade']['creditLimit']
				avgcrelimtype[atype] = [credit,avgcrelimtype[atype][1]+1] if atype in avgcrelimtype else [credit,1]
				avgcreindus[industry] = [credit,avgcreindus[industry][1]+1] if industry in avgcreindus else [credit,1]
				avgcreport[portfolio]= [credit,avgcreport[portfolio][1]+1] if portfolio in avgcreport else [credit,1]
			if 'highCredit' in r['trade']:
				highcre = r['trade']['highCredit']
				avghighcretype[atype] = [highcre,avghighcretype[atype][1]+1] if atype in avghighcretype else [highcre,1]
				avghighcreindus[industry] = [highcre,avghighcreindus[industry][1]+1] if industry in avghighcreindus else [highcre,1]
				avghighcreport[portfolio] = [highcre,avghighcreport[portfolio][1]+1] if portfolio in avghighcreport else [highcre,1]
			if 'accountRating' in r['trade']:
				rate = r['trade']['accountRating'] 
				highaccntrattype[atype] = rate if atype not in highaccntrattype else rate if highaccntrattype[atype]<rate else highaccntrattype[atype]
			
			
		if 'accountRating' in r['trade']:
			indus = r['trade']['subscriber']['industryCode']
			acctratindus[indus] = r['trade']['accountRating'] if indus not in acctratindus else r['trade']['accountRating'] if r['trade']['accountRating']>acctratindus[indus] else acctratindus[indus] 
			port = r['trade']['portfolioType']
			acctratport[port] =  r['trade']['accountRating'] if port not in acctratport else r['trade']['accountRating'] if r['trade']['accountRating']>acctratport[port] else acctratport[port] 
			
		
		if 'highCredit' in r['trade']:
			if maxhcred<float(r['trade']['highCredit']):
				maxhcred = float(r['trade']['highCredit'])
			avghighcre+=float(r['trade']['highCredit'])
			
		if 'creditLimit' in r['trade']:
			if maxcredlim<float(r['trade']['creditLimit']):
				maxcredlim = float(r['trade']['creditLimit'])
			avgcre+=float(r['trade']['creditLimit'])
		ic=0
		if 'paymentHistory' in r['trade']:
			if 'paymentPattern' in r['trade']['paymentHistory']:
				if 'text' in r['trade']['paymentHistory']['paymentPattern']:
					ic+=1
					ppat = r['trade']['paymentHistory']['paymentPattern']['text']
					avgnumtrad.append([ppat.count('1'),ic])
					avgnumnottrad.append([ppat.count('X'),ic])
					maxconsp = maxconsp if maxconsp > max((ppat).split('X')) else max(ppat.split('X'))
					maxconsnotp = max(ppat.split('1')) if max(ppat.split('1'))>maxconsnotp
					numcon2 += functools.reduce(lambda a,b:a+b,list[ppat.split('1')])
					numcon3 = 
		if 'dateOpened' in r['trade']:
			yt,mt,dt = r['trade']['dateOpened'].split('-')
			d2 = date(int(yt),int(mt),int(dt))
			diff = d2-d1
			days = diff.days
			indust = r['trade']['subscriber']['industryCode']
			monloantaken[mt] = monloantaken[mt]+1 if mt in monloantaken else 1
			if days<=15:
				NTRANGE['15'] = NTRANGE['15']+1 if '15' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '15' in NTINTYPERANGE:
					NTINTYPERANGE['15'] = {indust:NTINTYPERANGE['15'][indust]+1} if indust in NTINTYPERANGE['15'] else {indust:1}
				else:
					NTINTYPERANGE['15'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
			elif days<=30:
				NTRANGE['30'] = NTRANGE['30']+1 if '30' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				numtrad1+=1
				numtradind1[industry] = numtradind1[industry]+1 if industry in numtradind1 else 1
				numtradport1[industry] = numtradport1[industry]+1 if industry in numtradport1 else 1
				numtradaccnt1[industry] = numtradaccnt1[industry]+1 if industry in numtradaccnt1 else 1
				if '30' in NTINTYPERANGE:
					NTINTYPERANGE['30'] = {indust:NTINTYPERANGE['30'][indust]+1} if indust in NTINTYPERANGE['30'] else {indust:1}
				else:
					NTINTYPERANGE['30'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					PstDueRngVal['30'][pf] = PstDueRngVal['30'][pf]+1 if pf in PstDueRngVal['30'] else 1 
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['30'][pf][porto] = PstDueRngValPF['30'][pf][porto]+1 if porto in PstDueRngValPF['30'][pf] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
				
			elif days<=60:
				NTRANGE['60'] = NTRANGE['60']+1 if '60' in NTRANGE else 1				
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				numtrad2+=1
				numtradind2[industry] = numtradind2[industry]+1 if industry in numtradind2 else 1
				numtradport2[industry] = numtradport2[industry]+1 if industry in numtradport2 else 1
				numtradaccnt2[industry] = numtradaccnt2[industry]+1 if industry in numtradaccnt2 else 1
				if '60' in NTINTYPERANGE:
					NTINTYPERANGE['60'] = {indust:NTINTYPERANGE['60'][indust]+1} if indust in NTINTYPERANGE['60'] else {indust:1}
				else:
					NTINTYPERANGE['60'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					PstDueRngVal['60'][pf] = PstDueRngVal['60'][pf]+1 if pf in PstDueRngVal['60'] else 1 
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['60'][pf][porto] = PstDueRngValPF['60'][pf][porto]+1 if porto in PstDueRngValPF['60'][pf] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
					
			elif days<=90:
				NTRANGE['90'] = NTRANGE['90']+1 if '90' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				numtrad3+=1
				numtradind3[industry] = numtradind3[industry]+1 if industry in numtradind3 else 1
				numtradport3[industry] = numtradport3[industry]+1 if industry in numtradport3 else 1
				numtradaccnt3[industry] = numtradaccnt3[industry]+1 if industry in numtradaccnt3 else 1
				if '90' in NTINTYPERANGE:
					NTINTYPERANGE['90'] = {indust:NTINTYPERANGE['90'][indust]+1} if indust in NTINTYPERANGE['90'] else {indust:1}
				else:
					NTINTYPERANGE['90'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					PstDueRngVal['90'][pf] = PstDueRngVal['90'][pf]+1 if pf in PstDueRngVal['90'] else 1 
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['90'][pf][porto] = PstDueRngValPF['90'][pf][porto]+1 if porto in PstDueRngValPF['90'][pf] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
					
			elif days<=120:
				NTRANGE['120'] = NTRANGE['120']+1 if '120' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '120' in NTINTYPERANGE:
					NTINTYPERANGE['120'] = {indust:NTINTYPERANGE['120'][indust]+1} if indust in NTINTYPERANGE['120'] else {indust:1}
				else:
					NTINTYPERANGE['120'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
			elif days<=180:
				NTRANGE['180'] = NTRANGE['180']+1 if '180' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '180' in NTINTYPERANGE:
					NTINTYPERANGE['180'] = {indust:NTINTYPERANGE['180'][indust]+1} if indust in NTINTYPERANGE['180'] else {indust:1}
				else:
					NTINTYPERANGE['180'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					pf = PstDueRng(int(r['trade']['pastDue']))
					porto = r['trade']['portfolioType']
					PstDueRngVal['180'][pf] = PstDueRngVal['180'][pf]+1 if pf in PstDueRngVal['180'] else 1 
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['180'][pf][porto] = PstDueRngValPF['180'][pf][porto]+1 if porto in PstDueRngValPF['180'][pf] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
				
			elif days <=365:
				NTRANGE['1Y'] = NTRANGE['1Y']+1 if '1Y' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '1Y' in NTINTYPERANGE:
					NTINTYPERANGE['1Y'] = {indust:NTINTYPERANGE['1Y'][indust]+1} if indust in NTINTYPERANGE['1Y'] else {indust:1}
				else:
					NTINTYPERANGE['1Y'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					PstDueRngVal['1Y'][pf] = PstDueRngVal['1Y'][pf]+1 if pf in PstDueRngVal['1Y'] else 1 
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['1Y'][pf][porto] = PstDueRngValPF['1Y'][pf][porto]+1 if porto in PstDueRngValPF['1Y'][pf] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
					
			elif int(days/365)<=2:
				NTRANGE['2Y'] = NTRANGE['2Y']+1 if '2Y' in NTRANGE else 1	
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '2Y' in NTINTYPERANGE:
					NTINTYPERANGE['2Y'] = {indust:NTINTYPERANGE['2Y'][indust]+1} if indust in NTINTYPERANGE['2Y'] else {indust:1}
				else:
					NTINTYPERANGE['2Y'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
			elif int(days/365)<=3:
				NTRANGE['3Y'] = NTRANGE['3Y']+1 if '3Y' in NTRANGE else 1	
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '3Y' in NTINTYPERANGE:
					NTINTYPERANGE['3Y'] = {indust:NTINTYPERANGE['3Y'][indust]+1} if indust in NTINTYPERANGE['3Y'] else {indust:1}
				else:
					NTINTYPERANGE['3Y'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
			elif int(days/365)<=5:
				NTRANGE['5Y'] = NTRANGE['5Y']+1 if '5Y' in NTRANGE else 1
				NTRANGE['Ever'] = NTRANGE['Ever']+1 if 'Ever' in NTRANGE else 1
				if '5Y' in NTINTYPERANGE:
					NTINTYPERANGE['5Y'] = {indust:NTINTYPERANGE['5Y'][indust]+1} if indust in NTINTYPERANGE['5Y'] else {indust:1}
				else:
					NTINTYPERANGE['5Y'] = {indust:1}
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
			else:
				NTRANGE['ever'] = NTRANGE['ever']+1 if 'ever' in NTRANGE else 1
				if 'ever' in NTINTYPERANGE:
					NTINTYPERANGE['ever'] = {indust:NTINTYPERANGE['ever'][indust]+1} if indust in NTINTYPERANGE['ever'] else {indust:1}
				else:
					NTINTYPERANGE['ever'] = {indust:1}
				if 'pastDue' in r['trade']:
					PstDueRngVal['ever'][pf] = PstDueRngVal['ever'][pf]+1 if pf in PstDueRngVal['ever'] else 1
					PstDueRngValPF['ever'][pf][porto] = PstDueRngValPF['ever'][pf][porto]+1 if porto in PstDueRngValPF['ever'][pf] else 1
			
	Qdict = {}
	numinq1 = 0
	numinq2 = 0
	numinq3 = 0
	NIRANGE = {}
	NILETYPERANGE = {}
	for i in tree.iter(tag='{http://www.transunion.com/namespace}inquiry'):
		r=RecursiveParsing(i,{})
		Qindustry = r['inquiry']['subscriber']['industryCode']
		lender = r['inquiry']['subscriber']['name']['unparsed']
		Qdict[Qindustry] = Qdict[Qindustry]+1 if Qindustry in Qdict else 1
		if 'date' in r['inquiry']:
			yt,mt,dt = r['inquiry']['date'].split('-')
			d2 = date(int(yt),int(mt),int(dt))
			diff = d2-d1
			days = diff.days
			if days<=1:
				numinq1+=1
				NIRANGE['1'] = NIRANGE['1']+1 if '1' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '1' in NILETYPERANGE:
					NILETYPERANGE['1'] = {lender:NILETYPERANGE['1'][lender]+1} if lender in NILETYPERANGE['1'] else {lender:1}
				else:
					NILETYPERANGE['1'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=2:
				numinq1+=1
				NIRANGE['2'] = NIRANGE['2']+1 if '2' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '2' in NILETYPERANGE:
					NILETYPERANGE['2'] = {lender:NILETYPERANGE['2'][lender]+1} if lender in NILETYPERANGE['2'] else {lender:1}
				else:
					NILETYPERANGE['2'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=3:
				numinq1+=1
				NIRANGE['3'] = NIRANGE['3']+1 if '3' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '3' in NILETYPERANGE:
					NILETYPERANGE['3'] = {lender:NILETYPERANGE['3'][lender]+1} if lender in NILETYPERANGE['3'] else {lender:1}
				else:
					NILETYPERANGE['3'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=7:
				NIRANGE['7'] = NIRANGE['7']+1 if '7' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				numinq1+=1
				if '7' in NILETYPERANGE:
					NILETYPERANGE['7'] = {lender:NILETYPERANGE['7'][lender]+1} if lender in NILETYPERANGE['7'] else {lender:1}
				else:
					NILETYPERANGE['7'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=15:
				numinq1+=1
				NIRANGE['15'] = NIRANGE['15']+1 if '15' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '15' in NILETYPERANGE:
					NILETYPERANGE['15'] = {lender:NILETYPERANGE['15'][lender]+1} if lender in NILETYPERANGE['15'] else {lender:1}
				else:
					NILETYPERANGE['15'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=30:
				numinq1+=1
				NIRANGE['30'] = NIRANGE['30']+1 if '30' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '30' in NILETYPERANGE:
					NILETYPERANGE['30'] = {lender:NILETYPERANGE['30'][lender]+1} if lender in NILETYPERANGE['30'] else {lender:1}
				else:
					NILETYPERANGE['30'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=60:
				numinq2+=1
				NIRANGE['60'] = NIRANGE['60']+1 if '60' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '60' in NILETYPERANGE:
					NILETYPERANGE['60'] = {lender:NILETYPERANGE['60'][lender]+1} if lender in NILETYPERANGE['60'] else {lender:1}
				else:
					NILETYPERANGE['60'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=120:
				NIRANGE['120'] = NIRANGE['120']+1 if '120' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '120' in NILETYPERANGE:
					NILETYPERANGE['120'] = {lender:NILETYPERANGE['120'][lender]+1} if lender in NILETYPERANGE['120'] else {lender:1}
				else:
					NILETYPERANGE['120'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days<=180:
				NIRANGE['180'] = NIRANGE['180']+1 if '180' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '180' in NILETYPERANGE:
					NILETYPERANGE['180'] = {lender:NILETYPERANGE['180'][lender]+1} if lender in NILETYPERANGE['180'] else {lender:1}
				else:
					NILETYPERANGE['180'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif days <=365:
				NIRANGE['1Y'] = NIRANGE['1Y']+1 if '1Y' in NIRANGE else 1
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '1Y' in NILETYPERANGE:
					NILETYPERANGE['1Y'] = {lender:NILETYPERANGE['1Y'][lender]+1} if lender in NILETYPERANGE['1Y'] else {lender:1}
				else:
					NILETYPERANGE['1Y'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			elif int(days/365)<=2:
				NIRANGE['2Y'] = NIRANGE['2Y']+1 if '2Y' in NIRANGE else 1	
				NIRANGE['Ever'] = NIRANGE['Ever']+1 if 'Ever' in NIRANGE else 1
				if '2Y' in NILETYPERANGE:
					NILETYPERANGE['2Y'] = {lender:NILETYPERANGE['2Y'][lender]+1} if lender in NILETYPERANGE['2Y'] else {lender:1}
				else:
					NILETYPERANGE['2Y'] = {lender:1}
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
			else:
				NIRANGE['ever'] = NIRANGE['Ever']+1 if 'ever' in NIRANGE else 1
				if 'ever' in NILETYPERANGE:
					NILETYPERANGE['ever'] = {lender:NILETYPERANGE['ever'][lender]+1} if indust in NILETYPERANGE['ever'] else {lender:1}
				else:
					NILETYPERANGE['ever'] = {lender:1}
	pfset = set(pflist)
	pfdict={}
	for i in pfset:
		pfdict[i]=pflist.count(i)
	max_key = max(pfdict, key=lambda k: pfdict[k])
		
	##################################################---RESULT DICTIONARY---##########################################################
	
	ResultDictionary['totnumtrad'] = totrades
	ResultDictionary['numtype'] = len(actype)
	ResultDictionary['numtradtype'] = actype
	ResultDictionary['numindtrad'] = inddict
	ResultDictionary['numporttrad'] = portdict
	ResultDictionary['maxschmonthfreqcount'] = psmc.count(psmcount)
	ResultDictionary['maxschmonthly'] = max_key
	ResultDictionary['payfreq'] = list(pfset) 
	ResultDictionary['maxloandur'] = psmcount
	if 'monhly' in pfdict:
		ResultDictionary['nummonth'] = pfdict['monthly']	
	if 'bi-weekly' in pfdict:
		ResultDictionary['numbi'] = pfdict['bi-weekly']
	if 'semi-monthly' in pfdict:
		ResultDictionary['numsemi'] = pfdict['semi-monthly']
	ResultDictionary['maxmonschtype'] = mactype
	ResultDictionary['numinqtype'] = Qdict
	ResultDictionary['numtrad1'] = numtrad1
	ResultDictionary['numtrad2'] = numtrad2
	ResultDictionary['numtrad3'] = numtrad3
	ResultDictionary['numtradind1'] = numtradind1
	ResultDictionary['numtradind2'] = numtradind2
	ResultDictionary['numtradind3'] = numtradind3
	ResultDictionary['numtradport1'] = numtradport1
	ResultDictionary['numtradport2'] = numtradport2
	ResultDictionary['numtradport3'] = numtradport3
	ResultDictionary['numtradaccnt1'] = numtradaccnt1
	ResultDictionary['numtradaccnt2'] = numtradaccnt2
	ResultDictionary['numtradaccnt3'] = numtradaccnt3
	ResultDictionary['numinq1'] = numinq1
	ResultDictionary['numinq2'] = numinq2
	ResultDictionary['numinq3'] = numinq3
	ResultDictionary['monloantaken'] = monloantaken
	ResultDictionary['acctratindus'] = acctratindus
	ResultDictionary['ssnmnum'] = normname(root[3][1][1][1][1].tag)
	ResultDictionary['acctratport'] = acctratport
	ResultDictionary['maxhcred'] = maxhcred
	ResultDictionary['maxcredlim'] = maxcredlim
	ResultDictionary['avghighcre'] = avghighcre/totrades
	ResultDictionary['avgcre'] = avgcre/totrades
	ResultDictionary['NTRANGE'] = NTRANGE 
	ResultDictionary['NTINTYPERANGE'] = NTINTYPERANGE
	ResultDictionary['NIRANGE'] = NIRANGE
	ResultDictionary['NILETYPERANGE'] = NILETYPERANGE
	ResultDictionary['PstDueRngVal'] = PstDueRngVal
	ResultDictionary['PstDueRngValPF'] = PstDueRngValPF
	ResultDictionary['custstatind'] = normname(root[3][1][1][1][2].tag)
	ResultDictionary['maxmonschind'] = maxmonschind
	ResultDictionary['maxmonschport'] = maxmonschport
	ResultDictionary['highaccntrattype'] = highaccntrattype
	avgcrelimtype1 = {}
	avghighcretype1 = {}
	avgcreindus1 = {}
	avgcreport1 = {}
	avghighcreindus1 = {}
	avghighcreport1 = {}
	for i in avgcrelimtype:
		avgcrelimtype1[i] = float(float(avgcrelimtype[i][0])/float(avgcrelimtype[i][1]))
	for j in avghighcretype:
		avghighcretype1[j] = float(float(avghighcretype[j][0])/avghighcretype[j][1])
	for i in avgcreindus:
		avgcreindus1[i] = float(float(avgcreindus[i][0])/float(avgcreindus[i][1]))
	for j in avgcreport:
		avgcreport1[i] = float(float(avgcreport[j][0])/float(avgcreport[j][1]))
	for i in avghighcreindus:
		avghighcreindus1[i] = float(float(avghighcreindus[i][0])/float(avghighcreindus[i][1]))
	for j in avghighcreport:
		avghighcreport1[i] = float(float(avghighcreport[j][0])/float(avghighcreport[j][1]))
	ResultDictionary['avgcrelimtype'] = avgcrelimtype1
	ResultDictionary['avghighcretype'] = avghighcretype1
	ResultDictionary['avgcreindus'] = avgcreindus1
	ResultDictionary['avgcreport'] = avgcreport1
	ResultDictionary['avghighcreindus'] = avghighcreindus1
	ResultDictionary['avgcrehighport'] = avghighcreport1
	ResultDictionary['maxconsp'] = maxconsp
	ResultDictionary['maxconsnotp'] = maxconsnotp
	return ResultDictionary
	
	###########################################################--- ---#################################################################

###########################################--- ----###########################################

Result = TUParsing("TU.xml")
print(Result)
print(len(Result))