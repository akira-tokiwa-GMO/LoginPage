from __future__ import annotations

from flask import Blueprint, redirect, render_template, session, url_for

from login_app.domain.repositories import UserRepository


def create_dashboard_blueprint(user_repo: UserRepository) -> Blueprint:
    """成功ページ（ダッシュボード）を表示する Blueprint を生成します。"""
    bp = Blueprint("dashboard", __name__)

    @bp.route("/dashboard")
    def index() -> str:
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("auth.login"))
        user = user_repo.get_by_id(int(user_id))
        if user is None:
            return redirect(url_for("auth.login"))
        return render_template("dashboard.html", user=user)

    return bp
