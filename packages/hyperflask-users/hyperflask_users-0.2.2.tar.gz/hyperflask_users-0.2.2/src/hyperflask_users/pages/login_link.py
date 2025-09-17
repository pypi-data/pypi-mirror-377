from hyperflask import page, request, redirect, url_for, current_app, session, abort
from hyperflask.utils.request import is_safe_redirect_url
from .. import UserModel
from ..flow import login
from ..captcha import validate_captcha_when_configured


if "login_user" not in session:
    abort(404)

form = page.form()
user = UserModel.get(session['login_user'])


def get():
    if "token" in request.args:
        user_ = UserModel.from_token_or_404(request.args["token"], max_age=current_app.extensions['users'].token_max_age)
        if user_.get_id() != user.get_id():
            abort(403)
        login(user)
        clear_session()
        return _redirect()


@validate_captcha_when_configured
def post():
    if form.validate():
        if form.code.data == session.pop('login_code'):
            login(user, remember=request.form.get("remember") == "1", validate_email=True)
            clear_session()
            return _redirect()
        clear_session()
        return redirect(url_for(".login"))


def _redirect():
    next = request.args.get("next")
    return redirect(next if next and is_safe_redirect_url(next) else current_app.extensions['users'].login_redirect_url)


def clear_session():
    session.pop('login_user', None)
    session.pop('login_code', None)
