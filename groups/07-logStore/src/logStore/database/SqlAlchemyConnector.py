from sqlalchemy import create_engine
from functions.Constants import CBORTABLE, EVENTTABLE, KOTLINTABLE, SENSORREADINGTABLE, SENSORDESCRIPTIONTABLE
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
        session = sessionmaker(self.__db_engine)()
        obj = cbor_event(feed_id, seq_no, event_as_cbor)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def get_event(self, feed_id, seq_no):
        session = sessionmaker(self.__db_engine)()
        logger.debug(type(feed_id))
        qry = session.query(cbor_event).filter(cbor_event.feed_id == feed_id, cbor_event.seq_no == seq_no)
        res = qry.first()
        if res is not None:
            return res.event_as_cbor
        else:
            return None

    def get_current_seq_no(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        q = session.query(func.max(cbor_event.seq_no)).filter(cbor_event.feed_id == feed_id)
        res = q.first()
        if res is not None:
            return res[0]
        else:
            return -1

    def get_current_event_as_cbor(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(func.max(cbor_event.seq_no)).filter(feed_id == feed_id)
        qry = session.query(cbor_event).filter(cbor_event.feed_id == feed_id, cbor_event.seq_no == subqry)
        res = qry.first()
        if res is not None:
            return res.event_as_cbor
        else:
            return None

    def get_all_feed_ids(self):
        session = sessionmaker(self.__db_engine)()
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
                                   Column('text', String),
                                   Column('publickey', String))
        mapper(kotlin_event, kotlin_event_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_kotlin_event(self, feed_id, seq_no, application, username, timestamp, text, publickey):
        session = sessionmaker(self.__db_engine)()
        obj = kotlin_event(feed_id, seq_no, application, username, timestamp, text, publickey)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def get_all_usernames(self):
        session = sessionmaker(self.__db_engine)()
        qry = session.query(kotlin_event)
        list = []
        for row in qry:
            list.append((row.username, row.publickey))
        if list is not None:
            return list
        else:
            return None

    def get_all_kotlin_events(self, feed_id):
        session = sessionmaker(self.__db_engine)()
        qry = session.query(kotlin_event).filter(kotlin_event.feed_id == feed_id)
        list = []
        for row in qry:
            list.append((row.text, row.username, row.publickey, row.timestamp))

        if list is not None:
            return list
        else:
            return None

    def get_all_entries_by_publickey(self, publicKey):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(kotlin_event).filter(kotlin_event.publickey == publicKey)
        liste = []
        for row in subqry:
            liste.append((row.text, row.username, row.publickey, row.timestamp))

        if liste is not None:
            return liste
        else:
            return None

    def get_last_kotlin_event(self):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(kotlin_event).order_by(kotlin_event.id.desc()).first()

        result = (subqry.text, subqry.username, subqry.publickey, subqry.timestamp)
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
        session = sessionmaker(self.__db_engine)()
        obj = chat_event(feed_id, seq_no, application, chat_id, timestamp, data)
        session.add(obj)
        session.commit()
        session.expunge_all()

    def get_all_events_since(self, application, timestamp, feed_id, chat_id):
        session = sessionmaker(self.__db_engine)()
        # subqry = session.query(up_event).filter(up_event.timestamp > timestamp,
        #                                         up_event.application == application,
        #                                         up_event.chat_id == chat_id)
        qry = session.query(chat_event)
        liste = []
        for row in qry:
            if row.timestamp > timestamp:
                if row.chat_id == chat_id:
                    if row.application == application:
                        liste.append((row.chatMsg, row.timestamp))

        if liste is not None:
            return liste
        else:
            return None

    # TODO: Use feed_id or at least application to get all events from one app
    def get_all_event_from_application(self, application, chat_id):
        session = sessionmaker(self.__db_engine)()
        subqry = session.query(chat_event).filter(chat_event.chat_id == chat_id, chat_event.application == application)

        liste = []
        for row in subqry:
            liste.append((row.chatMsg, row.timestamp))

        if liste is not None:
            return liste
        else:
            return None

    """"Following comes the functionality used for the event Database regarding the sensor readings table:"""

    def create_sensor_reading_table(self):
        metadata = MetaData()
        sensor_reading_table = Table(SENSORREADINGTABLE, metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('feed_id', String),
                                     Column('seq_no', Integer),
                                     Column('reading_id', String),
                                     Column('timestamp', Integer),
                                     Column('reading', String))
        mapper(sensor_reading, sensor_reading_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def create_sensor_description_table(self):
        metadata = MetaData()
        sensor_description_table = Table(SENSORDESCRIPTIONTABLE, metadata,
                                         Column('id', Integer, primary_key=True),
                                         Column('feed_id', String),
                                         Column('seq_no', Integer),
                                         Column('description_id', String),
                                         Column('label', String),
                                         Column('description', String),
                                         Column('properties', Binary),
                                         Column('location', Binary))
        mapper(sensor_descritpion, sensor_description_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)


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
    def __init__(self, feed_id, seq_no, application, username, timestamp, text, publickey):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.application = application
        self.username = username
        self.timestamp = timestamp
        self.text = text
        self.publickey = publickey


class sensor_reading(object):
    def __init__(self, feed_id, seq_no, reading_id, timestamp, reading):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.reading_id = reading_id
        self.timestamp = timestamp
        self.reading = reading


class sensor_descritpion(object):
    def __init__(self, feed_id, seq_no, description_id, label, description, properties, location):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.description_id = description_id
        self.label = label
        self.description = description
        self.properties = properties
        self.location = location
