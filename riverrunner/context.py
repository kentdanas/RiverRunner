from riverrunner import settings
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Context:
    """ a connection to the database

    """
    def __init__(self, connection_string=settings.DATABASE):
        self.__engine = create_engine(URL(**connection_string))

        self.Session  = sessionmaker()
        self.Session.configure(bind=self.__engine)

        try:
            s = self.Session()
        except OperationalError:
            print("Unable to connect to destination db")
            exit(101)

        Base.metadata.create_all(self.__engine)


class Address(Base):
    __tablename__ = 'address'

    latitude  = Column(Float, primary_key=True)
    longitude = Column(Float, primary_key=True)

    address = Column(String(255))
    city    = Column(String(255))
    county  = Column(String(255))
    state   = Column(String(2))
    zip = Column(String(10))

    def __repr__(self):
        return '<Address(latitude="%s", longitude="%s")>' % (self.latitude, self.longitude)

    def __str__(self):
        return '%s, %s, %s' % (self.address, self.city, self.state)


class Measurement(Base):
    __tablename__ = 'measurement'

    date_time = Column(DateTime, primary_key=True)

    metric_id = Column(ForeignKey('metric.metric_id'), primary_key=True)
    metric    = relationship('Metric')

    station_id = Column(ForeignKey('station.station_id'), primary_key=True)
    station = relationship('Station')

    value = Column(Float)

    def __repr__(self):
        return '<Measurement(station_id="%s", datetime="%s", metric="%s")>' % \
               (self.station_id, self.date_time, self.metric.name)

    def __str__(self):
        return 'station: %s, datetime: %s, metric: %s' % \
               (self.station_id, self.date_time, self.metric.name)


class Metric(Base):
    __tablename__ = 'metric'

    metric_id = Column(Integer, primary_key=True)

    description = Column(String(255))
    name  = Column(String(255))
    units = Column(String(31))

    def __repr__(self):
        return '<Metric(metric_id="%s", name="%s")>' % (self.metric_id, self.name)

    def __str__(self):
        return 'metric_id: %s, name: %s' % (self.metric_id, self.name)


class Prediction(Base):
    __tablename__ = 'prediction'

    run_id = Column(ForeignKey('river_run.run_id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)

    fr_lb = Column(Float)
    fr    = Column(Float)
    fr_ub = Column(Float)

    def __repr__(self):
        return '<Prediction(run_id="%s", datetime="%s")>' % (self.run_id, self.timestamp)

    def __str__(self):
        return 'run_id: %s, %s, lb: %s, fr: %s, ub: %s' % \
               (self.run_id, self.timestamp, self.fr_lb, self.fr, self.fr_ub)


class RiverRun(Base):
    __tablename__ = 'river_run'

    run_id = Column(Integer, primary_key=True)

    class_rating = Column(String(31))
    max_level = Column(Integer)
    min_level = Column(Integer)

    put_in_latitude  = Column(Float, nullable=False)
    put_in_longitude = Column(Float, nullable=False)
    put_in_address = relationship(
        'Address',
        primaryjoin="and_(Address.latitude == foreign(RiverRun.put_in_latitude), "
                    "Address.longitude == foreign(RiverRun.put_in_longitude))")

    distance   = Column(Float)
    river_name = Column(String(255))
    run_name   = Column(String(255))

    take_out_latitude  = Column(Float, nullable=False)
    take_out_longitude = Column(Float, nullable=False)
    take_out_address = relationship(
        'Address',
        primaryjoin="and_(Address.latitude == foreign(RiverRun.take_out_latitude), "
                    "Address.longitude == foreign(RiverRun.take_out_longitude))")

    def __repr__(self):
        return 'RiverRun(run_id="%s", run_name="%s")>' % (self.run_id, self.run_name)

    def __str__(self):
        return self.run_name


class Station(Base):
    __tablename__ = 'station'

    station_id = Column(String(31), primary_key=True)

    source = Column(String(4))
    name   = Column(String(255))
    latitude  = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = relationship(
        'Address',
        primaryjoin="and_(Address.latitude == foreign(Station.latitude), "
                    "Address.longitude == foreign(Station.longitude))")

    def __repr__(self):
        return 'Station(station_id="%s", name="%s", source="%s")>' % \
               (self.station_id, self.name, self.source)

    def __str__(self):
        return self.name
