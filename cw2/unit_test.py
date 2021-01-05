import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from coursework2 import app, db, User, Post

class Testing(unittest.TestCase):
    def setup(self):
        app.confg.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
        self.app = app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def testing(self):
        user1 = User(name="ThisisID1",username="Sejin Cho",password="ThisisPassword1")
        user2 = User(name="ThisisID2", username="Sejin", password="Thisispasswowrd2")
        user3 = User(name="ThisisID3", username="Cho", password="Thisispassword3")
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()
        
        result1 = User.query.filter_by(name="ThisisID1").first()
        result2 = User.query.filter_by(name="ThisisID2").first()
        result3 = User.query.filter_by(name="ThisisID3").first()
        
        self.assertEqual(result1.username, user1.username )
        print("User table testing 1 pass...")
        
        self.assertEqual(result2.name, user2.name)
        print("User table testing 2 pass...")
        
        self.assertEqual(result3.password, user3.password)
        print("User table testing 2 pass...")
        
        posting = Post(title="ThisisTitle",text="ThisisText")
        db.session.add(posting)
        db.session.commit()
        
        result = Post.query.filter_by(title="ThisisTitle").first()
        self.assertEqual(result.title, posting.title)
        self.assertEqual(result.text, posting.text)
        print("Post table testing pass...")
        
        result1 = User.query.filter_by(name="ThisisID3").first()
        result1.posts.append(posting)
        db.session.commit()
        
        result4 = Post.query.filter(Post.fromUser.any(id_number=result1.id_number)).first()
        self.assertEqual(result4.title, posting.title)
        print("Relationship test pass...")
        
if __name__ =='__main__':
    unittest.main()