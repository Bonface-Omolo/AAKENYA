from flask import Flask,render_template,request,redirect,session
import pymysql
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "ssfksfj898d"#just a random string of characters.

UPLOAD_FOLDER = "static/img"
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/',methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/about',methods=['POST','GET'])
def about():
    return render_template('about.html')

@app.route('/adminhome',methods=['POST','GET'])
def adminihome():
    return render_template('adminhome.html')

@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
     return render_template('adminlogin.html')

@app.route('/loginadmin',methods=['POST','GET'])
def loginadmin():
    if request.method == "POST":
        #we check if the form has beed posted with empty fields
        email = str(request.form['email'])
        password = str(request.form['password'])
        if email == "" or password == "":
            return render_template("adminlogin.html",msg="Ensure that no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM admin WHERE email=%s AND password=%s"
            cur.execute(sql,(email,password))
            if cur.rowcount >= 1:#if this evaluates to true..
                #...then we login the user by creating a sesssion.
                results = cur.fetchall()
                session['fullname'] = results[0][1] + " "+results[0][2]
                session['username'] = email
                return redirect('/adminhome')
            else:
                return render_template("adminlogin.html",msg="The Email/Password Combination is Incorrect!")

    else:
        return render_template("adminlogin.html",msg = "Wrong Request Method")

@app.route('/employee',methods=['POST','GET'])
def employee():
     return render_template('employee.html')

@app.route('/viewapplied',methods=['POST','GET'])
def appliedview():
    if 'username' in session:
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM opportunity ORDER BY id ASC"
        cur.execute(sql)
        if(cur.rowcount >= 1):
            return render_template("view-applied.html",result = cur.fetchall())
        else:
            return render_template('view-applied.html')
    else:
        return render_template('adminlogin.html',msg="Please Login First")


@app.route('/viewcustomer',methods=['POST','GET'])
def customerview():
    if 'username' in session:
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM users ORDER BY id ASC"
        cur.execute(sql)
        if (cur.rowcount >= 1):
            return render_template("view-customer.html", result=cur.fetchall())
        else:
            return render_template('view-customer.html')
    else:
        return render_template('adminlogin.html', msg="Please Login First")


@app.route('/viewmanagement',methods=['POST','GET'])
def managementview():
    if 'username' in session:
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM admin ORDER BY id ASC"
        cur.execute(sql)
        if (cur.rowcount >= 1):
            return render_template("view-management.html", result=cur.fetchall())
        else:
            return render_template('view-management.html')
    else:
        return render_template('adminlogin.html', msg="Please Login First")


@app.route('/viewpost',methods=['POST','GET'])
def postview():
    if 'username' in session:
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM post ORDER BY id ASC"
        cur.execute(sql)
        if(cur.rowcount >= 1):
            return render_template("view-post.html",result = cur.fetchall())
        else:
            return render_template('view-post.html')
    else:
        return render_template('adminlogin.html',msg="Please Login First")


@app.route('/addemployee',methods=['POST','GET'])
def addemploy():
    if request.method == "POST":
        employid = str(request.form['id'])
        fname = request.form['fname']
        lname = str(request.form['lname'])
        email = str(request.form['email'])
        password = str(request.form['password'])
        if employid == "" or fname == "" or lname == "" or email == "" or password == "":
            return render_template("home.html",msg="Ensure no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO admin(employid,fname,lname,email,password)VALUES(%s,%s,%s,%s,%s)"
            cur.execute(sql,(employid,fname,lname,email,password))
            conn.commit()
            return render_template("employee.html", msg="Account created Successful")
    else:
        return redirect('/employee')

@app.route('/post',methods=['POST','GET'])
def post():
     return render_template('post.html')


@app.route('/posting',methods=['POST','GET'])
def addpost():
    if request.method == "POST":
        opportunuies = request.form['opportunity']
        amount = str(request.form['amount'])
        stage = str(request.form['stage'])
        if  opportunuies == "" or amount == "" or stage == "":
            return render_template("post.html", msg="Ensure no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO post (opportunity,amount,stage)VALUES(%s,%s,%s)"
            cur.execute(sql, ( opportunuies, amount, stage))
            conn.commit()
            return render_template("post.html", msg="Service Submited Successful")
    else:
        return redirect('/post')

@app.route('/services',methods=['POST','GET'])
def services():
     return render_template('services.html')

@app.route('/add-services',methods=['POST','GET'])
def addservices():
    if request.method == "POST":
        idnumber = str(request.form['id'])
        opportunities = request.form['opportunity']
        amount = str(request.form['amount'])
        stage = str(request.form['stage'])
        if idnumber == "" or opportunities == "" or amount == "" or stage == "":
            return render_template("services.html",msg="Ensure no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO opportunity(idnumber,opportunity,amount,stage)VALUES(%s,%s,%s,%s)"
            cur.execute(sql,(idnumber,opportunities,amount,stage))
            conn.commit()
            return render_template("services.html", msg="Service Submited Successful")
    else:
        return redirect('/services')




@app.route('/products',methods=['POST','GET'])
def products():
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM products ORDER BY product_id ASC"
    cur.execute(sql)
    if(cur.rowcount >= 1):
        return render_template("products.html",result = cur.fetchall())
    else:
        return render_template('products.html',result = "No Products Found")


@app.route('/checkout',methods=['POST','GET'])
def checkout():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM products WHERE product_id = %s"
    cur.execute(sql,(id))
    if(cur.rowcount >= 1):
        return render_template('checkout.html',result=cur.fetchall())
    else:
        return redirect('/checkout')


@app.route('/contacts',methods=['POST','GET'])
def contacts():
    return render_template('contacts.html')

@app.route('/home',methods=['POST','GET'])
def home():
    if 'username' in session:
        return render_template('home.html',fullname = session['fullname'])
    else:
        return render_template('login.html',msg="Please Login First")

@app.route('/view-products',methods=['POST','GET'])
def viewProduct():
    if 'username' in session:
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM opportunity ORDER BY id ASC"
        cur.execute(sql)
        if(cur.rowcount >= 1):
            return render_template("view_products.html",result = cur.fetchall())
        else:
            return render_template('view_products.html')
    else:
        return render_template('login.html',msg="Please Login First")


@app.route('/delete-post',methods=['POST','GET'])
def deletepost():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "DELETE FROM post WHERE id = %s"
    cur.execute(sql,(id))
    conn.commit()
    return redirect('/viewpost')

@app.route('/delete-applied',methods=['POST','GET'])
def deleteapplied():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "DELETE FROM opportunity WHERE id = %s"
    cur.execute(sql,(id))
    conn.commit()
    return redirect('/viewapplied')

@app.route('/delete-customer',methods=['POST','GET'])
def deletecustomer():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "DELETE FROM users WHERE id = %s"
    cur.execute(sql,(id))
    conn.commit()
    return redirect('/viewcustomer')

@app.route('/delete-management',methods=['POST','GET'])
def deletemanagement():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "DELETE FROM admin WHERE id = %s"
    cur.execute(sql,(id))
    conn.commit()
    return redirect('/viewmanagement')

@app.route('/update-applied',methods=['POST','GET'])
def updateapplied():
    applied_id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM opportunity WHERE id = %s"
    cur.execute(sql,(applied_id))
    if(cur.rowcount >= 1):
        return render_template("update-applied.html",result=cur.fetchall())
    else:
        return redirect('/view-applied')

@app.route('/update-management',methods=['POST','GET'])
def updatemanagement():
    prod_id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM admin WHERE id = %s"
    cur.execute(sql,(prod_id))
    if(cur.rowcount >= 1):
        return render_template("update-management.html",result=cur.fetchall())
    else:
        return redirect('/view-management')
@app.route('/update-customer',methods=['POST','GET'])
def updatecustomer():
    prod_id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM users WHERE id = %s"
    cur.execute(sql,(prod_id))
    if(cur.rowcount >= 1):
        return render_template("update-customer.html",result=cur.fetchall())
    else:
        return redirect('/view-customer')

@app.route('/update-post',methods=['POST','GET'])
def updatepost():
    post_id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM post WHERE id = %s"
    cur.execute(sql,(post_id))
    if(cur.rowcount >= 1):
        return render_template("update-post.html",result=cur.fetchall())
    else:
        return redirect('/view-post')

@app.route('/perform-post',methods=['POST','GET'])
def performpost():
    if request.method == 'POST':
        opportunity = str(request.form['opportunity'])
        amount = str(request.form['amount'])
        stage = str(request.form['stage'])
        post_id = str(request.form['id'])
        if opportunity == "" or amount == "" or stage == "":
            return redirect('/update-customer?id=')
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "UPDATE post SET opportunity=%s,amount=%s,stage=%s WHERE id=%s"
            cur.execute(sql, (opportunity, amount, stage,post_id))
            conn.commit()
            return redirect('/viewpost')
    else:
        return redirect('/adminhome')

@app.route('/perform-customer',methods=['POST','GET'])
def performcustomer():
    if request.method == 'POST':
        idnumber = str(request.form['idnumber'])
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        customer_id = str(request.form['id'])
        email = str(request.form['email'])
        if idnumber == "" or fname == "" or lname == "" or email =="":
            return redirect('/update-customer?id=')
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "UPDATE users SET idnumber=%s,fname=%s,lname=%s,email=%s WHERE id=%s"
            cur.execute(sql, (idnumber, fname, lname,email,customer_id))
            conn.commit()
            return redirect('/viewcustomer')
    else:
        return redirect('/adminhome')

@app.route('/perform-management',methods=['POST','GET'])
def performmanagement():
    if request.method == 'POST':
        idnumber = str(request.form['idnumber'])
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        admin_id = str(request.form['id'])
        email = str(request.form['email'])
        if idnumber == "" or fname == "" or lname == "" or email =="":
            return redirect('/update-management?id=')
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "UPDATE admin SET employid=%s,fname=%s,lname=%s,email=%s WHERE id=%s"
            cur.execute(sql, (idnumber, fname, lname,email,admin_id))
            conn.commit()
            return redirect('/viewmanagement')
    else:
        return redirect('/adminhome')


@app.route('/perform-applied',methods=['POST','GET'])
def performapplied():
    if request.method == 'POST':
        idnumber = str(request.form['idnumber'])
        opportunity = str(request.form['opportunity'])
        amount = str(request.form['amount'])
        applied_id = str(request.form['id'])
        stage = str(request.form['stage'])
        if idnumber == "" or opportunity == "" or amount == "" or stage =="":
            return redirect('/update-applied?id=')
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "UPDATE opportunity SET idnumber=%s,opportunity=%s,amount=%s,stage=%s WHERE id=%s"
            cur.execute(sql, (idnumber, opportunity, amount,stage,applied_id))
            conn.commit()
            return redirect('/viewapplied')
    else:
        return redirect('/adminhome')

@app.route('/user-home',methods=['POST','GET'])
def userHome():
    if 'customer' in session:
        return "something"
    else:
        return "some other thing here"

@app.route('/register',methods=['POST','GET'])
def register():
    return render_template('register.html')

@app.route('/add-users-to-db',methods=['POST','GET'])
def addUsers():
    if request.method == "POST":
        #we proceed with the registration
        idnumber = str(request.form['id'])
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        email = str(request.form['email'])
        password = str(request.form['password'])

        message = ""
        #we check if the fields are empty
        if idnumber == "" or  fname == "" or lname == "" or email == "" or password == "" :
            return render_template("register.html",msg="Ensure none of the fields are empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            check_sql = "SELECT email FROM users WHERE email=%s"
            check_id = "SELECT idnumber FROM users WHERE idnumber=%s"
            cur.execute(check_sql,(email))
            cur_id = conn.cursor()
            cur_id.execute(check_id, (idnumber))
            if cur.rowcount >= 1:
                message = "The email "+email+" is already registered"
                return render_template("register.html", msg=message)
            elif cur_id.rowcount >= 1:
                message = "The Id Number " + idnumber + " is already registered"
                return render_template("register.html", msg=message)
            elif cur.rowcount == 0:
                sql = "INSERT INTO users(idnumber, fname,lname,email,password)values(%s,%s,%s,%s,%s)"
                cur.execute(sql,( idnumber,fname,lname,email,password,))
                conn.commit()
                message = "Registered Successfully"
                return render_template("login.html")
    else:
        #we redirect the user to the login page
        return redirect('/register')

@app.route('/login',methods=['POST','GET'])
def login():
    return render_template('login.html')

@app.route('/login-user',methods=['POST','GET'])
def loginUser():
    if request.method == "POST":
        #we check if the form has beed posted with empty fields
        email = str(request.form['email'])
        password = str(request.form['password'])
        if email == "" or password == "":
            return render_template("login.html",msg="Ensure that no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM users WHERE email=%s AND password=%s"
            cur.execute(sql,(email,password))
            if cur.rowcount >= 1:#if this evaluates to true..
                #...then we login the user by creating a sesssion.
                results = cur.fetchall()
                session['fullname'] = results[0][2] + " "+results[0][3]
                session['username'] = email
                return redirect('/home')
            else:
                return render_template("login.html",msg="The Email/Password Combination is Incorrect!")

    else:
        return render_template("login.html",msg = "Wrong Request Method")

@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('username',None)
    return redirect('/')

def makeConnection():
    host = "127.0.0.1"
    user = "root"
    password = ""
    database = "AAKENYA" #this is the name of your database
    return pymysql.connect(host,user,password,database)

#return pymysql.connect("127.0.0.1","root","","login_example")

if __name__ == "__main__":
    app.run(debug=True,port=3000)