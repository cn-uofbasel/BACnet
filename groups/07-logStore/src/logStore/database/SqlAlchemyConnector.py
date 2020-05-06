from sqlalchemy import create_engine
from functions.log import create_logger
from sqlalchemy import Table, Column, Integer, String, MetaData, Binary, func
from sqlalchemy.orm import sessionmaker, mapper

logger = create_logger('SqlAlchemyConnector')

SQLITE = 'sqlite'

CBORTABLE = 'cborTable'
EVENTTABLE = 'eventTable'


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
            logger.debug(self.__db_engine)
        else:
            logger.debug("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        metadata = MetaData()
        cborTable = Table(CBORTABLE, metadata,
                          Column('id', Integer, primary_key=True),
                          Column('feed_id', String),
                          Column('seq_no', Integer),
                          Column('event_as_cbor', Binary))
        mapper(Event, cborTable)
        try:
            metadata.create_all(self.__db_engine)
            logger.debug('Tables created')
        except Exception as e:
            logger.error(e)

    def insert_byte_array(self, feed_id, seq_no, event_as_cbor):
        session = sessionmaker(self.__db_engine)()
        obj = Event(feed_id, seq_no, event_as_cbor)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def getter(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        res = session.query(Event).filter_by(feed_id=feed_id).first()
        return res.event_as_cbor

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
        logger.debug(subqry.first())
        qry = session.query(Event).filter(feed_id == feed_id, Event.seq_no == subqry)
        res = qry.first()
        if res is not None:
            return res.event_as_cbor
        else:
            return None

class Event(object):
    def __init__(self, feed_id, seq_no, event_as_cbor):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.event_as_cbor = event_as_cbor
