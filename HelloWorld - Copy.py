import tornado.ioloop
import tornado.web
import pyodbc
import json
import string

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
        self.write("Hello, world")

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




class DigitRecognizer(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><h1>Welcome HandWritten Digit Recognizer!</h1><body><form action="/recognizer/digit" method="post">'
                    '<input type="file" name="pic" accept="image/*">'
                   '</form></body></html>')

    def post(self):
        self.write('Welcome to the ImageHandler!')
        file_body = self.request.files['pic'][0]['body']
        img = Image.open(StringIO.StringIO(file_body))
        img.save("img/", img.format)
        self.write('<html><h1>Welcome HandWritten Digit Recognizer!</h1><body>Uploaded file</body></html>')



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
            (r"/login", LoginHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
