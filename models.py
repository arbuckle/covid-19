
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint

Base = declarative_base()

# This is how sessions are put together
_session = None

def session():
    return _session



def init_db(dbhost, dbuser, dbpass):
    pw = dbpass
    if pw == '':
        pw = ""
        with open(".password") as f:
            pw = f.read()
            pw = quote_plus(pw)
    
    conn = "postgresql://%s:%s@%s:5432/covid" % (dbuser, pw, dbhost)

    engine = create_engine(conn, convert_unicode=True, echo=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=engine))

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    print('wat')

    global _session
    _session = db_session


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    population = Column(Integer)
    area = Column(Integer)
    density = Column(Float)

    __table_args__ = (
        UniqueConstraint("name", name="unique_name"),
    )

    def __repr__(self):
        return "<Country(name=%s)" % self.name


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    fips = Column(String)
    county = Column(String)
    state = Column(String)
    country = Column(String)
    combined = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    pop = Column(Integer)

    cases = relationship("Case")

    __table_args__ = (
        UniqueConstraint("country", "state", "county", name="unique_location"),
    )


    def __repr__(self):
        return "<Loc(Country='%s' State='%s' County='%s' Id='%s')>" % (self.country, self.state, self.county, self.id)

    def json(self):
        out = {
            "id": self.id,
            "fips": self.fips,
            "county": self.county,
            "state": self.state,
            "country": self.country,
            "combined": self.combined,
            "lat": self.lat,
            "lon": self.lon,
            "pop": self.pop or -1,
        }
        return out

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    location_id = Column(Integer, ForeignKey('locations.id'))
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)

    __table_args__ = (
        UniqueConstraint("date", "location_id", name="unique_date_place"),
    )
    def __repr__(self):
        return "<Case(Date=%s %d/%d/%d/%d)" % (self.date, self.confirmed, self.deaths, self.recovered, self.active)
