import os
import pprint

from flask import Flask, request
from fortnox import Fortnox

CLIENT_ID = os.environ.get("FORTNOX_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FORTNOX_CLIENT_SECRET")

app = Flask(__name__)
fortnox = Fortnox(CLIENT_ID, CLIENT_SECRET)


@app.route("/auth")
def auth_redirect():
    error = request.args.get("error", default="")
    if error:
        error_description = request.args.get("error_description", default="")
        return f"<h4>Error: {error}</h4>\n<p>{error_description}</p>"
    authcode = request.args.get("code", default="")
    fortnox.auth_code = authcode
    fortnox.get_access_token()
    print(authcode)
    return authcode


@app.route("/test")
def account_totals():
    return str(fortnox.get("/vouchers"))


@app.route("/test2")
def test2():
    return str(
        fortnox.post("/vouchers?financialyear=1", fortnox.generate_vouchers()[0])
    )


@app.route("/test-many")
def test_many():
    return str(
        fortnox.post_many("/vouchers?financialyear=1", fortnox.generate_vouchers())
    )


@app.route("/vouchers")
def vouchers():
    pprint.pprint(fortnox.generate_vouchers())
    return "Check console for output :)"


@app.route("/finyears")
def finyears():
    return str(fortnox.get("/financialyears"))


app.run(
    debug=True,
    host="localhost",
    port=6060,
)
