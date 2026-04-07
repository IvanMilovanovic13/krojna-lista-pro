# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import get_language_options, normalize_language_code, tr


def run_i18n_multilang_contract() -> tuple[bool, str]:
    options = get_language_options()
    for code in ("sr", "en", "es", "pt-BR", "ru", "zh-CN", "hi"):
        if code not in options:
            return False, f"FAIL_missing_language_option:{code}"

    if normalize_language_code("pt-BR") != "pt-br":
        return False, "FAIL_ptbr_normalization"
    if normalize_language_code("zh-CN") != "zh-cn":
        return False, "FAIL_zhcn_normalization"
    if normalize_language_code("en-US") != "en":
        return False, "FAIL_enus_normalization"

    if tr("public.login_title", "es") != "Iniciar sesión":
        return False, "FAIL_spanish_login_title"
    if tr("public.login_title", "pt-BR") != "Entrar":
        return False, "FAIL_portuguese_login_title"
    if tr("public.login_title", "ru") != "Вход":
        return False, "FAIL_russian_login_title"
    if tr("public.login_title", "zh-CN") != "登录":
        return False, "FAIL_chinese_login_title"
    if tr("public.login_title", "hi") != "लॉग इन":
        return False, "FAIL_hindi_login_title"
    if tr("nova.auth_logout_btn", "ru") != "Выйти":
        return False, "FAIL_russian_logout_label"
    if tr("nova.user_projects_title", "zh-CN") != "我的项目":
        return False, "FAIL_chinese_projects_title"
    if tr("public.checkout_success_title", "pt-BR") != "O fluxo de pagamento foi iniciado com sucesso.":
        return False, "FAIL_portuguese_checkout_title"

    fallback = tr("settings.title", "es")
    if fallback not in {"Settings", "Podesavanja"}:
        return False, "FAIL_fallback_chain"

    return True, "OK"


if __name__ == "__main__":
    ok, message = run_i18n_multilang_contract()
    print(message)
    raise SystemExit(0 if ok else 1)
