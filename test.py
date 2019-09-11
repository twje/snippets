import os
from flask import Flask, Blueprint
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bp = Blueprint('api', __name__)


class APIHistory(db.Model):
    __tablename__ = 'api_history'
    
    id = db.Column(db.Integer, primary_key=True)
    api = db.Column(db.Text())
    calls = db.relationship('APICall', backref='history', lazy='dynamic')    

class APICall(db.Model):
    __tablename__ = 'api_call'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    history_id = db.Column(db.Integer, db.ForeignKey('api_history.id'))

    def __repr__(self):
        return self.name

class record_route:
    def __init__(self, decorator, path, url_prefix, history_route, **kwargs):
        self.decorator = decorator
        self.path = path
        self.url_prefix = url_prefix
        self.history_route = history_route        
        self.full_path = self.path if url_prefix is None else f"/{url_prefix}{path}"        
        self.kwargs = kwargs                

    def __call__(self, func):
        self.init_history()
        
        # register 'func' as route
        @self.decorator(self.path, **self.kwargs)
        @wraps(func)
        def route(*args, **kwargs):
            self.record_call()
            return func(*args, **kwargs)

        # register 'self.history_route' as route
        @self.decorator(f"{self.path}/history")
        @wraps(self.history_route)
        def history_route(*args, **kwargs):
            return self.history_route(*args, **kwargs)        

        return route        

    def init_history(self, _id):
        """
        db.create_all() 
        history = APIHistory.query.filter_by(api=self.full_path).first()
        if history is None:
            history = APIHistory(api=self.full_path)
            db.session.add(history)
            db.session.commit()
        """
    
    def record_call(self, _id, request):
        """
        history = APIHistory.query.filter_by(api=self.full_path).first()            
        call = APICall(name="HELLO")
        history.calls.append(call)
        db.session.commit()
        """

def history_route():
    return 'yes'

@record_route(bp.route, '/create', bp.name, history_route)
def hello():    
    return str(APICall.query.all())


app.register_blueprint(bp, url_prefix=f"/{bp.name}")

@app.shell_context_processor
def make_shell_context():
    return {"db": db}

if __name__ == "__main__":
    app.run(debug=True)
