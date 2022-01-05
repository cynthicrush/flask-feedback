from flask import Flask, redirect, render_template, session
from models import db, connect_db, User, Feedback
from forms import DeleteFeedbackForm, RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'shhh-secret'

connect_db(app)
db.create_all()

@app.route('/')
def homepage():
  '''Redirect to /register.'''

  return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
  '''Show register form and handle adding new users'''

  form = RegisterForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.register(username, password, email, first_name, last_name)

    db.session.add(new_user)
    try:
      db.session.commit()
    except IntegrityError:
      form.username.errors.append('Username taken, please pick another one.')
      return render_template('/user/register.html', form=form)
    session['username'] = new_user.username
    return redirect(f'/users/{username}')
  else:
    return render_template('/user/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  '''Show login form and handle login'''

  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    if user:
      session['username'] = username
      return redirect(f'/users/{username}')
    else:
      form.username.errors = ['Invalid username or password.']
  
  return render_template('/user/login.html', form=form)

@app.route('/logout')
def logout():
  '''Handle logout users.'''
  session.pop('username')
  return redirect('/')

@app.route('/users/<username>')
def show_user(username):
  '''Show informations of a user.'''

  if 'username' not in session or username != session['username']:
    raise Unauthorized()

  user = User.query.get_or_404(username)
  feedback = Feedback.query.filter(Feedback.username == username).all()
  form = DeleteFeedbackForm()
  return render_template('/user/user.html', user=user, feedback=feedback, form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
  '''Delete the user.'''
  
  if 'username' not in session or username != session['username']:
    raise Unauthorized()

  user = User.query.get(username)
  db.session.delete(user)
  db.session.commit()
  session.pop('username')
  return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
  '''Show add feedback form and handle add feedback.'''

  if 'username' not in session or username != session['username']:
    raise Unauthorized()

  form = FeedbackForm()
  if form.validate_on_submit():
    title = form.title.data
    content = form.content.data
    feedback = Feedback(title=title, content=content, username=username)
    
    db.session.add(feedback)
    db.session.commit()

    return redirect(f'/users/{username}')
  else:
    return render_template('/feedback/add.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
  '''Show update feedback form and handle update feedback.'''

  feedback = Feedback.query.get(feedback_id)

  if 'username' not in session or feedback.username != session['username']:
    raise Unauthorized()

  form = FeedbackForm(obj=feedback)
  if form.validate_on_submit():
    feedback.title = form.title.data
    feedback.content = form.content.data

    db.session.commit()

    return redirect(f'/users/{feedback.username}')
  else:
    return render_template('/feedback/update.html', feedback=feedback, form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
  '''Handle delete feedback.'''

  feedback = Feedback.query.get(feedback_id)

  if 'username' not in session or feedback.username != session['username']:
    raise Unauthorized()

  form = DeleteFeedbackForm()

  if form.validate_on_submit():
    db.session.delete(feedback)
    db.session.commit()

  return redirect(f'/users/{feedback.username}')

  




