from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from PIL import Image
from math import sqrt
from ast import literal_eval
from json import JSONEncoder
import PIL as pillow
import sqlite3 as sql
import os
import sys

#Init flask server
app = Flask(__name__)

#Directory to store uploaded images
app.config['UPLOAD_IMGS'] = 'static/images/'
#Image filt types to allow
app.config['VALID_EXTS'] = set(['png', 'jpg', 'jpeg'])

#Similarity of image colors is scaled against diff. between black and white
white = (255,255,255)
black = (0,0,0)
max_distance = sqrt(sum((white - black)**2 for white, black in zip(white, black)))


#unicode2ascii() method was found from source:
#http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def unicode2ascii(input):
    if isinstance(input, dict):
        return dict((unicode2ascii(key), unicode2ascii(value)) for key, value in input.iteritems())
    elif isinstance(input, list):
        return [unicode2ascii(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('ascii')
    else:
        return input

def get_average_color(img):
    """
    Calculate the Avg color in an image, which is the
    sum of the RGB values for each pixel / # of pixels

    IN: PIL Image (Python Image Library)
    OUT: Tuple of average R,G,B value for image
    """
    r, g, b = 0, 0, 0
    pixels = 0
    width, height = img.size
    img_pxs = img.load()
    ext = img.format.lower()
    #for every pixel in images x, y coordines
    for x in xrange(0,width):
        for y in xrange(0,height):
            #Some images have transparancy layer (which is ignored)
            if len(img_pxs[x,y]) == 3:
                p_red, p_green, p_blue = img_pxs[x,y]
            elif len(img_pxs[x,y]) == 4:
                p_red, p_green, p_blue, transp = img_pxs[x,y]
            else:
                raise Exception('Img Pixels not read properly')
            #get totals for each color amd # of pixels
            r += p_red
            g += p_green
            b += p_blue
            pixels += 1
    #return tuple w/ avg color of image
    avg_color = ((r/pixels), (g/pixels), (b/pixels))
    return avg_color

def color_distance(img1_avg,img2_avg):
    '''
    Calculate the similarity between two images

    IN: Two Images and their average color value
    OUT: similarity of two images (int)
    '''
    #Calculate color distance (Euclidean Distiance) between colors by treating r,g,b as a 3D vector
    distance = sqrt(sum((img1_avg - img2_avg)**2 for img1_avg, img2_avg in zip(img1_avg, img2_avg)))
    #Similarity is relative to the max_distance (distance from black to white)
    similarity = 1 - distance/max_distance
    print "Similarity:", similarity
    #round to integer value to allow sorting
    return round(similarity*100,2)

def compare_images(db_entries, uploaded_img, upload_img_name, upload_img_avgcolor):
    '''
    Looks through database at each image stored to find best matches

    IN: List of Databse Entries, PIL Image, Image Name, Image AvgColor
    OUT: List representing the most similar images and their similarity rating
    '''
    closest_imgs = []

    for entry in db_entries:
        print ""
        #Assign image id, name, color from DB
        img_id, db_img_name, db_img_avgcolor = (entry[0], entry[1], entry[2])
        #convert to ascii string from unicode stored in DB
        db_img_name = unicode2ascii(db_img_name)
        db_img_avgcolor = unicode2ascii(db_img_avgcolor)
        #covert to tuple
        db_img_avgcolor = literal_eval(db_img_avgcolor)

        #Try access image found in database to lookup similarity
        try:
            #Open image stored on disk that was found in DB
            db_img = Image.open('static/images/'+db_img_name)
            #Don't compare the same image (diff images with same name overwrite)
            if upload_img_name != db_img_name:
                print upload_img_name , "|",upload_img_avgcolor ,"| vs. |"  ,db_img_name , "|",db_img_avgcolor
                similarity = color_distance(upload_img_avgcolor, db_img_avgcolor)
                #Add image to closest images list
                closest_imgs.append((db_img_name,similarity))
                #Sort images
                #There are better ways then to sort this every single time
                #but since size of list will never be greater than 4 elements, probably not worth changing it
                closest_imgs = sorted(closest_imgs, key=lambda x: float(x[1]), reverse=True)
                #Only want 3 most similar images
                closest_imgs = closest_imgs[:3]
                print "Closest Imgs Are Now:", closest_imgs
        except Exception as inst:
            print(type(inst))
            print inst
            print "Error while accessing image from disk, databse or calculating similarity"
            continue
    return closest_imgs


def find_similar_img(img, upload_img_name):
    '''
    Looks through database at each image stored to find best matches

    IN: PIL Image, Image Name
    OUT: Dictionary of uploaded image name and similar images' name and similarity rating
    '''
    #Load uploaded image into PIL and get avg color
    uploaded_img = Image.open(img)
    upload_img_avgcolor = get_average_color(uploaded_img)

    #Open up database to compare files
    con = sql.connect('image_data.db')
    with con:
        cur = con.cursor()

        #Add new image into db
        cmd = "INSERT INTO ImageColors(Name, AvgColor) VALUES (?, ?)"
        cur.execute(cmd, (upload_img_name, str(upload_img_avgcolor)))
        con.row_factory = sql.Row

        #Get all image data from db
        cur.execute("SELECT * FROM ImageColors")
        rows = cur.fetchall()
        closest_imgs = []
        #If more than 1 image in database, compare to imgs there
        if len(rows) > 1:
            closest_imgs = compare_images(rows, uploaded_img, upload_img_name, upload_img_avgcolor)

    #Store all relevant info into dict and return as JSON
    similar_images = {}
    similar_images["Uploaded"] = upload_img_name
    similar_images["Similars"] = closest_imgs
    return similar_images



@app.route("/")
def initialize():
    '''
    Initialize the page

    IN: None
    OUT: None (loads page)
    '''
    #On page load, connect to database
    con = sql.connect('image_data.db')
    #generate table
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS ImageColors(Id INTEGER PRIMARY KEY, Name TEXT, AvgColor TEXT);")
    #render page from html
    return render_template('index.html')

@app.route("/uploadimg", methods=['POST', 'GET'])
def upload_img():
    '''
    Handle uploading of images to server, calls methods that analysze images
    To find the most similar image that has been previously stored

    IN: Image uploaded by use
    OUT: JSON representing the most similar images
    '''
    #Get file and file name
    img = request.files['file']
    upload_img_name = secure_filename(img.filename)

    #Check image was uploaded
    if not img:
        raise Exception('No files were uploaded!')

    #Check image is one of allowed filetypes
    ext = upload_img_name.rsplit('.', 1)[1].lower()
    if ext not in app.config['VALID_EXTS']:
        raise Exception('Uploaded file was not a valid .jpg or .png image!')

    #Save image in directory (overwrites existing img with same name)
    img.save(os.path.join(app.config['UPLOAD_IMGS'], upload_img_name))

    #find the top 3 most similar images and thier similarity rating
    similar_images = find_similar_img(img, upload_img_name)

    return JSONEncoder().encode(similar_images)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=int("8000"), debug=True)
