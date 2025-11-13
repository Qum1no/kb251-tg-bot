import datetime
import os
from zoneinfo import ZoneInfo
import urllib.parse
import urllib.request

# -------- НАСТРОЙКИ --------

# Сколько минут до пары присылать напоминание
AHEAD_MINUTES = 5

# Ключи дней недели (0 = понедельник)
WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# ТВОЕ РАСПИСАНИЕ ДЛЯ КБ-251
# Пример: в понедельник две пары: 08:30 и 10:25
# ВРЕМЯ в формате ЧЧ:ММ по Киеву
SCHEDULE = {
    "mon": [
        ("08:30", "1-я пара: Математика"),
        ("10:25", "2-я пара: Программирование"),
    ],
    "tue": [
        ("09:45", "1-я пара: Физика"),
    ],
    # Заполни остальные дни по своему расписанию
    "wed": [],
    "thu": [],
    "fri": [],
    "sat": [],
    "sun": [],
}

# -------- СЕРВИСНЫЕ ДАННЫЕ --------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str) -> None:
    """Отправка сообщения в Telegram чат."""
    if not TOKEN or not CHAT_ID:
        print("Нет токена или chat_id, проверь переменные окружения.")
        return

    base_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": text,
    }
    url = base_url + "?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as response:
            response.read()
        print("Сообщение отправлено:", text)
    except Exception as e:
        print("Ошибка при отправке сообщения:", e)


def main():
    # Текущее время в UTC
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Переводим в часовой пояс Киева
    kyiv_tz = ZoneInfo("Europe/Kyiv")
    now = now_utc.astimezone(kyiv_tz)

    weekday_index = now.weekday()  # 0 = понедельник, 6 = воскресенье
    weekday_key = WEEKDAY_KEYS[weekday_index]

    today_schedule = SCHEDULE.get(weekday_key, [])

    print("Текущее время (Киев):", now.strftime("%Y-%m-%d %H:%M"))
    print("День недели:", weekday_key)
    print("Пар сегодня:", len(today_schedule))

    for time_str, title in today_schedule:
        hour, minute = map(int, time_str.split(":"))
        lesson_time = now.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        diff_minutes = (lesson_time - now).total_seconds() / 60

        # Если до пары осталось от 0 до AHEAD_MINUTES минут (но не прошло)
        if 0 < diff_minutes <= AHEAD_MINUTES:
            message = f"Скоро начинается пара в {time_str} — {title}"
            send_message(message)


if __name__ == "__main__":
    main()
