from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import simplejson
import requests

pageids = {28486453: 'http://en.wikipedia.org/w/index.php?title=2010_Copiap%C3%B3_mining_accident',
27046954: 'http://en.wikipedia.org/wiki/Deepwater_Horizon_oil_spill',
25804468: 'http://en.wikipedia.org/wiki/2010_Haiti_earthquake',
31150160: 'http://en.wikipedia.org/wiki/2011_T%C5%8Dhoku_earthquake_and_tsunami',
32496189: 'http://en.wikipedia.org/wiki/2011_Norway_attacks',
7746616: 'http://en.wikipedia.org/wiki/Death_of_Osama_bin_Laden',
168079: 'http://en.wikipedia.org/wiki/2010_FIFA_World_Cup',
2401717: 'http://en.wikipedia.org/wiki/Super_Bowl_XLV'}

engine = create_engine('mysql://wiki:pedia@localhost:3306/wikipedia', echo=False)
Base = declarative_base(engine)

class Revision(Base):
	__tablename__ = 'revisions'
	__table_args__ = {'autoload': True, 'mysql_engine': 'MyISAM'}
	id = Column(Integer, primary_key=True, autoincrement=True)	
	pageid = Column(Integer)
	article_title = Column(Unicode(255))
	editor_id = Column(Integer)
	editor_name = Column(Unicode(255))
	revid = Column(Integer)
	parentid = Column(Integer)
	timestamp = Column(DateTime)
	comment = Column(UnicodeText)
	diff = Column(UnicodeText)

metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()

def store_revision(rev_json):
	page_id = rev_json['query']['pages'].keys()[0]
	page_info = rev_json['query']['pages'][page_id]
	rev = page_info['revisions'][0]
	revision = Revision(pageid = page_id,
		article_title = page_info['title'],
		editor_id = rev['userid'],
		editor_name = rev['user'],
		revid = rev['revid'],
		parentid = rev['parentid'],
		timestamp = rev['timestamp'],
		comment = rev['comment'],
		diff = rev['diff']['*'])
	session.add(revision)
	return rev['parentid']

def get_revision(revid, pageid):
	request = 'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&rvprop=ids%7Ctimestamp%7Cuser%7Cuserid%7Ccomment%7Ccontent&rvlimit=1&rvdiffto=prev&rvstartid='+str(revid)+'&pageids='+str(pageid)
	r = requests.get(request)
	sj = simplejson.loads(r.text)
	return sj

if __name__=="__main__":
	for pageid in pageids:
		first_request = 'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&rvprop=ids%7Ctimestamp%7Cuser%7Cuserid%7Ccomment%7Ccontent&rvlimit=1&rvdiffto=prev&pageids='+str(pageid)
		r = requests.get(first_request)
		sj = simplejson.loads(r.text)
		next_revid = store_revision(sj)
		#while next_revid 
		while True:
			print 'Getting revision %d for pageid %d (%s)' % (next_revid, pageid, pageids[pageid])
			sj = get_revision(next_revid, pageid)
			next_revid = store_revision(sj)
			session.commit()