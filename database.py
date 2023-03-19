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


def add_members(members_dict):
    # Create a table. If the table exists - the class is connected to it
    Base.metadata.create_all(engine)
    stringToReturn = ""
    #  Add new member to the table
    for items in members_dict.get('members'):
        try:
            DBSession = sessionmaker(bind=engine)
            session = DBSession()

            # If member with these nickname and chat_id exists - update his birthday
            q = session.query(Members).filter_by(nickname=items.get('nickname'), chat_id=items.get('chat_id')).first()
            if q:
                q.birthday = items.get('birthday')
            else:
                # Else - just add a new member
                new_member = Members(nickname=items.get('nickname'),
                                     birthday=items.get('birthday'), chat_id=items.get('chat_id'))
                session.add(new_member)
            session.commit()
            stringToReturn = stringToReturn + f"{items.get('nickname')}" + "\n"
        except exc.IntegrityError as e:
            # return error if something goes wrong
            session.rollback()
            log.error(e)
            return e.args
    return stringToReturn + "будут поздравлены!"


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
    try:
        session = DBSession()
        q = session.query(Members).filter_by(chat_id=chat_id, nickname=nickname)
        if q:
            q.wished_mark_year = datetime.now().strftime('%Y')
    except exc.OperationalError as e:
        log.error(e)


def is_member_wished(chat_id, nickname):
    try:
        session = DBSession()
        q = session.query(Members).filter_by(chat_id=chat_id, nickname=nickname)
        if q.wished_mark_year == datetime.now().strftime('%Y'):
            return True
        else:
            return False
    except exc.OperationalError as e:
        log.error(e)




