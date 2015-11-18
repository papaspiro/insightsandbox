from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

engine = create_engine('sqlite://', echo=True)
session = Session(bind=engine)
Base = declarative_base(bind=engine)


class CostCenter(Base):
    __tablename__ = 'cost_center'

    id = Column(Integer, primary_key=True)


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(Integer, primary_key=True)
    cost_center_id = Column(Integer, ForeignKey(CostCenter.id), nullable=False)
    value = Column(Numeric(8, 2), nullable=False, default=0)
    date = Column(DateTime, nullable=False)

    cost_center = relationship(CostCenter, backref='expenses')


Base.metadata.create_all()

session.add_all([
    CostCenter(expenses=[
        Expense(value=10, date=datetime(2014, 8, 1)),
        Expense(value=20, date=datetime(2014, 8, 1)),
        Expense(value=15, date=datetime(2014, 9, 1)),
    ]),
    CostCenter(expenses=[
        Expense(value=45, date=datetime(2014, 8, 1)),
        Expense(value=40, date=datetime(2014, 9, 1)),
        Expense(value=40, date=datetime(2014, 9, 1)),
    ]),
    CostCenter(expenses=[
        Expense(value=42, date=datetime(2014, 7, 1)),
    ]),
])
session.commit()

base_query = session.query(
    Expense.date,
    func.sum(Expense.value).label('total')
).join(Expense.cost_center
).group_by(Expense.date)

# first query considers center 1, output:
# 2014-08-01: 30.00
# 2014-09-01: 15.00
for row in base_query.filter(CostCenter.id.in_([1])).all():
    print('{}: {}'.format(row.date.date(), row.total))

# second query considers centers 1, 2, and 3, output:
# 2014-07-01: 42.00
# 2014-08-01: 75.00
# 2014-09-01: 95.00
for row in base_query.filter(CostCenter.id.in_([1, 2, 3])).all():
    print('{}: {}'.format(row.date.date(), row.total))





#ElectionCandidate.query.filter_by(election=Election.query.get(1) ).all()
#ElectionCandidate.query.filter_by(election=Election.query.get(1) ).all()

#db.session.query(label('total_votes',func.sum(ElectionCandidateConstituencyVote.votes)),
#ElectionCandidateConstituencyVote.election_candidate_id).filter(
#ElectionCandidateConstituencyVote.election_candidate_id.in_(candidate_ids)).group_by(
#ElectionCandidateConstituencyVote.election_candidate_id).order_by(desc('total_votes')).all()


#Election

#*Election.query.filter( Election.election_year==datetime.date(2008,12,6)).all()

#delete all elections
#for i in range(1,ElectionCandidateConstituencyVote.query.count() +1):
 #    eccv = ElectionCandidateConstituencyVote.query.get(i) 
  #   db.session.delete(eccv)
   #  db.session.delete(eccv



#Joins by direct and joins by subquery
#posts = Post.query.join(Author).filter(Author.name == the_author_name)

#author_query = Author.query.filter(Author.name == the_author_name)
#posts = Post.query.filter(Post.author_id.in_(author_query))





'''
published_sites_ids = session.query( msg_published.site_id ) \
            .filter( and_(*filter_clause) ) \
            .group_by( msg_published.site_id ) \
            .order_by( order_clause ) \
            .paginate( page_no, per_page, error_out = False )

published_sites = session.query(msg_published) \
                         .filter(msg_published.id.in_(published_sites_ids))




from  flask import Flask,render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate ,MigrateCommand
from flask.ext.script import Manager

import os
#base_dir = os.path.abspath( os.path.dirname(__file__) )

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'data-staging_rev6.sqlite')
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dev:n1mda@localhost/insight'



app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)


migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('migrate',MigrateCommand)


# json encoding
from json_encoder import AlchemyEncoder
app.json_encoder = AlchemyEncoder


from api.views import api_blueprint as api_blueprint


#Register blueprint
#app.register_blueprint(some_blueprint module)
app.register_blueprint(api_blueprint)


#import a module using its  blue print handler




# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def index():

    x=Constituency.query.all()
    return x

@app.route('/data')
def data():
    
    return "shit"

#api routes
#api
from api.views import *
api = Api(app)
api.add_resource(ElectionResource,'/api/v0.1/elections',endpoint='elections')


if __name__ == '__main__':
    app.run(debug=True)







'''

