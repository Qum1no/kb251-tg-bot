import datetime
import os
from zoneinfo import ZoneInfo
import urllib.parse
import urllib.request

# -------- НАСТРОЙКИ --------

# Сколько минут до пары присылать напоминание
AHEAD_MINUTES = 10

# День понедельника НЕПАРНОЙ недели, о которой ты сказал
# (на этой неделе расписание "непарное")
BASE_ODD_MONDAY = datetime.date(2025, 11, 10)

# Ключи дней недели (0 = понедельник)
WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# ВРЕМЕНА НАЧАЛА ПАР (для удобства, но можно и не использовать отдельно)
# Тут просто справочная информация — основное расписание ниже.
TIME_SLOTS = [
    "08:00",
    "09:40",
    "11:25",
    "13:10",
    "14:50",
    "16:25",
]

# -------- РАСПИСАНИЕ ДЛЯ КБ-251 --------
# Чётная неделя = "even" (парний)
# Нечётная неделя = "odd" (непарний)

SCHEDULE = {
    "even": {  # ПАРНАЯ НЕДЕЛЯ
        "mon": [
            ("08:00", "Фізика"),
            ("09:40", "Фізика"),
            ("11:25", "Web-технології"),
            ("13:10", "Web-технології"),
        ],
        "tue": [
            ("09:40", "Фіз-ра"),
            ("11:25", "Інформатика"),
            ("13:10", "Інформатика"),
        ],
        "wed": [
            ("13:10", "Англ. мова / Web-технології"),
            ("14:50", "Вища математика"),
        ],
        "thu": [
            ("09:40", "Фіз-ра"),
            ("11:25", "Вища математика"),
            ("13:10", "Вища математика"),
        ],
        "fri": [
            ("08:00", "Інформаційна безпека держави"),
            ("09:40", "Інформаційна безпека держави"),
            ("11:25", "Архітектура комп'ютерних систем / Інформатика"),
            ("13:10", "Архітектура комп'ютерних систем"),
        ],
        "sat": [],
        "sun": [],
    },
    "odd": {  # НЕПАРНАЯ НЕДЕЛЯ
        "mon": [
            ("11:25", "Web-технології (1)"),
            ("13:10", "Вища математика"),
            ("14:50", "Англ. мова"),
        ],
        "tue": [
            ("08:00", "Інформатика (1) / Архітектура комп'ютерних систем (2)"),
            ("09:40", "Фіз-ра"),
            ("11:25", "Інформатика (2)"),
        ],
        "wed": [
            ("08:00", "Web-технології (2)"),
            ("09:40", "Web-технології (1) / Архітектура комп'ютерних систем (2)"),
            ("11:25", "Фізика (1) / Інформатика (2)"),
            ("13:10", "Інформатика (1)"),
        ],
        "thu": [
            ("08:00", "Архітектура комп'ютерних систем (1)"),
            ("09:40", "Фіз-ра"),
            ("11:25", "Фізика (2)"),
            ("13:10", "Web-технології (2)"),
        ],
        "fri": [
            ("00:41", "Інформаційна безпека держави"),
            ("11:25", "Інформаційна безпека держави"),
            ("13:10", "Вища математика"),
            ("14:50", "Архітектура комп'ютерних систем (1)"),
        ],
        "sat": [],
        "sun": [],
    },
}

# -------- СЕРВИСНЫЕ ДАННЫЕ --------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_week_type(current_date: datetime.date) -> str:
    """
    Возвращает 'odd' или 'even' в зависимости от того,
    непарная или парная неделя относительно BASE_ODD_MONDAY.
    """
    delta_days = (current_date - BASE_ODD_MONDAY).days
    delta_weeks = delta_days // 7

    # если разница по неделям чётная (0, 2, 4...), то та же нечётность, что и у базовой
    if delta_weeks % 2 == 0:
        return "odd"
    else:
        return "even"


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

    # Определяем, неделя парная или непарная
    week_type = get_week_type(now.date())

    today_schedule = SCHEDULE.get(week_type, {}).get(weekday_key, [])

    print("Текущее время (Киев):", now.strftime("%Y-%m-%d %H:%M"))
    print("Тип недели:", week_type)
    print("День недели:", weekday_key)
    print("Пар сегодня:", len(today_schedule))

    for time_str, title in today_schedule:
        hour, minute = map(int, time_str.split(":"))
        lesson_time = now.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        diff_minutes = (lesson_time - now).total_seconds() / 60

        # Если до пары осталось от 0 до AHEAD_MINUTES минут
        if 0 < diff_minutes <= AHEAD_MINUTES:
            message = (
                f"Скоро начинается пара ({week_type} неделя) в {time_str} — {title}"
            )
            send_message(message)


if __name__ == "__main__":
    main()
