from flask import Flask,render_template,request,redirect,url_for,session
from flask_bootstrap import Bootstrap
import MySQLdb
import os
from math import sqrt
from sklearn import neighbors
from os import listdir
from os.path import isdir, join, isfile, splitext
import shutil
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.face_recognition_cli import image_files_in_folder
from datetime import datetime,timedelta
from pytz import timezone
import xlsxwriter
import pandas as pd
from glob import glob
from flask_mail import Mail, Message
from io import BytesIO
import base64
import lable_image

app = Flask(__name__,static_folder="excel")

# mail settings

app.config.update(
    DEBUG = True,
    #Email settings
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'college1118@gmail.com',
    MAIL_PASSWORD = 'yog12345',
    MAIL_DEFAULT_SENDER = 'college1118@gmail.com'
    )
mail = Mail(app)

# declaring timezone then creating custom date format 

india = timezone('Asia/Kolkata')
date = str(datetime.now(india))[:10] + "@" + str(datetime.now())[11:13] + "hrs"

# getting the location of root directory of the webapp

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

APP_ROOT1 = APP_ROOT.split('teachers_site')

# connection with mysql database using python package MySQLdb

conn = MySQLdb.connect(host="localhost",user="root",password="yog12345",db="login_info")


@app.route('/')
def index():
    return render_template("index.html",title="Faculty Login")
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/login',methods=['POST'])
def login():
    print(APP_ROOT)
    print(APP_ROOT1[0])
    user = str(request.form["user"])
    session['user'] = user
    paswd = str(request.form["password"])
    username = user.split(".",1)[0]
    username = str(username)
    print(username)
    print(type(username))
    cursor = conn.cursor()
    result = cursor.execute("SELECT * from teacher_login where binary username=%s and binary password=%s",[user,paswd])
    if(result is 1):
        return render_template("task.html",uname=username)
    else:
        return render_template("index.html",title="Faculty Login",msg="The username or password is incorrect")

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/upload_redirect',methods=['POST'])
def upload_redirect():
    if(os.path.isfile(APP_ROOT+"/image.jpeg")):
        os.remove(APP_ROOT + "/image.jpeg")
    return render_template("upload.html")

@app.route("/upload", methods=['POST'])
def upload():
    if not os.path.isfile(APP_ROOT+"/image.jpeg"):
        return render_template("upload.html",msg="spoof detected")
    id_folder = str(request.form['id_folder'])
    session['id_folder']= id_folder
    target = os.path.join(APP_ROOT,"test/")
    if not os.path.isdir(target):
        os.mkdir(target)
    target1 = os.path.join(target,str(request.form["folder_name"])+"/")
    test_append = str(request.form["folder_name"])
    session['test_append']= test_append
    print(target1)
    if not os.path.isdir(target1):
        os.mkdir(target1)
    shutil.copyfile(APP_ROOT+"/"+"image.jpeg",target1+"image.jpeg")
    destination = APP_ROOT + "/" + "test/" + test_append + "/" + "image.jpeg"
    
    session['destination'] = destination
    teacher_name = str(session.get('user'))
    session['teacher_name'] = teacher_name
    #return render_template("upload.html",msg="uploaded successfully")
    return match()

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def match():
    destination = str(session.get('destination'))
    print(destination)
    if os.path.isfile(destination):
        test_append = str(session.get('test_append'))
        session['test_append'] = test_append
        id_folder = str(session.get('id_folder'))

        train_dir = APP_ROOT1[0]+"admin_site/train/"+ test_append
        try:
            model = APP_ROOT1[0]+"admin_site/model/"+test_append+"/" + id_folder + "/" +"model"
            print(model)
            return predict1(model)
        except FileNotFoundError:
            os.remove(APP_ROOT1[0]+"teachers_site/image.jpeg")
            return render_template("upload.html",msg="trained model not present for " + test_append + ": "+id_folder)
        

def predict(X_img_path, knn_clf = None, model_save_path ="", DIST_THRESH = .45):
    if knn_clf is None and model_save_path == "":
        raise Exception("must supply knn classifier either thourgh knn_clf or model_save_path")

    if knn_clf is None:
        with open(model_save_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_img = face_recognition.load_image_file(X_img_path)
    X_faces_loc = face_locations(X_img)
    if len(X_faces_loc) == 0:
        return []

    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_faces_loc)


    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)

    is_recognized = [closest_distances[0][i][0] <= DIST_THRESH for i in range(len(X_faces_loc))]
    

    return [(pred) if rec else ("unknown") for pred, rec in zip(knn_clf.predict(faces_encodings), is_recognized)]

def predict1(model):
    test_append = str(session.get('test_append'))
    test_dir = APP_ROOT1[0]+"teachers_site/test/" + test_append
    f_preds = []
    for img_path in listdir(test_dir):
        preds = predict(join(test_dir, img_path) ,model_save_path=model)
        f_preds.append(preds)
        print(f_preds)
    print(len(preds))
    print(len(f_preds))
    for i in range(len(f_preds)):
        if(f_preds[i]==[]):
            os.remove(APP_ROOT1[0]+"teachers_site/image.jpeg")
            return render_template("upload.html",msg="upload again, face not found")
        else:
            os.remove(APP_ROOT1[0]+"teachers_site/image.jpeg")
    excel = os.path.join(APP_ROOT,"excel/")
    if not os.path.isdir(excel):
        os.mkdir(excel)
    excel1 = os.path.join(excel,test_append)
    if not os.path.isdir(excel1):
        os.mkdir(excel1)
    teacher_name = str(session.get('teacher_name'))
    excel2 = os.path.join(excel1,teacher_name)
    if not os.path.isdir(excel2):
        os.mkdir(excel2)
    session['excel2'] = excel2
    excel3 = excel2+"/"+date+'.xlsx'
    if not os.path.isfile(excel3):
        workbook = xlsxwriter.Workbook(excel2+"/"+date+'.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0,0,20)
        worksheet.write('A1','Roll Id')
        f_preds.sort()
        row = 1
        col = 0
        for i in range(len(f_preds)):
            for j in range(len(f_preds[i])):
                worksheet.write_string(row,col,f_preds[i][j])
                row += 1
        workbook.close()
        return render_template("upload.html",msg= f_preds[0][0] + " present")
    else:
        df = pd.read_excel(excel2+"/"+date+'.xlsx')
        writer = pd.ExcelWriter(excel2 + "/" + date+'.xlsx')
        df.to_excel(writer,sheet_name="Sheet1",index=False)
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']
        rows=df.shape[0]
        worksheet.write_string(rows+1,0,f_preds[0][0])
        writer.save()
        df = pd.read_excel(excel2+"/"+date+'.xlsx')
        df.drop_duplicates(['Roll Id'],keep='first',inplace=True)
        result = df.sort_values("Roll Id")
        writer = pd.ExcelWriter(excel2 + "/" + date+'.xlsx')
        result.to_excel(writer,'Sheet1',index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column(0,0,20)
        writer.save()
        return render_template("upload.html",msg= f_preds[0][0] + " present")

@app.route('/view_report',methods=['POST'])
def view_report():
    return render_template("excel.html")

# view route to download excel files 


@app.route('/view',methods=['POST'])
def view():
    test_append = str(request.form['folder_name'])
    session['test_append']=test_append
    teacher_name = str(session.get('user'))
    excel_dir = APP_ROOT+"/excel/"+test_append+"/"+teacher_name+"/"
    excel_date = request.form['fname']
    time = request.form['ftime']
    time = time[:2]
    print(time)
    final_excel=glob(excel_dir + "/" + excel_date+ "@" + time +"*.xlsx")[0]
    print(final_excel)

    df = pd.read_excel(final_excel)
    df.index += 1
    return render_template("files.html",msg=final_excel,df=df,date=excel_date+"@"+time+"hrs")
@app.route('/excel/<path:filename>', methods=['POST'])
def download(filename):    
    return send_from_directory(directory='excel', filename=filename)


# route to send emails to parents and students

@app.route('/send_mail',methods=['POST'])
def send_mail():
    test_append = str(request.form['folder_name'])
    teacher_name = str(session.get('user'))
    excel_dir = APP_ROOT+"/excel/"+test_append+"/"+teacher_name+"/"
    excel_date = request.form['fname']
    time = request.form['ftime']
    time = time[:2]
    final_send = glob(excel_dir + "/" + excel_date+ "@" + time +"*.xlsx")[0]
    print(final_send)
    df = pd.read_excel(final_send)
    roll_id = list(df['Roll Id'])
    print(type(roll_id))
    print(roll_id)
    cursor = conn.cursor()
    for i in range(len(roll_id)):
        cursor.execute("SELECT student_email,parent_email from student_login where binary roll_id=%s",[roll_id[i]])
        email = list(cursor.fetchone())
        print(type(email[1]))
        print(email[0])
        print(email[1])
        msg = Message('Auto Generated',recipients= [email[0],email[1]])
        msg.body = "Hi.. " + roll_id[i] + " is present for the lecture of " + "Prof. " +str(teacher_name.split('.',1)[0]) + ", which is held on " + excel_date + "@" + time + "hrs"
        msg.html = "Hi.. " + roll_id[i] + " is present for the lecture of " + "Prof. " +str(teacher_name .split('.',1)[0])+ ", which is held on " + excel_date + "@" + time + "hrs"
        mail.send(msg)
    return "<h1>mail sent<h1>"


@app.route('/update',methods=['POST'])
def update():
    test_append = str(request.form['excel_folder'])
    print(test_append)
    teacher_name = str(session.get('user'))
    print(teacher_name)
    excel_dir = APP_ROOT + "/excel/" + test_append + "/" + teacher_name + "/"
    print(excel_dir)
    for file in request.files.getlist("updated_excel"):
        print(file)
        filename = file.filename
        print(filename)
        destination = "/".join([excel_dir,filename])
        print(destination)
        file.save(destination)
    return render_template("excel.html",msg="updated successfully")

@app.route('/calculate',methods=['POST'])
def calculate():
    test_append = str(request.form['final_class'])
    print(test_append)
    teacher_name = str(session.get('user'))
    print(teacher_name)
    excel_root = APP_ROOT + "/excel/" + test_append + "/" + teacher_name + "/"
    print(excel_root)
    excel_names = os.listdir(excel_root)
    print(excel_names) 
    for i in range(len(excel_names)):
        if excel_names[i].startswith("."):
            os.remove(excel_root+excel_names[i])
        else:
            if os.path.isdir(excel_root+excel_names[i]):
                shutil.rmtree(excel_root+excel_names[i], ignore_errors=False, onerror=None)
    excel_names = os.listdir(excel_root)

    if(excel_names==[]):
        return render_template("excel.html",msg1="No excel files found")

    for i in range(len(excel_names)):
        excel_names[i] = excel_root + excel_names[i]
    print(type(excel_names))
    # read them in
    excels = [pd.ExcelFile(name) for name in excel_names]
    # turn them into dataframes
    frames = [x.parse(x.sheet_names[0], header=None,index_col=None) for x in excels]
    # delete the first row for all frames except the first
    # i.e. remove the header row -- assumes it's the first
    frames[1:] = [df[1:] for df in frames[1:]]
    # concatenate them..
    combined = pd.concat(frames)
    if not os.path.isdir(excel_root+"final/"):
        os.mkdir(excel_root + "final/")
    final = excel_root + "final/"
    print(final)
    # write it out
    combined.to_excel(final+"final.xlsx", header=False, index=False)

    # below code is to find actual repetative blocks

    workbook = pd.ExcelFile(final+"final.xlsx")
    df = workbook.parse('Sheet1')
    sample_data = df['Roll Id'].tolist()
    print (sample_data)
    #a dict that will store the poll results
    results = {}
    for response in sample_data:
        results[response] = results.setdefault(response, 0) + 1
    finaldf = (pd.DataFrame(list(results.items()), columns=['Roll Id', 'Total presenty']))
    finaldf = finaldf.sort_values("Roll Id")
    print (finaldf)
    writer = pd.ExcelWriter(final+"final.xlsx")
    finaldf.to_excel(writer,'Sheet1',index=False)
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(0,1,20)
    writer.save()
    final = final + "final.xlsx"
    session['final']=final
    final = final[91:]
    return viewfinal(final)

def viewfinal(final):
    test_append = str(session.get('test_append'))
    final_path = str(session.get('final'))
    df = pd.read_excel(final_path)
    df.index += 1
    return render_template("files.html",msg=final,course=test_append,df=df)


@app.route('/changetask',methods=['POST'])
def changetask():
    return render_template("task.html")

@app.route('/logout',methods=['POST'])
def logout():
    return render_template("index.html",title="Faculty Login",msg1="Logged out please login again")


@app.route('/hello',methods=['POST'])
def hello():
    data_url = request.values['imageBase64']
    data_url= data_url[22:] 
    im = Image.open(BytesIO(base64.b64decode(data_url)))
    print(type(im))
    im.save('image.jpeg')
    filepath = APP_ROOT + "/" + "image.jpeg"
    var = lable_image.function(filepath)
    print(var)
    for i in range(len(var)):
        if(var[i] > 0.8):
            os.remove(filepath)
    return ''

if(__name__ == '__main__'):
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0',port=4545,debug=True)