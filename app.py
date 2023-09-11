from flask import Flask , render_template, request, redirect, flash,session,  url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect, secure_filename
from passlib.hash import sha256_crypt
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app=Flask(__name__)
app.secret_key='Abcd1234'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Admindatabase.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS']=False
db=SQLAlchemy(app)
#db.init_app(app)
app.app_context().push()

                       # Table field


class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer, primary_key=True)
    user_email=db.Column(db.String(30),nullable=True)
    password=db.Column(db.String(20),nullable=False)
    bookings=db.relationship('Booking', backref='user', lazy='dynamic')

class Admin(db.Model):
    __tablename__='admin'
    admin_id=db.Column(db.Integer, primary_key=True)
    admin_email=db.Column(db.String(30),nullable=True)
    password=db.Column(db.String(20),nullable=False)
     
class Venue(db.Model):
    venue_id=db.Column(db.Integer, primary_key=True)
    venue_name=db.Column(db.String(20),unique=True, nullable=False)
    place=db.Column(db.String(50),nullable=False)
    location=db.Column(db.String(50), nullable=True)
    capacity=db.Column(db.Integer, nullable=False)
    shows=db.relationship('Show', backref='venue', lazy='dynamic')


class Show(db.Model):
    show_id=db.Column(db.Integer, primary_key=True)
    show_name=db.Column(db.String(20),unique=True, nullable=False)
    tags=db.Column(db.String(50),nullable=False)
    price=db.Column(db.Integer, nullable=False)
    rating=db.Column(db.Integer, nullable=False)
    time=db.Column(db.String, nullable=False)
    venue_id=db.Column(db.Integer, db.ForeignKey('venue.venue_id'))
    bookings=db.relationship('Booking', backref='show', lazy='dynamic')


class Booking(db.Model):
    booking_id=db.Column(db.Integer, primary_key=True) 
    seat=db.Column(db.Integer, nullable=False)
    #remaining_seat=db.Column(db.Integer)
    shows_id=db.Column(db.Integer, db.ForeignKey('show.show_id'))
    user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'))

  #--------+++++++++++--------------++++++++++++++---------------++++++++++++++++
                   # Home page

@app.route('/', methods=['GET', 'POST'])
def Homepage():
    return render_template('Homepage.html')

  # Admin login register pages

@app.route('/admin_register', methods=['GET','POST'])
def admin_register():
    if request.method=='POST':
        password=request.form['password']
        admin_email=request.form['email'] 
        encpassword=sha256_crypt.encrypt(password)
        entry=Admin(admin_email=admin_email, password=encpassword)
        db.session.add(entry)
        db.session.commit()
        #flash('Registered successfully')
        return redirect(url_for('admin_login'))
 
    return render_template('admin_register.html')

@app.route('/admin_login', methods=['GET','POST'])
def admin_login(): 
    if request.method=='POST':
        admin_email=request.form['email']
        password=request.form['password']
        data=Admin.query.filter_by(admin_email=admin_email).first()
        pas=data.password
        if(sha256_crypt.verify(password,pas)):
        ##if(pas == password and user_name==username):
            session['admin_email']=admin_email
            return redirect(url_for('admin_dashboard'))

        else:
            #flash('invalid username/password')
            return redirect(url_for('admin_login'))
     
    return render_template('admin_login.html') 

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_email',None)
    #flash('Logged out successfully')
    return render_template('admin_login.html')  


    #   --------------------User register login pages--------------

@app.route('/user_register', methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        password=request.form['password']
        user_email=request.form['email'] 
        encpassword=sha256_crypt.encrypt(password)
        entry=User(user_email=user_email, password=encpassword)
        db.session.add(entry)
        db.session.commit()
        #flash('Registered successfully')
        return redirect(url_for('user_login'))
 
    return render_template('user_register.html')


@app.route('/user_login', methods=['GET','POST'])
def user_login(): 
    if request.method=='POST':
        user_email=request.form['email']
        password=request.form['password']
        data=User.query.filter_by(user_email=user_email).first()
        vpas=data.password
        if(sha256_crypt.verify(password,vpas)):
        ##if(pas == password and user_name==username)
            session['user_email']=user_email
            return redirect(url_for('user_dashboard'))

        else:
            #flash('invalid username/password')
            return redirect(url_for('user_login'))
     
    return render_template('user_login.html')

@app.route('/user_logout')
def user_logout():
    session.pop('user_email',None)
    #flash('Logged out successfully')
    return render_template('user_login.html') 



@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    usar=User.query.filter_by(user_email=session['user_email']).first()
    datas=Venue.query.all()
    deta=Show.query.all()
    return render_template('user_dashboard.html', usar=usar, datas=datas, deta=deta)


@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    usar=User.query.filter_by(user_email=session['user_email']).first()
    return render_template('user_profile.html', usar=usar)


@app.route("/user_account_delete/<user_email>")
def user_account_delete(user_email):
    dele=User.query.filter_by(user_email=user_email).first()
    db.session.delete(dele)
    db.session.commit()
    return redirect(url_for('user_login'))


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    data=Venue.query.all()
    show_data=Show.query.all()
    return render_template('admin_dashboard.html', data=data, show_data=show_data)

                  #  Admin pages to create the venue and modify it

@app.route('/create_venue', methods=['GET', 'POST'])
def create_venue():
    if request.method=='POST':
        venue_name=request.form['venue-name']
        place=request.form['place']
        location=request.form['location']
        capacity=request.form['capacity']
        entry=Venue(venue_name=venue_name, place=place, location=location, capacity=capacity)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('create_venue.html')


@app.route("/update/<venue_name>", methods=['GET', 'POST'])
def update(venue_name):
    up=Venue.query.filter_by(venue_name=venue_name).first()
    if request.method=='POST':
        up.venue_name=request.form['venue-name']
        up.place=request.form['place']
        up.location=request.form['location']
        up.capacity=request.form['capacity']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('update_venue.html',up=up)

@app.route("/delete/<venue_name>")
def delete(venue_name):
    dele=Venue.query.filter_by(venue_name=venue_name).first()
    db.session.delete(dele)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

                  # Admin pages for show and modify it

@app.route('/create_show', methods=['GET', 'POST'])
def create_show():
    if request.method=='POST':
        show_name=request.form['show-name']
        tags=request.form['tags']
        price=request.form['price']
        rating=request.form['rating']
        time=request.form['time']
        id=request.form['ven-id']
        show_entry=Show(show_name=show_name, price=price, rating=rating,
        time=time, tags=tags, venue_id=id)
        #v=Venue.query.get(id)
        db.session.add(show_entry)
    
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    ven=Venue.query.all()
    return render_template('create_show.html', ven=ven)


@app.route("/update_show/<show_name>", methods=['GET', 'POST'])
def update_show(show_name):
    upp=Show.query.filter_by(show_name=show_name).first()
    if request.method=='POST':
        upp.show_name=request.form['show-name']
        upp.time=request.form['time']
        upp.tags=request.form['tags']
        upp.price=request.form['price']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('update_show.html',upp=upp)


@app.route("/show_delete/<int:show_id>")
def show_delete(show_id):
    dele=Show.query.filter_by(show_id=show_id).first()
    db.session.delete(dele)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


     ###   booking show by user 

@app.route('/confirm_booking/<int:show_id>', methods=['GET', 'POST'])
def confirm_booking(show_id):
    shov=Show.query.filter_by(show_id=show_id).first()
    z=User.query.filter_by(user_email=session['user_email']).first()
    item=Booking.query.filter_by(shows_id=show_id).all()
    sum=0
    for i in item:
        sum=sum+i.seat
    if request.method=='POST':
        seat=request.form['seat']
        data=Booking(seat=seat, shows_id=show_id, user_id=z.user_id)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('user_booked_page'))
    return render_template('confirm_booking.html', shov=shov, sum=int(sum))

@app.route('/user_booked_page', methods=['GET', 'POST'])
def user_booked_page():
    z=User.query.filter_by(user_email=session['user_email']).first()
    books=Booking.query.all()
    return render_template('user_booked_page.html', books=books, z=z)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method=='POST':
        inp=request.form['search']
        out=Venue.query.filter_by(place=inp).all()
        return render_template('search_output.html', out=out)
    return render_template('search.html')

@app.route('/search_output', methods=['GET', 'POST'])
def search_output():
    return render_template('search_output.html')


@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method=='GET':
        ven=Venue.query.all()
        x,y=[],[]      
        for i in ven:
            x.append(i.venue_name)
            y.append(i.capacity)
        plt.bar(x,y)
        plt.xlabel('venue')
        plt.ylabel('capacity')
        plt.title('Capacity of each venue per show :')
        plt.savefig('static/img.png')

        return render_template('summary.html')

if __name__ =="__main__":
    app.run(debug=True)          
