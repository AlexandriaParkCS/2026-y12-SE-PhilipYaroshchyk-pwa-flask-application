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
from datetime import datetime

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




sql_db = SqlDb("../runtime/db/sql.db", log=log)
user_service = UserService(sql_db, log)


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
    if not 'user_id' in session:
        return render_template("/public.html")
    try:
        exp = user_service.get_user_transactions(session['user_id'], 10, is_expense=True)
        inc = user_service.get_user_transactions(session['user_id'], 10, is_expense=False)
        goals = user_service.get_user_goals(session['user_id'])

        return render_template("/index.html", expenses=exp, income=inc, goals=goals)
    except Exception as e:
        log.info(f"Failed to fetch data for user {session['user_id']} {e}")
        return render_template("/error.html", error_message="Failed to fetch data for user")
        

@app.route("/expenses.html", methods=["GET"])
def expenses():

    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
         return render_template("/public.html")

    try:
        exp = user_service.get_all_user_transactions(session['user_id'])
        return render_template("/expenses.html", expenses=exp)
    except Exception as e:
        return render_template("/error.html", error_message="Failed to fetch expenses for user")
       


@app.route("/privacy_policy.html", methods=["GET"])
def privacy_policy():
    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")
    
    return render_template("/privacy.html")


@app.route('/summary/<goal_id>', methods=["GET"])
def render_summary(goal_id):

    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")

    try:
        sum = user_service.get_transaction_summary_for_a_goal(session['user_id'], goal_id)

        nonce = uuid.uuid4()


        if sum:

            labels = [tr.transaction_date for tr in sum.transactions]
            data = [tr.amount for tr in sum.transactions]

            aggregation_labels = [agg.name for agg in sum.aggregations]
            aggregation_data = [agg.amount for agg in sum.aggregations]

            tip = sum.tip

            return render_template("/summary.html", goal_summary=sum, nonce=nonce, labels=labels, data=data, 
                                aggregation_labels=aggregation_labels, aggregation_data=aggregation_data,
                                tip=tip)
        else:
        
            return render_template("/error.html", error_message="Summary not found")
    except Exception as e:
        log.info(f"Failed to fetch summary for goal {goal_id} {e}")
        return render_template("/error.html", error_message="Failed to fetch summary for goal")    

@app.route("/expense_form.html", methods=["GET"])
def expense_form():

    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")

    return render_template("/expense_form.html")


@app.route("/goal_form.html", methods=["GET"])
def goal_form():

    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")


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

    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")
    

    try:
        amount_dollars = request.form["amount"]
        # optional field, can be empty
        description = request.form["description"]
        date = request.form["date"]
        user_id = session["user_id"]
        transaction_type = request.form["transaction_type"]


        if not is_valid_float(amount_dollars):
            return render_template("/expense_form.html", error_message="Invalid amount format")
        
        if not is_valid_date(date):
            return render_template("/expense_form.html", error_message="Invalid date format. Use YYYY-MM-DD")
        
        if not is_valid_length_optional(description, 2, 50):
            return render_template("/expense_form.html", error_message="Description is opional. If provided, must be between 2 and 50 characters if provided")
        
        expense_type = "Income" if transaction_type == 'Income' else 'Expense'
        expense = user_service.add_transaction(user_id, transaction_type, amount_dollars, date, description, expense_type)

        if expense:
            log.info("successfully added expense")
        else:
            log.info("failed to add expense")    

        return redirect("/")
    
    except Exception as e:
        log.info(f"Failed to add_expense {e}")
        return render_template("/expense_form.html", error_message="Failed to add expense. Please try again.")

@app.route('/add_goal', methods=["POST"])    
def add_goal():


    # if user is not logged in, redirect to public page 
    if not 'user_id' in session:
        return render_template("/public.html")
    
    try: 

        user_id = session["user_id"]
        amount_dollars = request.form["amount"]
        goal_name = request.form["goal_name"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]


        if not is_valid_float(amount_dollars):
            return render_template("/goal_form.html", error_message="Invalid amount format")

        if not is_valid_date(start_date) or not is_valid_date(end_date):
            return render_template("/goal_form.html", error_message="Invalid date format. Use YYYY-MM-DD")
        
        if not is_valid_length_required(goal_name, 2, 50):
            return render_template("/goal_form.html", error_message="Goal name must be between 2 and 50 characters and is required")

        goal = user_service.add_goal(user_id, amount_dollars, goal_name, start_date, end_date)

        if goal:
            log.info("successfully added goal")
        else:
            log.info("failed to add goal")    

        return redirect("/")
    
    except Exception as e:
        log.info(f"Failed to add goal {e}")
        return render_template("/goal_form.html", error_message="Failed to add goal. Please try again.")



@app.route("/logout")
def logout():
    log.info(f"logging out user {session['username']}")
    session.pop('username', None)       
    session.pop('user_id', None)
    return redirect("/") 



def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    

def is_valid_float(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False    
    
def is_valid_length(value, min, max):
    return value and value.strip() != "" and len(value) >= min and len(value) <= max 

def is_valid_length_optional(value, min, max):
    if not value or (value and value.strip() == ""):
        return True
    if len(value) >= min and len(value) <= max:
        return True 
    return False
    
def is_valid_length_required(value, min, max):
    return value and not value.strip() == "" and len(value) >= min and len(value) <= max

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data)
    return "done"

if __name__ == "__main__":
    # app.logger.debug("Started")
    app.run(debug=True, host="0.0.0.0", port=5000)