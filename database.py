from sqlalchemy import create_engine, select, Table, Column, Integer, String, MetaData, UniqueConstraint, exc, DateTime
from sqlalchemy.orm import mapper, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date, time
import logging

logging.basicConfig(filename="main.log", level=logging.DEBUG, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

# Declarative method
engine = create_engine("sqlite:///bithdb.db", echo=True)
Base = declarative_base()


# Describing class(table) with chat members
class Members(Base):
    __tablename__ = 'Members'
    id = Column(Integer, primary_key=True)
    nickname = Column(String(250), nullable=False)
    birthday = Column(String(250), nullable=False)
    chat_id = Column(String(250), nullable=False)
    wished_mark_year = Column(String(250))
    __table_args__ = (UniqueConstraint('nickname', 'chat_id', name='unique_name_chat_id'),)

    def __init__(self, nickname, birthday, chat_id):
        self.nickname = nickname
        self.chat_id = chat_id
        self.birthday = birthday

    def get_nickname(self):
        return self.nickname

    def get_chat_id(self):
        return self.chat_id

    def get_birthday(self):
        return self.birthday

    def add_member(self):
        # Create a table. If the table exists - the class is connected to it
        Base.metadata.create_all(engine)
        string_to_return = ""
        #  Add new member to the table
        try:
            DBSession = sessionmaker(bind=engine)
            session = DBSession()

            # If member with these nickname and chat_id exists - update his birthday
            q = session.query(Members).filter_by(nickname=self.get_nickname(), chat_id=self.get_chat_id()).first()
            if q:
                q.birthday = self.get_birthday()
            else:
                # Else - just add a new member
                session.add(self)
            session.commit()
            return None
        except exc.IntegrityError as e:
            # return error if something goes wrong
            session.rollback()
            log.error(e)
            return e.args


def get_members_of_chat(chat_id=None):
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        string_to_return = ""
        # Searching members
        for member in session.query(Members).filter_by(chat_id=chat_id):

            # And making beauty-formatted string for user
            string_to_return = string_to_return + f"{member.nickname} {member.birthday}" + "\n"
        return string_to_return if string_to_return else "Список пуст"
    except exc.OperationalError as e:
        # If we get  error - send raw exception
        log.error(e)
        return e.args


def get_birthday_boys():
    current_dateTime = datetime.now().strftime('%d.%m')
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        res = session.query(Members).filter_by(birthday=current_dateTime)
        return res
    except exc.OperationalError as e:
        log.error(e)


def mark_wished_member(chat_id, nickname):
    # Mark wished member in db
    log.debug(f"Mark wished member in db. chat_id ={chat_id}, nickname = {nickname}")
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        for member in session.query(Members).filter_by(chat_id=chat_id, nickname=nickname):
            member.wished_mark_year = datetime.now().strftime('%Y')
            session.commit()
    except exc.OperationalError as e:
        session.rollback()
        log.error(e)


def is_member_wished(chat_id, nickname):
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        for member in session.query(Members).filter_by(chat_id=chat_id, nickname=nickname):
            if member.wished_mark_year == datetime.now().strftime('%Y'):
                return True
            else:
                return False
    except exc.OperationalError as e:
        log.error(e)




