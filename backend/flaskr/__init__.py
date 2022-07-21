import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS(app)
    CORS(app, resources={"/": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # handle GET requests for all available categories
    @app.route('/categories')
    def get_all_categories():
        # get all categories
        categories = Category.query.order_by(Category.type).all()

        #  checking if categories where gotten in other to avoid errors
        if len(categories) == 0:
            abort(404)

        return jsonify({'success': True, 'categories': {
                       category.id: category.type for category in categories}})

    # GET requests for questions including pagination (every 10 questions).
    # This endpoint returns a list of questions, number of total questions,
    # current category, categories.

    @app.route('/questions')
    def get_all_questions():

        # get all questions
        selection = Question.query.order_by(Question.id).all()
        # getting current categories
        current_questions = paginate_questions(request, selection)
        # getting all categories
        categories = Category.query.order_by(Category.id).all()

        # checking for currentquestions in order to avaid errors
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': {category.id: category.type for category in categories},
            'currentCategory': {question.category: question.id for question in selection}
        })

    # DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # get specific question to be deleted
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            # checking if question exists in other to avaoid errors
            if question is None:
                abort(404)
            # if question exists we call the delete method to delete
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions
            })

        except BaseException:
            abort(422)

    # POST a new question, or search for a question which will require the
    # question and answer text, category,difficulty score, and searchTerm.

    @app.route('/questions', methods=['POST'])
    def create_question():
        # loading jsons
        body = request.get_json()
        # getting the body of the json object
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)
        try:
            # checking if search exists
            if search is not None:
                selection = Question.query.order_by(
                    Question.id).filter(
                    Question.question.ilike(
                        '%{}%'.format(search)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'current_category': {question.category: question.id for question in selection}
                })
            # if search doesntg exist we create a new question from the body
            # provided
            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty)
                question.insert()
                # get all questions
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
        except BaseException:
            abort(422)
    # GET question based on categories

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_specific_question(category_id):
        try:
            # quering the database for the specific category id
            questions = Question.query.filter(
                Question.category == str(category_id)).all()
            # checking if question exist in that category in other to avoid
            # errors
            if questions is None:
                abort(404)
            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except BaseException:
            abort(404)
    # POST endpoint to get questions to play the quiz, This endpoint takes
    # category and previous question parameters and returns a random question
    # within the given category if provided, and that is not one of the
    # previous questions.

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            # get the qestion category an the previous question
            body = request.get_json()

            category = body.get('quiz_category', None)
            previous_questions = body.get('previous_questions', None)

            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == category['id']).all()

            if questions:
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except BaseException:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

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
    return
