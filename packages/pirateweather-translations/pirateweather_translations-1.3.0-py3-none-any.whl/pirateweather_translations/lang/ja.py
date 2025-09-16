def join_with_shared_prefix(a, b, joiner):
    i = 0

    # Find the shared prefix length where characters match
    while i != len(a) and i != len(b) and ord(a[i]) == ord(b[i]):  # pragma: no cover
        i += 1

    # Move back to the last space character if needed
    while i > 0 and a[i - 1] != " ":  # pragma: no cover
        i -= 1

    # Return the concatenated result
    return a[:i] + a[i:] + joiner + b[i:]


def and_function(stack, a, b):
    return join_with_shared_prefix(a, b, ",及び" if "," in a else "及び")


def through_function(stack, a, b):
    return join_with_shared_prefix(a, b, "から")


def sentence_function(stack, s):
    if not s.endswith("。"):
        s += "。"
    return s


template = {
    "clear": "晴れ",
    "no-precipitation": "降水なし",
    "mixed-precipitation": "みぞれ",
    "possible-very-light-precipitation": "弱い降水の可能性あり",
    "very-light-precipitation": "弱い降水",
    "possible-light-precipitation": "弱い降水の可能性あり",
    "light-precipitation": "弱い降水",
    "medium-precipitation": "降水",
    "heavy-precipitation": "強い降水",
    "possible-very-light-rain": "霧雨の可能性あり",
    "very-light-rain": "霧雨",
    "possible-light-rain": "小雨の可能性あり",
    "light-rain": "小雨",
    "medium-rain": "雨",
    "heavy-rain": "大雨",
    "possible-very-light-sleet": "弱いみぞれの可能性あり",
    "very-light-sleet": "弱いみぞれ",
    "possible-light-sleet": "弱いみぞれの可能性あり",
    "light-sleet": "弱いみぞれ",
    "medium-sleet": "みぞれ",
    "heavy-sleet": "強いみぞれ",
    "possible-very-light-snow": "にわか雪の可能性あり",
    "very-light-snow": "にわか雪",
    "possible-light-snow": "小雪の可能性あり",
    "light-snow": "小雪",
    "medium-snow": "雪",
    "heavy-snow": "大雪",
    "possible-thunderstorm": "激しい雷雨の可能性あり",
    "thunderstorm": "雷雨",
    "possible-medium-precipitation": "降水の可能性あり",
    "possible-heavy-precipitation": "大降水の可能性あり",
    "possible-medium-rain": "雨の可能性あり",
    "possible-heavy-rain": "大雨の可能性あり",
    "possible-medium-sleet": "みぞれの可能性あり",
    "possible-heavy-sleet": "強いみぞれの可能性あり",
    "possible-medium-snow": "雪の可能性あり",
    "possible-heavy-snow": "大雪の可能性あり",
    "possible-very-light-freezing-rain": "凍りつく霧雨の可能性あり",
    "very-light-freezing-rain": "凍りつく霧雨",
    "possible-light-freezing-rain": "軽い氷雨の可能性あり",
    "light-freezing-rain": "軽い氷雨",
    "possible-medium-freezing-rain": "凍雨の可能性あり",
    "medium-freezing-rain": "凍雨",
    "possible-heavy-freezing-rain": "大凍雨の可能性あり",
    "heavy-freezing-rain": "大凍雨",
    "possible-hail": "雹の可能性あり",
    "hail": "雹",
    "light-wind": "弱い風",
    "medium-wind": "強い風",
    "heavy-wind": "猛烈な風",
    "low-humidity": "乾燥",
    "high-humidity": "多湿",
    "fog": "霧",
    "very-light-clouds": "ほぼ晴れ",
    "light-clouds": "薄曇り",
    "medium-clouds": "曇り",
    "heavy-clouds": "曇り",
    "today-morning": "今朝",
    "later-today-morning": "今日の午前中",
    "today-afternoon": "今日の昼過ぎ",
    "later-today-afternoon": "今日の夕方",
    "today-evening": "今日の夜の初め頃",
    "later-today-evening": "今日の夜遅く",
    "today-night": "今夜",
    "later-today-night": "今夜遅く",
    "tomorrow-morning": "明日の朝",
    "tomorrow-afternoon": "明日の昼過ぎ",
    "tomorrow-evening": "明日の夕方",
    "tomorrow-night": "明日の夜",
    "morning": "朝",
    "afternoon": "昼過ぎ",
    "evening": "夕方",
    "night": "夜",
    "today": "今日",
    "tomorrow": "明日",
    "sunday": "日曜日",
    "monday": "月曜日",
    "tuesday": "火曜日",
    "wednesday": "水曜日",
    "thursday": "木曜日",
    "friday": "金曜日",
    "saturday": "土曜日",
    "next-sunday": "次の日曜日",
    "next-monday": "次の月曜日",
    "next-tuesday": "次の火曜日",
    "next-wednesday": "次の水曜日",
    "next-thursday": "次の木曜日",
    "next-friday": "次の金曜日",
    "next-saturday": "次の土曜日",
    "minutes": "$1分",
    "fahrenheit": "$1\u00b0F",
    "celsius": "$1\u00b0C",
    "inches": "$1インチ",
    "centimeters": "$1センチメートル",
    "less-than": "$1未満",
    "and": and_function,
    "through": through_function,
    "with": "$1$2",
    "range": "$1\u2013$2",
    "parenthetical": "$1 ($2)",
    "for-hour": "一時間$1。",
    "starting-in": "$1が$2に始まる。",
    "stopping-in": "$1が$2に終わる。",
    "starting-then-stopping-later": "$1が$2に始まり、$3後終わる。",
    "stopping-then-starting-later": "$1が$2に終わり、また$3後始まる。",
    "for-day": "一日中$1。",
    "starting": "$2から$1が始まる。",
    "until": "$2まで$1。",
    "until-starting-again": "$2まで$1、$3からまた始まる。",
    "starting-continuing-until": "$1が$2から始まり$3まで続く。",
    "during": "$2にかけて$1。",
    "for-week": "一週間中$1。",
    "over-weekend": "土、日曜日に$1。",
    "temperatures-peaking": "$2は最高気温$1。",
    "temperatures-rising": "気温は$1、$2に上がる",
    "temperatures-valleying": "$2は最低気温$1。",
    "temperatures-falling": "気温は$1、$2に下がる",
    "title": "$1",
    "sentence": sentence_function,
    "next-hour-forecast-status": "次の1時間予報は$2により$1",
    "unavailable": "利用不可",
    "temporarily-unavailable": "一時的に利用できません",
    "partially-unavailable": "一部利用不可",
    "station-offline": "近くのレーダーステーションはすべてオフライン",
    "station-incomplete": "近くのレーダー基地からのカバー範囲のギャップ",
    "smoke": "煙",
    "haze": "もや",
    "mist": "霧",
}
