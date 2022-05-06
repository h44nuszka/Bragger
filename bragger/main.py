import math
from io import BytesIO

from flask import Flask, \
    render_template, \
    redirect, \
    request, \
    session, \
    send_file

import os
import glob
from flask_session.__init__ import Session
from datetime import timedelta
from zipfile import ZipFile
from os.path import exists

UPLOAD_FOLDER = 'static/yourTemplates/static/img'
DOWNLOAD_FOLDER = 'static/yourTemplates'
ZIP_DIRECTORY = 'static/zipDirectory'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.debug = True
app.config['IMAGE_UPLOADS'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ZIP_DIRECTORY'] = ZIP_DIRECTORY
app.config["SESSION_TYPE"] = "filesystem"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
Session(app)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    return redirect('/main')


@app.route('/main')
def main():
    session['portfolioName'] = None
    session['backgroundColor'] = None
    session['fontColor'] = None
    session['columns'] = None
    session['language'] = None
    session['menuElementsQty']= None
    session['menuItems'] = None
    session['siteContent'] = None
    session['menuElementsQty'] = None
    session['filenames'] = None
    session['names'] = None
    session['imageQty']= None
    session['imageInAColumn']= None

    deleteItems()

    if exists("yourTemplates.zip"):
        os.remove("yourTemplates.zip")

    session.modified = True

    session.clear()
    return render_template('index.html')


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/dataForm', methods=['GET','POST'])
def dataForm():
    if request.method == 'POST':
        session['portfolioName'] = request.form['portfolioName']

        if request.form['colors'] == 'light':
            session['backgroundColor'] = '#FFFFFF'
            session['fontColor'] = '#606367'
        elif request.form['colors'] == 'dark':
            session['backgroundColor'] = '#757575'
            session['fontColor'] = '#E8D4D4'
        else:
            session['backgroundColor'] = request.form['background']
            session['fontColor'] = request.form['font']

        gridLayout = request.form['grid']
        gridLayout = gridLayout.split("x", 1)
        session['columns'] = int(gridLayout[0]) - 1

        session['language'] = request.form['language']

        session['menuElementsQty'] = int(request.form['menuElements'])
        session['menuItems'] = []
        session['siteContent'] = []
        appendMenuItemsAndContent()
        createFilesList()

        if session['imageQty'] % (session['columns']+1) < 2:
            session['imageInAColumn'] = session['imageQty'] // (session['columns']+1)
        else:
            if session['imageQty'] == 6:
                session['imageInAColumn'] = session['imageQty'] // (session['columns'] + 1)
            else:
                session['imageInAColumn'] = math.ceil(session['imageQty'] / (session['columns'] + 1))

        if session['menuElementsQty'] == 1:
            saveTemplate('mainPage.html')
        if session['menuElementsQty'] == 2:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
        if session['menuElementsQty'] == 3:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
            saveTemplate('thirdPage.html')
        if session['menuElementsQty'] == 4:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
            saveTemplate('thirdPage.html')
            saveTemplate('fourthPage.html')

        session.modified = True

        return redirect('/mainPage.html')


@app.route('/mainPage.html')
def mainPage():
    return render_template('mainPage.html', filenamesNames = zip(session['filenames'], session['names']), imageInAColumn=session['imageInAColumn'], images=session['filenames'], menuItems=session['menuItems'],menuElementsQty=session['menuElementsQty'], imageQty=session['imageQty'], columns=session['columns'], portfolioName=session['portfolioName'], language=session['language'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'])


@app.route('/secondPage.html')
def secondPage():
    return render_template('secondPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'])


@app.route('/thirdPage.html')
def thirdPage():
    return render_template('thirdPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'])


@app.route('/fourthPage.html')
def fourthPage():
    return render_template('fourthPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'])


@app.route('/end')
def end():
    """
    Zip and send full package with compressed directory.
    """
    fileName = 'yourTemplates.zip'

    directory = app.config['DOWNLOAD_FOLDER']
    rootdir = os.path.basename(directory)

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:
        for dirpath, dirnames, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(dirpath, file)
                parentpath = os.path.relpath(filepath, directory)
                arcname = os.path.join(rootdir, parentpath)
                zf.write(filepath, arcname)

    memory_file.seek(0)
    return send_file(memory_file, attachment_filename=fileName, as_attachment=True, cache_timeout=0)

@app.route('/delete')
def delete():
    deleteItems()
    return redirect('/instructions')


def createFilesList():
    """
    Save uploaded images.
    session['filenames'] is a list of filenames.
    session['names'] is a list of filenames formatted to names displayed on the template.
    """
    session['filenames'] = []
    session['names'] = []
    images = request.files.getlist('image')
    cwd = os.getcwd()

    for image in images:
        image.save(os.path.join(cwd, app.config['IMAGE_UPLOADS'], image.filename))
        session['filenames'].append(image.filename)

    session['imageQty'] = len(images)

    for filename in session['filenames']:
        name = filename.split('.', 1)
        session['names'].append(name[0])

    tmp = []
    for name in session['names']:
        tmp.append(name.replace("_", " "))

    session['names'] = tmp
    session['names'].sort()
    session['filenames'].sort()
    session.modified = True


def deleteItems():
    path = app.config['IMAGE_UPLOADS'] + '/*'
    files = glob.glob(path)
    for f in files:
        os.remove(f)


def appendMenuItemsAndContent():
    if session['menuElementsQty'] == 4:
        saveMenuItems1()
        saveMenuItems2()
        saveMenuItems3()
        saveMenuItems4()
    elif session['menuElementsQty'] == 3:
        saveMenuItems1()
        saveMenuItems2()
        saveMenuItems3()
    elif session['menuElementsQty'] == 2:
        saveMenuItems1()
        saveMenuItems2()
    elif session['menuElementsQty'] == 1:
        saveMenuItems1()


def saveTemplate(pageName):
    name = pageName
    if pageName == 'mainPage.html':
        pageTemplate = render_template('mainPage.html', filenamesNames = zip(session['filenames'],
                                            session['names']), imageInAColumn=session['imageInAColumn'],
                                            images=session['filenames'], menuItems=session['menuItems'],
                                            menuElementsQty=session['menuElementsQty'], imageQty=session['imageQty'],
                                            columns=session['columns'], portfolioName=session['portfolioName'],
                                            language=session['language'], backgroundColor=session['backgroundColor'],
                                            fontColor=session['fontColor'])

        pageTemplate = pageTemplate.replace("/static/yourTemplates/static/img", "static/img")
        print(pageTemplate)
    else:
        pageTemplate = render_template(name, menuItems=session['menuItems'],
                                             menuElementsQty=session['menuElementsQty'],
                                             backgroundColor=session['backgroundColor'], fontColor=session['fontColor'],
                                             language=session['language'], siteContent=session['siteContent'])

    path = app.config['DOWNLOAD_FOLDER'] + '/' + name
    with open(path, 'w') as f:
        f.write(pageTemplate)
        f.close()


def saveMenuItems1():
    session['menuItems'].append(request.form['menuItem1'])

def saveMenuItems2():
    session['menuItems'].append(request.form['menuItem2'])
    session['siteContent'].append(request.form['description2'])

def saveMenuItems3():
    session['menuItems'].append(request.form['menuItem3'])
    session['siteContent'].append(request.form['description3'])

def saveMenuItems4():
    session['menuItems'].append(request.form['menuItem4'])
    session['siteContent'].append(request.form['description4'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5121', debug=True)
