from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from urllib.parse import urlencode
import os
import secrets
from descope import DescopeClient, AuthException
import requests
from agents.team import Team

app = Flask(__name__, template_folder='templates')
app.secret_key = "super-secret-key"  # change in production

# --- Config ---
PROJECT_ID = "P32EWDJvVgaIyVQcl851PmS7N7L7"
descope_client = DescopeClient(project_id=PROJECT_ID)

# Inbound App OAuth credentials
INBOUND_CLIENT_ID = "UDMyRVdESnZWZ2FJeVZRY2w4NTFQbVM3TjdMNzpUUEEzMk4xTGtaMDhhTXZ4M0dKc0ZSdnRLRExvQjc="
INBOUND_CLIENT_SECRET = "qWLwZewM0GsZgvqdPMTNo770qUMhCuOQyxxgVweAXAG"

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
    # If JWT already set (after callback), skip widget and go to chat
    if "jwt" in session:
        return redirect(url_for("chat"))
    # Ensure inbound app OAuth is completed before showing consent flow
    if "code" not in session:
        return redirect(url_for("start_google_oauth"))
    return render_template("login.html", project_id=PROJECT_ID)



@app.route("/callback", methods=["POST", "GET"])
def callback():
    # Accept session token from POST JSON or GET query param
    print("CALLING")
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
        print("User info from Descope:", user)

        # Extract user details safely from Descope validation response
        user_info = user.get("user", {}) if isinstance(user, dict) else {}
        user_email = user_info.get("email") or user_info.get("loginId")
        user_name = user_info.get("name") or user_email

        # Persist to session for later use
        if user_email:
            session["user_email"] = user_email
        session["user_name"] = user_name

        # For POST (AJAX from the login page), return JSON so frontend can redirect
        if request.method == "POST":
            return jsonify({"success": True})

        # For GET callback (if ever used), redirect to chat
        return redirect(url_for("chat"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

# @app.route("/callback", methods=["GET"])
# def callback_get():
#     # Show a clear error if this endpoint is hit by mistake
#     return "Invalid callback method. Please log in via the login page.", 400

GOOGLE_SCOPES = [
    # Inbound app scopes configured in Descope
    "email",
    "calendar.write",
    "message.send"
]

@app.route("/start-google-oauth")
def start_google_oauth():
    redirect_uri = url_for('google_oauth_callback', _external=True)
    # Optional: allow caller to override requested scopes via query (?scopes=a+b+c)
    requested_scopes = request.args.get('scopes')  # space-delimited if provided

    # CSRF state
    state = secrets.token_urlsafe(24)
    session['oauth_state'] = state

    # Minimal required params per Descope docs
    base_params = {
        'client_id': INBOUND_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'state': state,
        # Allow partial/previously granted scopes; user may choose not to grant some
        'include_granted_scopes': 'true'
    }
    # Only include scope if explicitly provided to avoid mismatch when user selects a subset later
    if requested_scopes:
        base_params['scope'] = requested_scopes
    query = urlencode(base_params)

    oauth_url = f"https://api.descope.com/oauth2/v1/apps/authorize?{query}"
    return redirect(oauth_url)

@app.route("/google-oauth-callback")
def google_oauth_callback():
    print("Google OAuth callback received")
    code = request.args.get("code")
    print("Code received:", code)
    error = request.args.get("error")
    print("Error received:", error)
    returned_state = request.args.get('state')
    # Validate state if present
    if returned_state and session.get('oauth_state') and returned_state != session['oauth_state']:
        return "Invalid OAuth state", 400
    # If the user denied or no code returned, continue gracefully to login (no scopes)
    if error:
        description = request.args.get("error_description", "")
        print("Authorization skipped/failed:", error, description)
        session["code"] = None
        session.pop("inbound_tokens", None)
        return redirect(url_for("login"))
    if not code:
        print("No authorization code received; proceeding without inbound tokens")
        session["code"] = None
        session.pop("inbound_tokens", None)
        return redirect(url_for("login"))
    try:
        # Exchange authorization code for inbound app tokens via Descope REST API
        token_url = "https://api.descope.com/oauth2/v1/apps/token"
        redirect_uri = url_for('google_oauth_callback', _external=True)
        form = {
            "grant_type": "authorization_code",
            "client_id": INBOUND_CLIENT_ID,
            "client_secret": INBOUND_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        resp = requests.post(token_url, data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)
        try:
            tokens = resp.json()
        except Exception:
            tokens = {"error": "non_json_response", "text": resp.text}
        if resp.ok:
            session["inbound_tokens"] = tokens  # may include access_token, refresh_token, expires_in, scope
        else:
            print("Inbound token exchange failed; continuing without tokens")
            session.pop("inbound_tokens", None)
            session["inbound_tokens_error"] = tokens
        # Persist code for the next step (render the inbound consent widget)
        session["google_token"] = code
        session["code"] = code
        # After OAuth, show the consent flow (login page renders descope-wc with inbound-apps-user-consent)
        return redirect(url_for("chat"))
    except Exception as e:
        return f"Token exchange failed: {str(e)}", 400
        

@app.route("/chat")
def chat():
    # if "jwt" not in session:
    #     return redirect(url_for("login"))
    # if "google_token" not in session:
    #     return redirect(url_for("start_google_oauth"))
    # # Initialize chat history if not present
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
    # if "jwt" not in session:
    #     return {"error": "Unauthorized"}, 401
    #extract scopes from session
    inbound_app_scopes = session.get("inbound_tokens", [])
    scopes = inbound_app_scopes.get("scope", [])
    scopes = scopes.split(" ")
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
    async for msg in team_agent.run_once(user_msg,scopes):
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