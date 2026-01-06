# RND Monitoring - Manual Installation Guide

თუ ZIP ფაილის ჩამოტვირთვა არ მუშაობს, აი ალტერნატიული გზები:

## Option 1: GitHub-ის გამოყენება (რეკომენდებული)

v0 საშუალებას გაძლევთ პროექტი GitHub-ზე გამოაგზავნოთ:

1. v0 chat-ში, sidebar-ში იპოვეთ "GitHub" ან "Publish" ღილაკი
2. დააკავშირეთ თქვენი GitHub ანგარიში
3. შექმენით ახალი repository სახელით "rnd-monitoring"
4. შემდეგ ლოკალურად clone გაუკეთეთ:
```bash
git clone https://github.com/YOUR-USERNAME/rnd-monitoring.git
cd rnd-monitoring
chmod +x setup-rnd-monitoring.sh
./setup-rnd-monitoring.sh
```

## Option 2: ხელით ფაილების კოპირება

თუ GitHub-იც არ მუშაობს, შეგიძლიათ თითოეული ფაილი ცალ-ცალკე დააკოპიროთ:

### ნაბიჯი 1: შექმენით დირექტორია
```bash
mkdir -p rnd-monitoring
cd rnd-monitoring
mkdir -p frontend/src/{components,pages,services}
mkdir -p routers monitoring/snmp monitoring/victoria
mkdir -p migrations data logs
```

### ნაბიჯი 2: შექმენით ძირითადი ფაილები

v0 chat-ში ყოველი კოდის ბლოკის გვერდით არის "Copy" ღილაკი. დააკოპირეთ შემდეგი ფაილები თითო-თითოდ:

**Backend Files:**
1. `main.py` - მთავარი FastAPI აპლიკაცია
2. `requirements.txt` - Python dependencies
3. `docker-compose.yml` - Docker configuration
4. `Dockerfile` - Docker build file
5. `celery_app.py` - Celery configuration
6. `database.py` - Database setup
7. `models.py` - Database models
8. `.env.example` - Environment variables template

**Routers:**
9. `routers/auth.py`
10. `routers/devices.py`
11. `routers/diagnostics.py`
12. `routers/monitoring.py`
13. `routers/zabbix.py`
14. `routers/integrations.py` (ახალი!)

**Frontend Files:**
15. `frontend/package.json`
16. `frontend/index.html`
17. `frontend/vite.config.ts`
18. `frontend/tsconfig.json`
19. `frontend/tailwind.config.js`
20. `frontend/src/App.tsx`
21. `frontend/src/pages/Login.tsx`
22. `frontend/src/components/layout/Header.tsx`

### ნაბიჯი 3: დააკოპირეთ setup script
```bash
# შექმენით setup-rnd-monitoring.sh და ჩასვით script-ის კოდი
chmod +x setup-rnd-monitoring.sh
```

### ნაბიჯი 4: გაუშვით setup
```bash
./setup-rnd-monitoring.sh
```

## Option 3: Vercel Deploy (ყველაზე მარტივი!)

თუ v0-ს გაქვთ Vercel-თან დაკავშირებული:

1. v0 chat-ში დააჭირეთ "Publish to Vercel" ღილაკს
2. Vercel-ში პროექტი ავტომატურად deploy-დება
3. შემდეგ შეგიძლიათ:
```bash
# Install Vercel CLI
npm install -g vercel

# Clone from Vercel
vercel pull
cd YOUR-PROJECT-NAME

# Run locally
./setup-rnd-monitoring.sh
```

## რა იცოდეთ პრობლემის შესახებ

v0 ZIP download შეიძლება არ მუშაობდეს თუ:
- პროექტი ძალიან დიდია (>50MB)
- Browser-ს აქვს popup blocker
- Network timeout problems

## დამატებითი დახმარება

თუ ვერც ერთი მეთოდი არ მუშაობს:
1. გახსენით browser developer console (F12)
2. სცადეთ download, და console-ში ნახეთ errors
3. Screenshot გაუკეთეთ error message-ს
4. მომწერეთ და დეტალურად ავხსნით

## გაშვება Setup-ის შემდეგ

როცა ყველა ფაილი გექნებათ:

```bash
# 1. Setup გაუშვით
./setup-rnd-monitoring.sh

# 2. დაელოდეთ 30-40 წამი services-ს startup-ს

# 3. გახსენით browser
open http://localhost:5001

# 4. Login გაუკეთეთ
Username: admin
Password: admin123
```

## Service Management

```bash
# View logs
docker-compose logs -f api

# Stop everything
docker-compose down

# Restart
docker-compose restart

# Full reset
docker-compose down -v  # ფრთხილად! წაშლის data-ს
./setup-rnd-monitoring.sh
```

## სტატუსის შემოწმება

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:5001/api/v1/health

# Check logs
docker-compose logs --tail=50 api
```

---

თუ კვლავ გაქვთ პრობლემები, მომწერეთ კონკრეტული error message-ბი და დაგეხმარებით! 🚀
