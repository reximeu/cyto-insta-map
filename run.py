from os import path
from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Namespace, Resource
from instaloader import Instaloader, Profile, load_structure_from_file, save_structure_to_file


class Config:
    MAX_NO_FOLLOWEES = 600
    CRAWLER_NAME = ""

app = Flask(__name__)

CORS(app, resources={r"*": {"origins": "*"}})

api = Api(app, title='My Title', version='1.0', description='A description', )

ns = Namespace('users', description='Users related operations')

@ns.route('/<name>')
class UsersItem(Resource):
    def get(self, name):
        try:
            crawler = Config.CRAWLER_NAME

            loader = Instaloader()
            loader.load_session_from_file(crawler)

            profile = Profile.from_username(loader.context, name)

            data = {
                'id' : profile.userid,
                'username' : profile.username,
                'full_name' : profile.full_name,
                'biography' : profile.biography,
                'is_private' : profile.is_private,
                'is_verified' : profile.is_verified,
                'followers' : profile.followers,
                'followees' : profile.followees,
                'profile_pic_url' : profile.profile_pic_url,
            }
            
            return data, 200
        except Exception as e:
            return { 'response' : str(e) }, 500

@ns.route('/<name>/followees')
class UserItemFollowees(Resource):
    def get(self, name):
        try:
            crawler = Config.CRAWLER_NAME

            loader = Instaloader()
            loader.load_session_from_file(crawler)

            profile = Profile.from_username(loader.context, name)
            
            iterator_path = f'{name}'

            try:
                iterator = profile.get_followees().thaw(load_structure_from_file(iterator_path))
            except:
                iterator = profile.get_followees()

            try:
                followees = []

                for followee in iterator:
                    followees.append(followee.username)
                    if len(followees) > Config.MAX_NO_FOLLOWEES:
                        break

            except Exception as e:
                print(e)
                save_structure_to_file(iterator.freeze(), iterator_path)
            
            return followees, 200
        except Exception as e:
            return { 'response' : str(e) }, 500

api.add_namespace(ns)

if __name__ == '__main__':
    app.run(debug=True)
