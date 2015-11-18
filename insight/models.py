from insight import db
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
  as Serializer, BadSignature, SignatureExpired)
from flask import current_app

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class Role(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	rolename = db.Column(db.String(64))
	
	users = db.relationship('User',backref="role")

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64) ,index=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


	def hash_password(self,password):
		self.password_hash = pwd_context.encrypt(password)


	def verify_password(self,password):
		return pwd_context.verify(password, self.password_hash)


	def generate_auth_token(self,expiration=600):
		s = Serializer(current_app.config['SECRET_KEY'],expires=expiration)
		#s = Serializer(current_app.config['SECRET_KEY'],expires=expiration)

		return s.dumps({'id',self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config(['SECRET_KEY']))
		try:
			data = s.loads(token)	
		except SignatureExpired:
			return None
		
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return user

	#encrypted dictionary of user id with expiration time
	def generate_auth_token(self,expiration=600):		
		s = Serializer(current_app.config['SECRET_KEY'],expires_in=600)
		return s.dumps({'id':self.id})

	#decode token and load user wit the id
	@staticmethod
	def verify_auth_token(token):
		s =Serializer(current_app.config['SECRET_KEY'])
		#print current_app.config['SECRET_KEY']
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return User






class Region(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	constituencies = db.relationship('Constituency',backref='region',lazy='dynamic')
	code = db.Column(db.String(4))

	def __repr__(self):
		return "<Region> %r  %r"  %(self.name,self.code)

class Constituency(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(40))
	region_id = db.Column(db.Integer,db.ForeignKey('region.id'))
	
	#simple one to many relationship1
	polling_stations = db.relationship('PollingStation',backref='constituency',lazy='dynamic')

	#many to many relationship type1
	elections = db.relationship('ElectionConstituency' ,backref='constituency')

	def __repr__(self):
		return "<Constituence > %r" %self.name

class PollingStation(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(40))
	constituency_id = db.Column(db.Integer,db.ForeignKey('constituency.id'))


	elections = db.relationship('ElectionPollingStation' ,backref='pollinstation')


	def __repr__(self):
		return "<Constituency > %r" %self.name



class Iteration(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	description = db.Column(db.String(12))

	elections = db.relationship('Election',backref="iteration", lazy='dynamic')

	def __repr__(self):
		return "<Iteration %r>" %self.description


class Party(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(45))
	avartar = db.Column(db.String(70) )
	code = db.Column(db.String(10))

	#election candidates
	election_candidates=db.relationship("ElectionCandidate",backref="party",lazy="dynamic")

	def __repr__(self):
		return "<Party>  %r (%r)" %(self.name,self.code)


class Candidate(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	first_name = db.Column(db.String(70))
	last_name = db.Column(db.String(140))
	avartar = db.Column(db.String(140))

	#elections a candidate has participated in
	elections = db.relationship('ElectionCandidate',backref='candidate')

	def __repr__(self):
		return "<Candidate>  %r %r" %(self.first_name,self.last_name) 

class ElectionType(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	type = db.Column(db.String(20), unique=True)
	elections = db.relationship('Election',backref=db.backref('electiontype',lazy="joined"),lazy='dynamic')	

	def __repr__(self):
		return " <ElectionType> %r" %self.type


class Election(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_year = db.Column(db.Date)
	iteration_id = db.Column(db.Integer,db.ForeignKey('iteration.id'))
	election_type_id = db.Column(db.Integer,db.ForeignKey('election_type.id'))


	def __repr__(self):
		return "<Election %r >" % self.election_year.year

class ElectionCandidate(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_id = db.Column(db.Integer,db.ForeignKey('election.id'))
	candidate_id = db.Column(db.Integer,db.ForeignKey('candidate.id'))
	party_id = db.Column(db.Integer,db.ForeignKey('party.id'))

	#what the fuck is this? = elections and candidates for a particular election
	election = db.relationship('Election',backref="electioncandidates")

	def __repr__(self):
		return "<Election  %r party: %r Election: %r>" %(self.candidate ,self.party,self.election )


	def __json__(self):

		return [self.candidate,self.election,self.party]



class ElectionConstituency(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_id = db.Column(db.Integer,db.ForeignKey('election.id'))
	constituency_id = db.Column(db.Integer,db.ForeignKey('constituency.id'))
	number_of_registered_voters = db.Column(db.Integer)

    #many to many type1
	election = db.relationship('Election',backref="constituency_electionconstituencies")


	def __repr__(self):
		return "<Election  %r : %r Constituency:  Total Registered Voters %r>" %(
			self.election ,self.constituency,self.number_of_registered_voters )


	def __json__(self):

		return [self.candidate,self.election,self.party]


class ElectionPollingStation(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_id = db.Column(db.Integer,db.ForeignKey('election.id'))
	polling_station_id = db.Column(db.Integer,db.ForeignKey('polling_station.id'))
	number_of_registered_voters = db.Column(db.Integer)

	#what the fuck is this? = elections and candidates for a particular election
	election = db.relationship('Election',backref="pollingstation_electionpollingstations")

	def __repr__(self):
		return "<ElectionPollingStation> Election:%r : %r Polling Station:  Total Registered Voters: %r>" %(
			self.election ,self.polling_station,self.total_registered_voters )


	def __json__(self):

		return [self.election,self.pooling_station,self.number_of_registered_voters]


class ElectionCandidateConstituencyVote(db.Model):   
	id = db.Column(db.Integer,primary_key=True)
	election_candidate_id = db.Column(db.Integer,db.ForeignKey('election_candidate.id'))
	constituency_id = db.Column(db.Integer,db.ForeignKey('constituency.id'))
	votes = db.Column(db.Integer)


	constituency = db.relationship('Constituency',backref=db.backref("ecconstituencyvotes",
		cascade="all,delete-orphan"))

	election_candidate = db.relationship('ElectionCandidate',backref=db.backref("ecconstituencyvotes",
		cascade="all,delete-orphan"))

	def __repr__(self):
		return "Election: %r ,Candidate %r , Constituency %r votes %r" %(
			self.election_candidate.election,self.election_candidate.candidate, self.constituency,self.votes)
	
	def __json__(self):
		return [self.constituency,self.electioncandidate,self.votes]



class ElectionCandidatePollingStationVote(db.Model):   
	
	id = db.Column(db.Integer,primary_key=True)
	election_candidate_id = db.Column(db.Integer,db.ForeignKey('election_candidate.id'))
	polling_station_id = db.Column(db.Integer,db.ForeignKey('polling_station.id'))
	votes = db.Column(db.Integer)

	polling_station = db.relationship('PollingStation',backref=db.backref("ecpollingstationvotes",
		cascade="all,delete-orphan"),lazy='joined')
	election_candidate = db.relationship('ElectionCandidate',backref=db.backref("ecpollingstationvotes",
		cascade="all,delete-orphan",lazy='joined'))
	


	def __repr__(self):
		pass


	def __json__(self):
		return [self.polling_station_id,self.electioncandidate,self.votes]

	

class IncidentType(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	type = db.Column(db.String(64))


class IncidentStatus(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	status = db.Column(db.String(20 ))


class Incident(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	description = db.Column(db.String(240))
	election_polling_station_id = db.Column(db.Integer,db.ForeignKey('election_polling_station.id'))
	election_constituency_id = db.Column(db.Integer,db.ForeignKey('election_constituency.id'))
	status_type_id = db.Column(db.Integer,db.ForeignKey('incident_status.id'))

	election_polling_station = db.relationship('ElectionPollingStation',backref=db.backref('incidents',lazy="joined"))

	election_constituency = db.relationship('ElectionConstituency',backref=db.backref('incidents',))

	status = db.relationship('IncidentStatus',backref="incidents")

	def __repr__(self):
		return "<Incident>  %r constituency: %r status: %r, " %(
			self.description, self.election_constituency,self.status)




class ConstituencyRegister(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_id = db.Column(db.Integer,db.ForeignKey('election.id'))
	constituency_id = db.Column(db.Integer,db.ForeignKey('constituency.id'))
	number_of_registered_voters = db.Column(db.Integer)

	constituency = db.relationship('Constituency',backref=db.backref('election_registers',lazy='joined'))
	election = db.relationship('Election',backref=db.backref('constituencies_register',lazy='joined'))



class PollingStationRegister(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	election_id = db.Column(db.Integer,db.ForeignKey('election.id'))
	polling_station_id = db.Column(db.Integer,db.ForeignKey('polling_station.id'))
	number_of_registered_voters = db.Column(db.Integer)


	polling_station = db.relationship('PollingStation',backref=db.backref("elections_register"))
	election = db.relationship('Election',backref=db.backref('polling_stations_register',lazy='joined'))

	
#data file for import
import datetime 

#2008 presidential first round
f2008R1= 'data/hatua/2008PresR1.xlsx'
#d.import_constituencies(f2008R1,const_rowstep=8)	
#d.import_candidate_party(f2008R1,cand_rowstep=8)
#d.import_election_candidate(f2008R1,ddate2008,it1,etype,cand_rowstep=8)
#d.import_election_constituencies_vote(f2008R1,ddate2008,it1,etype,cand_rowstep=8)

#2008 presidential second round
f2008R2 = 'data/hatua/2008PresR2.xlsx'
#d.import_constituencies(f2008R2,const_rowstep=8)	
#d.import_candidate_party(f2008R2,cand_rowstep=8)
#d.import_election_candidate(f2008R2,ddate2008,it2,etype,cand_rowstep=8)
#d.import_election_constituencies_vote(f2008R2,ddate2008,it2,etype,cand_rowstep=8)



#200r presidential first round
ddate2004	 = datetime.date(2004,12,6)
f2004R1="data/hatua/2004Presidential.xls"
#d.import_constituencies(f2004R1,const_rowstep=4)	
#d.import_candidate_party(f2004R1,cand_rowstep=4)
#d.import_election_candidate(f2004R1,ddate2000,it1,etype,cand_rowstep=4)
#d.import_election_constituencies_vote(f2004R1,ddate2004,it1,etype,cand_rowstep=4)



#2000 presidential first round
ddate2000	 = datetime.date(2000,12,6)
f2000R1="data/hatua/2000PresidentialRnd1.xls"
#d.import_constituencies(f2000R1,const_rowstep=7)	
#d.import_candidate_party(f2000R1,cand_rowstep=7)
#d.import_election_candidate(f2000R1,ddate2000,it1,etype,cand_rowstep=7)
#d.import_election_constituencies_vote(f2000R1,ddate2000,it1,etype,cand_rowstep=7)

#2000 presidential second round
f2000R2 = "data/hatua/2000PresidentialRnd2.xls"
# d.import_constituencies(f2000R2,const_rowstep=2)	
#d.import_candidate_party(f2000R2,cand_rowstep=2)
#d.import_election_candidate(f2000R2,ddate2000,it2,etype,cand_rowstep=2)
#d.import_election_constituencies_vote(f2000R2,ddate2000,it2,etype,cand_rowstep=2)



'''etype = ElectionType.query.get(1)
it1 = Iteration.query.get(1)
it2 = Iteration.query.get(2)
iteration = Iteration.query.get(3)
'''

def batch_ingest():
	d = Data()
	etype = ElectionType.query.get(1)
	it1 = Iteration.query.get(1)
	it2 = Iteration.query.get(2)
	iteration = Iteration.query.get(3)



	#2000 presidential first round
	ddate2000	 = datetime.date(2000,12,6)
	f2000R1="data/hatua/2000PresidentialRnd1.s"
	d.import_constituencies(f2000R1,const_rowstep=7)	
	d.import_candidate_party(f2000R1,cand_rowstep=7)
	d.import_election_candidate(f2000R1,ddate2000,it1,etype,cand_rowstep=7)
	d.import_election_constituencies_vote(f2000R1,ddate2000,it1,etype,cand_rowstep=7)

	#2000 presidential second round
	f2000R2 = "data/hatua/2000PresidentialRnd2.xlsx"
	d.import_constituencies(f2000R2,const_rowstep=2)	
	d.import_candidate_party(f2000R2,cand_rowstep=2)
	d.import_election_candidate(f2000R2,ddate2000,it2,etype,cand_rowstep=2)
	d.import_election_constituencies_vote(f2000R2,ddate2000,it2,etype,cand_rowstep=2)


	#2004 presidential first round
	ddate2004	 = datetime.date(2004,12,6)
	f2004R1="data/hatua/2004PresidentialRnd1.xls"
	d.import_constituencies(f2004R1,const_rowstep=4)	
	d.import_candidate_party(f2004R1,cand_rowstep=4)
	d.import_election_candidate(f2004R1,ddate2004,it1,etype,cand_rowstep=4)
	d.import_election_constituencies_vote(f2004R1,ddate2004,it1,etype,cand_rowstep=4)



	#2008 presidential firstround
	f2008R1= 'data/hatua/2008PresR1.xlsx'
	d.import_constituencies(f2008R1,const_rowstep=8)	
	d.import_candidate_party(f2008R1,cand_rowstep=8)
	d.import_election_candidate(f2008R1,ddate2008,it1,etype,cand_rowstep=8)
	d.import_election_constituencies_vote(f2008R1,ddate2008,it1,etype,cand_rowstep=8)

	#2008 presidential secondround
	f2008R2 = 'data/hatua/2008PresR2.xlsx'
	d.import_constituencies(f2008R2,const_rowstep=8)	
	d.import_candidate_party(f2008R2,cand_rowstep=8)
	d.import_election_candidate(f2008R2,ddate2008,it2,etype,cand_rowstep=8)
	d.import_election_constituencies_vote(f2008R2,ddate2008,it2,etype,cand_rowstep=8)



class Data():


	def set_up(self):
		#setup
		#election types
		print "Seting up Election types"
		et1 = ElectionType(type="presidential")
		et2 = ElectionType(type="parliamentary")
		db.session.add_all([et1,et2])
		db.session.commit()

		print "done setting up election types \n"

		print "setting up iterations \n"

		it1 = Iteration(description='first round')
		it2 = Iteration(description='second round')
		it3 = Iteration(description='by-election')
		db.session.add_all([it1,it2,it3])

		db.session.commit()

		print "Elections"
		ddate2000 = datetime.date(2000,12,6)
		ddate2004 = datetime.date(2004,12,6)
		ddate2008 = datetime.date(2008,12,6)

		e2000PR1 = Election(election_year=ddate2000,iteration=it1,electiontype=et1)
		e2000PR2 = Election(election_year=ddate2000,iteration=it2,electiontype=et1)

		e2004PR = Election(election_year=ddate2004,iteration=it1,electiontype=et1)

		e2008PR1 = Election(election_year=ddate2008,iteration=it1,electiontype=et1)
		e2008PR2 = Election(election_year=ddate2008,iteration=it2,electiontype=et1)

		elections = [e2000PR1,e2000PR2,e2004PR,e2008PR1,e2008PR2]
		db.session.add_all(elections)

		db.session.commit()
	

	#create region if not exists
	def create_region(self,name,code):
		reg = Region.query.filter_by(name=name,code=code).first()
		if reg is  None:
			new_reg = Region(name=name,code=code)
			db.session.add(new_reg)
			db.session.commit()
			return new_reg
		return reg


	def create_constituency(self,name,region):
		const = Constituency.query.filter_by(name=name).first()
		if const is None:
			new_const = Constituency(name=name)
			region.constituencies.append(new_const)
			db.session.add(region)
			db.session.commit()
			return new_const
		return const

	def create_polling_station(self,name,consituency):	
		p_station = PollingStation.query.filter_by(name=name).first()
		if p_station is None:
			new_p_station= PollingStation(name=name)
			Constituency.polling_stations.append(new_p_station)
			db.session.add(region)
			db.session.commit()
			return new_p_station
		return p_station


	def create_party(self,name,code):
		if name =='':
			party = Party.query.filter_by(code=code).first()
		else:
			party = Party.query.filter_by(name=name,code=code).first()
		if party is None:
			new_party =Party(name=name,code=code)
			db.session.add(new_party)
			db.session.commit()
			return new_party
		return party

	def create_election(self,election_year,iteration,etype):
		e = Election.query.filter_by(election_year=election_year,iteration=iteration,electiontype=etype).first()
		if e is None:
			new_e = Election.query.filter_by(election_year=election_year,iteration=iteration,
			electiontype=etype)
			db.session.add(new_e)
			db.session.commit()
			return new_e
		return e


	def create_candidate(self,first_name,last_name):
		cand = Candidate.query.filter_by(first_name=first_name,last_name=last_name).first()
		if cand is None:
			new_cand = Candidate(first_name=first_name,last_name=last_name)
			db.session.add(new_cand)
			return new_cand
		return cand


	def import_regions(self,f):
		codes= ['GR', 'AS', 'ER', 'CR', 'WR', 'VR', 'BA', 'NR', 'UE', 'UW']
		import xlrd

		x = 0
		wb=xlrd.open_workbook(f)
		for sheet in wb.sheets():
			name= sheet.name
			code = codes[x]
			self.create_region(name,code)
			#reg = Region(name=name,code=code)
			#db.session.add(reg)
			#db.session.commit()
			x=x+1

	def import_constituencies(self,f,step=0,const_rowstart=2,const_rowstep=8,const_name_col=0):
		import xlrd
		wb=xlrd.open_workbook(f)
		for sheet in wb.sheets():
			#reg_id = Region.query.filter_by(name=sheet.name).first().id
			region = Region.query.filter_by(name=sheet.name.title()).first()
			print region
			for i in range(const_rowstart,sheet.nrows,const_rowstep):
				constituency_name = sheet.cell(i,const_name_col).value
				const=self.create_constituency(constituency_name,region)
				print const
				#constituency = Constituency(region_id=reg_id,name=constituency_name)
				#constituency = Constituency(name=constituency_name)
				#region.constituencies.append(cons)
				#db.session.add(region)
				#db.session.commit()



	#creats party and candia
	def import_candidate_party(self,f,cand_rowstart=2,cand_rowstep=10,cand_party_col=2):
		import  xlrd
		wb = xlrd.open_workbook(f)
		sheet = wb.sheets()[0]



		party_dict= {
		'NDC':'National Democratic Congress', 
		'NPP':'New Patriotic Party', 
		'CPP':"Convention People's Party",
		'PNC':"People's National Convention",
		'DFP': 'Democratic Freedom Party', 
		'DPP':"Democratic People's Party",	 
		'Ind':"Ind", 
		'RPD':"Reformed Patriotic Democrats",
		'UGM':'United Ghana Movement',
		'GCPP':"Great Consolidate People Party"
		}

		#range covers the number of children
		for i in range(cand_rowstart ,cand_rowstart+cand_rowstep):
			
			#party
			party_code = sheet.cell(i,cand_party_col).value
			party_name = party_dict.get(party_code,'')
			party = self.create_party(party_name,party_code)
			print party_name

			#party = self.create_party(name=party_name,code=party_code)
			#pname_id = pname_id + 1
			#party = Party.query.filter_by(code=party_code).first()
			print party
			'''if party is None:
				party = Party(name=party_name,code=party_code)
				db.session.add(party)
				db.session.commit()'''
			#print  "New Party %r"  %party_code
			
			#party_id =  Party.query.filter_by(code=party_code).first().id

			#candidates
			first_name, last_name = sheet.cell(i,1).value.split(' ',1 ) 
			print first_name,last_name
			#candidate = Candidate(current_party_id=party_id,first_name=first_name,
			#	other_names=other_names)
			#candidate = Candidate(first_name=first_name,last_name=last_name)
			candidate = self.create_candidate(first_name=first_name,last_name=last_name)

			#db.session.add(candidate)
			#db.session.commit()

	#extract candidates from the first sheet in a workbook 
	#registers a candidate for an election
	def import_election_candidate(self,f,election_year,iteration,e_type,cand_rowstart=2,cand_rowstep=10,
		cand_name_col=1, cand_party_col=2):
		import xlrd
		
		#et = ElectionType.query.get(1)
		#datetime.date(2008, 12, 6)
		#it = Iteration.query.get(q)
		#your_model_object.query.with_entities(Your_model.your_attribute)
		#	Person.query.add_columns(func.count(...)).group_by(...).all()
		wb = xlrd.open_workbook(f)
		sheet = wb.sheets()[0]
		for i in range(cand_rowstart, cand_rowstart + cand_rowstep):

				first_name,last_name = sheet.cell(i,cand_name_col).value.split(' ',1 ) 
				c_code = sheet.cell(i,cand_party_col).value
				
				#c_id = Candidate.query.filter_by(first_name=fname,last_name=last_name).first().id
				#p_id = Party.query.filter_by(code=c_code).first().id
				#e_id = Election.query.filter_by(election_year=election_year,iteration_id=iteration,
					#election_type_id=e_type).first().id

				party = Party.query.filter_by(code=c_code).first()

				election = Election.query.filter_by(election_year=election_year,iteration=iteration,
						electiontype=e_type).first()

				#candidate = Candidate.query.filter_by(first_name=fname,last_name=last_name).first()
				candidate = self.create_candidate(first_name=first_name,last_name=last_name)

				ec = ElectionCandidate.query.filter_by(election=election,candidate=candidate).first()
				if ec is None:
					#party is the extra data in the ec association object
					ec =ElectionCandidate(party=party)
					ec.election = election
					candidate.elections.append(ec)
					db.session.add(candidate)
					db.session.commit()
					
				print ec


	def import_election_constituencies_vote(self,f,election_year,iteration,e_type,cand_start_row=2,cand_rowstep=8,
		const_name_col=0,cand_name_col=1,cand_vote_col=3,cand_party_col=2):
		#eg 2008rnd1 cand_start_row = 2, cand_rowstep=8,const_name_col=0,cand_name_col=1
		#cand_vote_col=3

		import xlrd
		wb=xlrd.open_workbook(f)
		eccvotes = []
		for sheet in wb.sheets():
			reg_id = Region.query.filter_by(name=sheet.name.title()).first().id
			print sheet.name
			for i in range(cand_start_row,sheet.nrows,cand_rowstep):
				constituency_name = sheet.cell(i,const_name_col).value
				const = Constituency.query.filter_by(name=constituency_name).first()
				#print const

				#candidates
				for k in range(i,i+cand_rowstep):
					try:
						first_name,other_names = sheet.cell(k,cand_name_col).value.strip().split(' ',1) 
					except ValueError:
						print "In cell %r, column %r with value  %r" %(k,cell_name_col,
							cell(k,cand_name_col).value)
						return
					cand_const_vote = sheet.cell(k,cand_vote_col).value
					party_code = sheet.cell(k,cand_party_col).value
					cand = Candidate.query.filter_by(first_name=first_name,last_name=other_names).first()
					#print cand

					#create candidate if not exists
					if cand is None:
						print "candidate is not none"
						cand = Candidate()
						cand.first_name =first_name
						cand.last_name = other_names
						db.session.add(cand)
						db.session.commit()
						cand = Candidate(first_name=first_name,last_name=other_names)

					e= Election.query.filter_by(election_year=election_year,iteration=iteration,
						electiontype=e_type).first()
					ec= ElectionCandidate.query.filter_by(candidate=cand,election=e).first()
					#print ec
					#create and add election candidate if not exist
					if ec is None:
						#party is the extra data in the ec association object
						print "Election:   " , e
						print "Candidate", cand
						print "ec is none"
						party = Party.query.filter_by(code=party_code).first()
						ec =ElectionCandidate(party=party)
						ec.election = e
						candidate.elections.append(ec)
						db.session.add(candidate)
						db.session.commit()
										
					
				    #create ElectionCandidateConstituencyVote if not exists
					eccv = ElectionCandidateConstituencyVote.query.filter_by(
						election_candidate=ec,constituency=const).first()
					if eccv is None:
						#print ec.id
						print const
						print "Eccv is none"
						ec_vote=ElectionCandidateConstituencyVote(votes=cand_const_vote,constituency=const,
							election_candidate=ec)
						#ec.ecconstituencyvotes.append(ec_vote)
						db.session.add(ec_vote)
						db.session.commit()

d = Data()



