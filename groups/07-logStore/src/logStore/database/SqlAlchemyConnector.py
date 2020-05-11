from sqlalchemy import create_engine
from functions.Constants import SQLITE, CBORTABLE, EVENTTABLE
from functions.log import create_logger
from sqlalchemy import Table, Column, Integer, String, MetaData, Binary, func
from sqlalchemy.orm import sessionmaker, mapper

logger = create_logger('SqlAlchemyConnector')
SQLITE = 'sqlite'


class SqLiteDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }
    __db_engine = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.__db_engine = create_engine(engine_url)
        else:
            logger.debug("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        metadata = MetaData()
        cbor_table = Table(CBORTABLE, metadata,
                           Column('id', Integer, primary_key=True),
                           Column('feed_id', String),
                           Column('seq_no', Integer),
                           Column('event_as_cbor', Binary))
        mapper(Event, cbor_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def create_event_table(self):
        metadata = MetaData()
        event_table = Table(EVENTTABLE, metadata,
                            Column('id', Integer, primary_key=True),
                            Column('feed_id', String),
                            Column('seq_no', Integer),
                            Column('application', String),
                            # TODO: Is data really a string or a binary?
                            Column('timestamp', Integer),
                            Column('data', String))
        mapper(up_event, event_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_byte_array(self, feed_id, seq_no, event_as_cbor):
        session = sessionmaker(self.__db_engine)()
        obj = Event(feed_id, seq_no, event_as_cbor)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def insert_event(self, feed_id, seq_no, application, timestamp, data):
        session = sessionmaker(self.__db_engine)()
        obj = up_event(feed_id, seq_no, application, timestamp, data)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def get_event(self, feed_id, seq_no):
        session = sessionmaker(self.__db_engine)()
        qry = session.query(Event).filter(feed_id == feed_id, Event.seq_no == seq_no)
        res = qry.first()
        if res is not None:
            return res.event_as_cbor
        else:
            return None

    def get_current_seq_no(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        q = session.query(func.max(Event.seq_no)).filter(feed_id == feed_id)
        res = q.first()
        if res is not None:
            return res[0]
        else:
            return -1

    def get_current_event_as_cbor(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(func.max(Event.seq_no)).filter(feed_id == feed_id)
        qry = session.query(Event).filter(feed_id == feed_id, Event.seq_no == subqry)
        res = qry.first()
        if res is not None:
            return res.event_as_cbor
        else:
            return None

    def get_all_events_since(self, application, timestamp, feed_id):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(up_event).filter(up_event.application == application).filter(
            up_event.timestamp > timestamp).filter(up_event.feed_id == feed_id)
        if subqry is not None:
            return subqry
        else:
            return None

    def get_all_event_from_application(self, application, feed_id):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(up_event).filter(up_event.application == application).filter(up_event.feed_id == feed_id)
        if subqry is not None:
            return subqry
        else:
            return None


class Event(object):
    def __init__(self, feed_id, seq_no, event_as_cbor):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.event_as_cbor = event_as_cbor


class up_event(object):
    def __init__(self, feed_id, seq_no, application, timestamp, data):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.application = application
        self.timestamp = timestamp
        self.data = data
