from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys


CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_pick_survey_form():    

    return render_template("pick-survey.html", surveys=surveys)


@app.route("/", methods=["POST"])
def pick_survey():    

    survey_id = request.form['survey_code']
    
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_start.html",
                           survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():    

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():    

    choice = request.form['answer']
    text = request.form.get("text", "")
    
    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})
    
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):        
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):   

    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):       
        return redirect("/")

    if (len(responses) == len(survey.questions)):       
        return redirect("/complete")

    if (len(responses) != qid):        
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/complete")
def say_thanks():    

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("completion.html",
                           survey=survey,
                           responses=responses)
    
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
