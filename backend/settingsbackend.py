#initilisation of flask app
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
db = SQLAlchemy(app)

# define model for settings 
class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    font_size = db.Column(db.Integer, default=16)
    dark_mode = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<UserSettings %r>' % self.id

# route for settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_settings = UserSettings.query.first()
    if not user_settings:
        user_settings = UserSettings()
        db.session.add(user_settings)
        db.session.commit()

#update settings when POST 
    if request.method == 'POST':
        font_size = request.form.get('font_size')
        dark_mode = request.form.get('dark_mode') == 'on'
        notifications_enabled = request.form.get('notifications_enabled') == 'on'

        user_settings.font_size = font_size
        user_settings.dark_mode = dark_mode
        user_settings.notifications_enabled = notifications_enabled

        db.session.commit()

    return render_template('settings.html', user_settings=user_settings)
# run the code when integrated with other files
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)