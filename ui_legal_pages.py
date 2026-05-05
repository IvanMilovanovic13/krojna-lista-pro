# -*- coding: utf-8 -*-
"""
Legalne stranice: Privacy Policy i Terms of Service.
Rute: /privacy  /terms
"""
from __future__ import annotations

from nicegui import ui

# ---------------------------------------------------------------------------
# Sadržaj — edituj ovde kada budeš imao finalnog teksta od pravnika
# ---------------------------------------------------------------------------

_PRIVACY_SR = """
## Politika privatnosti

**Poslednje ažuriranje:** 5. maj 2026.

### Ko smo mi
CabinetCutPro (KrojnaListaPRO) je web aplikacija za projektovanje kuhinjskog nameštaja.
Operater servisa: Ivan Milovanovic, kontakt: ivan_milovanovic@live.com

### Koje podatke prikupljamo
- **Email adresa** — za kreiranje naloga i komunikaciju
- **Podaci projekata** — kuhinjski planovi koje korisnik kreira i čuva
- **Podaci o plaćanju** — obrađuje ih Lemon Squeezy; mi ne vidimo broj kartice
- **Tehnički podaci** — IP adresa, browser tip (Render server logovi, max 30 dana)

### Kako koristimo podatke
- Da vam pružimo pristup aplikaciji
- Da procesuiramo plaćanje (Lemon Squeezy)
- Da šaljemo transakcione emailove (verifikacija, reset lozinke)
- Da poboljšamo aplikaciju (anonimizovana statistika)

### Čuvanje podataka
Podaci su smešteni na serverima Render.com (SAD), zaštićeni SSL-om.
Projekti se čuvaju dok ne obrišete nalog.

### Vaša prava (GDPR)
Imate pravo da tražite: pristup podacima, ispravku, brisanje naloga i svih podataka.
Zahtev pošaljite na: ivan_milovanovic@live.com

### Kolačići (Cookies)
Koristimo samo session kolačić neophodan za funkcionisanje prijave. Nema tracking piksela ni reklamnih kolačića.

### Deljenje sa trećim stranama
- **Lemon Squeezy** — payment procesor (ima sopstvenu privacy policy)
- **Render.com** — hosting (ima sopstvenu privacy policy)
- **Resend.com** — slanje emailova
- Niko drugi. Podatke ne prodajemo.

### Izmene politike
Obavestićemo vas emailom o bitnim izmenama.

### Kontakt
ivan_milovanovic@live.com
"""

_TERMS_SR = """
## Uslovi korišćenja

**Poslednje ažuriranje:** 5. maj 2026.

### 1. Prihvatanje uslova
Korišćenjem CabinetCutPro aplikacije prihvatate ove uslove. Ako ih ne prihvatate, ne koristite servis.

### 2. Opis servisa
CabinetCutPro je SaaS alat za projektovanje kuhinjskog nameštaja — generisanje krojna liste, plana bušenja i 2D/3D prikaza.

### 3. Nalozi i pretplate
- Registracija zahteva validnu email adresu
- Trial period traje 14 dana bez kartice
- Plaćena pretplata se naplaćuje unapred (mesečno/godišnje)
- Otkazivanje je moguće u bilo kom trenutku; pristup traje do kraja plaćenog perioda

### 4. Prihvatljivo korišćenje
Zabranjeno je:
- Pokušavati da se zaobiđe sistem autorizacije
- Koristiti servis za ilegalnu delatnost
- Preprodavati pristup trećim licima

### 5. Intelektualna svojina
Kod i UI aplikacije su vlasništvo operatera. Vaši projektni podaci su vaši.

### 6. Dostupnost servisa
Cilj je 99% uptime. Ne garantujemo neprekidan rad. Nismo odgovorni za gubitak podataka zbog tehničkih kvarova — pravite sopstvene backup-e.

### 7. Ograničenje odgovornosti
Servis se pruža "takav kakav je". Maksimalna odgovornost operatera ograničena je na iznos koji ste platili u poslednjih 12 meseci.

### 8. Raskid
Zadržavamo pravo da ugasimo nalog koji krši ove uslove, uz povraćaj srazmernog iznosa za neiskorišćeni period.

### 9. Merodavno pravo
Primenjuje se pravo Republike Srbije.

### 10. Kontakt
ivan_milovanovic@live.com
"""

_PRIVACY_EN = """
## Privacy Policy

**Last updated:** May 5, 2026.

### Who We Are
CabinetCutPro (KrojnaListaPRO) is a web application for kitchen furniture design.
Operator: Ivan Milovanovic, contact: ivan_milovanovic@live.com

### What Data We Collect
- **Email address** — to create your account and communicate with you
- **Project data** — kitchen plans you create and save in the app
- **Payment data** — processed by Lemon Squeezy; we never see your card number
- **Technical data** — IP address, browser type (Render server logs, max 30 days)

### How We Use Your Data
- To provide you access to the application
- To process payments (Lemon Squeezy)
- To send transactional emails (verification, password reset)
- To improve the application (anonymized analytics)

### Data Storage
Data is stored on Render.com servers (USA), protected by SSL.
Projects are stored until you delete your account.

### Your Rights (GDPR)
You have the right to: access your data, correction, deletion of your account and all data.
Send requests to: ivan_milovanovic@live.com

### Cookies
We use only the session cookie required for login to work. No tracking pixels or advertising cookies.

### Third-Party Sharing
- **Lemon Squeezy** — payment processor (has its own privacy policy)
- **Render.com** — hosting (has its own privacy policy)
- **Resend.com** — email delivery
- No one else. We do not sell data.

### Changes to This Policy
We will notify you by email of significant changes.

### Contact
ivan_milovanovic@live.com
"""

_TERMS_EN = """
## Terms of Service

**Last updated:** May 5, 2026.

### 1. Acceptance of Terms
By using CabinetCutPro you agree to these terms. If you do not agree, do not use the service.

### 2. Service Description
CabinetCutPro is a SaaS tool for kitchen furniture design — generating cut lists, drilling plans and 2D/3D views.

### 3. Accounts and Subscriptions
- Registration requires a valid email address
- Trial period is 14 days, no credit card required
- Paid subscription is charged upfront (monthly/annually)
- You can cancel at any time; access continues until the end of the paid period

### 4. Acceptable Use
Prohibited:
- Attempting to bypass the authorization system
- Using the service for illegal activities
- Reselling access to third parties

### 5. Intellectual Property
Application code and UI belong to the operator. Your project data belongs to you.

### 6. Service Availability
We aim for 99% uptime. We do not guarantee uninterrupted service. We are not liable for data loss due to technical failures — maintain your own backups.

### 7. Limitation of Liability
The service is provided "as is". Maximum operator liability is limited to the amount you paid in the last 12 months.

### 8. Termination
We reserve the right to terminate accounts that violate these terms, with a prorated refund for the unused period.

### 9. Governing Law
Laws of the Republic of Serbia apply.

### 10. Contact
ivan_milovanovic@live.com
"""

# Mapa: jezik → sadržaj
_PRIVACY = {"sr": _PRIVACY_SR, "en": _PRIVACY_EN}
_TERMS   = {"sr": _TERMS_SR,   "en": _TERMS_EN}


def _legal_shell(title: str, content_md: str) -> None:
    """Renderuje pravnu stranicu sa čistim layoutom."""
    from ui_public_site import PUBLIC_PAGE_STYLE, _public_shell  # type: ignore

    _public_shell()

    with ui.column().classes("w-full min-h-screen bg-white items-center"):
        # Topbar — samo logo i link nazad
        with ui.row().classes(
            "w-full max-w-5xl px-6 py-4 items-center justify-between"
        ):
            ui.html(
                '<a href="/" style="font-size:20px;font-weight:800;'
                'color:#111827;text-decoration:none;">CabinetCutPro</a>'
            )
            ui.html(
                '<a href="/" style="font-size:13px;color:#6b7280;'
                'text-decoration:none;">← Nazad / Back</a>'
            )

        # Sadržaj
        with ui.column().classes("w-full max-w-3xl px-6 pb-16 gap-0"):
            ui.markdown(content_md).classes("prose max-w-none text-gray-800")

        # Footer
        with ui.row().classes("w-full justify-center py-6 border-t border-gray-100"):
            ui.html(
                '<span style="font-size:12px;color:#9ca3af;">'
                'CabinetCutPro &copy; 2026 &nbsp;|&nbsp; '
                '<a href="/privacy" style="color:#6b7280;">Privacy</a>'
                ' &nbsp;|&nbsp; '
                '<a href="/terms" style="color:#6b7280;">Terms</a>'
                '</span>'
            )


def _get_lang() -> str:
    """Dohvata jezik iz storage-a, fallback na 'en'."""
    try:
        from nicegui import app as _app
        lang = str(_app.storage.user.get("language", "en") or "en").lower().strip()
        return lang if lang in ("sr", "en") else "en"
    except Exception:
        return "en"


def render_privacy_page() -> None:
    lang = _get_lang()
    content = _PRIVACY.get(lang) or _PRIVACY["en"]
    _legal_shell("Privacy Policy", content)


def render_terms_page() -> None:
    lang = _get_lang()
    content = _TERMS.get(lang) or _TERMS["en"]
    _legal_shell("Terms of Service", content)
