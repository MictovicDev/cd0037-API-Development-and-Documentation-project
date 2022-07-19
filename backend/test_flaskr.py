import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','awa','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

       


    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'resource not found')

    def test_create_question(self):
        new_question = {
            'question': 'who',
            'answer': 'me',
            'difficulty': '4',
            'category': '5',
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertEquals(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_422_cannot_create_question(self):
        new_question = {
            'question': 'who',
            'answer': 'me',
            'difficulty': '4',
            'category': '5',
        }
        res = self.client().post('/questions/455', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'method not allowed')

    def search_question(self):
        res = self.client().post('/questions', json={"searchTerm":"who"})
        data = json.loads(res.data)

        self.assertEqual(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'])

    def test_invalid_search_question(self):
        res = self.client().post('/questions', json={"searchTerm":"felony"})
        data = json.loads(res.data)

        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'],'method not allowed')

    
    def test_delete_questions(self):
        res = self.client().delete('/questions/66')
        data = json.loads(res.data)
        # print(res)
        # print(data)

        question = Question.query.filter(Question.id == 66).one_or_none()
        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEquals(data['deleted'],66)
        self.assertTrue(data['questions'])
        self.assertEqual(question, None)


    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        # print(res)
        # print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'unprocessable')

    def test_specific_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        # print(res)
        # print(data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['current_category'])

    def test_specific_category_out_of_range(self):
        res = self.client().post('/categories/20000/questions')
        data = json.loads(res.data)
        # print(res)
        # print(data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'method not allowed')
        self.assertEqual(data['error'], 405)

    def test_play_quiz(self):
        input_data = {
            'previous_questions': [4,6],
            'quiz_category':{
                'id':5,
                'type':'Entertainment'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)
        # print(res)
        # print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
        self.assertNotEqual(data['question']['id'], 4)
        self.assertNotEqual(data['question']['id'], 6)

        # self.assertEqaul(data['question']['category'])

    
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()