from sqlalchemy import create_engine
from logStore.funcs.constants import CBORTABLE, EVENTTABLE, KOTLINTABLE, SENSORREADINGTABLE, SENSORDESCRIPTIONTABLE
from logStore.funcs.log import create_logger
from sqlalchemy import Table, Column, Integer, String, MetaData, Binary, func
from sqlalchemy.orm import sessionmaker, mapper
from contextlib import contextmanager

logger = create_logger('SqlAlchemyConnector')
SQLITE = 'sqlite'


class SqLiteDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }
    __db_engine = None
    __Session = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        try:
            self.__Session = sessionmaker()
            dbtype = dbtype.lower()
            if dbtype in self.DB_ENGINE.keys():
                engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
                self.__db_engine = create_engine(engine_url)
                self.__Session.configure(bind=self.__db_engine)
            else:
                logger.debug("DBType is not found in DB_ENGINE")
        except Exception as e:
            logger.error(e)
        finally:
            with self.session_scope():
                return

    """"Following comes the functionality used for the cbor Database:"""

    def create_cbor_db_tables(self):
        metadata = MetaData()
        cbor_table = Table(CBORTABLE, metadata,
                           Column('id', Integer, primary_key=True),
                           Column('feed_id', String),
                           Column('seq_no', Integer),
                           Column('event_as_cbor', Binary))
        mapper(cbor_event, cbor_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_byte_array(self, feed_id, seq_no, event_as_cbor):
        with self.session_scope() as session:
            obj = cbor_event(feed_id, seq_no, event_as_cbor)
            session.add(obj)

    def get_event(self, feed_id, seq_no):
        with self.session_scope() as session:
            qry = session.query(cbor_event).filter(cbor_event.feed_id == feed_id, cbor_event.seq_no == seq_no)
            res = qry.first()
            if res is not None:
                return res.event_as_cbor
            else:
                return None

    def get_current_seq_no(self, feed_id):
        with self.session_scope() as session:
            q = session.query(func.max(cbor_event.seq_no)).filter(cbor_event.feed_id == feed_id)
            res = q.first()
            if res is not None:
                return res[0]
            else:
                return -1

    def get_current_event_as_cbor(self, feed_id):
        with self.session_scope() as session:
            subqry = session.query(func.max(cbor_event.seq_no)).filter(feed_id == feed_id)
            qry = session.query(cbor_event).filter(cbor_event.feed_id == feed_id, cbor_event.seq_no == subqry)
            res = qry.first()
            if res is not None:
                return res.event_as_cbor
            else:
                return None

    def get_all_feed_ids(self):
        with self.session_scope() as session:
            feed_ids = []
            for feed_id in session.query(cbor_event.feed_id).distinct():
                feed_ids.append(feed_id[0])
            return feed_ids

    """"Following comes the functionality used for the event Database regarding the kotlin table:"""

    def create_kotlin_table(self):
        metadata = MetaData()
        kotlin_event_table = Table(KOTLINTABLE, metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('feed_id', String),
                                   Column('seq_no', Integer),
                                   Column('application', String),
                                   Column('username', String),
                                   Column('timestamp', Integer),
                                   Column('text', String))
        mapper(kotlin_event, kotlin_event_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_kotlin_event(self, feed_id, seq_no, application, username, timestamp, text):
        with self.session_scope() as session:
            obj = kotlin_event(feed_id, seq_no, application, username, timestamp, text)
            session.add(obj)

    def get_all_usernames(self):
        with self.session_scope() as session:
            qry = session.query(kotlin_event)
            list = []
            for row in qry:
                list.append((row.username, row.feed_id))
            if list is not None:
                return list
            else:
                return None

    def get_all_kotlin_events(self, feed_id):
        with self.session_scope() as session:
            qry = session.query(kotlin_event).filter(kotlin_event.feed_id == feed_id)
            list = []
            for row in qry:
                list.append((row.text, row.username, row.feed_id, row.timestamp))

            if list is not None:
                return list
            else:
                return None

    # TODO: Where is the difference between those two?
    def get_all_entries_by_feed_id(self, feed_id):
        with self.session_scope() as session:
            subqry = session.query(kotlin_event).filter(kotlin_event.feed_id == feed_id)
            liste = []
            for row in subqry:
                liste.append((row.text, row.username, row.feed_id, row.timestamp))

            if liste is not None:
                return liste
            else:
                return None

    def get_last_kotlin_event(self):
        with self.session_scope() as session:
            subqry = session.query(kotlin_event).order_by(kotlin_event.id.desc()).first()
            result = (subqry.text, subqry.username, subqry.feed_id, subqry.timestamp)
            return result

    """"Following comes the functionality used for the event Database regarding the chat table:"""

    def create_chat_event_table(self):
        metadata = MetaData()
        chat_event_table = Table(EVENTTABLE, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('feed_id', String),
                                 Column('seq_no', Integer),
                                 Column('application', String),
                                 Column('chat_id', String),
                                 Column('timestamp', Integer),
                                 Column('chatMsg', String))
        mapper(chat_event, chat_event_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_event(self, feed_id, seq_no, application, chat_id, timestamp, data):
        with self.session_scope() as session:
            obj = chat_event(feed_id, seq_no, application, chat_id, timestamp, data)
            session.add(obj)

    def get_all_events_since(self, application, timestamp, chat_id):
        with self.session_scope() as session:
            subqry = session.query(chat_event).filter(chat_event.timestamp > timestamp,
                                                      chat_event.application == application,
                                                      chat_event.chat_id == chat_id)
            liste = []
            for row in subqry:
                liste.append((row.chatMsg, row.timestamp))
            if liste is not None:
                return liste
            else:
                return None

    # TODO: Use feed_id or at least application to get all events from one app
    def get_all_event_with_chat_id(self, application, chat_id):
        with self.session_scope() as session:
            subqry = session.query(chat_event).filter(chat_event.chat_id == chat_id, chat_event.application == application)
            liste = []
            for row in subqry:
                liste.append((row.chatMsg, row.timestamp))
            if liste is not None:
                return liste
            else:
                return None

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.__Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise
        finally:
            session.close()


class cbor_event(object):
    def __init__(self, feed_id, seq_no, event_as_cbor):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.event_as_cbor = event_as_cbor


class chat_event(object):
    def __init__(self, feed_id, seq_no, application, chat_id, timestamp, data):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.application = application
        self.chat_id = chat_id
        self.timestamp = timestamp
        self.chatMsg = data


class kotlin_event(object):
    def __init__(self, feed_id, seq_no, application, username, timestamp, text):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.application = application
        self.username = username
        self.timestamp = timestamp
        self.text = text
