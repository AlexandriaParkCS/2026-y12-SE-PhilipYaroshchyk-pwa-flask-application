import logging
import uuid

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
    if 'user_id' in session:

        exp = user_service.get_user_transactions(session['user_id'], 10, is_expense=True)
        inc = user_service.get_user_transactions(session['user_id'], 10, is_expense=False)
        goals = user_service.get_user_goals(session['user_id'])

        return render_template("/index.html", expenses=exp, income=inc, goals=goals)
    else:
        return render_template("/public.html")

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")


@app.route('/summary/<goal_id>', methods=["GET"])
def render_summary(goal_id):
    sum = user_service.get_transaction_summary_for_a_goal(session['user_id'], goal_id)

    nonce = uuid.uuid4()


    if sum:

        labels = [tr.get_transaction_date() for tr in sum.get_transactions()]
        data = [tr.get_amount() for tr in sum.get_transactions()]

        aggregation_labels = [agg.get_name() for agg in sum.get_aggregations()]
        aggregation_data = [agg.get_amount() for agg in sum.get_aggregations()]

        tip = sum.get_tip()

        return render_template("/summary.html", goal_summary=sum, nonce=nonce, labels=labels, data=data, 
                               aggregation_labels=aggregation_labels, aggregation_data=aggregation_data,
                               tip=tip)
    else:
        log.info(f"Failed to fetch summary for goal {goal_id}")
        return redirect("/")

@app.route("/expense_form.html", methods=["GET"])
def expense_form():
    return render_template("/expense_form.html")


@app.route("/goal_form.html", methods=["GET"])
def goal_form():
    return render_template("/goal_form.html")

@app.route("/signup.html", methods=["POST"])
def signup():
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]

    log.info(f"creating new user {username}")

    try:
        user = user_service.signup(username, email, password)
        session['username'] = username
        session['user_id'] = user['id']
        return redirect("/")

    except Exception as e:
        log.info(f"Failed to create user {username}")
        return render_template("/public.html", error_message=str(e))
    

@app.route('/login', methods=["POST"])    
def login():
    username = request.form["username"]
    password = request.form["password"]


    try:
        user = user_service.login(username, password)

        if user != None:
            session['username'] = username
            session['user_id'] = user['id']
            log.info(f"successfully logged in user {username}")

            return redirect("/")
        else:
            log.info(f"Failed to login user {username}")
            return render_template("/public.html", error_message="Failed to login")
    except Exception as e:
        log.info(f"Failed to login user {username}")
        return render_template("/public.html", error_message=str(e))    


@app.route('/add_expense', methods=["POST"])    
def add_expense():
    amount = request.form["amount"]
    description = request.form["description"]
    date = request.form["date"]
    user_id = session["user_id"]
    transaction_type = request.form["transaction_type"]

    expense_type = "Income" if transaction_type == 'Income' else 'Expense'

    amount = float(request.form["amount"])

    if expense_type == "Expense":
        amount = -amount   

    print(f"submitted transaction_type={transaction_type} amount={amount} expdnse_type={expense_type} {description} {date}")
    expense = user_service.add_transaction(user_id, transaction_type, amount, date, description)

    if expense:
        print("successfully added expense")
    else:
        print("failed to add expense")    


    return redirect("/")

@app.route('/add_goal', methods=["POST"])    
def add_goal():

    user_id = session["user_id"]

    amount = request.form["amount"]
    goal_name = request.form["goal_name"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]


    print(f"add goal called amount={amount} name={goal_name} {start_date} {end_date}")
    goal = user_service.add_goal(user_id, amount, goal_name, start_date, end_date)

    if goal:
        print("successfully added goal")
    else:
        print("failed to add goal")    

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
