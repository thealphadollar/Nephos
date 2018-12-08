"""
Used to Create a Base for testing the flask app
"""
import os
import unittest
from flask_testing import TestCase
from nephos.web.webServer import APP


class BaseTestCase(TestCase):
    """
    Reusable Template for a Test Case
    """
    def create_app(self):
        """
        Create the App so you can test it
        """
        # executed prior to each test
        def setUp(self):
            """
            Set up for the Test Case
            """
            APP.config['TESTING'] = True
            APP.config['WTF_CSRF_ENABLED'] = False
            APP.config['DEBUG'] = False
            APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                os.path.join(APP.config['BASEDIR'], 'nephos/databases/jobs.db')
            self.APP = APP.test_client()
            DB.create_all() 

        return APP

        # executed after each test
        def tearDown(self):
            """
            When finished to teardown
            """
            DB.drop_all()


if __name__ == "__main__":
    unittest.main()
