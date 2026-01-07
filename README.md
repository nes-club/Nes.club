<div align="center">
  <br>
  <img src="frontend/static/images/logo/logo-256.png" alt="">
  <h1>Сообщество выпускников РЭШ</h1>
</div>

Welcome to the NES alumni community (non-official) codebase. We're building a private alumni community. We've opensourced the code so that every member could contribute or implement a feature that they want.

This project is based on the vas3k.club engine and adapted for the NES alumni community. It is a private, invite-driven space focused on thoughtful conversations, networking, and mutual help for alumni, staff, and friends of NES.

Our values: honesty, fair share, respect for other members, rationality, friendliness and usefulness. We have a zero-tolerance policy on anonymity, insults and toxicity. But we always try to stay in touch with reality, so we're also not tolerant of witch hunting and call-out culture.

We're a bullshitless community!

## 🛠 Tech stack

👨‍💻 **TL;DR: Django, Postgres, Redis, Vue.js, Webpack**

We try to keep our stack as simple and stupid as possible. Because we're not very smart either.

The trickiest part of our stack is how we develop the frontend and backend as a single service. We don't use SPA, as many people do, but only make parts of the page dynamic by inserting Vue.js components directly into Django templates. This may seem weird, but it actually makes it very easy for one person to develop and maintain the entire site.

You don't really need to understand how the magic of webpack <-> django communication works under the hood to develop new components. Just run `django runserver` and `npm run watch` at the same time and enjoy your coding.

Feel free to propose "state of the art" refactorings for UI or backend code if you know how to do it better. We're open for best practices from both worlds.

## 🔮 Installing and running locally (Docker)

1. Install Docker Desktop.
2. Open the repository folder in your terminal.
3. Build and run all dev services:

    ```sh
    docker compose up --build
    ```

This starts the app in dev mode on http://127.0.0.1:8000/ plus Postgres, Redis, queue workers, and webpack.

After the containers are up:

1. Wait for `Starting development server at http://0.0.0.0:8000/`.
2. Open http://127.0.0.1:8000/.
3. Quick admin session: http://127.0.0.1:8000/godmode/dev_login/
4. Random test user: http://127.0.0.1:8000/godmode/random_login/

Hot reload works for both backend and frontend. If assets look stale:

```sh
docker compose restart club_app webpack
```

If you changed templates and still see old texts, check the page source in the DB (docs pages are stored in the database).
If you need to fully reset everything:

```sh
docker compose down -v
docker compose up --build
```

## 🔗 Local links

- Home: http://127.0.0.1:8000/
- Join: http://127.0.0.1:8000/join/
- Django admin: http://127.0.0.1:8000/admin/
- Dev login (admin): http://127.0.0.1:8000/godmode/dev_login/
- Random user: http://127.0.0.1:8000/godmode/random_login/

Create a Django superuser (optional):

```sh
docker compose exec club_app python3 manage.py createsuperuser
```

## 🤖 Telegram bots (optional)

Local dev uses polling (no public webhook needed).

1. Set env vars (minimum):
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_ADMIN_CHAT_ID`
2. Uncomment `bot` and/or `helpdeskbot` in `docker-compose.yml`.
3. Start the bot containers:

```sh
docker compose up --build bot helpdeskbot
```

## 🧪 Dev environment on a server

Same stack as local, but run it in the background and point `APP_HOST` to your dev domain.

1. Create a `.env` file with:
   - `APP_HOST=https://dev.alumni.nes.ru` (or `http://<server-ip>:8000`)
   - Optional bot vars if you need Telegram bots (see below)
2. Run:

```sh
docker compose up --build -d
```

3. Check logs if something failed:

```sh
docker compose logs -f club_app
```

Open the site on your dev domain or `http://<server-ip>:8000/` and use the same links as in local:

- Admin: `http://<server-ip>:8000/admin/`
- Dev login: `http://<server-ip>:8000/godmode/dev_login/`
- Random user: `http://<server-ip>:8000/godmode/random_login/`

If you want HTTPS and a clean domain, put Nginx/Traefik in front of `127.0.0.1:8000` and set `APP_HOST` to the public URL.

To update code in dev:

```sh
git pull
docker compose up --build -d
docker compose restart club_app webpack
```

To reset dev data:

```sh
docker compose down -v
docker compose up --build -d
```

## 🏭 Production environment on a server

Production is described in `docker-compose.production.yml` and expects an external Postgres.
All domains and secrets are read from `.env` (see `.env.production.example`).

1. Create `.env` with at least:
   - `APP_HOST=https://alumni.nes.ru`
   - `MEDIA_UPLOAD_URL=` (optional; leave empty for local media)
   - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
   - `TELEGRAM_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID` (if bots are enabled)
2. Start production services:

```sh
docker compose -f docker-compose.production.yml up -d
```

3. Put a reverse proxy in front of the app:
   - App listens on `127.0.0.1:8814`
   - Bot webhooks (if enabled) should be reachable at `${APP_HOST}/telegram/webhook/`

Optional services for prod:

```sh
docker compose -f docker-compose.production.yml up -d bot helpdeskbot cron queue
```

### ✅ Production checklist

1. Nginx/Traefik
   - Reverse proxy to `127.0.0.1:8814`
   - Pass `Host` and `X-Forwarded-*` headers
   - Gzip/brotli enabled
2. SSL
   - Get TLS certs (Let’s Encrypt or your CA)
   - Force HTTPS redirects
   - Update `APP_HOST=https://your-domain`
3. Healthchecks
   - Add an external monitor for `GET /` (200)
   - Optional: monitor `GET /metrics` if you expose it
4. Backups
   - Postgres daily dump (off-host)
   - `gdpr/downloads` volume backup if you use it
   - Store backups encrypted and test restore monthly

### 📦 Nginx пример

```nginx
server {
    listen 80;
    server_name alumni.nes.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name alumni.nes.ru;

    ssl_certificate /etc/letsencrypt/live/alumni.nes.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alumni.nes.ru/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8814;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }
}
```

### 🗄️ Postgres backup script

Use `scripts/backup_postgres.sh` and run it from cron on the server.

```sh
export POSTGRES_HOST=localhost
export POSTGRES_DB=vas3k_club
export POSTGRES_USER=vas3k
export POSTGRES_PASSWORD=your_password
export BACKUP_KEEP_DAYS=14
./scripts/backup_postgres.sh /var/backups/nes_club
```

Example cron entry (daily at 03:30):

```cron
30 3 * * * cd /srv/nes.club && /usr/bin/env POSTGRES_HOST=localhost POSTGRES_DB=vas3k_club POSTGRES_USER=vas3k POSTGRES_PASSWORD=your_password BACKUP_KEEP_DAYS=14 ./scripts/backup_postgres.sh /var/backups/nes_club
```

## 🧑‍💻 Advanced setup for devs

For more information on how to test the telegram bot, run project without docker and other useful notes, read [docs/setup.md](docs/setup.md).

## ☄️ Testing

We use standard Django testing framework. No magic, really. You can run them from PyCharm or using Django CLI. 

See [docs/test.md](docs/test.md) for more insights.

> We don't have UI tests, sorry. Maybe in the future

## 🚢 Deployment

No k8s, no AWS, we ship dockers directly via ssh and it's beautiful!

The entire production configuration is described in the [docker-compose.production.yml](docker-compose.production.yml) file. 

Then, [Github Actions](.github/workflows/deploy.yml) have to take all the dirty work. They build, test and deploy changes to production on every merge to master (only official maintainers can do it).

Explore the whole [.github](.github) folder for more insights.

We're open for proposals on how to improve our deployments without overcomplicating it with modern devops bullshit.

## 🛤 Forking and tweaking

Forks are welcome. We're small and our engine is not universal like Wordpress, but with sufficient programming skills (and using grep), you can launch your own Club website in a couple of weeks. 

Three huge requests for everyone:

- Please give kudos the original authors. "Works on vas3k.club engine" in the footer of your site will be enough.
- Please share new features you implement with us, so other folks can also benefit from them, and your own codebase minimally diverges from the original one (so you can sync updates and security fixes) . Use our [feature-flags](club/features.py).
- Do not use our issues and other official channels as a support desk. Use [chats](https://t.me/joinchat/T5DDOpAVcZwzODg0).

> ♥️ [Feature-flags](club/features.py) are great. Use them to tweak your fork. Create new flags to upstream your new features or disable existing ones.

## 🙋‍♂️ How to report a bug?

- 🆕Open [a new issue](https://github.com/vas3k/vas3k.club/issues/new). 
- 🔦 Please, **use a search**, to check, if there is already existed issue!
- Explain your idea or proposal in all the details: 
    - Make sure you clearly describe "observed" and "expected" behaviour. It will dramatically save time for our contributors and maintainers. 
    - **For minor fixes** please just open a PR.
    
## 💎 Now to propose a new feature?

- Go to our [Discussions](https://github.com/vas3k/vas3k.club/discussions)
- Check to see if someone else has already come up with the idea before
- Create a new discussion
- 🖼 If it's **UI/UX** related: attach a screenshot or wireframe

## 😍 Contributions

Contributions are welcome.  

The main point of interaction is the [Issues page](https://github.com/vas3k/vas3k.club/issues).

Here's our contribution guidelines — [CONTRIBUTING.md](CONTRIBUTING.md).

We also run the public [Github Project Board](https://github.com/vas3k/vas3k.club/projects/3) to track progress and develop roadmaps.

> The official development language at the moment is Russian, because 100% of our users speak it. We don't want to introduce unnecessary barriers for them. But we are used to writing commits and comments in English and we won't mind communicating with you in it.

### 😎 I want to write some code

- Open our [Issues page](https://github.com/vas3k/vas3k.club/issues) to see the most important tickets at top. 
- Pick one issue you like and **leave a comment** inside that you're getting it.

**For big changes** open an issues first or (if it's already opened) leave a comment with brief explanation what and why you're going to change. Many tickets hang open not because they cannot be done, but because they cause many logical contradictions that you may not know. It's better to clarify them in comments before sending a PR.

### 🚦Pay attention to issue labels!

#### 🟩 Ready to implement

- **good first issue** — good tickets **for first-timers**. Usually these are simple and not critical things that allow you to quickly feel the code and start contributing to it.
- **bug** — if **something is not working**, it needs to be fixed, obviously.
- **critical** — the **first priority** tickets.
- **improvement** — accepted improvements for an existing module. Like adding a sort parameter to the feed. If improvement requires UI, **be sure to provide a sketch before you start.**

#### 🟨 Discussion is needed

- **new feature** —  completely new features. Usually they're too hard for newbies, leave them **for experienced contributors.**
- **idea** — **discussion is needed**. Those tickets look adequate, but waiting for real proposals how they will be done. Don't implement them right away.

#### 🟥 Questionable

- [¯\\_(ツ)\_/¯](https://github.com/vas3k/vas3k.club/labels/%C2%AF%5C_%28%E3%83%84%29_%2F%C2%AF) - special label for **questionable issues**. (should be closed in 60 days of inactivity)
- **[no label]** — ticket is new, unclear or still not reviewed. Feel free to comment it but **wait for our maintainers' decision** before starting to implement it.


## 🔐 Security and vulnerabilities

If you think you've found a critical vulnerability that should not be exposed to the public yet, you can always email me directly on Telegram [@vas3k](https://t.me/vas3k) or by email: [me@vas3k.ru](mailto:me@vas3k.ru).

Please do not test vulnerabilities in public. If you start spamming the website with "test-test-test" posts or comments, our moderators will ban you even if you had good intentions.


## 👍 Our top contributors

Take some time to press F and give some respects to our [best contributors](https://github.com/vas3k/vas3k.club/graphs/contributors), who spent their own time to make the club better.

- [@vas3k](https://github.com/vas3k)
- [@dimabory](https://github.com/dimabory)
- [@devcooch](https://github.com/devcooch)
- [@nlopin](https://github.com/nlopin)
- [@fr33mang](https://github.com/fr33mang)
- [@Vostenzuk](https://github.com/Vostenzuk)
- [@nikolay-govorov](https://github.com/nikolay-govorov)
- [@FMajesty](https://github.com/FMajesty)


## 👩‍💼 License 

[MIT](LICENSE)

In other words, you can use the code for private and commercial purposes with an author attribution (by including the original license file or mentioning the Club 🎩).

Feel free to contact us via email [atishin@nes.ru](mailto:atishin@nes.ru).

❤️
