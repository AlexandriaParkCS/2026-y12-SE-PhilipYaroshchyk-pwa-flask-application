import logging

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
from user_service import UserService

from sqldb import SqlDb
# OR
# from ormdb import OrmDb

log = logging.getLogger(__name__)
logging.basicConfig(
    filename="../runtime/log/app.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=" %(asctime)s %(message)s",
)




sql_db = SqlDb("../runtime/db/sql.db")
user_service = UserService(sql_db)


# OR
# orm_db = OrmDb("../runtime/db/orm.db")

app = Flask(__name__)
app.secret_key = b"G6z115u8WnfQ0UIJ"  # To get a unique basic 16 key: https://acte.ltd/utils/randomkeygen

csrf = CSRFProtect(app)

# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)

@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    if 'username' in session:
        return render_template("/index.html")
    else:
        return render_template("/public.html")

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")

     
@app.route("/signup.html", methods=["POST"])
def signup():
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]

    log.info(f"creating new user {username}")

    user = user_service.signup(username, email, password)
    
    if user:        
        session['username'] = username
        session['user_id'] = user['id']
        return render_template("/index.html")
    else:
        log.info(f"Failed to create user {username}")
        return render_template("/public.html")
        
    

@app.route('/login', methods=["POST"])    
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = user_service.login(username, password)

    if user != None:
        session['username'] = username
        session['user_id'] = user['id']

        expenses = user_service.get_all_user_expenses(user['id'])


    else:
        log.info(f"Failed to login user {username}")
    return redirect("/")

@app.route('/add_expense', methods=["POST"])    
def add_expense():
    amount = request.form["amount"]
    expense_type = request.form["expense_type"]
    description = request.form["description"]
    date = request.form["date"]
    user_id = session["user_id"]

    print(f"submitted amount={amount} type={expense_type} {description} {date}")
    expense = user_service.add_expense(user_id, expense_type, amount, date, description)

    if expense:
        print("successfully added expense")
    else:
        print("failed to add expense")    


    return redirect("/")



@app.route("/logout")
def logout():
    log.info(f"logging out user {session['username']}")
    session.pop('username', None)       
    session.pop('user_id', None)
    return redirect("/") 


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data)
    return "done"

if __name__ == "__main__":
    # app.logger.debug("Started")
    app.run(debug=True, host="0.0.0.0", port=5000)
