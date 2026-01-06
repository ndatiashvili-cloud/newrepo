# 🐳 RND FLUX - Docker Setup (მარტივი)

## სწრაფი დაწყება

\`\`\`bash
# 1. შექმენი .env ფაილი
cp .env.example .env

# 2. გაუშვი Docker Compose
docker compose up -d

# ან თუ docker-compose გამოიყენებ
docker-compose up -d
\`\`\`

## წვდომა

- **Web UI**: http://localhost:5001
- **API Docs**: http://localhost:5001/docs
- **Default Login**: `admin` / `admin123`

## სასარგებლო ბრძანებები

\`\`\`bash
# ლოგების ნახვა
docker compose logs -f api

# სერვისების გაჩერება
docker compose down

# სერვისების გადატვირთვა
docker compose restart api
\`\`\`

## სერვისები

- **api** - მთავარი აპლიკაცია (პორტი 5001)
- **postgres** - მონაცემთა ბაზა (პორტი 5432)
- **redis** - cache და message broker (პორტი 6379)
- **celery-worker** - SNMP polling
- **celery-beat** - scheduled tasks

---

**RND FLUX v2.0** - Network Monitoring Platform
