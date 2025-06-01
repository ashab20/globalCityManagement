from sqlalchemy.orm import Session
from utils.database import Session as DBSession
from models.user import User


class AuthController:
    def authenticate(self, username, password):
        session = DBSession()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        return True
        # if user and user.password == password:
        #     return True
        # return False
