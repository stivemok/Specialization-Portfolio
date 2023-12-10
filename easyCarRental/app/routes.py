from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Stive'}
    return '''
<html>
    <header>
        <title>Home page - Easy Rentals</title>
    </header>
    <body>
        <h1>Hello, ''' + user['username'] + '''!</h1>
    </body>
</html>'''