# Cloudflare + Railway: настройка

Cloudflare стоит перед Railway и кэширует статику (`/static/*`) на своих серверах. Railway получает только запросы к динамическому контенту.

## Схема работы

```
Браузер → Cloudflare (кэш CSS/JS) → Railway (Gunicorn + WhiteNoise)
```

При первом запросе к `/static/main.abc123.css` Cloudflare запрашивает у Railway и кэширует. Последующие запросы Railway не достигают.

## Настройка: шаг за шагом

### 1. Добавь домен в Cloudflare

1. Зарегистрируйся на [cloudflare.com](https://cloudflare.com) (бесплатный план)
2. Добавь свой домен: **Add a Site** → введи домен
3. Cloudflare покажет NS-серверы — смени NS у регистратора домена на cloudflare

### 2. Создай DNS-запись

В Cloudflare → DNS → Add Record:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` (или `nesclub`) | `nesclub-production.up.railway.app` | ✅ Proxied (оранжевое облако) |

Важно: **Proxied** (не DNS only) — иначе Cloudflare не будет кэшировать.

### 3. Обнови APP_HOST в Railway

В Railway Variables замени:
```
APP_HOST=https://твой-домен.com
```

Это важно — от `APP_HOST` строятся URL для email-ссылок, Telegram webhook и OG-картинок.

### 4. Настрой кэширование статики в Cloudflare

Cloudflare → **Rules** → **Cache Rules** → Create Rule:

- **Field**: URI Path
- **Operator**: starts with
- **Value**: `/static/`
- **Cache**: Eligible for cache
- **Edge TTL**: 1 year (WhiteNoise добавляет хэш к именам файлов, файлы никогда не устаревают)

### 5. SSL/TLS режим

Cloudflare → **SSL/TLS** → установи режим **Full** (не Full Strict, т.к. Railway использует свой сертификат).

## Проверка

После настройки открой DevTools → Network → любой `.css` файл.
В заголовках ответа должно быть:
```
CF-Cache-Status: HIT   ← файл отдан из кэша Cloudflare
```

При первом запросе будет `MISS`, при последующих — `HIT`.

## Переменные окружения

Для Cloudflare новых переменных в приложении **не нужно** — всё настраивается на стороне Cloudflare.

Единственное что меняется: `APP_HOST` должен содержать твой домен (а не railway.app).

## WhiteNoise — что это и зачем

WhiteNoise — библиотека которая позволяет Gunicorn раздавать статику без Nginx.
Настроена в `club/settings.py`:

```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

При деплое автоматически запускается `python3 manage.py collectstatic` (см. Makefile),
который собирает все CSS/JS/картинки в папку `staticfiles/` с хэшами в именах.

Cloudflare кэширует эти файлы на год — Railway почти не получает запросов к статике.
