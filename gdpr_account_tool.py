# -*- coding: utf-8 -*-
"""
GDPR alat: izvoz i brisanje podataka korisnika po zahtevu (Clan 15 - pravo na
pristup/prenosivost, Clan 17 - pravo na brisanje).

Radi i sa lokalnim SQLite i sa Render Postgres bazom (isti obrazac kao
list_users_cli.py) — DATABASE_URL odredjuje na koju bazu se povezuje.

Primeri:
  # Lokalna baza (podrazumevano)
  venv\\Scripts\\python.exe gdpr_account_tool.py export --email korisnik@example.com
  venv\\Scripts\\python.exe gdpr_account_tool.py delete --email korisnik@example.com
  venv\\Scripts\\python.exe gdpr_account_tool.py delete --email korisnik@example.com --confirm

  # Render Postgres (privremeno postavi konekcioni string u istoj sesiji)
  $env:DATABASE_URL = "postgresql://KORISNIK:LOZINKA@HOST:5432/BAZA"
  venv\\Scripts\\python.exe gdpr_account_tool.py delete --email korisnik@example.com --confirm

Sta se desava pri brisanju:
  - users, projects, subscriptions, auth_sessions, password_reset_tokens,
    email_verification_tokens, export_jobs -> potpuno obrisano (FK CASCADE
    na nivou baze, pokriva i SQLite i Postgres)
  - billing_events, login_attempts -> email se anonimizuje (zapis transakcije
    / pokusaja prijave ostaje radi finansijske i bezbednosne evidencije, ali
    bez licnog identifikatora)
  - audit_logs -> email se uklanja iz teksta (detail polja); zapis ostaje sa
    internim ID-jem radi bezbednosnog traga

Bez --confirm, delete komanda samo prikazuje sta bi bilo obuhvaceno (dry-run)
i nista ne menja u bazi.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import project_store as ps

_CHILD_TABLES = (
    "projects",
    "subscriptions",
    "auth_sessions",
    "password_reset_tokens",
    "email_verification_tokens",
    "export_jobs",
    "billing_events",
    "audit_logs",
)


def cmd_export(email: str) -> int:
    ps.init_project_store()
    user = ps.get_user_by_email(email)
    if user is None:
        print(f"Nema naloga za email: {email}")
        return 1

    with ps._connect() as conn:
        projects = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, name, project_type, kitchen_layout, language, source,
                       is_demo, is_autosave, payload_json, created_at, updated_at, last_opened_at
                FROM projects WHERE user_id = ?
                """,
                (user.id,),
            ).fetchall()
        ]
        subscription = [
            dict(row)
            for row in conn.execute(
                """
                SELECT provider, plan_code, billing_status, current_period_end,
                       trial_started_at, created_at, updated_at
                FROM subscriptions WHERE user_id = ?
                """,
                (user.id,),
            ).fetchall()
        ]

    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "auth_mode": user.auth_mode,
            "access_tier": user.access_tier,
            "status": user.status,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
        "subscription": subscription,
        "projects": projects,
    }

    out_path = f"gdpr_export_{user.username or user.id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Nalog: #{user.id} {user.email}")
    print(f"Izvezeno {len(projects)} projekata.")
    print(f"Fajl: {out_path}")
    return 0


def cmd_delete(email: str, confirm: bool) -> int:
    ps.init_project_store()
    user = ps.get_user_by_email(email)
    if user is None:
        print(f"Nema naloga za email: {email}")
        return 1

    with ps._connect() as conn:
        counts: dict[str, int] = {}
        for table in _CHILD_TABLES:
            row = conn.execute(
                f"SELECT COUNT(*) AS c FROM {table} WHERE user_id = ?", (user.id,)
            ).fetchone()
            counts[table] = int(dict(row)["c"]) if row else 0
        login_row = conn.execute(
            "SELECT COUNT(*) AS c FROM login_attempts WHERE lower(email) = lower(?)",
            (user.email,),
        ).fetchone()
        counts["login_attempts"] = int(dict(login_row)["c"]) if login_row else 0

    print(f"Nalog: #{user.id} {user.email} ({user.username or '-'})")
    print("Obuhvaceno:")
    for table, count in counts.items():
        print(f"  {table}: {count}")

    if not confirm:
        print("\n(dry-run — nista nije obrisano; dodaj --confirm da izvrsis brisanje)")
        return 0

    anon_email = f"deleted-user-{user.id}@deleted.invalid"
    with ps._connect() as conn:
        # Finansijska/bezbednosna evidencija se anonimizuje, ne brise —
        # cuva se cinjenica da se transakcija/pokusaj desio, bez licnog
        # identifikatora.
        conn.execute("UPDATE billing_events SET email = ? WHERE user_id = ?", (anon_email, user.id))
        conn.execute(
            "UPDATE login_attempts SET email = ? WHERE lower(email) = lower(?)",
            (anon_email, user.email),
        )
        conn.execute(
            "UPDATE audit_logs SET detail = ? WHERE user_id = ?",
            (f"email={anon_email} (originalni podatak obrisan na zahtev korisnika)", user.id),
        )
        # Brise nalog; FK CASCADE brise projects, subscriptions, auth_sessions,
        # password_reset_tokens, email_verification_tokens, export_jobs.
        conn.execute("DELETE FROM users WHERE id = ?", (user.id,))
        conn.commit()

    print(f"\nObrisano. Nalog #{user.id} i licni podaci su uklonjeni.")
    print(f"Finansijski/bezbednosni zapisi zadrzani anonimizovano ({anon_email}).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GDPR izvoz/brisanje podataka korisnika")
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser("export", help="Izvezi sve podatke korisnika u JSON fajl")
    p_export.add_argument("--email", required=True)

    p_delete = sub.add_parser("delete", help="Obrisi nalog i licne podatke korisnika")
    p_delete.add_argument("--email", required=True)
    p_delete.add_argument(
        "--confirm", action="store_true", help="Stvarno izvrsi brisanje (bez ovoga je samo dry-run prikaz)"
    )

    args = parser.parse_args()
    if args.command == "export":
        return cmd_export(args.email)
    if args.command == "delete":
        return cmd_delete(args.email, args.confirm)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
