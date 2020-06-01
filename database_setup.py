from sqlalchemy import Column, String, Boolean
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from datetime import datetime

# create declarative_base instance
Base = declarative_base()

# We will add classes here
class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(String(250), primary_key=True, unique=True)
    sender = Column(String(250), nullable=False)
    receiver = Column(String(250), nullable=False)
    creation_date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow())
    message = Column(String(250))
    subject = Column(String(250))
    unread = Column(Boolean(), default=True)

    @property
    def serialize(self):
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'message': self.message,
            'subject': self.subject,
            'creation_date': self.creation_date,
            'unread': self.unread
        }

# creates a create_engine instance at the bottom of the file
engine = create_engine('sqlite:///messages-collection.db')
Base.metadata.create_all(engine)