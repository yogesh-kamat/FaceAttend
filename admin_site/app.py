from flask import Flask,render_template,request,redirect,url_for,session
import MySQLdb
import os

#import for face recongition
from math import sqrt
from sklearn import neighbors
from os import listdir
from os.path import isdir, join, isfile, splitext
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.face_recognition_cli import image_files_in_folder



app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)

conn = MySQLdb.connect(host="localhost",user="root",password="yog12345",db="login_info")

@app.route('/')
def index():
	return render_template("index.html",title="Admin Login")
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login',methods=['POST'])
def login():
	user = str(request.form["user"])
	paswd = str(request.form["password"])
	cursor = conn.cursor()
	result = cursor.execute("SELECT * from admin_login where binary username=%s and binary password=%s",[user,paswd])
	if(result is 1):
		return render_template("task.html")
	else:
		return render_template("index.html",title="Admin Login",msg="The username or password is incorrect")


@app.route('/register_teacher',methods=['POST'])
def register_teacher():
	return render_template("signup.html",title="SignUp")
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/student',methods=['POST'])
def file_upload():
	return render_template("upload.html")


@app.route('/signup_teacher',methods=['POST'])
def signup():
	user = str(request.form["user"])
	paswd = str(request.form["password"])
	email = str(request.form["email"])
	cursor = conn.cursor()
	result = cursor.execute("SELECT * from teacher_login where binary username=%s",[user])
	print (result)
	if(result == 1):
		return render_template("signup.html",title="SignUp",uname=user,msg="already present")
	cursor.execute("INSERT INTO teacher_login (username,password,email) VALUES(%s, %s, %s)",(user,paswd,email))
	conn.commit()
	return render_template("signup.html",title="SignUp",msg="successfully signup",uname=user) 


@app.route('/signup_student',methods=['POST'])
def signup_student():
	user = str(request.form["student_name"])
	email = str(request.form["student_email"])
	roll_id = str(request.form["roll_id"])
	email1 = str(request.form["parent_email"])
	cursor = conn.cursor()
	result = cursor.execute("SELECT * from student_login where binary username=%s",[user])
	print (result)
	if(result == 1):
		return render_template("upload.html",uname=user,msg=" already present")
	cursor.execute("INSERT INTO student_login (username,student_email,parent_email,roll_id) VALUES(%s, %s, %s, %s)",(user,email,email1,roll_id))
	conn.commit()
	return render_template("upload.html",uname=user,msg=" successfully signup")


@app.route("/upload", methods=['POST']) 
def upload():
	target = os.path.join(APP_ROOT,"train/")
	if not os.path.isdir(target):
		os.mkdir(target)
	classfolder = str(request.form['class_folder'])
	session['classfolder'] = classfolder
	target1 = os.path.join(target,str(request.form["class_folder"])+"/")
	session['target1']=target1
	print(target1)
	model = os.path.join(APP_ROOT,"model/")
	if not os.path.isdir(model):
		os.mkdir(model)
	classname = str(request.form['class_folder']+"/")
	model = os.path.join(model,classname)
	if not os.path.isdir(model):
		os.mkdir(model)
	session['model']=model
	session['classname'] = classname
	if not os.path.isdir(target1):
		os.mkdir(target1)
	id_folder = str(request.form["id_folder"])
	session['id_folder']= id_folder
	target2 = os.path.join(target1,id_folder+"/")
	if not os.path.isdir(target2):
		os.mkdir(target2)
	target3 = os.path.join(target2,id_folder+"/")
	if not os.path.isdir(target3):
		os.mkdir(target3)
	for file in request.files.getlist("file"):
		print(file)
		filename = file.filename
		destination = "/".join([target3,filename])
		print(destination)
		file.save(destination)
	return call_train()

def call_train():
	id_folder = str(session.get('id_folder'))
	model=str(session.get('model'))
	if not os.path.isdir(model + id_folder):
		os.mkdir(model + id_folder)
	model = model + id_folder + "/"
	model = model + "model"
	target1=str(session.get('target1'))
	print(id_folder)
	print (target1)
	target1 = target1 +id_folder 
	print(target1)
	print(model)
	return train(train_dir=target1,model_save_path=model)

def train(train_dir, model_save_path = "", n_neighbors = None, knn_algo = 'ball_tree', verbose=True):
    id_folder=str(session.get('id_folder'))
    X = []
    y = []
    z = 0
    for class_dir in listdir(train_dir):
        if not isdir(join(train_dir, class_dir)):
            continue
        for img_path in image_files_in_folder(join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            faces_bboxes = face_locations(image)
            if len(faces_bboxes) != 1:
                if verbose:
                    print("image {} not fit for training: {}".format(img_path, "didn't find a face" if len(faces_bboxes) < 1 else "found more than one face"))
                    os.remove(img_path)
                    z = z + 1
                continue
            X.append(face_recognition.face_encodings(image, known_face_locations=faces_bboxes)[0])
            y.append(class_dir)
    print(listdir(train_dir+"/"+id_folder))
    train_dir_f = listdir(train_dir+"/"+id_folder)
    for i in range(len(train_dir_f)):
    	if(train_dir_f[i].startswith('.')):
    		os.remove(train_dir+"/"+id_folder+"/"+train_dir_f[i])

    print(listdir(train_dir+"/"+id_folder))
    
    if(listdir(train_dir+"/"+id_folder)==[]):
    	return render_template("upload.html",msg1="training data empty, upload again")
    elif(z >= 1):
    	return render_template("upload.html",msg1="Data trained for "+id_folder+", But one of the image not fit for trainning")
    if n_neighbors is None:
        n_neighbors = int(round(sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically as:", n_neighbors)

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    if model_save_path != "":
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return render_template("upload.html",msg1="Data trained for "+ id_folder)

    
@app.route('/changetask',methods=['POST'])
def changetask():
	return render_template("task.html")


@app.route('/logout',methods=['POST'])
def logout():
	return render_template("index.html",title="Admin Login",msg1="Logged out please login again")

if(__name__ == '__main__'):
	app.secret_key = 'secretkey'
	app.run(host="0.0.0.0",port=4555,debug=True)