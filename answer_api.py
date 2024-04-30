from data import db_session
from flask import abort, jsonify, make_response
from data.answers import Answer
from flask_restful import reqparse, abort, Resource
from flask_login import current_user


def abort_if_answer_not_found(answer_id):
    session = db_session.create_session()
    a = session.query(Answer).get(answer_id)
    if not a:
        abort(404, message=f"Answer {answer_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('text', required=True)
parser.add_argument('autor', required=True, type=int)
parser.add_argument('question', required=True, type=int)


class AnswerListResource(Resource):
    def get(self):
        session = db_session.create_session()
        ans = session.query(Answer).all()
        return jsonify(
            {
                'answers': [a.to_dict(only=('id', 
                                        'text', 
                                        'date',
                                        'is_like_autor',
                                        'autor',
                                        'question',
                                        'like_users')) for a in ans]
            }
        )
    
    def post(self):
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_admin):
            args = parser.parse_args()
            session = db_session.create_session()
            ans = Answer(
                text=args['text'],
                autor=args['autor'],
                question=args['question']
            )
            session.add(ans)
            session.commit()
            return jsonify({'id': ans.id})
    

class AnswerResource(Resource):
    def get(self, answer_id):
        abort_if_answer_not_found(answer_id)
        session = db_session.create_session()
        a = session.query(Answer).get(answer_id)
        return jsonify({'answer': a.to_dict(
            only=('id', 
                  'text', 
                  'date',
                  'is_like_autor',
                  'autor',
                  'question',
                  'like_users'))})

    def delete(self, answer_id):
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_admin):
            abort_if_answer_not_found(answer_id)
            session = db_session.create_session()
            ans = session.query(Answer).get(answer_id)
            session.delete(ans)
            session.commit()
            return jsonify({'success': 'OK'})

    def put(self, answer_id):
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_admin):
            db_sess = db_session.create_session()
            ans = db_sess.query(Answer).get(answer_id)
            if not ans:
                return make_response(jsonify({'error': 'Not found'}), 404)
            args = parser.parse_args()
            ans.text = args.text
            ans.autor = args.autor
            ans.question = args.question
            db_sess.commit()
            return jsonify({'success': 'OK'})