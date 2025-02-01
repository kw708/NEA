from flask import Flask, render_template, request 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)
# define the model for notes 
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Note {self.id}'

# route for the page 
@app.route ('/')
def index():
    return render_template('psychology.html','history.html', notes=notes)

# route for the search bar  including the query for the titles. 
@app.route('/search', methods=['GET,POST'])
def search():
    search_term = request.form['search']
    notes = Notes.query.filter(Notes.title.contains(search_term)).all()
    return render_template('psychology.html','history.html', notes=notes)

# runs the application and creates the tables needed. 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)