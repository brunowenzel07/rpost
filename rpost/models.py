#OUTSOURCE THIS TO racespg.py

# -*- coding: utf-8 -*-
#/Users/vmac/RACING1/HKG/scrapers/dist/hkjc
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, UniqueConstraint, CheckConstraint, Time, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BYTEA, TIMESTAMP
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship, backref
from sqlalchemy.pool import SingletonThreadPool
#for Oracle, Firebird
from sqlalchemy import *
import settings


#for multithreading
# from twisted.web import xmlrpc, server
# from twisted.internet import reactor
Base = declarative_base()
engine = create_engine(URL(**settings.DATABASE))
metadata = MetaData(bind=engine)

ModelBase = declarative_base()




class GBOwner(ModelBase):
    __tablename__ = "gb_owner"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    Homecountry = Column('homecountry', String(3), nullable=False)
    rpownerid = Column("rpownerid", Integer)
    gbrunners = relationship("GBRunner", backref="owner")
    # UniqueConstraint('name', name='OwnerName_uidx')


class Going(ModelBase):
    __tablename__ = "going"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    gbraces = relationship("GBRace", backref="going")
    # UniqueConstraint('name', name='GoingName_uidx')

class GBRaceclass(ModelBase):
    __tablename__ = "gb_raceclass"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    gbraces = relationship("GBRace", backref="gb_raceclass")
    # UniqueConstraint('name', name='RaceClassName_uidx')

class GBRacetype(ModelBase):
    __tablename__ = "gb_racetype"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    gbraces = relationship("GBRace", backref="gb_raceclass")

class GBDistance(ModelBase):
    __tablename__= "gb_distance"
    id = Column(Integer, primary_key=True)
    ImperialName = Column("imperialname", String, unique=True)
    MetricName = Column("metricname", Integer)
    Miles = Column("miles", Float)
    Furlongs = Column("furlongs", Integer)
    Yards = Column("Yards", Integer)
    gbraces = relationship("GBRace", backref="gb_distance") 
    # UniqueConstraint('metricname', name='HKDistance_MetricName_uidx')

class Railtype(ModelBase):
    __tablename__= "hk_railtype"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(256), unique=True)
    races = relationship("HKRace", backref="hk_railtype")
    # UniqueConstraint('name', name='HKRailType_Name_uidx')

class GBHorse(ModelBase):
    __tablename__ = "gb_horse"
    __tableargs__ = ( 
        UniqueConstraint('publicraceindex', name='GBHorse_PublicRaceIndex_uidx'),
    CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")')
        )
    id = Column(Integer, primary_key=True)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False, unique=True) # horsename sire dam
    Name = Column("name", String(255), nullable=False)
    Sex = Column("sex", String(2), nullable=True)
    Homecountry = Column('homecountry', String(3), nullable=False)
    SireName = Column("sirename", String(255))
    DamName = Column("damname", String(255))
    DamSireName = Column("damsirename", String(255))
    SalePriceYearling = Column("salepriceyearling", Float)
    YearofBirth = Column("yearofbirth", Integer)
    DateofBirth = Column(Date, nullable=True)
    rphorseid = Column("rphorseid", Integer)
    rpsireid = Column("rpsireid", Integer)
    rpdamid = Column("rpdamid", Integer)
    rpdamsireid = Column("rpdamsireid", Integer)
    gbrunners = relationship("GBRunner", backref="horse")
    # hkrunners = relationship("HKRunner", backref="horse")



class Jockey(ModelBase):
    __tablename__ = "gb_jockey"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "GB", "IRE", "DUB", "IRE", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(100), unique=True)
    Code = Column("code", String(10))
    Homecountry = Column('homecountry', String(3), nullable=False)
    runners = relationship("HKRunner", backref="jockey")
    # UniqueConstraint('name', name='JockeyName_uidx')

class Trainer(ModelBase):
    __tablename__ = "trainer"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "GB", "IRE", "DUB", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    Code = Column("code", String(10))
    Homecountry = Column('homecountry', String(3), nullable=False)
    runners = relationship("HKRunner", backref="trainer")
    # UniqueConstraint('name', name='Trainername_uidx')

class Racecourse(ModelBase):
    __tablename__ = "racecourse"
    __tableargs__ = ( CheckConstraint('Jurisdiction in ("HKG", "SIN", "AUS", "NZL", "RSA". "GB", "IRE", "DUB", "MAC", "USCA", "ARG", "JPN", "KOR")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    Jurisdiction = Column('homecountry', String(3), nullable=False)

#CHILD for G RC D RT DIV  
class GBRace(ModelBase):
    __tablename__ = "gb_race"
    __tableargs__ = ( 
        CheckConstraint('Prizecurrency in ("EUR", "GBP")'),
        UniqueConstraint('publicraceindex', name='HKRace_PublicRaceIndex_uidx'),
        )
    id = Column(Integer, primary_key=True)
    Rpraceid = Column(Integer)
    racecourse_id = Column("racecourseid", Integer, ForeignKey("racecourse.id"))
    Name = Column('name', String(255), nullable=True)
    RaceDate = Column('racedate', Date, nullable=True)
    RaceConditions = Column('raceconditions', String(255), nullable=True)
    RaceDateTime = Column('racedatetime', String, nullable=True)
    RaceNumber = Column('racenumber', Integer, nullable=True)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False, unique=True)
    going_id = Column("goingid", Integer, ForeignKey("going.id"))
    gb_racetype_id = Column("racetypeid", Integer, ForeignKey("gb_racetype.id"))
    gb_raceclass_id = Column("raceclassid", Integer, ForeignKey("gb_raceclass.id"))
    gb_distance_id = Column("distanceid", Integer, ForeignKey("gb_distance.id"))
    gb_railtype_id = Column("railtypeid", Integer, ForeignKey("gb_railtype.id"))
    gb_dividend_id = Column("hkdividendid", Integer, ForeignKey("hk_dividend.id"))
    Raceratingspan = Column("raceratingspan", String)
    Agerestriction = Column("agerestriction", String)
    Prizemoney = Column("prizemoney", Integer)
    Prizecurrency =  Column("prizecurrency", String)
    Surface = Column('surface', String)
    Dayofweek = Column('dayofweek', String)
    Isnight = Column("isnight", Boolean) 
    Racereport Column("racereport", String)
    Paceinfo = Column("paceinfo", String)
    FinishTime = Column("finishtime", Float)

    runners = relationship("GBRunner", backref="gb_race") #RA is Parent of RU
    # UniqueConstraint('publicraceindex', name='HKRace_PublicRaceIndex_uidx')
    # odds = relationship("HKOdds", backref="hk_race")


#CHILD FOR h j t o g
class GBRunner(ModelBase):
    __tablename__ = "gb_runner"

    __tableargs__ = ( 
        UniqueConstraint('publicraceindex', name='HKRunner_PublicRaceIndex_uidx')
    )

    id = Column(Integer, primary_key=True)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False, unique=True)
    # isScratched = Column('isscratched', Boolean)
    gb_race_id = Column("raceid", Integer, ForeignKey("gb_race.id"))
    horse_id = Column("horseid", Integer, ForeignKey("horse.id"))
    gb_gear_id = Column("gearid", Integer, ForeignKey("gb_gear.id"))
    owner_id = Column("ownerid", Integer, ForeignKey("owner.id"))
    jockey_id =Column("jockeyid", Integer, ForeignKey("jockey.id"))
    trainer_id =Column("trainerid", Integer, ForeignKey("trainer.id"))
    HorseNumber= Column('horsenumber', String, nullable=True)
    PlaceNum = Column('placenum', Integer)
    Place = Column('place', String)
    Jockey= Column('jockey', String, nullable=True)
    JockeyWtOver = Column('jockeywtover', Integer, nullable=True)
    Trainer= Column('trainer', String, nullable=True)
    ActualWt= Column('actualWt', Integer, nullable=True)
    OR= Column('OR', Integer, nullable=True)
    TS= Column('TS', Integer, nullable=True)
    RPR= Column('RPR', Integer, nullable=True)
    Diomed= Column('diomed', String, nullable=True)
    Spotlight= Column('spotlight', String, nullable=True)
    Draw= Column('draw', Integer, nullable=True)
    LBW= Column('lbw', Float, nullable=True)
    RatingChangeL1 = Column('ratingchangeL1', Integer, nullable=True)
    SeasonStakes = Column('seasonStakes', Integer, nullable=True)
    Age = Column('age', Integer, nullable=True)  #from raceday
    WinOdds= Column('winodds', Float, nullable=True)
    Horseprize = Column('horseprize',Float, nullable=True)
    HorseReport = Column('horsereport', String, nullable=True)
    HorseColors = Column('horsecolors', BYTEA, nullable=True)
    gbodds = relationship("GBOdds", backref="gb_runner")

class FormStats(ModelBase):
    __tablename__ = "gb_formstats"

    id = Column(Integer, primary_key=True)
    gb_runner_id = Column("gbrunnerid", Integer, ForeignKey("gb_runner.id"))
    L1RaceDate = Column('racedate', Date, nullable=True)
    DaysSinceLastRun = Column('dayssincelastrun', Integer)
    L1Distance = Column('L1distanceid', Integer, ForeignKey("gb_distance.id"))
    L1DistanceDiffFurl = Column('L1distancedifffurl', Float)
    L1CarriedWt= Column('L1carriedwt', String)
    L1WeightDiff = Column('L1weightdiff', Float)
    L1Comment = Column('L1comment', String)
    L1SP = Column('L1sp', String)
    L1BF = Column('L1bf', Boolean)
    L1gear = Column('L1gearid', Integer, ForeignKey("gb_gear.id"))
    #in monet last three


#OTHER TABLES

# class RaceStats(ModelBase):
#     __tablename__ = "hk_racestats"
#     id = Column(Integer, primary_key=True)
#     Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     FieldSize= Column('FieldSize', Integer)
#     NoLSWs = Column('NoLSWs', Integer)
#     NoFirstStarters = Column('NoFirstStarters', Integer)
#     MinStarts = Column(Integer)
#     MaxDistChange = Column(Integer)
    #pace?? winning style bias


# class HorseStats(ModelBase):
#     __tablename__ = "hk_horsestats"
#     id = Column(Integer, primary_key=True)
#     Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     Horseid = Column(Integer, ForeignKey("horse.id"))
#     API_career = Column('API_career', Float)    
#     API_season = Column('API_season', Float)
#     CareerWins = Column(Integer)
#     CareerRuns = Column(Integer)
#     CareerScratches = Column(Integer)
#     CareerPlaces = Column(Integer)
#     CareerF4s = Column(Integer)
#     WinsPrep = Column(Integer)
#     RunsPrep = Column(Integer)
#     PlacesPrep = Column(Integer)
#     F4Prep = Column(Integer)
#     TotalDistancePrep = Column(Integer)
#     AVI_career_rk = Column(Integer)
#     AVI_season_rk = Column(Integer)
#     AvgCareerWins_rk = Column(Integer)
#     Winodds_rk = Column(Integer)
#     WeightBelowMax = Column(Integer)



# class FormStats(ModelBase):
#     __tablename__ = "hk_form"
#     id = Column(Integer, primary_key=True)
#     # Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     Runnerid = Column(Integer, ForeignKey("hk_runner.id"))
#     DaystoL1 = Column(Integer)
#     DaystoL2 = Column(Integer)
#     nUp = Column(Integer)
#     WinsatNup = Column(Integer)
#     RunsatNup = Column(Integer)
#     WinsInClass = Column(Integer)
#     RunsInClass = Column(Integer)
#     AvgLBWClass = Column(Float)
#     AvgLBWDistance = Column(Float)
#     AvgLBWCD = Column(Float)
#     AvgLBWL3 = Column(Float)
#     L1Position = Column(String)
#     L2Position = Column(String)
#     L1Margin = Column(Float)
#     L2Margin = Column(Float)
#     isDroppingDown = Column(Boolean)
#     isHorseForCourse = Column(Boolean)
#     isHorseandJockey = Column(Boolean)
#     WinsAtTrack = Column(Integer)
#     RunsAtTrack = Column(Integer)
#     WinsatDistance = Column(Integer)
#     RunsAtDistance = Column(Integer)
#     WinsatCD = Column(Integer)
#     RunsatCD = Column(Integer)
#     WinsOnSurface = Column(Integer)
#     RunsOnSurface = Column(Integer)
#     PlacesOnSurface = Column(Integer)
    ##rankings AVI MAX THIS RACE


#PROGENY
#SWITCHES gear stats incl gelded trackworkthisjockey jockeyswitches
#odds stats
#time stats
#market stats

#CHILD TO RUNNER MANY TO ONE
class GBOdds(ModelBase):
    __tablename__ = "gb_odds"
    __tableargs__ = ( 
        UniqueConstraint('raceid', 'horsenumber','updatedate', 'updatetime', name='HKOdds_RaceidHorseNoUpdateDateTime_uidx')
    )

    id = Column(Integer, primary_key=True)
    Horsenumber = Column("horsenumber", Integer, nullable=False)
    Updatedatetime = Column("updatedatetime", Datetime, nullable=False)
    Winodds = Column("winodds", Float)
    Placeodds = Column("placeodds", Float)
    Runnerid = Column("gb_runnerid", Integer, ForeignKey("gb_runner.id"))
    # Horseid = Column(Integer, ForeignKey("horse.id"))
    # UniqueConstraint('raceid', 'horsenumber', 'updatedate', 'updatetime', name='HKOdds_RaceidHorseNoUpdateDateTime_uidx')
    # 1:M race:HKodds
    # race = relationship("HKRace", backref=backref("odds", order_by=(Updatedate, Updatetime)))
     
# poolclass=SingletonThreadPool, 
def get_engine():
    return create_engine(URL(**settings.DATABASE), pool_size=0)
    # return DBDefer(URL(**settings.DATABASE))

def create_schema(engine):
    ModelBase.metadata.create_all(engine)

