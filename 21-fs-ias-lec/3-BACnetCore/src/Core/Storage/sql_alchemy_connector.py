from contextlib import contextmanager

import cbor2
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Binary, func, Boolean
from sqlalchemy.orm import sessionmaker, mapper

from ...log import create_logger
from ...constants import SQLITE, EVENTTABLE, MASTERTABLE
from filters import identifier_is, feed_id_is

logger = create_logger("SQLAlchemy-logger")


class Database:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }
    __db_engine = None
    __Session = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        try:
            self.__Session = sessionmaker()
            dbtype = dbtype.lower()
            logger.error(dbname)
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
        cbor_table = Table(EVENTTABLE, metadata,
                           Column('id', Integer, primary_key=True),
                           Column('feed_id', String),
                           Column('seq_no', Integer),
                           Column('event_as_cbor', Binary))
        mapper(RawEvent, cbor_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_event(self, feed_id, seq_no: int, event_as_cbor: cbor2.CBORSimpleValue) -> None:
        with self.session_scope() as session:
            obj = RawEvent(feed_id, seq_no, event_as_cbor)
            session.add(obj)

    def get_event(self, feed_id, seq_no):
        with self.session_scope() as session:
            qry = session.query(RawEvent).filter(RawEvent.feed_id == feed_id, RawEvent.seq_no == seq_no)
            res = qry.first()
            if res is not None:
                return res.event_as_cbor
            else:
                return None

    def get_current_seq_no(self, feed_id):
        with self.session_scope() as session:
            q = session.query(func.max(RawEvent.seq_no)).filter(RawEvent.feed_id == feed_id)
            res = q.first()
            if res is not None:
                return res[0]
            else:
                return -1

    def get_current_event_as_cbor(self, feed_id):
        with self.session_scope() as session:
            res = session.query(RawEvent).filter(RawEvent.feed_id == feed_id).all()  # noqa: E711
            if res is not None:
                return res[-1].event_as_cbor
            return None

    def get_all_feed_ids(self):
        with self.session_scope() as session:
            feed_ids = []
            for feed_id in session.query(RawEvent.feed_id).distinct():
                feed_ids.append(feed_id[0])
            return feed_ids

    def __get_events_filtered(self, query_filter):
        """
        Takes a filter function RawEvent -> Bool and returns all matching rows completely
        Parameters
        ----------
        query_filter: a function RawEvent -> Bool that is used to filter for events

        Returns
        -------
        All rows that match the query-parameters as a list
        """
        with self.session_scope() as session:
            return session.query(RawEvent).filter(query_filter(RawEvent)).all()


    """"Following comes the functionality used for the event Database regarding the master table:"""

    def create_master_table(self):
        metadata = MetaData()
        master_event_table = Table(MASTERTABLE, metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('master', Boolean),
                                   Column('feed_id', Binary),
                                   Column('app_feed_id', Binary),
                                   Column('trust_feed_id', Binary),
                                   Column('seq_no', Integer),
                                   Column('trust', Boolean),
                                   Column('name', String),
                                   Column('radius', Integer),
                                   Column('event_as_cbor', Binary),
                                   Column('app_name', String))
        mapper(MasterEvent, master_event_table)
        try:
            metadata.create_all(self.__db_engine)
        except Exception as e:
            logger.error(e)

    def insert_master_event(self, master, feed_id, app_feed_id, trust_feed_id, seq_no, trust, name, radius,
                            event_as_cbor, app_name):
        with self.session_scope() as session:
            obj = MasterEvent(master, feed_id, app_feed_id, trust_feed_id, seq_no, trust, name, radius, event_as_cbor,
                              app_name)
            session.add(obj)

    def get_trusted(self, master_id):
        with self.session_scope() as session:
            feed_ids = []
            for subqry in session.query(MasterEvent.trust_feed_id).filter(
                    MasterEvent.feed_id == master_id).distinct():
                if subqry[0] is not None:
                    q1 = session.query(func.max(MasterEvent.seq_no), MasterEvent).filter(
                        MasterEvent.trust_feed_id == subqry[0])
                    if q1[0] is not None and q1[0][1].trust == True:  # noqa: E712
                        feed_ids.append(q1[0][1].trust_feed_id)
            return feed_ids

    def get_blocked(self, master_id):
        with self.session_scope() as session:
            feed_ids = []
            for subqry in session.query(MasterEvent.trust_feed_id).filter(
                    MasterEvent.feed_id == master_id).distinct():
                if subqry[0] is not None:
                    q1 = session.query(func.max(MasterEvent.seq_no), MasterEvent).filter(
                        MasterEvent.trust_feed_id == subqry[0])
                    if q1[0] is not None and q1[0][1].trust is False:
                        feed_ids.append(q1[0][1].trust_feed_id)
            return feed_ids

    def get_all_master_ids(self):
        with self.session_scope() as session:
            master_ids = []
            master_id = self.get_host_master_id()
            if master_id is None:
                return None
            for master_id in session.query(MasterEvent.feed_id).filter(MasterEvent.master == True,  # noqa: E712
                                                                       MasterEvent.feed_id != master_id):  # noqa: E712
                if master_id is not None:
                    master_ids.append(master_id[0])
            return master_ids

    def get_all_master_ids_feed_ids(self, master_id):
        with self.session_scope() as session:
            feed_ids = []
            for feed_id in session.query(MasterEvent.app_feed_id).filter(MasterEvent.feed_id == master_id).distinct():
                if feed_id is not None:
                    if feed_id[0] is not None:
                        feed_ids.append(feed_id[0])
            return feed_ids

    def get_username(self, master_id):
        with self.session_scope() as session:
            res = session.query(MasterEvent.name).filter(MasterEvent.feed_id == master_id,
                                                         MasterEvent.name != None).all()  # noqa: E711
            if res is not None:
                return res[-1][0]
            return None

    def get_my_last_event(self):
        with self.session_scope() as session:
            master_id = self.get_host_master_id()
            if master_id is None:
                return None
            res = session.query(MasterEvent.event_as_cbor).filter(
                MasterEvent.seq_no == func.max(MasterEvent.seq_no).select(),
                MasterEvent.feed_id == master_id).distinct()
            if res is not None:
                return res[0][0]
            return None

    def get_host_master_id(self):
        with self.session_scope() as session:
            master_id = session.query(MasterEvent.feed_id).filter(MasterEvent.master == True).first()  # noqa: E712
            if master_id is not None:
                return master_id[0]
            return None

    def get_radius(self):
        with self.session_scope() as session:
            master_id = self.get_host_master_id()
            if master_id is None:
                return None
            res = session.query(MasterEvent.radius).filter(
                MasterEvent.seq_no == 1, MasterEvent.feed_id == master_id).first()
            if res is not None:
                return res[0]
            return None

    def get_master_id_from_feed(self, feed_id):
        with self.session_scope() as session:
            res = session.query(MasterEvent.feed_id).filter(MasterEvent.app_feed_id == feed_id).first()
            if res is not None:
                return res[0]
            return None

    def get_application_name(self, feed_id):
        with self.session_scope() as session:
            res = session.query(MasterEvent.app_name).filter(MasterEvent.app_feed_id == feed_id).first()
            if res is not None:
                return res[0]
            return None

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        with self.session_scope() as session:
            feed_ids = []
            for res in session.query(MasterEvent.app_feed_id).filter(MasterEvent.feed_id == master_id,
                                                                     MasterEvent.app_name == application_name):
                if res is not None:
                    feed_ids.append(res[0])
            return feed_ids

    def get_feed_ids_in_radius(self):
        with self.session_scope() as session:
            radius = self.get_radius()
            if radius is None:
                return None
            feed_ids = []
            for feed_id in session.query(MasterEvent.feed_id).distinct():
                res = session.query(MasterEvent.feed_id).filter(
                    MasterEvent.seq_no == 1, MasterEvent.radius >= 0,
                    MasterEvent.radius <= radius, MasterEvent.feed_id == feed_id[0]).first()
                if res is not None:
                    feed_ids.append(res[0])
            return feed_ids

    def set_feed_ids_radius(self, feed_id, radius):
        with self.session_scope() as session:
            rad = session.query(MasterEvent.radius).filter(MasterEvent.feed_id == feed_id,
                                                           MasterEvent.seq_no == 1).update(
                {MasterEvent.radius: radius})
            return rad

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
            return -1
        finally:
            session.close()


class RawEvent(object):
    def __init__(self, feed_id, seq_no, event_as_cbor):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.event_as_cbor = event_as_cbor


class MasterEvent(object):
    def __init__(self, master, feed_id, app_feed_id, trust_feed_id, seq_no, trust, name, radius, event_as_cbor,
                 app_name):
        self.master = master
        self.feed_id = feed_id
        self.app_feed_id = app_feed_id
        self.trust_feed_id = trust_feed_id
        self.seq_no = seq_no
        self.trust = trust
        self.name = name
        self.radius = radius
        self.event_as_cbor = event_as_cbor
        self.app_name = app_name

