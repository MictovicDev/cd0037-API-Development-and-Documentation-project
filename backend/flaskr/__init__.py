import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    

    
    CORS(app, resources={"/":{"origins":"*"}})


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
        return response

   
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}})


    

    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': {category.id: category.type for category in categories},
            'currentCategory': None
        })

   

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
          question = Question.query.filter(Question.id==question_id).one_or_none()

          if question is None:
            abort(404)

          question.delete()
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)


          return jsonify({
                'success': True,
                'deleted' : question_id, 
                'questions': current_questions
        })

        except:
            abort(422)

    
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()


        new_question = body.get('question',None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)
        try:
            if search != None:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request,selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'current_category': None
                })

            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)


                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all()) 
                })
        except:
            abort(422)


    
    

    @app.route('/categories/<int:category_id>/questions',methods=['GET'])
    def get_specific_question(category_id):
        try:
            questions = Question.query.filter(Question.category==str(category_id)).all()

            if questions is None:
                abort(404)
            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

    

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()

            category = body.get('quiz_category',None)
            previous_questions = body.get('previous_questions',None)

            if category['id'] == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions),Question.category == category['id']).all()
        
        
            if questions:
                question= random.choice(questions)

            return jsonify({
            'success': True,
            'question': question.format()
        })
        except:
            abort(422)
        


   
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                'success': False,
                'error': 404,
                'message': 'resource not found'
            }),404
    
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
                'success': False,
                'error': 405,
                'message': 'method not allowed'
            }),405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        })
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        })

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal error, Wait a while and try again later'
        })
    return app

