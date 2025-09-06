from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from descope import DescopeClient, AuthException
from agents.team import Team

app = Flask(__name__, template_folder='templates')
app.secret_key = "super-secret-key"  # change in production

# --- Config ---
PROJECT_ID = "P32EWDJvVgaIyVQcl851PmS7N7L7"
descope_client = DescopeClient(project_id=PROJECT_ID)

# --- In-memory Team ---
team_agent = Team()

init_done = False

@app.before_request
def before_request_func():
    global init_done
    if not init_done:
        team_agent.initialize_queue()
        init_done = True


@app.route("/")
def home():
    if "jwt" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("chat"))


@app.route("/login")
def login():
    session.pop("messages", None)  # Clear chat history on login
    session.pop("google_token", None)  # Clear Google token on login
    return render_template("login.html", project_id=PROJECT_ID)



@app.route("/callback", methods=["POST", "GET"])
def callback():
    # Accept session token from POST JSON or GET query param
    session_jwt = None
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            session_jwt = data.get("sessionJwt")
    elif request.method == "GET":
        session_jwt = request.args.get("sessionToken")

    print("Received session JWT:", session_jwt)
    if not session_jwt:
        return jsonify({"success": False, "error": "No session JWT"}), 400

    try:
        user = descope_client.validate_session(session_jwt)
        session["jwt"] = session_jwt
        # session["user_name"] = user.get("name", user.get("loginId", "Unknown User"))
        # Redirect to chat after login
        return redirect(url_for("chat"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

# @app.route("/callback", methods=["GET"])
# def callback_get():
#     # Show a clear error if this endpoint is hit by mistake
#     return "Invalid callback method. Please log in via the login page.", 400

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly"
]

@app.route("/start-google-oauth")
def start_google_oauth():
    client_id = "UDMyRVdESnZWZ2FJeVZRY2w4NTFQbVM3TjdMNzpUUEEzMkV4dUNXQWlrRHh2TVJxME14eGFuYkUyYWo="  # Your inbound app's client_id
    redirect_uri = url_for('google_oauth_callback', _external=True)
    scopes = ' '.join(GOOGLE_SCOPES)

    oauth_url = (
        f"https://api.descope.com/oauth2/v1/apps/authorize"
        f"?client_id={client_id}"
        f"&projectId={PROJECT_ID}"
        f"&provider=google"
        f"&scopes={scopes}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    return redirect(oauth_url)

@app.route("/google-oauth-callback")
def google_oauth_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return f"Authorization failed: {error}", 400
    if not code:
        return "No code received", 400

    # Placeholder for exchanging the code for tokens
    # Example: tokens = descope_client.inbound_app.exchange_code(code)
    # For now, store the authorization code in the session
    session["google_token"] = code
    return redirect(url_for("chat"))

@app.route("/chat")
def chat():
    if "jwt" not in session:
        return redirect(url_for("login"))
    if "google_token" not in session:
        return redirect(url_for("start_google_oauth"))
    # Initialize chat history if not present
    if "messages" not in session:
        session["messages"] = []
    return render_template("chat.html", user_name=session.get("user_name", "Unknown User"))

@app.route("/history")
def history():
    # Return chat history for frontend rendering
    return jsonify(session.get("messages", []))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clear_history")
def clear_history():
    session.pop("messages", None)
    return jsonify({"success": True})


# --- Chat Endpoint ---
@app.route("/send", methods=["POST"])
async def send():
    if "jwt" not in session:
        return {"error": "Unauthorized"}, 401

    user_msg = request.json.get("message", "")
    if "messages" not in session:
        session["messages"] = []

    # Add user message to history
    session["messages"].append({"role": "user", "content": user_msg})
    session.modified = True

    # Add loading placeholder for assistant
    session["messages"].append({"role": "assistant", "content": "__loading__"})
    session.modified = True

    # Run a single, self-terminating stream for this request
    reply = ""
    async for msg in team_agent.run_once(user_msg):
        # Some events can be TaskResult or other types; extract text defensively
        try:
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                reply += content
        except Exception:
            pass

    # Replace last assistant message (loader) with actual reply
    if session["messages"] and session["messages"][-1]["role"] == "assistant" and session["messages"][-1]["content"] == "__loading__":
        session["messages"][-1]["content"] = reply    
        return jsonify({"reply": reply, "messages": session["messages"]})
    else:
        session["messages"].append({"role": "assistant", "content": reply})
    session.modified = True


if __name__ == "__main__":
    # Disable the reloader to avoid duplicate event loops and shutdown cancellations
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)