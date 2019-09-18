from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField



class TestForm(FlaskForm):
    username = StringField('username')    
    submit = SubmitField('Submit')


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "secret"

@app.route("/", methods=['POST', 'GET'])
def hello():
    form = TestForm()
    if request.form.get('action', None):
        data = [
            {
                'status': 'failed',
                'msg': 'A failed message'
            },
            {
                'status': 'success',
                'msg': 'A success message'
            },
        ]
        return jsonify(data)
    else:        
        return render_template('test.jn2', form=form)

@app.route("/test", methods=['POST'])
def test():
    print ("ASD")
    return "Hello World"

if __name__ == "__main__":
    app.run(debug=True)
