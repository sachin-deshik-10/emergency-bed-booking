from flask import Flask, json, redirect, render_template, flash, request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_required, logout_user, login_user, login_manager, LoginManager, current_user

# from flask_mail import Mail
import json



# # Initialize Firebase with your service account credentials
# cred = credentials.Certificate("project/dbsel-fbee9-firebase-adminsdk-7ea51-530821c34f.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'finalel.appspot.com'
# })
import pyrebase
config = {
    "apiKey": "AIzaSyBdXOBQ2D9fH1zl1Daa6dizItfW9G6mLt0",
    "authDomain": "finalel.firebaseapp.com",
    "projectId": "finalel",
    "storageBucket": "finalel.appspot.com",
    "messagingSenderId": "1020059885152",
    "appId": "1:1020059885152:web:ae43265559d72ee6bead05",
    "measurementId": "G-HNLSWK8R0T"
}
firebase=pyrebase.initialize_app(config)
storage=firebase.storage()
# Create a storage client
storage_client = storage.bucket()
# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "aneesrehmankhan"

# with open('config.json','r') as c:
#     params=json.load(c)["params"]


# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME='gmail account',
#     MAIL_PASSWORD='gmail account password'
# )
# mail = Mail(app)


# this is for getting the unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqldb://root:@localhost/emergency_bed'
dbsql=SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class Test(dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    name = dbsql.Column(dbsql.String(50))


class User(UserMixin, dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    # srfid=dbsql.Column(dbsql.String(20),unique=True)
    email = dbsql.Column(dbsql.String(50))
    dob = dbsql.Column(dbsql.String(1000))


class Hospitaluser(UserMixin, dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    hcode = dbsql.Column(dbsql.String(20))
    email = dbsql.Column(dbsql.String(50))
    password = dbsql.Column(dbsql.String(1000))


class Hospitaldata(dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    hcode = dbsql.Column(dbsql.String(20), unique=True)
    hname = dbsql.Column(dbsql.String(100))
    normalbed = dbsql.Column(dbsql.Integer)
    hicubed = dbsql.Column(dbsql.Integer)
    icubed = dbsql.Column(dbsql.Integer)
    vbed = dbsql.Column(dbsql.Integer)


class Trig(dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    hcode = dbsql.Column(dbsql.String(20))
    normalbed = dbsql.Column(dbsql.Integer)
    hicubed = dbsql.Column(dbsql.Integer)
    icubed = dbsql.Column(dbsql.Integer)
    vbed = dbsql.Column(dbsql.Integer)
    querys = dbsql.Column(dbsql.String(50))
    date = dbsql.Column(dbsql.String(50))


class Bookingpatient(dbsql.Model):
    id = dbsql.Column(dbsql.Integer, primary_key=True)
    # srfid=dbsql.Column(dbsql.String(20),unique=True)
    bedtype = dbsql.Column(dbsql.String(100))
    hcode = dbsql.Column(dbsql.String(20))
    spo2 = dbsql.Column(dbsql.Integer)
    pname = dbsql.Column(dbsql.String(100))
    pphone = dbsql.Column(dbsql.String(100))
    paddress = dbsql.Column(dbsql.String(100))
    email = dbsql.Column(dbsql.String(50), unique=True, nullable=False)


download_url = ""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trigers")
def trigers():
    query = Trig.query.all()
    return render_template("trigers.html", query=query)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        # srfid=request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        # print(srfid,email,dob)
        encpassword = generate_password_hash(dob)
        # user=User.query.filter_by(srfid=srfid).first()
        emailUser = User.query.filter_by(email=email).first()
        if emailUser:
            flash("Email id is already taken", "warning")
            return render_template("usersignup.html")
        # new_user=dbsql.engine.execute(f"INSERT INTO user (srfid,email,dob) VALUES ('{srfid}','{email}','{encpassword}') ")
        new_user = User(email=email, dob=encpassword)
        dbsql.session.add(new_user)
        dbsql.session.commit()

        flash("SignUp Success Please Login", "success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        # srfid=request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        # user=User.query.filter_by(srfid=srfid).first()
        emailUser = User.query.filter_by(email=email).first()
        if emailUser and check_password_hash(emailUser.dob, dob):
            login_user(emailUser)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")


@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if (username == "admin" and password == "admin"):
            session['user'] = username
            flash("login success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials", "danger")

    return render_template("admin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('login'))


@app.route('/addHospitalUser', methods=['POST', 'GET'])
def hospitalUser():
    if ('user' in session and session['user'] == "admin"):

        if request.method == "POST":
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')
            encpassword = generate_password_hash(password)
            hcode = hcode.upper()
            emailUser = Hospitaluser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email or srif is already taken", "warning")

            # dbsql.engine.execute(f"INSERT INTO hospitaluser (hcode,email,password) VALUES ('{hcode}','{email}','{encpassword}') ")
            query = Hospitaluser(hcode=hcode, email=email, password=encpassword)
            dbsql.session.add(query)
            dbsql.session.commit()

            # my mail starts from here if you not need to send mail comment the below line

            # mail.send_message('COVID CARE CENTER',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\n Email Address: {email}\nPassword: {password}\n\nHospital Code {hcode}\n\n Do not share your password\n\n\nThank You..." )

            flash("Data Sent and Inserted Successfully", "warning")
            return render_template("addHosUser.html")

    else:
        flash("Login and try Again", "warning")
        return render_template("addHosUser.html")


# testing wheather dbsql is connected or not
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'


@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')


def updatess(code):
    postsdata = Hospitaldata.query.filter_by(hcode=code).first()
    return render_template("hospitaldata.html", postsdata=postsdata)


@app.route("/addhospitalinfo", methods=['POST', 'GET'])
def addhospitalinfo():
    email = Hospitaluser.email
    posts = Hospitaluser.query.filter_by(email=email).first()
    # if not posts:
    #     return redirect('/admin')
    code = posts.hcode
    postsdata = Hospitaldata.query.filter_by(hcode=code).first()

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        nbed = request.form.get('normalbed')
        hbed = request.form.get('hicubeds')
        ibed = request.form.get('icubeds')
        vbed = request.form.get('ventbeds')
        hcode = hcode.upper()
        huser = Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser = Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..", "primary")
            return render_template("hospitaldata.html")
        if huser:
            # dbsql.engine.execute(f"INSERT INTO hospitaldata (hcode,hname,normalbed,hicubed,icubed,vbed) VALUES ('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')")
            query = Hospitaldata(hcode=hcode, hname=hname, normalbed=nbed, hicubed=hbed, icubed=ibed, vbed=vbed)
            dbsql.session.add(query)
            dbsql.session.commit()
            flash("Data Is Added", "primary")
            return redirect('/addhospitalinfo')


        else:
            flash("Hospital Code not Exist", "warning")
            return redirect('/addhospitalinfo')

    return render_template("hospitaldata.html", postsdata=postsdata)


@app.route("/hedit/<string:id>", methods=['POST', 'GET'])
@login_required
def hedit(id):
    posts = Hospitaldata.query.filter_by(id=id).first()

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        nbed = request.form.get('normalbed')
        hbed = request.form.get('hicubeds')
        ibed = request.form.get('icubeds')
        vbed = request.form.get('ventbeds')
        hcode = hcode.upper()
        # dbsql.engine.execute(f"UPDATE hospitaldata SET hcode ='{hcode}',hname='{hname}',normalbed='{nbed}',hicubed='{hbed}',icubed='{ibed}',vbed='{vbed}' WHERE hospitaldata.id={id}")
        post = Hospitaldata.query.filter_by(id=id).first()
        post.hcode = hcode
        post.hname = hname
        post.normalbed = nbed
        post.hicubed = hbed
        post.icubed = ibed
        post.vbed = vbed
        dbsql.session.commit()
        flash("Slot Updated", "info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html", posts=posts)


@app.route("/hdelete/<string:id>", methods=['POST', 'GET'])
@login_required
def hdelete(id):
    # dbsql.engine.execute(f"DELETE FROM hospitaldata WHERE hospitaldata.id={id}")
    post = Hospitaldata.query.filter_by(id=id).first()
    dbsql.session.delete(post)
    dbsql.session.commit()
    flash("Date Deleted", "danger")
    return redirect("/addhospitalinfo")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    # Upload file to Firebase Storage
    bucket = storage_client.bucket('dbsel-fbee9')
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)

    # Get the public URL of the uploaded file
    download_url = blob.public_url

    # Store the download URL in the session variable
    session['download_url'] = download_url

    return render_template("base.html")


@app.route('/view_pdf')
def view_pdf():
    # Retrieve the download URL from the session
    download_url = session.get('download_url')
    return render_template("view_pdf.html", download_url=download_url)


@app.route("/pdetails", methods=['GET'])
@login_required
def pdetails():
    download_url = session.get('download_url', None)
    email = current_user.email
    posts = Hospitaluser.query.filter_by(email=email).first()
    # if not posts:
    #     return redirect('/admin')
    code = posts.hcode
    data = Bookingpatient.query.filter_by(hcode=code).first()
    return render_template("detials.html", data=data, download_url=download_url)


@app.route("/slotbooking", methods=['POST', 'GET'])
@login_required
def slotbookig():
    # query1=dbsql.engine.execute(f"SELECT * FROM hospitaldata ")
    # query=dbsql.engine.execute(f"SELECT * FROM hospitaldata ")
    query1 = Hospitaldata.query.all()
    query = Hospitaldata.query.all()
    if request.method == "POST":

        # srfid=request.form.get('srfid')
        email = request.form.get('email')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')
        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = Bookingpatient.query.filter_by(email=email).first()

        if checkpatient:
            flash("already email id is registered ", "warning")
            return render_template("booking.html", query=query, query1=query1)

        if not check2:
            flash("Hospital Code not exist", "warning")
            return render_template("booking.html", query=query, query1=query1)

        code = hcode
        # dbsqlb=dbsql.engine.execute(f"SELECT * FROM hospitaldata WHERE hospitaldata.hcode='{code}' ")
        dbsqlb = Hospitaldata.query.filter_by(hcode=hcode).first()
        bedtype = bedtype
        if bedtype == "NormalBed":
            # bb
            seat = dbsqlb.normalbed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=code).first()
            ar.normalbed = seat - 1
            dbsql.session.commit()


        elif bedtype == "HICUBed":
            # for d in dbsqlb:
            seat = dbsqlb.hicubed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=code).first()
            ar.hicubed = seat - 1
            dbsql.session.commit()

        elif bedtype == "ICUBed":
            # for d in dbsqlb:
            seat = dbsqlb.icubed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=code).first()
            ar.icubed = seat - 1
            dbsql.session.commit()

        elif bedtype == "VENTILATORBed":
            # for d in dbsqlb:
            seat = dbsqlb.vbed
            ar = Hospitaldata.query.filter_by(hcode=code).first()
            ar.vbed = seat - 1
            dbsql.session.commit()
        else:
            pass

        check = Hospitaldata.query.filter_by(hcode=hcode).first()
        if check != None:
            if (seat > 0 and check):
                res = Bookingpatient(bedtype=bedtype, hcode=hcode, spo2=spo2, pname=pname, pphone=pphone,
                                     paddress=paddress)
                dbsql.session.add(res)
                dbsql.session.commit()
                flash("Slot is Booked kindly Visit Hospital for Further Procedure", "success")
                return render_template("upload_file.html", query=query, query1=query1)
            else:
                flash("Something Went Wrong", "danger")
                return render_template("booking.html", query=query, query1=query1)
        else:
            flash("Give the proper hospital Code", "info")
            return render_template("booking.html", query=query, query1=query1)

    return render_template("booking.html", query=query, query1=query1)


app.run(debug=True)