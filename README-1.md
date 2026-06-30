# DigiVaani64 Telegram Bot — Setup Guide

Ye guide step-by-step batati hai ki bot ko kaise banaye aur Render pe free mein 24/7 host kare.

---

## STEP 1: Telegram Bot Token Lo

1. Telegram pe **@BotFather** ko search karo, chat open karo
2. `/newbot` bhejo
3. Bot ka display name do: `DigiVaani64 Bot`
4. Bot ka username do (bot se end hona chahiye): `DigiVaani64_bot` (agar liya ho to alag try karo)
5. BotFather token dega jaise: `7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. **Ye token safe rakho — kisi ko mat do**

---

## STEP 2: GitHub Pe Code Upload Karo

1. GitHub pe naya repository banao — naam do `digivaani64-bot`
2. Is folder ki saari files (`bot.py`, `requirements.txt`) usme upload karo
3. **IMPORTANT:** `BOT_TOKEN` ko seedha code mein mat likho — Render pe environment variable se dena hai (Step 4 mein)

---

## STEP 3: Render Account Banao

1. [render.com](https://render.com) pe jaake free account banao (GitHub se sign in kar sakte ho — easy hai)
2. Dashboard pe **"New +"** → **"Web Service"** click karo
3. Apna GitHub repo (`digivaani64-bot`) connect karo aur select karo

---

## STEP 4: Render Settings Configure Karo

Render form mein ye values bharo:

| Field | Value |
|-------|-------|
| **Name** | `digivaani64-bot` (ya kuch bhi) |
| **Region** | Singapore (India ke sabse close) |
| **Branch** | `main` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python bot.py` |
| **Instance Type** | **Free** |

Phir niche **"Environment Variables"** section mein:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | (Tera BotFather wala token paste karo) |

**"Create Web Service"** click karo. 2-3 minute mein deploy ho jayega.

---

## STEP 5: Test Karo

1. Render ke logs mein dekho: `✅ Bot start ho gaya!` message aana chahiye
2. Telegram pe apne bot ko khojo (username se), `/start` bhejo
3. Buttons dikhne chahiye — Services, Skills/Courses, Visit Website

---

## ⚠️ Free Tier Ki Limitation

Render free web services **15 minutes inactivity ke baad "sleep" mode mein chale jaate hain**. Iska matlab:
- Agar koi 15+ min tak message nahi karta, bot so jata hai
- Agla message aane pe bot ko wake hone mein **30-50 second** lag sakte hain (pehla reply slow aayega)
- Uske baad normal speed se chalega jab tak phir se 15 min inactive na ho

**Isse bachne ka free tarika:**
[UptimeRobot](https://uptimerobot.com) (free) use karke har 10 minute mein apne Render URL (jo Render deploy ke baad dega, jaise `https://digivaani64-bot.onrender.com`) ko ping karwa sakte ho — isse bot kabhi sleep nahi karega.

---

## Future Mein Naya Service/Course Add Karna Ho?

`bot.py` file mein `SERVICES` aur `COURSES` list dikhegi upar — wahi pattern follow karke naya item add karo, GitHub pe push karo, Render automatically redeploy kar dega.

---

## Koi Problem Aaye To

- Render ke "Logs" tab mein error dikhega — wahi se pata chalega kya galat hai
- Sabse common issue: `BOT_TOKEN` environment variable sahi se set nahi hua — double check karo
