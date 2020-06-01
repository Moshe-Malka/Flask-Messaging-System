from uuid import uuid4
from datetime import datetime

from flask import Flask, abort, request, jsonify
from flask_restful import Resource, Api

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Message

# Connect to Database and create database session
engine = create_engine('sqlite:///messages-collection.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

def json_valid(data):
    try:
        sender = data['sender']
        receiver = data['receiver']
        message = data['message']
        subject = data['subject']
        assert len(sender) > 0
        assert len(receiver) > 0
        assert len(message) > 0
        assert len(subject) > 0
        return True
    except Exception:
        return False

def constructe_message(data):
    return Message(
        message_id= data.get('message_id',str(uuid4())),
        sender=data.get('sender', ''),
        receiver=data.get('receiver', ''),
        message=data.get('message', ''),
        subject=data.get('subject', ''),
        creation_date=data.get('creation_date', datetime.utcnow())
    )

#####################################################################
################################ API ################################
#####################################################################

@app.route('/messages/all/', methods=['GET'])
def get_all_messages():
    try:
        messages = session.query(Message).all()
        if len(messages) > 0:
            return jsonify(statusCode=200, messages=[m.serialize for m in messages]), 200
        else:
            return jsonify(statusCode=404, error="No Messages Found"), 404
    except Exception as e:
        return jsonify(statusCode=500, error=str(e)), 500

@app.route('/message/<message_id>', methods=['GET'])
def get_message_by_id(message_id):
    try:
        message = session.query(Message).filter_by(message_id=str(message_id)).one()
        message.unread = False
        return jsonify(statusCode=200, message=message.serialize), 200
    except MultipleResultsFound as mrf:
        return jsonify(statusCode=500, error=str(mrf)), 500
    except NoResultFound as nrf:
        return jsonify(statusCode=404, error=str(nrf)), 404
    except Exception as e:
        return jsonify(statusCode=500, error=str(e)), 500
    
@app.route('/message/new/', methods=['POST'])
def post_new_message():
    try:
        data = request.get_json()
        if not json_valid(data): raise Exception('Invalid message')
        newMessage = constructe_message(data)
        session.add(newMessage)
        session.commit()
        return jsonify(statusCode=200, new_message=newMessage.serialize), 200
    except Exception as e:
        print(e)
        return jsonify(statusCode=500, error="Internal Server Error"), 500
    
@app.route('/message/delete/<message_id>', methods=['DELETE'])
def delete_message_by_id(message_id):
    try:
        message = session.query(Message).filter_by(message_id=message_id).one()
        session.delete(message)
        return jsonify(statusCode=200, deleted_message=message.serialize), 200
    except Exception as e:
        return jsonify(statusCode=404, error=str(e)), 404

@app.route('/messages/all/<receiver>', methods=['GET'])
def get_all_messages_for_receiver(receiver):
    messages = session.query(Message).filter_by(receiver=receiver)
    for message in messages:
        message.unread = False
    return jsonify(statusCode=200, messages=[m.serialize for m in messages]), 200

@app.route('/messages/unread/<receiver>', methods=['GET'])
def gel_all_unread_messages_for_receiver(receiver):
    unread_messages = session.query(Message).filter_by(receiver=receiver, unread=True)
    for message in unread_messages:
        message.unread = False
    return jsonify(statusCode=200, messages=[m.serialize for m in unread_messages]), 200

if __name__ == '__main__':
    print("Starting...")
    app.run(threaded=True, port=5000)
    