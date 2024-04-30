import flask
from flask import jsonify, make_response, request
from flask_login import login_required, current_user
from data import db_session
from data.answers import Answer
from data.users import User


blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/like_answer_user', methods=['PUT'])
def like_answer_user():
    a_id = request.json["ans_id"]
    sess = db_session.create_session()
    a = sess.query(Answer).filter(Answer.id == a_id).first()
    a.like(current_user.id)
    u = sess.query(User).filter(User.id == a.autor).first()
    u.give_experience(5)
    sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/dislike_answer_user', methods=['PUT'])
def dislike_answer_user():
    a_id = request.json["ans_id"]
    sess = db_session.create_session()
    a = sess.query(Answer).filter(Answer.id == a_id).first()
    a.dislike(current_user.id)
    u = sess.query(User).filter(User.id == a.autor).first()
    u.take_experience(5)
    sess.commit()
    return jsonify({'success': 'OK'})