from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for

from login_app.usecases import AuthUsecase


def create_auth_blueprint(auth_uc: AuthUsecase) -> Blueprint:
    """認証関連のエンドポイントを提供する Blueprint を生成します。"""
    bp = Blueprint("auth", __name__)

    @bp.route("/register", methods=["GET", "POST"])
    def register() -> str:
        if request.method == "POST":
            username = request.form.get("username", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            try:
                auth_uc.register(username, email, password)
                return redirect(url_for("auth.login"))
            except Exception as exc:  # noqa: BLE001
                return render_template("register.html", error=str(exc))
        return render_template("register.html")

    @bp.route("/login", methods=["GET", "POST"])
    def login() -> str:
        if request.method == "POST":
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            try:
                user = auth_uc.login(email, password)
                session["user_id"] = user.id
                return redirect(url_for("dashboard.index"))
            except Exception as exc:  # noqa: BLE001
                return render_template("login.html", error=str(exc))
        return render_template("login.html")

    @bp.post("/logout")
    def logout() -> str:
        auth_uc.logout(session)
        return redirect(url_for("auth.login"))

    return bp
