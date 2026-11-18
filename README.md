# ClientBridge Smart Enquiry Portal

ClientBridge is a prototype B2B enquiry and sales-management portal for an industrial fluid-sealing products manufacturer based in Kolkata. It includes a public enquiry form, fallback/Gemini chatbot, private admin dashboard, Gmail SMTP sending and IMAP reply polling.

## Funnel fast-track

| Enquiry type | Starts at stage |
|---|---|
| New customer | 1. Awareness |
| Referral | 4. Discussion |
| Repeat order | 5. Negotiation |
| Existing customer, new product | 3. Solve client problem |

## Setup

### Windows

```bat
python -m pip install -r backend\requirements.txt
cd frontend
npm install
cd ..
copy .env.example .env
run.bat
```

### macOS / Linux

```sh
python3 -m pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
cp .env.example .env
chmod +x run.sh
./run.sh
```

Open `http://localhost:5173`. The API is at `http://localhost:8000`; API documentation is at `/docs`.

## Netlify frontend deployment

The FastAPI backend cannot run directly on Netlify Static Hosting. Deploy this frontend to Netlify and deploy `backend/` to a host that supports Python or a persistent process, then set:

- Netlify environment variable: `VITE_API_URL=https://your-backend-host`
- Backend environment variable: `FRONTEND_ORIGIN=https://your-netlify-site.netlify.app`
- Backend Gmail variables: `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `MAIL_RECIPIENT`, `MAIL_POLL_SECONDS`
- Backend JSON storage requires persistent disk or it resets on redeploy/restart

The industry and product dropdown data is bundled with the frontend, so it displays even before the backend is connected. Form submission, admin data, chat, and mail still require `VITE_API_URL` to point to a running backend. Do not use the example placeholder URL.

Gmail polling only works while the backend process remains running. Multiple comma-separated Netlify origins may be placed in `FRONTEND_ORIGIN`.

## Environment

Set the values in `.env`. Gmail requires a 16-character App Password. Turn on 2-Step Verification for the Gmail account, open Google Account > Security > App passwords, and create an app password. Place it in `GMAIL_APP_PASSWORD`.

ClientBridge tries SMTP STARTTLS on port 587 first, then SMTP SSL on port 465 if the connection closes unexpectedly.

Set `ADMIN_EMAIL` to the email address used to enter the admin portal. Client and admin entry require email only; no public registration is used.

For Gemini, create an API key in Google AI Studio and set `GEMINI_API_KEY`. Set `GEMINI_MODEL` explicitly. The chatbot also works without Gemini using a keyword fallback.

## Gmail reply sync

The backend checks Gmail every `MAIL_POLL_SECONDS` seconds while running. Replies are matched first by In-Reply-To/References against saved outgoing Message-ID headers, then by `[ENQ-xxxx]` in the subject. Unrelated mail is ignored. Attachments are represented only by file name. Quoted history and signatures are stripped when recognizable, but stripping may not be perfect.

Use a different Gmail account to send test replies. Start a reply from an email sent by the portal so Gmail creates the correct thread headers.

## Chatbot rules

The client-message counter is stored per session. After the fourth client message, the bot gives the sales phone unless the issue is solved. Price, human/person, quote, negotiation, complaint, urgent or angry requests give the phone immediately. The bot never invents prices, delivery dates, stock status, certifications or technical specifications.

## Admin

Use the `ADMIN_EMAIL` from `.env` at `/admin/login`, then `/admin`. The configured authorized address is `soumabha015@gmail.com`.

## Prototype limitations

Data is stored in local JSON files under `backend/data/`, with no database. There is one admin password, no multi-user roles, and seed enquiries are illustrative. Gmail synchronization depends on the backend remaining running and uses a polling delay of roughly 45 seconds.

## Future improvements

Real database, proper accounts and roles, Gmail OAuth with push notifications, WhatsApp integration, quotation PDF generation, CRM integration and richer analytics.

## Screenshot placeholders

- Client portal hero and enquiry form
- Admin dashboard
- Admin enquiry detail and Gmail thread
