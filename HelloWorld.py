import tornado.ioloop
import tornado.web
import pyodbc
import json
import string
import os
import math
import random
import sys
import time
import tensorflow as tf
from PIL import Image, ImageFilter


def predictint(imvalue):
    """
    This function returns the predicted integer.
    The imput is the pixel values from the imageprepare() function.
    """

    # Define the model (same as when creating the model file)
    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))

    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])

    x_image = tf.reshape(x, [-1, 28, 28, 1])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])

    y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

    init_op = tf.global_variables_initializer()
    saver = tf.train.Saver()

    """
    Load the model2.ckpt file
    file is stored in the same directory as this python script is started
    Use the model to predict the integer. Integer is returend as list.

    Based on the documentatoin at
    https://www.tensorflow.org/versions/master/how_tos/variables/index.html
    """
    with tf.Session() as sess:
        sess.run(init_op)
        saver.restore(sess, "C:/Users/Anil.Gangadharaiah/Desktop/GIT/anilg007/tensorflow-mnist-predict/model2.ckpt")
        print ("Model restored.")

        prediction = tf.argmax(y_conv, 1)
        return prediction.eval(feed_dict={x: [imvalue], keep_prob: 1.0}, session=sess)


def imageprepare(argv):
    """
    This function returns the pixel values.
    The imput is a png file location.
    """
    im = Image.open(argv).convert('L')
    width = float(im.size[0])
    height = float(im.size[1])
    newImage = Image.new('L', (28, 28), (255))  # creates white canvas of 28x28 pixels

    if width > height:  # check which dimension is bigger
        # Width is bigger. Width becomes 20 pixels.
        nheight = int(round((20.0 / width * height), 0))  # resize height according to ratio width
        if (nheigth == 0):  # rare case but minimum is 1 pixel
            nheigth = 1
            # resize and sharpen
        img = im.resize((20, nheight), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wtop = int(round(((28 - nheight) / 2), 0))  # caculate horizontal pozition
        newImage.paste(img, (4, wtop))  # paste resized image on white canvas
    else:
        # Height is bigger. Heigth becomes 20 pixels.
        nwidth = int(round((20.0 / height * width), 0))  # resize width according to ratio height
        if (nwidth == 0):  # rare case but minimum is 1 pixel
            nwidth = 1
            # resize and sharpen
        img = im.resize((nwidth, 20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wleft = int(round(((28 - nwidth) / 2), 0))  # caculate vertical pozition
        newImage.paste(img, (wleft, 4))  # paste resized image on white canvas

    # newImage.save("sample.png")

    tv = list(newImage.getdata())  # get pixel values

    # normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [(255 - x) * 1.0 / 255.0 for x in tv]
    return tva
    # print(tva)


def main(argv):
    """
    Main function.
    """
    imvalue = imageprepare(argv)
    predint = predictint(imvalue)
    print (predint[0])  # first value in list
    return predint[0]


def getConn():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ANILG01;DATABASE=MyApp.Database;UID=sa;PWD=pass@word1')
    return conn

def verifyDatabase():
    conn = getConn()
    c = conn.cursor()
    try:
        print(c.execute('SELECT * FROM Images'))
        print('Table already exists')
    except:
        print('Creating table \'cars\'')
    conn.commit()
    conn.close()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("html5-canvas-drawing-app.html")

    def post(self):
        self.write("hi")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('GET - Welcome to the ImageHandler!')
        conn = getConn()
        cursor = conn.cursor()
        result = cursor.execute("select * from dbo.Images")
        rows = cursor.fetchall()
        data=[]
        for row in rows:
            data.append([x for x in row]) # or simply data.append(list(row))
        self.write(json.dumps(data))

    def post(self):
        self.write('POST - Welcome to the ImageHandler!')
        background = self.get_argument('background', '')
        imgSrc = self.get_argument('imgSrc', '')
        name = self.get_argument('name', '')
        conn = getConn()
        cursor = conn.cursor()
        cursor.execute("insert into Images(background, imgSrc,name) values ('"+background+"', '"+imgSrc+"','"+name+"')")
        conn.commit()
        self.write(" "+background)
        self.write(" "+imgSrc)
        self.write(" "+name)



class DrawImage(tornado.web.RequestHandler):
    def get(self):
        self.render("html5-canvas-drawing-app.html")

    def post(self):
        self.write("hi")

class DigitRecognizer(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><h1>Welcome HandWritten Digit Recognizer!</h1><body><form enctype="multipart/form-data" action="/recognizer/digit" method="post">'
                    'File: <input type="file" name="file1" />'
                    '<input type="submit" value="upload" />'
                    '</form></body></html>')

    def post(self):
        file1 = self.request.get['theimage'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename = fname + extension
        output_file = open("img/" + final_filename, 'wb')
        output_file.write(file1['body'])
        output_file.close()
        #time.sleep(5)  # delays for 5 seconds
        digit = main("img/"+final_filename)
        self.write("Digit uploaded is: ")
        self.write(str(digit))
        self.write('"<a href="http://localhost:8883/recognizer/digit">another digit</a>')





class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   'Pass: <input type="password" name="pass">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        name = self.get_argument("name")
        pas = self.get_argument("pass")
        conn = getConn()
        cursor = conn.cursor()
        try:
            Pass = cursor.execute("select Password from dbo.credential where Username='"+name+"'").fetchone()[0]
            if str(Pass).strip() == str(pas).strip():
                self.redirect("/")

        except:
            self.redirect("/login")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/api/v1/images/?", ImageHandler),
            (r"/api/v1/images/[0-9][0-9][0-9][0-9]/?", ImageHandler),
            (r"/recognizer/digit", DigitRecognizer),
            (r"/draw/image",DrawImage),
            (r"/login", LoginHandler)
        ]
        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": True
        }
        tornado.web.Application.__init__(self, handlers,**settings)


if __name__ == "__main__":
    app = Application()
    app.listen(8883)
    tornado.ioloop.IOLoop.current().start()
