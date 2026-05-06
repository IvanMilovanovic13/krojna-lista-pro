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

_PRIVACY_DE = """
## Datenschutzerklärung

**Letzte Aktualisierung:** 5. Mai 2026.

### Wer wir sind
CabinetCutPro (KrojnaListaPRO) ist eine Web-Anwendung für die Planung von Kücheneinrichtungen.
Betreiber: Ivan Milovanovic, Kontakt: ivan_milovanovic@live.com

### Welche Daten wir erheben
- **E-Mail-Adresse** — zur Kontoerstellung und Kommunikation
- **Projektdaten** — Küchenpläne, die Sie in der App erstellen und speichern
- **Zahlungsdaten** — werden von Lemon Squeezy verarbeitet; wir sehen Ihre Kartennummer nie
- **Technische Daten** — IP-Adresse, Browser-Typ (Render-Server-Logs, max. 30 Tage)

### Wie wir Ihre Daten verwenden
- Um Ihnen Zugang zur Anwendung zu gewähren
- Um Zahlungen zu verarbeiten (Lemon Squeezy)
- Um Transaktions-E-Mails zu senden (Verifizierung, Passwort-Reset)
- Um die Anwendung zu verbessern (anonymisierte Statistiken)

### Datenspeicherung
Daten werden auf Render.com-Servern (USA) gespeichert, gesichert durch SSL.
Projekte werden gespeichert, bis Sie Ihr Konto löschen.

### Ihre Rechte (DSGVO)
Sie haben das Recht auf: Datenzugang, Berichtigung, Löschung Ihres Kontos und aller Daten.
Anfragen an: ivan_milovanovic@live.com

### Cookies
Wir verwenden nur das für die Anmeldung notwendige Session-Cookie. Keine Tracking-Pixel oder Werbe-Cookies.

### Weitergabe an Dritte
- **Lemon Squeezy** — Zahlungsanbieter (eigene Datenschutzerklärung)
- **Render.com** — Hosting (eigene Datenschutzerklärung)
- **Resend.com** — E-Mail-Versand
- Niemand sonst. Wir verkaufen keine Daten.

### Änderungen dieser Richtlinie
Wir informieren Sie per E-Mail über wesentliche Änderungen.

### Kontakt
ivan_milovanovic@live.com
"""

_TERMS_DE = """
## Nutzungsbedingungen

**Letzte Aktualisierung:** 5. Mai 2026.

### 1. Annahme der Bedingungen
Durch die Nutzung von CabinetCutPro akzeptieren Sie diese Bedingungen. Wenn Sie nicht zustimmen, nutzen Sie den Dienst nicht.

### 2. Beschreibung des Dienstes
CabinetCutPro ist ein SaaS-Tool zur Küchenplanung — Erstellung von Schnittlisten, Bohrplänen und 2D/3D-Ansichten.

### 3. Konten und Abonnements
- Die Registrierung erfordert eine gültige E-Mail-Adresse
- Testzeitraum: 14 Tage ohne Kreditkarte
- Bezahlte Abonnements werden im Voraus abgerechnet (monatlich/jährlich)
- Kündigung jederzeit möglich; Zugang gilt bis Ende des bezahlten Zeitraums

### 4. Zulässige Nutzung
Verboten ist:
- Versuche, das Autorisierungssystem zu umgehen
- Nutzung des Dienstes für illegale Aktivitäten
- Weiterverkauf des Zugangs an Dritte

### 5. Geistiges Eigentum
Anwendungscode und UI gehören dem Betreiber. Ihre Projektdaten gehören Ihnen.

### 6. Verfügbarkeit des Dienstes
Angestrebte Verfügbarkeit: 99%. Kein Anspruch auf ununterbrochenen Betrieb. Keine Haftung für Datenverlust durch technische Fehler — erstellen Sie eigene Backups.

### 7. Haftungsbeschränkung
Der Dienst wird "wie besehen" bereitgestellt. Die maximale Haftung des Betreibers ist auf den in den letzten 12 Monaten gezahlten Betrag beschränkt.

### 8. Kündigung
Wir behalten uns das Recht vor, Konten bei Verstoß gegen diese Bedingungen zu sperren, mit anteiliger Rückerstattung für den ungenutzten Zeitraum.

### 9. Anwendbares Recht
Es gilt das Recht der Republik Serbien.

### 10. Kontakt
ivan_milovanovic@live.com
"""

_PRIVACY_FR = """
## Politique de confidentialité

**Dernière mise à jour :** 5 mai 2026.

### Qui sommes-nous
CabinetCutPro (KrojnaListaPRO) est une application web de conception de cuisines.
Opérateur : Ivan Milovanovic, contact : ivan_milovanovic@live.com

### Données collectées
- **Adresse e-mail** — pour la création du compte et la communication
- **Données de projet** — plans de cuisine créés et sauvegardés dans l'app
- **Données de paiement** — traitées par Lemon Squeezy ; nous ne voyons jamais votre numéro de carte
- **Données techniques** — adresse IP, type de navigateur (logs Render, max 30 jours)

### Utilisation des données
- Pour vous donner accès à l'application
- Pour traiter les paiements (Lemon Squeezy)
- Pour envoyer des e-mails transactionnels (vérification, réinitialisation du mot de passe)
- Pour améliorer l'application (statistiques anonymisées)

### Stockage des données
Les données sont stockées sur les serveurs Render.com (États-Unis), protégés par SSL.
Les projets sont conservés jusqu'à la suppression de votre compte.

### Vos droits (RGPD)
Vous avez le droit de demander : accès à vos données, rectification, suppression du compte et de toutes vos données.
Envoyez votre demande à : ivan_milovanovic@live.com

### Cookies
Nous n'utilisons que le cookie de session nécessaire au bon fonctionnement de la connexion. Aucun pixel de suivi ni cookie publicitaire.

### Partage avec des tiers
- **Lemon Squeezy** — processeur de paiement (politique de confidentialité propre)
- **Render.com** — hébergement (politique de confidentialité propre)
- **Resend.com** — envoi d'e-mails
- Personne d'autre. Nous ne vendons pas vos données.

### Modifications de cette politique
Nous vous informerons par e-mail des modifications importantes.

### Contact
ivan_milovanovic@live.com
"""

_TERMS_FR = """
## Conditions d'utilisation

**Dernière mise à jour :** 5 mai 2026.

### 1. Acceptation des conditions
En utilisant CabinetCutPro, vous acceptez ces conditions. Si vous n'êtes pas d'accord, n'utilisez pas le service.

### 2. Description du service
CabinetCutPro est un outil SaaS de conception de cuisines — génération de listes de découpe, plans de perçage et vues 2D/3D.

### 3. Comptes et abonnements
- L'inscription requiert une adresse e-mail valide
- Période d'essai : 14 jours sans carte bancaire
- L'abonnement payant est facturé d'avance (mensuel/annuel)
- Résiliation possible à tout moment ; l'accès reste valable jusqu'à la fin de la période payée

### 4. Utilisation acceptable
Sont interdits :
- Toute tentative de contournement du système d'autorisation
- L'utilisation du service à des fins illégales
- La revente de l'accès à des tiers

### 5. Propriété intellectuelle
Le code et l'interface de l'application appartiennent à l'opérateur. Vos données de projet vous appartiennent.

### 6. Disponibilité du service
Objectif de disponibilité : 99 %. Aucune garantie de service ininterrompu. Aucune responsabilité pour la perte de données due à des défaillances techniques — effectuez vos propres sauvegardes.

### 7. Limitation de responsabilité
Le service est fourni "tel quel". La responsabilité maximale de l'opérateur est limitée au montant payé au cours des 12 derniers mois.

### 8. Résiliation
Nous nous réservons le droit de supprimer les comptes en violation de ces conditions, avec remboursement au prorata de la période non utilisée.

### 9. Droit applicable
Le droit de la République de Serbie s'applique.

### 10. Contact
ivan_milovanovic@live.com
"""

_PRIVACY_ES = """
## Política de privacidad

**Última actualización:** 5 de mayo de 2026.

### Quiénes somos
CabinetCutPro (KrojnaListaPRO) es una aplicación web para el diseño de cocinas.
Operador: Ivan Milovanovic, contacto: ivan_milovanovic@live.com

### Qué datos recopilamos
- **Dirección de correo electrónico** — para crear su cuenta y comunicarnos con usted
- **Datos de proyecto** — planos de cocina que crea y guarda en la app
- **Datos de pago** — procesados por Lemon Squeezy; nunca vemos su número de tarjeta
- **Datos técnicos** — dirección IP, tipo de navegador (logs del servidor Render, máx. 30 días)

### Cómo usamos sus datos
- Para darle acceso a la aplicación
- Para procesar pagos (Lemon Squeezy)
- Para enviar correos transaccionales (verificación, restablecimiento de contraseña)
- Para mejorar la aplicación (estadísticas anonimizadas)

### Almacenamiento de datos
Los datos se almacenan en servidores de Render.com (EE. UU.), protegidos con SSL.
Los proyectos se conservan hasta que elimine su cuenta.

### Sus derechos (RGPD)
Tiene derecho a: acceder a sus datos, corregirlos, eliminar su cuenta y todos sus datos.
Envíe su solicitud a: ivan_milovanovic@live.com

### Cookies
Solo utilizamos la cookie de sesión necesaria para el funcionamiento del inicio de sesión. Sin píxeles de seguimiento ni cookies publicitarias.

### Compartir con terceros
- **Lemon Squeezy** — procesador de pagos (política de privacidad propia)
- **Render.com** — alojamiento (política de privacidad propia)
- **Resend.com** — envío de correos
- Nadie más. No vendemos datos.

### Cambios en esta política
Le notificaremos por correo electrónico sobre cambios importantes.

### Contacto
ivan_milovanovic@live.com
"""

_TERMS_ES = """
## Términos de servicio

**Última actualización:** 5 de mayo de 2026.

### 1. Aceptación de los términos
Al usar CabinetCutPro, acepta estos términos. Si no está de acuerdo, no utilice el servicio.

### 2. Descripción del servicio
CabinetCutPro es una herramienta SaaS para el diseño de cocinas — generación de listas de corte, planos de taladrado y vistas 2D/3D.

### 3. Cuentas y suscripciones
- El registro requiere una dirección de correo electrónico válida
- Período de prueba: 14 días sin tarjeta de crédito
- La suscripción de pago se cobra por adelantado (mensual/anual)
- Puede cancelar en cualquier momento; el acceso se mantiene hasta el final del período pagado

### 4. Uso aceptable
Está prohibido:
- Intentar eludir el sistema de autorización
- Usar el servicio para actividades ilegales
- Revender el acceso a terceros

### 5. Propiedad intelectual
El código y la interfaz de la aplicación pertenecen al operador. Sus datos de proyecto le pertenecen a usted.

### 6. Disponibilidad del servicio
Objetivo: 99% de disponibilidad. No garantizamos un servicio ininterrumpido. No somos responsables de la pérdida de datos por fallos técnicos — realice sus propias copias de seguridad.

### 7. Limitación de responsabilidad
El servicio se proporciona "tal como está". La responsabilidad máxima del operador se limita al importe pagado en los últimos 12 meses.

### 8. Rescisión
Nos reservamos el derecho de cancelar cuentas que incumplan estos términos, con reembolso proporcional por el período no utilizado.

### 9. Ley aplicable
Se aplica el derecho de la República de Serbia.

### 10. Contacto
ivan_milovanovic@live.com
"""

_PRIVACY_PT = """
## Política de Privacidade

**Última atualização:** 5 de maio de 2026.

### Quem somos
CabinetCutPro (KrojnaListaPRO) é uma aplicação web para design de cozinhas.
Operador: Ivan Milovanovic, contato: ivan_milovanovic@live.com

### Dados que coletamos
- **Endereço de e-mail** — para criar sua conta e comunicação
- **Dados de projeto** — planos de cozinha que você cria e salva no app
- **Dados de pagamento** — processados pelo Lemon Squeezy; nunca vemos seu número de cartão
- **Dados técnicos** — endereço IP, tipo de navegador (logs do servidor Render, máx. 30 dias)

### Como usamos seus dados
- Para fornecer acesso à aplicação
- Para processar pagamentos (Lemon Squeezy)
- Para enviar e-mails transacionais (verificação, redefinição de senha)
- Para melhorar a aplicação (estatísticas anonimizadas)

### Armazenamento de dados
Os dados são armazenados nos servidores da Render.com (EUA), protegidos por SSL.
Os projetos são mantidos até que você exclua sua conta.

### Seus direitos (LGPD / RGPD)
Você tem direito a: acessar seus dados, corrigi-los, excluir sua conta e todos os dados.
Envie sua solicitação para: ivan_milovanovic@live.com

### Cookies
Utilizamos apenas o cookie de sessão necessário para o funcionamento do login. Sem pixels de rastreamento ou cookies publicitários.

### Compartilhamento com terceiros
- **Lemon Squeezy** — processador de pagamentos (política de privacidade própria)
- **Render.com** — hospedagem (política de privacidade própria)
- **Resend.com** — envio de e-mails
- Ninguém mais. Não vendemos dados.

### Alterações nesta política
Notificaremos você por e-mail sobre alterações importantes.

### Contato
ivan_milovanovic@live.com
"""

_TERMS_PT = """
## Termos de Serviço

**Última atualização:** 5 de maio de 2026.

### 1. Aceitação dos termos
Ao usar o CabinetCutPro, você aceita estes termos. Se não concordar, não use o serviço.

### 2. Descrição do serviço
CabinetCutPro é uma ferramenta SaaS para design de cozinhas — geração de listas de corte, planos de furação e visualizações 2D/3D.

### 3. Contas e assinaturas
- O cadastro requer um endereço de e-mail válido
- Período de teste: 14 dias sem cartão de crédito
- A assinatura paga é cobrada antecipadamente (mensal/anual)
- Cancelamento possível a qualquer momento; o acesso permanece até o fim do período pago

### 4. Uso aceitável
É proibido:
- Tentar contornar o sistema de autorização
- Usar o serviço para atividades ilegais
- Revender o acesso a terceiros

### 5. Propriedade intelectual
O código e a interface da aplicação pertencem ao operador. Seus dados de projeto pertencem a você.

### 6. Disponibilidade do serviço
Meta: 99% de disponibilidade. Não garantimos serviço ininterrupto. Não nos responsabilizamos por perda de dados devido a falhas técnicas — faça seus próprios backups.

### 7. Limitação de responsabilidade
O serviço é fornecido "como está". A responsabilidade máxima do operador é limitada ao valor pago nos últimos 12 meses.

### 8. Rescisão
Reservamo-nos o direito de encerrar contas que violem estes termos, com reembolso proporcional pelo período não utilizado.

### 9. Lei aplicável
Aplica-se a lei da República da Sérvia.

### 10. Contato
ivan_milovanovic@live.com
"""

_PRIVACY_RU = """
## Политика конфиденциальности

**Последнее обновление:** 5 мая 2026 г.

### Кто мы
CabinetCutPro (KrojnaListaPRO) — веб-приложение для проектирования кухонной мебели.
Оператор: Ivan Milovanovic, контакт: ivan_milovanovic@live.com

### Какие данные мы собираем
- **Email-адрес** — для создания аккаунта и коммуникации
- **Данные проектов** — кухонные планы, которые вы создаёте и сохраняете в приложении
- **Платёжные данные** — обрабатываются Lemon Squeezy; мы никогда не видим номер вашей карты
- **Технические данные** — IP-адрес, тип браузера (логи сервера Render, макс. 30 дней)

### Как мы используем данные
- Для предоставления доступа к приложению
- Для обработки платежей (Lemon Squeezy)
- Для отправки транзакционных писем (верификация, сброс пароля)
- Для улучшения приложения (анонимизированная статистика)

### Хранение данных
Данные хранятся на серверах Render.com (США), защищены SSL.
Проекты хранятся до момента удаления аккаунта.

### Ваши права (GDPR)
Вы вправе запросить: доступ к данным, исправление, удаление аккаунта и всех данных.
Запрос отправляйте на: ivan_milovanovic@live.com

### Файлы cookie
Мы используем только сессионный cookie, необходимый для работы авторизации. Никаких пикселей отслеживания и рекламных cookie.

### Передача третьим сторонам
- **Lemon Squeezy** — платёжный процессор (собственная политика конфиденциальности)
- **Render.com** — хостинг (собственная политика конфиденциальности)
- **Resend.com** — отправка писем
- Никому больше. Мы не продаём данные.

### Изменения политики
Мы уведомим вас по email о существенных изменениях.

### Контакт
ivan_milovanovic@live.com
"""

_TERMS_RU = """
## Условия использования

**Последнее обновление:** 5 мая 2026 г.

### 1. Принятие условий
Используя CabinetCutPro, вы принимаете настоящие условия. Если вы не согласны — не используйте сервис.

### 2. Описание сервиса
CabinetCutPro — SaaS-инструмент для проектирования кухонь: создание списков раскроя, планов сверловки, 2D/3D-просмотра.

### 3. Аккаунты и подписки
- Для регистрации необходим действительный email-адрес
- Пробный период: 14 дней без карты
- Платная подписка оплачивается авансом (ежемесячно/ежегодно)
- Отменить можно в любой момент; доступ сохраняется до конца оплаченного периода

### 4. Допустимое использование
Запрещено:
- Попытки обойти систему авторизации
- Использование сервиса в незаконных целях
- Перепродажа доступа третьим лицам

### 5. Интеллектуальная собственность
Код и интерфейс приложения принадлежат оператору. Ваши проектные данные принадлежат вам.

### 6. Доступность сервиса
Целевой показатель: 99% аптайм. Непрерывная работа не гарантируется. Мы не несём ответственности за потерю данных из-за технических сбоев — делайте собственные резервные копии.

### 7. Ограничение ответственности
Сервис предоставляется "как есть". Максимальная ответственность оператора ограничена суммой, уплаченной за последние 12 месяцев.

### 8. Расторжение
Мы оставляем за собой право закрыть аккаунт, нарушающий настоящие условия, с пропорциональным возвратом средств за неиспользованный период.

### 9. Применимое право
Применяется право Республики Сербии.

### 10. Контакт
ivan_milovanovic@live.com
"""

_PRIVACY_ZH = """
## 隐私政策

**最后更新：** 2026年5月5日

### 关于我们
CabinetCutPro（KrojnaListaPRO）是一款用于厨房设计的网页应用。
运营者：Ivan Milovanovic，联系方式：ivan_milovanovic@live.com

### 我们收集哪些数据
- **电子邮件地址** — 用于账户创建和沟通
- **项目数据** — 您在应用中创建并保存的厨房设计方案
- **支付数据** — 由 Lemon Squeezy 处理；我们从不获取您的银行卡号
- **技术数据** — IP 地址、浏览器类型（Render 服务器日志，最长 30 天）

### 我们如何使用您的数据
- 为您提供应用访问权限
- 处理支付（Lemon Squeezy）
- 发送事务性邮件（验证、密码重置）
- 改进应用（匿名统计）

### 数据存储
数据存储于 Render.com 服务器（美国），受 SSL 保护。
项目数据将保留至您删除账户为止。

### 您的权利（GDPR）
您有权要求：访问数据、更正数据、删除账户及所有数据。
请发送请求至：ivan_milovanovic@live.com

### Cookie
我们仅使用登录功能所必需的会话 Cookie，不使用跟踪像素或广告 Cookie。

### 与第三方共享
- **Lemon Squeezy** — 支付处理商（有其自己的隐私政策）
- **Render.com** — 托管服务（有其自己的隐私政策）
- **Resend.com** — 邮件发送
- 不与其他任何方共享。我们不出售数据。

### 政策变更
我们将通过电子邮件通知您重大变更。

### 联系方式
ivan_milovanovic@live.com
"""

_TERMS_ZH = """
## 服务条款

**最后更新：** 2026年5月5日

### 1. 接受条款
使用 CabinetCutPro 即表示您同意本条款。如不同意，请勿使用本服务。

### 2. 服务说明
CabinetCutPro 是一款用于厨房设计的 SaaS 工具——可生成裁切清单、钻孔计划及 2D/3D 视图。

### 3. 账户与订阅
- 注册需要有效的电子邮件地址
- 试用期：14天，无需信用卡
- 付费订阅按月/年预付
- 可随时取消；访问权限延续至付费期结束

### 4. 可接受的使用
禁止：
- 尝试绕过授权系统
- 将本服务用于非法活动
- 向第三方转售访问权限

### 5. 知识产权
应用程序代码和界面归运营者所有。您的项目数据归您所有。

### 6. 服务可用性
目标可用率：99%。我们不保证服务不中断。对因技术故障导致的数据丢失不承担责任——请自行备份。

### 7. 责任限制
本服务按"现状"提供。运营者的最高责任限于您在过去12个月内支付的金额。

### 8. 终止
我们保留对违反本条款的账户进行终止的权利，并按比例退还未使用期间的费用。

### 9. 适用法律
适用塞尔维亚共和国法律。

### 10. 联系方式
ivan_milovanovic@live.com
"""

_PRIVACY_HI = """
## गोपनीयता नीति

**अंतिम अपडेट:** 5 मई 2026

### हम कौन हैं
CabinetCutPro (KrojnaListaPRO) रसोई डिज़ाइन के लिए एक वेब एप्लिकेशन है।
संचालक: Ivan Milovanovic, संपर्क: ivan_milovanovic@live.com

### हम कौन से डेटा एकत्र करते हैं
- **ईमेल पता** — खाता बनाने और संचार के लिए
- **प्रोजेक्ट डेटा** — आपके द्वारा ऐप में बनाए और सहेजे गए किचन प्लान
- **भुगतान डेटा** — Lemon Squeezy द्वारा संसाधित; हम आपका कार्ड नंबर कभी नहीं देखते
- **तकनीकी डेटा** — IP पता, ब्राउज़र प्रकार (Render सर्वर लॉग, अधिकतम 30 दिन)

### हम डेटा का उपयोग कैसे करते हैं
- आपको एप्लिकेशन तक पहुंच प्रदान करने के लिए
- भुगतान संसाधित करने के लिए (Lemon Squeezy)
- लेन-देन संबंधी ईमेल भेजने के लिए (सत्यापन, पासवर्ड रीसेट)
- एप्लिकेशन को बेहतर बनाने के लिए (अनामीकृत आंकड़े)

### डेटा संग्रहण
डेटा Render.com सर्वर (USA) पर संग्रहीत है, SSL द्वारा सुरक्षित।
प्रोजेक्ट तब तक सहेजे रहते हैं जब तक आप खाता नहीं हटाते।

### आपके अधिकार (GDPR)
आपको अधिकार है: डेटा तक पहुंच, सुधार, खाते और सभी डेटा को हटाना।
अनुरोध भेजें: ivan_milovanovic@live.com

### कुकीज़
हम केवल लॉगिन के लिए आवश्यक सेशन कुकी का उपयोग करते हैं। कोई ट्रैकिंग पिक्सेल या विज्ञापन कुकी नहीं।

### तृतीय पक्षों के साथ साझाकरण
- **Lemon Squeezy** — भुगतान प्रोसेसर (अपनी गोपनीयता नीति के साथ)
- **Render.com** — होस्टिंग (अपनी गोपनीयता नीति के साथ)
- **Resend.com** — ईमेल वितरण
- और कोई नहीं। हम डेटा नहीं बेचते।

### नीति में बदलाव
हम महत्वपूर्ण बदलावों के बारे में ईमेल से सूचित करेंगे।

### संपर्क
ivan_milovanovic@live.com
"""

_TERMS_HI = """
## सेवा की शर्तें

**अंतिम अपडेट:** 5 मई 2026

### 1. शर्तों की स्वीकृति
CabinetCutPro का उपयोग करके आप इन शर्तों से सहमत होते हैं। यदि आप सहमत नहीं हैं, तो सेवा का उपयोग न करें।

### 2. सेवा का विवरण
CabinetCutPro रसोई डिज़ाइन के लिए एक SaaS टूल है — कट लिस्ट, ड्रिलिंग प्लान और 2D/3D व्यू बनाने के लिए।

### 3. खाते और सदस्यताएं
- पंजीकरण के लिए वैध ईमेल पता आवश्यक है
- ट्रायल अवधि: 14 दिन, क्रेडिट कार्ड के बिना
- भुगतान सदस्यता अग्रिम में चार्ज की जाती है (मासिक/वार्षिक)
- किसी भी समय रद्द किया जा सकता है; पहुंच भुगतान अवधि के अंत तक जारी रहती है

### 4. स्वीकार्य उपयोग
निषिद्ध है:
- प्राधिकरण प्रणाली को बायपास करने का प्रयास
- अवैध गतिविधियों के लिए सेवा का उपयोग
- तृतीय पक्षों को पहुंच पुनः बेचना

### 5. बौद्धिक संपदा
एप्लिकेशन कोड और UI संचालक की संपत्ति है। आपका प्रोजेक्ट डेटा आपका है।

### 6. सेवा उपलब्धता
लक्ष्य: 99% अपटाइम। निर्बाध सेवा की गारंटी नहीं। तकनीकी खराबी के कारण डेटा हानि के लिए जिम्मेदार नहीं — अपना बैकअप बनाएं।

### 7. दायित्व सीमा
सेवा "जैसी है" प्रदान की जाती है। संचालक की अधिकतम देयता पिछले 12 महीनों में भुगतान की गई राशि तक सीमित है।

### 8. समाप्ति
हम इन शर्तों का उल्लंघन करने वाले खाते को बंद करने का अधिकार सुरक्षित रखते हैं, अप्रयुक्त अवधि के लिए आनुपातिक धनवापसी के साथ।

### 9. लागू कानून
सर्बिया गणराज्य का कानून लागू होता है।

### 10. संपर्क
ivan_milovanovic@live.com
"""

# Mapa: jezik → sadržaj
_PRIVACY = {
    "sr":    _PRIVACY_SR,
    "en":    _PRIVACY_EN,
    "de":    _PRIVACY_DE,
    "fr":    _PRIVACY_FR,
    "es":    _PRIVACY_ES,
    "pt-br": _PRIVACY_PT,
    "ru":    _PRIVACY_RU,
    "zh-cn": _PRIVACY_ZH,
    "hi":    _PRIVACY_HI,
}
_TERMS = {
    "sr":    _TERMS_SR,
    "en":    _TERMS_EN,
    "de":    _TERMS_DE,
    "fr":    _TERMS_FR,
    "es":    _TERMS_ES,
    "pt-br": _TERMS_PT,
    "ru":    _TERMS_RU,
    "zh-cn": _TERMS_ZH,
    "hi":    _TERMS_HI,
}


_BACK_LABEL: dict[str, str] = {
    "sr":    "← Nazad",
    "en":    "← Back",
    "de":    "← Zurück",
    "fr":    "← Retour",
    "es":    "← Volver",
    "pt-br": "← Voltar",
    "ru":    "← Назад",
    "zh-cn": "← 返回",
    "hi":    "← वापस",
}


def _legal_shell(title: str, content_md: str, lang: str = "en") -> None:
    """Renderuje pravnu stranicu sa čistim layoutom."""
    from ui_public_site import PUBLIC_PAGE_STYLE, _public_shell  # type: ignore

    _public_shell()

    back_lbl = _BACK_LABEL.get(lang, "← Back")

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
                f'<a href="/" style="font-size:13px;color:#6b7280;'
                f'text-decoration:none;">{back_lbl}</a>'
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


_SUPPORTED_LANGS = frozenset(_PRIVACY.keys())


def _get_lang() -> str:
    """Dohvata jezik iz storage-a, fallback na 'en'."""
    try:
        from nicegui import app as _app
        lang = str(_app.storage.user.get("language", "en") or "en").lower().strip()
        return lang if lang in _SUPPORTED_LANGS else "en"
    except Exception:
        return "en"


def render_privacy_page() -> None:
    lang = _get_lang()
    content = _PRIVACY.get(lang) or _PRIVACY["en"]
    _legal_shell("Privacy Policy", content, lang=lang)


def render_terms_page() -> None:
    lang = _get_lang()
    content = _TERMS.get(lang) or _TERMS["en"]
    _legal_shell("Terms of Service", content, lang=lang)
