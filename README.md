# Face-recognition-based-attendance-system

Detail project working here...
https://www.youtube.com/watch?v=0ADsRSF_MHw&t=9s

Project contains two webapp's developed using flask and python3.(http://flask.pocoo.org/)

Database used : MySQL community edition.

For face reocognition I used python3 "face_recogntion" by ageitgey.(https://github.com/ageitgey/face_recognition), Built using dlib's state-of-the-art face recognition built with deep learning. The model has an accuracy of 99.38% on the Labeled Faces in the Wild benchmark.

For spoof detection I used tensorflow inception model by retraining it's last layer so that it can detect mobile phones in an image.(https://www.tensorflow.org/tutorials/image_recognition)

To generate and manage excel I used xlrx and xlrd and pandas. 

For sending email's I used flask-mail.(https://pythonhosted.org/Flask-Mail/)

admin site dependency : flask, mysqlclient, sklearn, numpy, scipy, pillow, dlib, face_recognition

teachers site dependency : flask_bootstrap, pytz, xlsxwriter, pandas, flask_mail, tensorflow,xlrd  

There are mainly two webapps for this project one is say admin site and other one is teacher's site.

The whole concept is at the time of admission to college or school admin should register the students details such as his name email address and also create training data of each student by entering his roll id and taking snaps of his or her frontal face and then webapp will automatically create model for that particular roll id and save it on server, The model which is created for each student is about 8kb in size. Admin can also register teachers using this site.

Now using teacher's site (It will be used when teacher will actually enter the class), teacher has to login first and then after clicking on attendance tab there will be no back button as teacher will pass on the phone to student.

Student's will then have to just click a snap enter class and roll id and press enter to mark their attandance.

After that there is also a problem of spoof attack in face recognition i.e. someone will show someone's image of face through their mobile phone and trick our webapp and they will mark the attendace of their friends who were not present.

But I solved this issue using tensorflow, by training inception to detect mobile phones in an image then I used that model in the webapp as soon as student's click a snap it will first check if the face is spoof or original. 
To retrain inception's last layer I used 200 images of mobile phones and I feed them to tensorflow to retrain the last layer of inception. To do this follow https://codelabs.developers.google.com/codelabs/tensorflow-for-poets/#0
To download 200 images at once use fatkun-batch-download chrome extension.

Now after student's part is done. Teacher can then login again and then go to report's tab to see attendance. Here there are several option's I have given.

If teacher want to see today's attendace, just select date and time to see the attendance. And there is also an option to download the attendace sheet in excel form and then again reupload it after making any changes if sometime required by the teacher. And the teacher can also see total attendance for his or her lecture. so that they can analyze how many lectures each student from particular class had attended so far.

One additional feature is that teacher can send email for the attendance marked to all the parents as well as students by selecting class and clicking on send mail button.
