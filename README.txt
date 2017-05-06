--- INSTRUCTIONS ---

The web app can be run from terminal using:
python app.py

Then open up Google Chrome and navigate to 127.0.0.1:8000

Once the page loads, you can begin uploading images. Use the "Choose File" button to select an image (must be JPG or PNG) and then press the upload button. Once an image has been uploaded, a "Similar Images" section will appear, showing the top three images to the one uploaded.


--- SIMILARITY ALGORITHM ---
The similarity algorithm works by finding the average color for the uploaded image and comparing it to the average color of previously uploaded images. The average color of an image is calculated by summing up the 0-255 Red, Green, Blue (RGB) values of every pixel, and then dividing that sum by the total number of pixels in the image. The difference between two images is calculated using the "Color Distance". The Color Distance is found by treating the RGB values for two images as a set of two 3-Dimensional Vectors and then finding the Euclidean Distance between the end points of each vector. This distance is then divided by the maximum possible distance, which is the Color Distance between black and white. That value is subtracted from one and multiplied by 100, giving a number that ranges from 0 (as different as possible) to 100 (identical average color). The similarity for each image is then stored along with the image name in an SQLite database for easy access by the program.
I am aware of many different methods that could be used for comparing images, such as Image Histogram comparison, Comparing N corresponding points in the two images, or a complex machine learning approach where the images are compared to an existing database of known objects, and each new image is tagged with objects determined to be present. However given the time constraints, I wanted to stick to an algorithm that I already knew how to implement. Thus, this algorithm was chosen for its simplicity and ease of implementation.


--- TECH STACK ---
The tech stack for the application is as follows:
Backend:
Python v2.7
    - Pillow (Python Image Library)
Flask v0.12.1
SQLite v3

FrontEnd:
HTML5
CSS3
Javascript
JQuery

Frameworks:
Twitter Bootstrap


--- COMMENTS/WRITE-UP ---

This was a fun and challenging project to put together, and I enjoyed getting to put together multiple different packages and technologies I had not used together before.

Program Summary:
Every time a file is uploaded, it calculates the average color value for that image. Then it stores the image filename and average color value into an SQLite database. If there exists more than 1 image already in the database (one image would be the one just uploaded) then the program does a comparison of the uploaded image and all the images stored in the databse. It then returns the top three most similar images found in the DB

Features to Add/Change:
- Allow user to upload images with the same filename without overwriting the previous one
- UI Improvements I did not have time to include
    - Stylize Choose File and upload buttons
    - utilize Font Awesome icons
    - Better handle what user seems when there is only 1 or 2 similar images in database
- Store all jQuery, bootstrap, etc files locally instead of referencing link to web address (at present has an unnecessary dependency on other websites and a web connection)
- Improve similarity algorithm
    - See algorithm discription for other methods that could be used

Bugs/Known Issues:
- If two images with the same filename are uploaded, it keeps multiple copies in the DB in spite of only keeping one copy stored on the server, so If 5 different images with the same filename were uploaded, it would result in one file (with the most recent image stored), but would still be shown in the DB 5 times (allowing that same image to be shown multiple times in the results)
- Does not work on Firefox: 405 Method Not Allowed upon upload - Did not had time to debug this issue : (
- Has not been tested on Internet Explorer, Edge, or Safari (Browsers are not available for Ubuntu)
