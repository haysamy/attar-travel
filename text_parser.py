"""
Enhanced Bilingual (Arabic & English) Text Parser for Travel Packages & Quotations.
Handles Markdown artifacts, multi-flight splits (ذهاب/عودة / Outbound/Return), car rentals, flexible dynamic sections, and automatic date/nights calculations.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def clean_markdown(val: str) -> str:
    """Strips Markdown bold, italics, headers, and bullet marks."""
    if not val:
        return ""
    # Remove markdown bold/italic markers
    s = re.sub(r"[*_~`#]+", " ", val)
    # Remove leading dashes, bullet points
    s = re.sub(r"^[\s\-•–\>]+", "", s)
    return s.strip()


def detect_language(text: str) -> str:
    """Detects whether the input package text is primarily English ('en') or Arabic ('ar')."""
    if not text:
        return "ar"
    # Strip URLs and airport codes before counting
    stripped = re.sub(r"https?://\S+", "", text)
    ar_chars = len(re.findall(r"[\u0600-\u06FF]", stripped))
    en_chars = len(re.findall(r"[A-Za-z]", stripped))
    if ar_chars == 0 and en_chars > 0:
        return "en"
    # Check strong English field indicators
    en_keywords = re.findall(
        r"\b(?:Booking No|Quotation No|Destination|Check-in|Check-out|Room Type|Meal Plan|Outbound Flight|Return Flight|Departure Time|Arrival Time|Pickup Location|Dropoff Location|Total Price|Grand Total)\b",
        stripped,
        re.IGNORECASE
    )
    if len(en_keywords) >= 2 and ar_chars < en_chars:
        return "en"
    if en_chars > ar_chars * 2.5 and ar_chars < 30:
        return "en"
    return "ar"


ARABIC_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "ابريل": 4, "أبريل": 4,
    "مايو": 5, "يونيو": 6, "يوليو": 7, "اغسطس": 8, "أغسطس": 8,
    "سبتمبر": 9, "اكتوبر": 10, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12
}

ENGLISH_MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}


def parse_arabic_time(t_str: str) -> Optional[int]:
    """Converts Arabic or English time string (e.g. '12:30 ظهراً', '3:40 PM') to minutes from midnight."""
    if not t_str:
        return None
    m = re.search(r"(\d{1,2})\s*:\s*(\d{2})", t_str)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    t_lower = t_str.lower()
    is_pm = any(w in t_str for w in ["مساء", "عصر", "ظهر", "م", "ليلا", "ليلاً"]) or bool(re.search(r"\bpm\b|\bp\.m\.", t_lower))
    is_am = any(w in t_str for w in ["صباح", "ص", "فجر", "فجراً"]) or bool(re.search(r"\bam\b|\ba\.m\.", t_lower))
    if is_pm:
        if hour < 12:
            hour += 12
    elif is_am:
        if hour == 12:
            hour = 0
    return hour * 60 + minute


def format_arabic_time(minutes: int, lang: str = "ar") -> str:
    """Formats minutes from midnight into standard Arabic or English time string."""
    minutes = minutes % (24 * 60)
    hour = minutes // 60
    minute = minutes % 60
    if lang == "en":
        period = "AM" if hour < 12 else "PM"
        hr12 = hour % 12
        if hr12 == 0:
            hr12 = 12
        return f"{hr12:02d}:{minute:02d} {period}"
    if hour == 0:
        return f"12:{minute:02d} صباحاً"
    elif hour < 12:
        return f"{hour:02d}:{minute:02d} صباحاً"
    elif hour == 12:
        return f"12:{minute:02d} ظهراً"
    elif hour < 16:
        return f"{hour - 12:02d}:{minute:02d} ظهراً"
    elif hour < 19:
        return f"{hour - 12:02d}:{minute:02d} عصراً"
    else:
        return f"{hour - 12:02d}:{minute:02d} مساءً"


def normalize_12h_time(t_str: Optional[str], lang: str = "ar") -> Optional[str]:
    """Converts any 24-hour time into strict 12-hour Arabic or English time."""
    if not t_str:
        return t_str
    s = clean_markdown(t_str)
    # Remove leading emoji if present
    s = re.sub(r"^[^\w\d\u0600-\u06FF]+", "", s).strip()
    m = re.search(r"\b(\d{1,2})\s*:\s*(\d{2})\b", s)
    if not m:
        return s
    hr = int(m.group(1))
    mn = int(m.group(2))
    paren_m = re.search(r"(\([^)]+\))", s)
    extra = f" {paren_m.group(1)}" if paren_m else ""

    if lang == "en":
        s_lower = s.lower()
        if hr >= 13 or hr == 0:
            period = "AM" if hr == 0 else "PM"
            hr12 = 12 if hr == 0 else (hr - 12 if hr > 12 else hr)
            return f"{hr12:02d}:{mn:02d} {period}{extra}"
        elif re.search(r"\b(?:am|pm|a\.m\.|p\.m\.)\b", s_lower):
            period = "PM" if "p" in s_lower else "AM"
            return f"{hr:02d}:{mn:02d} {period}{extra}"
        elif any(w in s for w in ["مساء", "عصر", "ظهر", "ليلا", "ليلاً"]):
            return f"{hr:02d}:{mn:02d} PM{extra}"
        elif any(w in s for w in ["صباح", "فجر", "فجراً"]):
            return f"{hr:02d}:{mn:02d} AM{extra}"
        return s

    if hr >= 13 or hr == 0:
        period = "صباحاً"
        if hr == 0:
            hr12 = 12
            period = "فجراً"
        elif hr < 16:
            hr12 = hr - 12
            period = "ظهراً"
        elif hr < 19:
            hr12 = hr - 12
            period = "عصراً"
        else:
            hr12 = hr - 12
            period = "مساءً"
        return f"{hr12:02d}:{mn:02d} {period}{extra}"
    return s


def parse_transit_minutes(dur_str: str) -> Optional[int]:
    """Parses transit duration string (e.g. '50 دقيقة', '8 ساعات و30 دقيقة', '2h 30m', '2 hours 30 minutes') to minutes."""
    if not dur_str:
        return None
    total = 0
    hr_m = re.search(r"(\d+)\s*(?:ساعة|ساعات|س|hours?|hrs?|h\b)", dur_str, re.IGNORECASE)
    if hr_m:
        total += int(hr_m.group(1)) * 60
    elif "ساعتين" in dur_str or "ساعتان" in dur_str:
        total += 120
    elif "ساعة" in dur_str or re.search(r"\ban?\s+hour\b", dur_str, re.IGNORECASE):
        total += 60

    min_m = re.search(r"(\d+)\s*(?:دقيقة|دقائق|د|minutes?|mins?|m\b)", dur_str, re.IGNORECASE)
    if min_m:
        total += int(min_m.group(1))
    elif "نصف ساعة" in dur_str or "half an hour" in dur_str.lower():
        total += 30

    return total if total > 0 else None


def parse_date_obj(date_str: str) -> Optional[datetime]:
    """Tries to parse standard Arabic/English date formats, including Arabic & English month names."""
    if not date_str:
        return None
    cleaned = clean_markdown(date_str).strip()
    formats = [
        "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d",
        "%d-%m-%y", "%d.%m.%Y", "%Y.%m.%d",
        "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    # Try matching Arabic month names (e.g. '20 نوفمبر' or '20 نوفمبر 2026')
    for m_name, m_num in ARABIC_MONTHS.items():
        if m_name in cleaned:
            d_m = re.search(r"(\d{1,2})", cleaned)
            y_m = re.search(r"(20\d{2})", cleaned)
            day = int(d_m.group(1)) if d_m else 1
            year = int(y_m.group(1)) if y_m else datetime.now().year
            try:
                return datetime(year, m_num, day)
            except ValueError:
                pass

    # Try matching English month names (e.g. '20 November' or 'Nov 20, 2026')
    cleaned_lower = cleaned.lower()
    for m_name, m_num in ENGLISH_MONTHS.items():
        if re.search(rf"\b{m_name}\b", cleaned_lower):
            y_m = re.search(r"(20\d{2})", cleaned)
            cleaned_no_year = re.sub(r"20\d{2}", "", cleaned)
            d_m = re.search(r"(\d{1,2})", cleaned_no_year)
            day = int(d_m.group(1)) if d_m else 1
            year = int(y_m.group(1)) if y_m else datetime.now().year
            try:
                return datetime(year, m_num, day)
            except ValueError:
                pass
    return None


def generate_smart_notes(data: Dict[str, Any], lang: str = "ar") -> List[str]:
    notes = []
    has_flights = bool(data.get("flights"))
    has_cars = bool(data.get("car_rentals"))
    has_hotels = bool(data.get("hotels"))
    has_transports = bool(data.get("transports"))

    if lang == "en":
        if has_flights:
            notes.append("Flight tickets (domestic and international) are non-refundable and non-changeable after issuance; any permitted modifications are subject to airline fees and fare differences.")
            notes.append("Baggage allowance is strictly as specified in the flight schedule; any excess weight or extra pieces are payable directly to the airline at the airport.")
            notes.append("Passengers must arrive at the airport at least 2 hours before domestic flights and 3 hours before international flights, ensuring passport validity (minimum 6 months) and required visas.")
        if has_cars:
            notes.append("Car rental requires presenting a valid original national driving license, an International Driving Permit (IDP), original passport, and a physical Credit Card in the main driver's name for the refundable security deposit.")
            notes.append("Minimum driver age is 21 years. Comprehensive insurance requires an immediate official police report in the event of any accident.")
            notes.append("The vehicle is delivered with a specific fuel level and must be returned with the same level. Any traffic fines or toll charges are the sole responsibility of the renter.")
        if has_hotels:
            notes.append("Standard hotel check-in starts at 14:00 (2:00 PM) and check-out is up to 12:00 PM (noon). Early check-in or late check-out is subject to availability and hotel charges.")
            notes.append("Standard rooms accommodate 2 adults. Extra beds for children or adults are subject to hotel policy and additional charges.")
            notes.append("Some hotels may require a credit card or refundable cash deposit upon check-in to cover incidental expenses.")
            notes.append("City Tax / Tourist Tax in certain destinations is payable directly by the guest to the hotel upon check-in or check-out according to local regulations.")
            notes.append("Hotel cancellation or modification is subject to the hotel's seasonal terms and cancellation policy.")
        if has_transports:
            if has_cars:
                notes.append("The mentioned activities and attractions are suggested itineraries designed for your self-drive convenience; entrance tickets to attractions are not included.")
            else:
                notes.append("Daily private tour duration is up to 8 hours maximum with a private driver within the city limits, including vehicle and fuel but excluding attraction entrance tickets (itineraries are flexible within the city scope).")
                notes.append("Vehicle size is selected based on the number of passengers specified in the quotation; any increase in passengers or luggage requires a vehicle upgrade at an additional cost.")
        notes.append("Quoted prices are preliminary and subject to availability until payment is completed and bookings are officially issued.")
        return notes

    # 1. Flights
    if has_flights:
        notes.append("تذاكر الطيران (الداخلي والدولي) غير قابلة للاسترجاع أو تغيير الأسماء بعد الإصدار، وتخضع التعديلات لرسوم وغرامات شركة الطيران المعنية.")
        notes.append("الوزن المسموح به هو الموضح في جدول الرحلات، وأي أوزان أو حقائب إضافية يسددها المسافر مباشرة لشركة الطيران بالمطار.")
        notes.append("يلزم التواجد في المطار قبل موعد الرحلات الداخلية بساعتين وقبل الدولية بـ 3 ساعات، مع التأكد من سريان الجواز (6 أشهر على الأقل) والتأشيرات المطلوبة.")

    # 2. Car Rentals
    if has_cars:
        notes.append("استئجار السيارة يتطلب إلزامياً إبراز أصل رخصة القيادة المحلية سارية المفعول + رخصة القيادة الدولية المعتمدة (International Driving Permit) وأصل جواز السفر وبطاقة ائتمانية (Credit Card باسم السائق حصراً) لحجز مبلغ التأمين المسترد.")
        notes.append("الحد الأدنى لعمر السائق 21 سنة. التأمين شامل ويُشترط لتفعيله عند وقوع أي حادث (لا قدر الله) إحضار تقرير شرطة رسمي فوري وضبط الحادث.")
        notes.append("تُسلّم السيارة بمستوى وقود محدد وتُعاد بنفس المستوى، وأي مخالفات مرورية أو رسوم بوابات تقع على عاتق المستأجر بالكامل.")

    # 3. Hotels
    if has_hotels:
        notes.append("تسجيل الدخول المعتاد للفنادق يبدأ الساعة 14:00 (2:00 ظهراً) وتسجيل المغادرة حتى الساعة 12:00 ظهراً، والدخول المبكر أو الخروج المتأخر يخضع لتوفر الغرف ورسوم الفندق.")
        notes.append("الغرف القياسية مخصصة لـ (2 بالغين)، وطلب سرير إضافي للأطفال أو البالغين يخضع لسياسة الفندق وبرسوم إضافية.")
        notes.append("قد تشترط بعض الفنادق بطاقة ائتمانية أو مبلغ تأمين نقدي مسترد عند تسجيل الدخول لضمان الخدمات الإضافية الخاصة بالنزيل.")
        notes.append("ضريبة المدينة أو ضريبة السياحة البلدية (City Tax / Tourist Tax) في بعض الوجهات تسدد مباشرة من قبل النزيل للفندق عند تسجيل الدخول أو المغادرة بحسب القوانين المحلية.")
        notes.append("الإلغاء أو التعديل الفندقي يخضع لسياسة وشروط الفندق في مواسم الحجز.")

    # 4. Transports / Tours
    if has_transports:
        if has_cars:
            notes.append("الأنشطة والمعالم المذكورة هي مسارات مقترحة تم تصميمها لتناسب تنقلاتكم بحرية بالسيارة المستأجرة، ولا يشمل العرض تذاكر دخول المعالم.")
        else:
            notes.append("مدة الجولة السياحية اليومية 8 ساعات كحد أقصى مع سائق خاص داخل نطاق المدينة، وتشمل الوقود والسيارة دون تذاكر المزارات السياحية (الجولات والأنشطة اختيارية ومتاحة للتعديل أو التغيير ضمن نطاق المدينة حسب رغبتكم).")
            notes.append("تم تحديد حجم السيارة بناءً على عدد الأشخاص الموضح بالعرض؛ وأي زيادة في عدد الركاب أو الأمتعة تتطلب ترقية السيارة مع تحمل فارق التكلفة.")

    # 5. General & Pricing confirmation
    notes.append("الأسعار المعروضة مبدئية وخاضعة للإتاحة حتى سداد الدفعة وتأكيد إصدار الحجوزات الفعلي.")

    return notes


def parse_travel_text(text: str, lang: Optional[str] = None) -> Dict[str, Any]:
    lines = [clean_markdown(line) for line in text.splitlines() if line.strip()]
    full_text = "\n".join(lines)

    detected_lang = lang if lang in ("ar", "en") else detect_language(full_text)
    is_en = (detected_lang == "en")

    ar_months_num = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    en_months_num = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    now_dt = datetime.now()
    today_str = (
        f"{now_dt.day} {en_months_num[now_dt.month]} {now_dt.year}"
        if is_en
        else f"{now_dt.day} {ar_months_num[now_dt.month]} {now_dt.year}"
    )

    data: Dict[str, Any] = {
        "meta": {
            "lang": detected_lang,
            "company_name": "Attar Travel" if is_en else "عطار للسياحة",
            "company_name_en": "Attar Travel",
            "tagline": "Attar Travel" if is_en else "عطار ترافل",
            "booking_no": "TAJ" + now_dt.strftime("%y%m%d%H"),
            "quotation_no": "QTAJ" + now_dt.strftime("%y%m%d%H"),
            "destination": "Travel Package" if is_en else "رحلة سياحية",
            "total_nights": None,
            "issue_date": today_str,
            "booking_status": "Preliminary Unconfirmed Booking" if is_en else "حجز مبدئي غير مؤكد"
        },
        "hotels": [],
        "flights": [],
        "transports": [],
        "car_rentals": [],
        "extra_services": [],
        "total_price": None,
        "notes": []
    }

    # 1. Parse Meta Information
    comp_m = re.search(r"(?:اسم الشركة|Company Name|Company)\s*:\s*([^\n\r]+)", full_text, re.IGNORECASE)
    if comp_m:
        c_name = clean_markdown(comp_m.group(1))
        data["meta"]["company_name"] = c_name
        if is_en:
            data["meta"]["company_name_en"] = c_name
            data["meta"]["tagline"] = c_name
        else:
            data["meta"]["tagline"] = c_name.replace("للسياحة", "ترافل")

    book_m = re.search(r"(?:رقم الحجز|Booking No\.?|Booking Number|Booking Ref|Booking ID)\s*:\s*([A-Za-z0-9_-]+)", full_text, re.IGNORECASE)
    if book_m:
        data["meta"]["booking_no"] = book_m.group(1).strip()

    quot_m = re.search(r"(?:رقم عرض السعر|Quotation No\.?|Quotation Number|Quote No\.?|Quote ID)\s*:\s*([A-Za-z0-9_-]+)", full_text, re.IGNORECASE)
    if quot_m:
        data["meta"]["quotation_no"] = quot_m.group(1).strip()

    dest_m = re.search(r"(?:الوجهة|Destination)\s*:\s*([^\n\r\(\–\-]+)(?:[\(\–\-]\s*(\d+)\s*(?:ليلة|ليالي|ايام|أيام|يوم|Nights?|Days?))?", full_text, re.IGNORECASE)
    if dest_m:
        data["meta"]["destination"] = clean_markdown(dest_m.group(1)).strip()
        if dest_m.group(2):
            data["meta"]["total_nights"] = int(dest_m.group(2))

    issue_m = re.search(r"(?:تاريخ الإصدار|Issue Date|Date of Issue)\s*:\s*([^\n\r]+)", full_text, re.IGNORECASE)
    if issue_m:
        data["meta"]["issue_date"] = clean_markdown(issue_m.group(1)).strip()

    status_m = re.search(r"(?:حالة الحجز|الحالة|Booking Status|Status)\s*:\s*([^\n\r]+)", full_text, re.IGNORECASE)
    if status_m:
        data["meta"]["booking_status"] = clean_markdown(status_m.group(1)).strip()

    # 2. Section Extraction Patterns (Anchored to header lines to prevent false matches inside sentences/notes)
    hdr_prefix = r"^[ \t#*•\-–🌟✈️🏨🚘🚗🚆🎁💰📌📋]*(?:(?:\d+|[١-٩]+)[\.\-\)\s]+|(?:أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً)\s*[:\-]?\s*)?"
    hdr_suffix = r"(?:\s*\([^)\n\r]*\))?[ \t\*:：]*$"
    section_patterns = [
        ("hotels", hdr_prefix + r"(?:حجز الفنادق|الفنادق|فنادق|Hotel Booking|Hotels & Accommodation|Accommodation|Hotels)" + hdr_suffix),
        ("flights", hdr_prefix + r"(?:حجز الطيران|الطيران الداخلي|الطيران الدولي|الطيران|Flight Booking|Flight Details|International Flights|Domestic Flights|Flights|رحلة الذهاب|رحلة المغادرة|Outbound Flight|Departure Flight)" + hdr_suffix),
        ("transports", hdr_prefix + r"(?:الأنشطة والمسارات السياحية المقترحة|الأنشطة والمسارات السياحية|الأنشطة والمسارات|المسارات السياحية المقترحة|المسارات السياحية|المسارات المقترحة|المواصلات والجولات السياحية|المواصلات والقطارات السياحية|حجز القطارات والتنقلات السياحية|المواصلات والجولات|المواصلات والقطارات|المواصلات|الجولات السياحية|الجولات|Transfers & Sightseeing Tours|Suggested Self-Drive Sightseeing Routes|Transfers & Express Trains|Transfers & Tours|Tours & Transfers|Transportation & Tours|Daily Itinerary|Suggested Itinerary|Itinerary & Tours|Transportation|Transfers|Tours|Itinerary)" + hdr_suffix),
        ("car_rentals", hdr_prefix + r"(?:استئجار السيارات الخاصة|استئجار السيارات|استئجار سيارة|تأجير سيارة|تأجير السيارات|إيجار سيارات|إيجار السيارات|Car Rental|Private Car Rental|Car Hire|Vehicle Rental|Rent a Car)" + hdr_suffix),
        ("extra_services", hdr_prefix + r"(?:خدمات وهدايا مشمولة|الخدمات والهدايا المشمولة|خدمات وهدايا|خدمات أخرى مجانية|خدمات أخرى|خدمات مجانية|خدمات إضافية|Free Services|Extra Services|Included Services|Complimentary Services|Additional Services|Gifts & Services)" + hdr_suffix),
        ("total_price", hdr_prefix + r"(?:السعر الإجمالي|الإجمالي كلياً|الاجمالي كليا|Total Price|Grand Total|Total Package Price|Total Amount|Total Cost|💰\s*(?:السعر|Price|Total)|(?:السعر|Price)\s*:)"),
        ("notes", hdr_prefix + r"(?:ملاحظات مهمة جداً|ملاحظات مهمة|الشروط والملاحظات المهمة|الشروط والأحكام|شروط الحجز|Important Notes|Terms & Conditions|Terms and Conditions|Booking Terms|Notes & Conditions|Notes)" + hdr_suffix)
    ]

    sec_indices = []
    for sec_id, pattern in section_patterns:
        m = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        if m:
            sec_indices.append((m.start(), sec_id))
    sec_indices.sort()

    sections_text = {}
    for i in range(len(sec_indices)):
        start_pos, sec_id = sec_indices[i]
        end_pos = sec_indices[i + 1][0] if i + 1 < len(sec_indices) else len(full_text)
        sections_text[sec_id] = full_text[start_pos:end_pos]

    # --- 2.1 Parse Hotels ---
    if "hotels" in sections_text:
        htl_text = sections_text["hotels"]
        # Split by city header or hotel header or day range header (Arabic & English)
        split_pat = r'(?im)(?=(?:^[ \t]*(?:المدينة\s+[^\n:]+|City\s+\d+|(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|1st|2nd|3rd|\d+(?:th)?)\s+City)\s*:|^[ \t]*(?:فندق|Hotel)\s+\d+\s*:|^[ \t]*[^\n\r:]{2,35}\s*\((?:\d+\s*(?:ليلة|ليالي|ليالٍ|ليال|ايام|أيام|Nights?|Days?)|ليلتين|ليلة واحدة)\)))'
        hotel_blocks = [b for b in re.split(split_pat, htl_text) if re.search(r"(?:الفندق|فندق|Hotel|Resort)", b, re.IGNORECASE)]
        if not hotel_blocks and re.search(r"(?:الفندق|فندق|Hotel|Resort)", htl_text, re.IGNORECASE):
            hotel_blocks = re.split(r"(?i)(?=\b(?:الفندق|Hotel|Resort)\s*:)", htl_text)

        arabic_ordinals = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة"]
        english_ordinals = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth"]

        for h_idx, blk in enumerate(hotel_blocks):
            if not re.search(r"(?:الفندق|فندق|Hotel|Resort)", blk, re.IGNORECASE):
                continue

            if is_en:
                default_ord = f"{english_ordinals[h_idx]} City" if h_idx < len(english_ordinals) else f"Station {h_idx+1}"
                city_order = default_ord
            else:
                default_ord = arabic_ordinals[h_idx] if h_idx < len(arabic_ordinals) else f"المحطة {h_idx+1}"
                city_order = f"المدينة {default_ord}"
            city_name = data["meta"]["destination"]
            nights_count = None

            # 1a. Arabic: المدينة الأولى: بانكوك (3 ليالي)
            alt_city_ar = re.search(r"المدينة\s+([^:\(\n]+):\s*([^\(\n\r]+)(?:[\(\-–]\s*(\d+|ليلتين|ليلة واحدة)\s*(?:ليلة|ليالي|ليالٍ|ليال)?)?", blk)
            # 1b. English: First City: Bangkok (2 Nights) or City 1: Bangkok (2 Nights)
            alt_city_en = re.search(r"(?:((?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|1st|2nd|3rd|\d+(?:th)?)\s+City|City\s+\d+))\s*:\s*([^\(\n\r]+)(?:[\(\-–]\s*(\d+)\s*(?:Nights?|Days?)?)?", blk, re.IGNORECASE)

            if alt_city_ar:
                city_order = f"المدينة {clean_markdown(alt_city_ar.group(1)).strip()}"
                city_name = clean_markdown(alt_city_ar.group(2)).strip()
                raw_n = alt_city_ar.group(3)
                if raw_n == "ليلتين":
                    nights_count = 2
                elif raw_n == "ليلة واحدة":
                    nights_count = 1
                elif raw_n and raw_n.isdigit():
                    nights_count = int(raw_n)
            elif alt_city_en:
                city_order = clean_markdown(alt_city_en.group(1)).strip()
                city_name = clean_markdown(alt_city_en.group(2)).strip()
                raw_n = alt_city_en.group(3)
                if raw_n and raw_n.isdigit():
                    nights_count = int(raw_n)
            else:
                # 2. بانكوك (3 ليالي) or Bangkok (3 Nights)
                city_line_m = re.search(r"^[ \t]*([^\n\r:\(\d]{2,35}?)\s*\((?:(\d+)\s*(?:ليلة|ليالي|ليالٍ|ليال|ايام|أيام|Nights?|Days?)|(ليلتين)|(ليلة واحدة))\)", blk, re.MULTILINE | re.IGNORECASE)
                if city_line_m:
                    city_name = clean_markdown(city_line_m.group(1)).strip()
                    if city_line_m.group(2):
                        nights_count = int(city_line_m.group(2))
                    elif city_line_m.group(3):
                        nights_count = 2
                    elif city_line_m.group(4):
                        nights_count = 1
                else:
                    city_explicit_m = re.search(r"(?:المدينة|City)\s*:\s*([^\(\n\r]+)", blk, re.IGNORECASE)
                    if city_explicit_m:
                        city_name = clean_markdown(city_explicit_m.group(1)).strip()

            nights_explicit_m = re.search(r"(?:عدد الليالي|الليالي|Nights|Number of Nights)\s*:\s*(\d+)", blk, re.IGNORECASE)
            if nights_explicit_m:
                nights_count = int(nights_explicit_m.group(1))

            checkin_m = re.search(r"(?:تاريخ الدخول|الدخول|Check-?in Date|Check-?in)\s*:\s*([0-9\-\/]+)", blk, re.IGNORECASE)
            checkout_m = re.search(r"(?:تاريخ الخروج|الخروج|Check-?out Date|Check-?out)\s*:\s*([0-9\-\/]+)", blk, re.IGNORECASE)
            check_in = clean_markdown(checkin_m.group(1)) if checkin_m else "2026-11-24"
            check_out = clean_markdown(checkout_m.group(1)) if checkout_m else "2026-11-25"

            if not nights_count:
                d_in = parse_date_obj(check_in)
                d_out = parse_date_obj(check_out)
                if d_in and d_out and d_out > d_in:
                    nights_count = (d_out - d_in).days
                else:
                    nights_count = 1

            day_range_m = re.search(r"((?:اليوم|Day)\s+[^\n\-–]+?)\s*(?:[\-–]|to)\s*((?:اليوم|Day)\s+[^\n\r]+)", blk, re.IGNORECASE)
            if day_range_m:
                day_range = f"{day_range_m.group(1).strip()}<br>{day_range_m.group(2).strip()}"
            else:
                day_range = f"Duration: {nights_count} Nights" if is_en else f"المدة: {nights_count} ليالي"

            hotel_name_m = re.search(r"(?:الفندق|اسم الفندق|Hotel Name|Hotel|Resort)\s*:\s*([^\n\r]+)", blk, re.IGNORECASE)
            hotel_name = clean_markdown(hotel_name_m.group(1)) if hotel_name_m else ("Luxury Hotel" if is_en else "فندق فاخر")

            room_type = "Standard Room" if is_en else "غرفة قياسية"
            rooms_count = 1
            room_m = re.search(r"(?:نوع الغرفة|الغرفة|Room Type|Room)\s*:\s*([^\|\n\r]+)(?:\|\s*(?:العدد|عدد الغرف|Rooms|Count|Qty|Quantity)\s*:\s*(\d+))?", blk, re.IGNORECASE)
            if room_m:
                room_type = clean_markdown(room_m.group(1))
                if room_m.group(2):
                    try:
                        rooms_count = int(room_m.group(2))
                    except ValueError:
                        pass
            rooms_explicit_m = re.search(r"(?:عدد الغرف|Rooms Count|Number of Rooms|Rooms)\s*:\s*(\d+)", blk, re.IGNORECASE)
            if rooms_explicit_m:
                rooms_count = int(rooms_explicit_m.group(1))

            meal_plan = "Breakfast Included" if is_en else "شامل الإفطار"
            meal_m = re.search(r"(?:الوجبة|الوجبات|نظام الوجبات|Meal Plan|Meals|Board)\s*:\s*([^\n\r]+)", blk, re.IGNORECASE)
            if meal_m:
                meal_plan = clean_markdown(meal_m.group(1))

            details_url = "#"
            url_m = re.search(r"(?:رابط بوكينج|رابط بوكنج|رابط الفندق|رابط التفاصيل|لينك بوكينج|لينك الفندق|رابط|الرابط|Booking|Hotel Link|Link|URL)\s*:\s*(https?://[^\s\n\r\)]+)", blk, re.IGNORECASE)
            if url_m:
                details_url = url_m.group(1).strip()
            else:
                raw_url_m = re.search(r"(https?://(?:www\.)?booking\.com/[^\s\n\r\)]+)", blk, re.IGNORECASE)
                if raw_url_m:
                    details_url = raw_url_m.group(1).strip()
                else:
                    gen_url_m = re.search(r"(https?://[^\s\n\r\)]+)", blk)
                    if gen_url_m:
                        details_url = gen_url_m.group(1).strip()

            data["hotels"].append({
                "day_range": day_range,
                "city_order": city_order,
                "city_name": city_name,
                "nights_count": nights_count,
                "hotel_name": hotel_name,
                "details_url": details_url,
                "room_type": room_type,
                "rooms_count": rooms_count,
                "meal_plan": meal_plan,
                "check_in": check_in,
                "check_out": check_out
            })

    # --- 2.2 Parse Flights (Supports Arabic & English Outbound, Return, Domestic, Connecting, Transit, etc.) ---
    if "flights" in sections_text:
        flt_text = sections_text["flights"]

        # Check for section-wide luggage note at the end
        section_luggage_match = re.findall(r"(?:الأمتعة|الوزن المسموح به|الوزن المسموح|الوزن|Baggage Allowance|Baggage|Luggage|Weight)\s*:\s*([^\n\r]+)", flt_text, re.IGNORECASE)
        global_luggage = clean_markdown(section_luggage_match[-1]) if section_luggage_match else ("20 kg" if is_en else "20 كيلو")

        # Split by flight boundaries including connecting/transit legs (Arabic & English)
        flight_blocks = re.split(
            r"(?im)(?=^[ \t]*(?:(?:ال)?رحلة\s*(?:الذهاب|ذهاب|العودة|عودة|مغادرة|وصول|داخلية|داخلي|دولية|دولي|متابعة|تكميلية|ترانزيت|ربط|\d+|الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|الأول|الثاني)|الطيران\s*(?:الداخلي|الدولي)|(?:Outbound|Inbound|Departure|Return|Domestic|Internal|International|Connecting|Transit)\s+Flight|Flight\s*\d+))",
            flt_text
        )

        # Fallback if no explicit split keyword was found but multiple flights exist
        date_count = len(re.findall(r"(?:التاريخ|تاريخ السفر|Date|Travel Date|Flight Date)\s*:", flt_text, re.IGNORECASE))
        if len([b for b in flight_blocks if re.search(r"(?:من|From|Origin|التاريخ|تاريخ السفر|Date)\s*:", b, re.IGNORECASE)]) <= 1 and date_count > 1:
            flight_blocks = re.split(r"(?i)(?=\b(?:التاريخ|تاريخ السفر|Date|Travel Date|Flight Date)\s*:)", flt_text)

        raw_flights = []

        for fblk in flight_blocks:
            has_from_to = bool(re.search(r"(?:من|إلى|الى|From|To|Origin|Destination)\s*:", fblk, re.IGNORECASE)) or any(k in fblk for k in ["💨", "✈️", "->"])
            if not has_from_to:
                continue

            label_m = re.search(r"^(?:(?:ال)?رحلة\s*[^\n\r:]+|طيران\s*[^\n\r:]+|(?:Outbound|Inbound|Departure|Return|Domestic|Internal|International|Connecting|Transit)\s+Flight[^\n\r:]*|Flight\s*\d+[^\n\r:]*)", fblk.strip(), re.IGNORECASE)
            label = clean_markdown(label_m.group(0)) if label_m else ""

            date_m = re.search(r"(?:التاريخ|تاريخ السفر|تاريخ الرحلة|Flight Date|Travel Date|Date)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            date_str = clean_markdown(date_m.group(1)) if date_m else "2026-11-20"

            from_m = re.search(r"(?:من|مطار الإقلاع|From|Origin|Departure Airport)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            to_m = re.search(r"(?:إلى|الى|مطار الوصول|To|Destination|Arrival Airport)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            from_ap = clean_markdown(from_m.group(1)) if from_m else None
            to_ap = clean_markdown(to_m.group(1)) if to_m else None

            if not from_ap or not to_ap:
                route_emoji_m = re.search(r"(?:🚦\s*)?([\u0600-\u06FFA-Za-z\s]{2,25}?)\s*(?:💨|✈️|->|←|إلى|\bto\b)\s*([\u0600-\u06FFA-Za-z\s]{2,25}?)(?:\s*🚦|$)", fblk, re.MULTILINE | re.IGNORECASE)
                if route_emoji_m:
                    from_ap = from_ap or clean_markdown(route_emoji_m.group(1)).strip()
                    to_ap = to_ap or clean_markdown(route_emoji_m.group(2)).strip()

            from_ap = from_ap or ("Airport" if is_en else "المطار")
            to_ap = to_ap or ("Airport" if is_en else "المطار")

            airline_m = re.search(r"(?:شركة الطيران|الناقل الجوي|Airline|Carrier|Airways)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            airline = clean_markdown(airline_m.group(1)) if airline_m else None

            adults, children, infants = 2, 0, 0
            pax_ar_m = re.search(r"بالغين\s*:\s*(\d+)(?:.*?الأطفال\s*:\s*(\d+))?(?:.*?الرضع\s*:\s*(\d+))?", fblk)
            pax_en_m = re.search(r"Adults?\s*:\s*(\d+)(?:.*?Child(?:ren)?\s*:\s*(\d+))?(?:.*?Infants?\s*:\s*(\d+))?", fblk, re.IGNORECASE)
            pax_en_alt = re.search(r"(\d+)\s*Adults?(?:[,|\s]+(\d+)\s*Child(?:ren)?)?(?:[,|\s]+(\d+)\s*Infants?)?", fblk, re.IGNORECASE)
            if pax_ar_m:
                adults = int(pax_ar_m.group(1)) if pax_ar_m.group(1) else 2
                children = int(pax_ar_m.group(2)) if pax_ar_m.group(2) else 0
                infants = int(pax_ar_m.group(3)) if pax_ar_m.group(3) else 0
            elif pax_en_m:
                adults = int(pax_en_m.group(1)) if pax_en_m.group(1) else 2
                children = int(pax_en_m.group(2)) if pax_en_m.group(2) else 0
                infants = int(pax_en_m.group(3)) if pax_en_m.group(3) else 0
            elif pax_en_alt:
                adults = int(pax_en_alt.group(1)) if pax_en_alt.group(1) else 2
                children = int(pax_en_alt.group(2)) if pax_en_alt.group(2) else 0
                infants = int(pax_en_alt.group(3)) if pax_en_alt.group(3) else 0

            luggage_m = re.search(r"(?:الأمتعة|الوزن المسموح به|الوزن المسموح|الوزن|الحقائب|Baggage Allowance|Baggage|Luggage|Weight)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            luggage = clean_markdown(luggage_m.group(1)) if luggage_m else global_luggage

            time_m = re.search(r"(?:وقت الإقلاع|وقت الاقلاع|إقلاع الرحلة الساعة|اقلاع الرحلة الساعة|الإقلاع|الاقلاع|الوقت|الساعة|Departure Time|Departure|Departs)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            departure_time = normalize_12h_time(time_m.group(1), lang=detected_lang) if time_m else ("10:30 AM" if is_en else "10:30 صباحاً")

            arr_m = re.search(r"(?:وقت الوصول|وقت وصول|الوصول(?:\s+إلى\s+[^\n\r:]+)?(?:\s+الساعة)?|Arrival Time|Arrival|Arrives)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            arrival_time = normalize_12h_time(arr_m.group(1), lang=detected_lang) if arr_m else None

            tr_ap_m = re.search(r"(?:مطار الترانزيت|محطة الترانزيت|ترانزيت في|التوقف في|مطار التوقف|Transit Airport|Stopover Airport|Layover Airport|Transit in|Stopover in|Layover in)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            transit_ap_single = clean_markdown(tr_ap_m.group(1)) if tr_ap_m else None

            tr_m = re.search(r"(?:مدة الترانزيت|الترانزيت|مدة التوقف|التوقف|Transit Duration|Layover Duration|Stopover Duration|Transit|Layover|Stopover)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            transit_dur = clean_markdown(tr_m.group(1)) if tr_m else None
            if transit_dur and not transit_ap_single and any(k in transit_dur.lower() for k in ["مطار", "الدوحة", "اسطنبول", "إسطنبول", "دبي", "أبوظبي", "القاهرة", "فرانكفورت", "airport", "doha", "istanbul", "dubai", "abu dhabi", "cairo", "frankfurt"]):
                paren_m = re.search(r"([^\(\|\-]+?)\s*[\(\|\-]\s*([^\)\n\r]+)\)?", transit_dur)
                if paren_m:
                    transit_ap_single = paren_m.group(1).strip()
                    transit_dur = paren_m.group(2).strip()

            type_m = re.search(r"(?:نوع الرحلة|نوع الطيران|التصنيف|Flight Type|Category|Cabin Class|Class)\s*:\s*([^\n\r]+)", fblk, re.IGNORECASE)
            flight_type = None
            fblk_no_airports = re.sub(r"(?:من|إلى|الى|From|To|Origin|Destination)\s*:[^\n\r]+", "", fblk, flags=re.IGNORECASE)
            label_lower = label.lower()
            if type_m:
                flight_type = clean_markdown(type_m.group(1)).strip()
            elif re.search(r"(?:طيران\s*داخلي|رحلة\s*داخلية|\bداخلي\b|internal|domestic)", fblk_no_airports, re.IGNORECASE) or any(k in label_lower for k in ["داخلية", "داخلي", "domestic", "internal"]):
                flight_type = "Domestic Flight" if is_en else "طيران داخلي"
            elif re.search(r"(?:طيران\s*دولي|رحلة\s*دولية|\bدولي\b|international)", fblk_no_airports, re.IGNORECASE) or any(k in label_lower for k in ["دولية", "دولي", "الذهاب", "العودة", "outbound", "return", "inbound", "departure", "international"]):
                flight_type = "International Flight" if is_en else "طيران دولي"
            elif "الطيران الداخلي" in flt_text[:120] or "طيران داخلي" in flt_text[:120] or "internal" in flt_text[:120].lower() or "domestic" in flt_text[:120].lower():
                flight_type = "Domestic Flight" if is_en else "طيران داخلي"
            elif "الطيران الدولي" in flt_text[:120] or "طيران دولي" in flt_text[:120] or "international" in flt_text[:120].lower():
                flight_type = "International Flight" if is_en else "طيران دولي"

            raw_flights.append({
                "label": label,
                "date": date_str,
                "from_airport": from_ap,
                "to_airport": to_ap,
                "airline": airline,
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants": infants
                },
                "luggage": luggage,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "transit_airport": transit_ap_single,
                "transit_duration": transit_dur,
                "flight_type": flight_type
            })

        # Smart Grouping of Multi-Leg / Connecting Flights
        grouped_flights = []
        i = 0
        separate_journey_keywords = [
            "داخلية", "داخلي", "العودة", "عودة", "الذهاب", "ذهاب",
            "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
            "domestic", "internal", "return", "inbound", "outbound", "departure"
        ]
        while i < len(raw_flights):
            curr = raw_flights[i]
            connecting_legs = []
            j = i + 1
            while j < len(raw_flights):
                nxt = raw_flights[j]
                nxt_label = nxt.get("label", "").lower()
                explicit_transit = any(kw in nxt_label for kw in ["متابعة", "ترانزيت", "ربط", "تكميلية", "connecting", "transit"])
                explicit_separate = any(kw in nxt_label for kw in separate_journey_keywords) and not explicit_transit

                if explicit_separate:
                    break

                d_curr = parse_date_obj(curr.get("date", ""))
                d_nxt = parse_date_obj(nxt.get("date", ""))
                within_one_day = (not d_curr or not d_nxt or abs((d_nxt - d_curr).days) <= 1)
                not_round_trip = (curr.get("from_airport") != nxt.get("to_airport"))

                is_connecting = (
                    explicit_transit or
                    (not nxt_label and within_one_day and not_round_trip and nxt.get("from_airport") and curr.get("to_airport") and nxt["from_airport"] in curr["to_airport"])
                )
                if is_connecting:
                    connecting_legs.append(nxt)
                    j += 1
                else:
                    break

            if connecting_legs:
                first_leg = curr
                last_leg = connecting_legs[-1]
                transit_ap = first_leg["to_airport"]
                transit_dur = connecting_legs[0].get("transit_duration") or first_leg.get("transit_duration")

                first_arr = first_leg.get("arrival_time")
                if not first_arr and transit_dur and connecting_legs[0].get("departure_time"):
                    t_dept = parse_arabic_time(connecting_legs[0]["departure_time"])
                    d_dur = parse_transit_minutes(transit_dur)
                    if t_dept is not None and d_dur is not None:
                        t_first_dept = parse_arabic_time(first_leg.get("departure_time", ""))
                        if t_first_dept is not None and t_dept < t_first_dept:
                            t_dept += 1440
                        arr_mins = t_dept - d_dur
                        first_arr = format_arabic_time(arr_mins, lang=detected_lang)
                elif first_arr and not transit_dur and connecting_legs[0].get("departure_time"):
                    t_arr = parse_arabic_time(first_arr)
                    t_next_dept = parse_arabic_time(connecting_legs[0]["departure_time"])
                    if t_arr is not None and t_next_dept is not None:
                        diff_m = t_next_dept - t_arr
                        if diff_m < 0:
                            diff_m += 1440
                        if 0 < diff_m <= 1440:
                            h_tr, m_tr = divmod(diff_m, 60)
                            if is_en:
                                transit_dur = f"{h_tr}h {m_tr}m" if h_tr and m_tr else (f"{h_tr}h" if h_tr else f"{m_tr}m")
                            else:
                                transit_dur = f"{h_tr} ساعات و {m_tr} دقيقة" if h_tr and m_tr else (f"{h_tr} ساعات" if h_tr else f"{m_tr} دقيقة")

                dates = [first_leg["date"]] + [c["date"] for c in connecting_legs if c.get("date")]
                unique_dates = []
                for d in dates:
                    if d not in unique_dates:
                        unique_dates.append(d)
                date_display = " - ".join(unique_dates)

                seg_list = [{
                    "segment_type": "Departure" if is_en else "إقلاع",
                    "date": first_leg["date"],
                    "from_airport": first_leg["from_airport"],
                    "to_airport": first_leg["to_airport"],
                    "airline": first_leg.get("airline"),
                    "departure_time": first_leg["departure_time"],
                    "arrival_time": first_arr,
                    "transit_duration": transit_dur
                }]
                for cl in connecting_legs:
                    seg_list.append({
                        "segment_type": "Connecting" if is_en else "رحلة متابعة",
                        "date": cl.get("date", first_leg["date"]),
                        "from_airport": cl["from_airport"],
                        "to_airport": cl["to_airport"],
                        "airline": cl.get("airline") or first_leg.get("airline"),
                        "departure_time": cl["departure_time"],
                        "arrival_time": cl.get("arrival_time"),
                        "transit_duration": cl.get("transit_duration")
                    })

                journey_item = {
                    "date": date_display,
                    "from_airport": first_leg["from_airport"],
                    "to_airport": last_leg["to_airport"],
                    "transit_airport": transit_ap,
                    "transit_duration": transit_dur,
                    "airline": first_leg.get("airline") or last_leg.get("airline"),
                    "departure_time": first_leg["departure_time"],
                    "arrival_time": last_leg.get("arrival_time") or first_arr,
                    "flight_type": first_leg.get("flight_type") or ("International Flight" if is_en else "طيران دولي"),
                    "flight_label": first_leg.get("label") or ("International Flight" if is_en else "رحلة دولية"),
                    "luggage": first_leg.get("luggage", global_luggage),
                    "passengers": first_leg.get("passengers", {"adults": 2, "children": 0, "infants": 0}),
                    "segments": seg_list
                }
                grouped_flights.append(journey_item)
                i = j
            else:
                has_single_transit = bool(curr.get("transit_airport") or curr.get("transit_duration"))
                seg_list = [{
                    "segment_type": ("Transit" if has_single_transit else "Direct") if is_en else ("ترانزيت" if has_single_transit else "مباشر"),
                    "date": curr["date"],
                    "from_airport": curr["from_airport"],
                    "to_airport": curr["to_airport"],
                    "airline": curr.get("airline"),
                    "departure_time": curr["departure_time"],
                    "arrival_time": curr.get("arrival_time"),
                    "transit_duration": curr.get("transit_duration")
                }]
                journey_item = {
                    "date": curr["date"],
                    "from_airport": curr["from_airport"],
                    "to_airport": curr["to_airport"],
                    "transit_airport": curr.get("transit_airport"),
                    "transit_duration": curr.get("transit_duration"),
                    "airline": curr.get("airline"),
                    "departure_time": curr["departure_time"],
                    "arrival_time": curr.get("arrival_time"),
                    "flight_type": curr.get("flight_type") or ("International Flight" if is_en else "طيران دولي"),
                    "flight_label": curr.get("label") or ("Flight" if is_en else "رحلة طيران"),
                    "luggage": curr.get("luggage", global_luggage),
                    "passengers": curr.get("passengers", {"adults": 2, "children": 0, "infants": 0}),
                    "segments": seg_list
                }
                grouped_flights.append(journey_item)
                i += 1

        data["flights"] = grouped_flights

    # --- 2.3 Parse Car Rentals (استئجار سيارة / Car Rental) ---
    if "car_rentals" in sections_text:
        car_text = sections_text["car_rentals"]
        car_blocks = re.split(r"(?i)(?=\b(?:سيارة\s+\d+|السيارة\s+\d+|نوع السيارة\s*:|Car\s+\d+|Vehicle\s+\d+|Car Model\s*:|Car Type\s*:|Vehicle\s*:))", car_text)
        if not car_blocks or len(car_blocks) == 1:
            car_blocks = [car_text]

        for cblk in car_blocks:
            if not re.search(r"(?:نوع|موديل|استلام|Model|Type|Vehicle|Pick-?up)", cblk, re.IGNORECASE):
                continue

            model_m = re.search(r"(?:نوع السيارة|الموديل|نوع وموديل السيارة|Car Model|Car Type|Vehicle Model|Vehicle|Model)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            car_model = clean_markdown(model_m.group(1)) if model_m else ("Modern Family SUV" if is_en else "سيارة حديثة عائلية")

            pickup_loc_m = re.search(r"(?:مكان الاستلام|الاستلام من|الاستلام|Pick-?up Location|Pick-?up from|Pick-?up)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            pickup_loc = clean_markdown(pickup_loc_m.group(1)) if pickup_loc_m else ("International Arrival Airport" if is_en else "مطار الوصول الدولي")

            dropoff_loc_m = re.search(r"(?:مكان التسليم|التسليم في|التسليم|Drop-?off Location|Return Location|Drop-?off at|Drop-?off)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            dropoff_loc = clean_markdown(dropoff_loc_m.group(1)) if dropoff_loc_m else pickup_loc

            pickup_date_m = re.search(r"(?:تاريخ الاستلام|من تاريخ|Pick-?up Date|From Date)\s*:\s*([0-9\-\/]+)", cblk, re.IGNORECASE)
            dropoff_date_m = re.search(r"(?:تاريخ التسليم|إلى تاريخ|الى تاريخ|Drop-?off Date|Return Date|To Date)\s*:\s*([0-9\-\/]+)", cblk, re.IGNORECASE)
            p_date = clean_markdown(pickup_date_m.group(1)) if pickup_date_m else "2026-08-17"
            d_date = clean_markdown(dropoff_date_m.group(1)) if dropoff_date_m else "2026-08-26"

            days_m = re.search(r"(?:عدد الأيام|المدة|Number of Days|Rental Days|Days|Duration)\s*:\s*(\d+)", cblk, re.IGNORECASE)
            days_count = int(days_m.group(1)) if days_m else None
            if not days_count:
                pd_obj = parse_date_obj(p_date)
                dd_obj = parse_date_obj(d_date)
                if pd_obj and dd_obj and dd_obj > pd_obj:
                    days_count = (dd_obj - pd_obj).days

            insurance_m = re.search(r"(?:التأمين|Insurance|Coverage)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            insurance = clean_markdown(insurance_m.group(1)) if insurance_m else ("Full Coverage" if is_en else "شامل كلي (Full Coverage)")

            trans_m = re.search(r"(?:ناقل الحركة|القير|Transmission|Gearbox|Gear)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            transmission = clean_markdown(trans_m.group(1)) if trans_m else ("Automatic" if is_en else "أوتوماتيك")

            mileage_m = re.search(r"(?:الكيلومترات|المسافة|Mileage|Kilometers)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            mileage = clean_markdown(mileage_m.group(1)) if mileage_m else ("Unlimited Mileage" if is_en else "كيلومترات مفتوحة")

            driver_m = re.search(r"(?:السائق|نوع القيادة|Driver|Driving Type|Driver Option)\s*:\s*([^\n\r]+)", cblk, re.IGNORECASE)
            driver_type = clean_markdown(driver_m.group(1)) if driver_m else ("Self-Drive (No Driver)" if is_en else "بدون سائق (قيادة ذاتية)")

            data["car_rentals"].append({
                "car_model": car_model,
                "pickup_location": pickup_loc,
                "dropoff_location": dropoff_loc,
                "pickup_date": p_date,
                "dropoff_date": d_date,
                "days_count": days_count,
                "insurance": insurance,
                "transmission": transmission,
                "mileage": mileage,
                "driver_type": driver_type
            })

    # --- 2.4 Parse Transports & Tours ---
    if "transports" in sections_text:
        tr_text = sections_text["transports"]
        lines_tr = tr_text.splitlines()
        current_city = data["meta"]["destination"]
        current_items = []
        transports_list = []

        # Detect vehicle from text context
        is_train_section = any(w in tr_text for w in ["قطار", "القطارات", "Railjet", "EuroCity", "Train"])
        if is_en:
            default_vehicle = "Fast Tourist Train" if is_train_section else "Private Car"
            if "mercedes" in tr_text.lower() or "vito" in tr_text.lower():
                default_vehicle = "Mercedes Vito VIP"
            elif "van" in tr_text.lower() or "minivan" in tr_text.lower():
                default_vehicle = "Private Van"
            elif "bus" in tr_text.lower() or "coach" in tr_text.lower():
                default_vehicle = "Tourist Coach"
            elif is_train_section and "first class" in tr_text.lower():
                default_vehicle = "Fast Train (First Class)"
        else:
            default_vehicle = "قطار سياحي سريع" if is_train_section else "سيارة خاصة"
            if "مرسيدس فيتو" in tr_text and "سيارة" not in tr_text and "سياره" not in tr_text:
                default_vehicle = "مرسيدس فيتو VIP"
            elif is_train_section:
                if "الدرجة الأولى" in tr_text or "درجة أولى" in tr_text:
                    default_vehicle = "قطار سريع (درجة أولى)"
                else:
                    default_vehicle = "قطار سياحي سريع"

        veh_kw_re = re.compile(
            r"(?:سيار[ةه]|فان|باص|حافل[ةه]|VIP|مرسيدس|قطار|سيدان|هايس|فورتشنر|انوفا|إينوفا|جمس|سوبربان|"
            r"Private\s*Car|Small\s*Car|Medium\s*Car|Family\s*Van|Family\s*Bus|Sedan|SUV|Van|Minivan|Bus|Coach|Mercedes|Vito|Sprinter|Train|Limousine)",
            re.IGNORECASE
        )

        def _normalize_vehicle_ar(v_str: str) -> str:
            v_str = clean_markdown(v_str).strip(" .:-،,")
            replacements = {
                "سياره": "سيارة",
                "متوسطه": "متوسطة",
                "صغيره": "صغيرة",
                "كبيره": "كبيرة",
                "خاصه": "خاصة",
                "عائليه": "عائلية",
                "حافله": "حافلة",
                "سياحيه": "سياحية",
                "فان عائلي": "فان عائلي",
            }
            words = v_str.split()
            norm_words = [replacements.get(w, w) for w in words]
            return " ".join(norm_words)

        def _extract_top_level_parens(s: str):
            """Returns list of (start_idx, end_idx, inner_text) for top-level balanced parentheses."""
            groups = []
            depth = 0
            start_idx = -1
            for idx, ch in enumerate(s):
                if ch == "(":
                    if depth == 0:
                        start_idx = idx
                    depth += 1
                elif ch == ")":
                    if depth > 0:
                        depth -= 1
                        if depth == 0 and start_idx != -1:
                            groups.append((start_idx, idx + 1, s[start_idx + 1:idx].strip()))
                            start_idx = -1
            return groups

        def _split_top_level_dashes(s: str):
            """Splits string by dash (- / – / —) only at depth 0 outside nested parentheses."""
            parts = []
            curr = []
            depth = 0
            for ch in s:
                if ch == "(":
                    depth += 1
                    curr.append(ch)
                elif ch == ")":
                    if depth > 0:
                        depth -= 1
                    curr.append(ch)
                elif ch in ("-", "–", "—") and depth == 0:
                    piece = clean_markdown("".join(curr)).strip()
                    if piece:
                        parts.append(piece)
                    curr = []
                else:
                    curr.append(ch)
            last_piece = clean_markdown("".join(curr)).strip()
            if last_piece:
                parts.append(last_piece)
            return parts

        detail_prefixes = (
            "وقت المغادرة", "وقت الإقلاع", "وقت الاقلاع", "مغادرة", "المغادرة",
            "وقت الوصول", "وصول", "الوصول",
            "نوع التذكرة", "الدرجة", "درجة الحجز", "المقاعد",
            "من محطة", "إلى محطة", "الى محطة", "المحطة",
            "رقم القطار", "شركة القطار", "نوع القطار", "القطار",
            "المسار", "التفاصيل", "ملاحظة", "يشمل", "شامل",
            "Departure Time", "Departure", "Arrival Time", "Arrival",
            "Ticket Type", "Class", "Station", "Train", "Route", "Details", "Note", "Includes"
        )

        for line in lines_tr:
            line_s = line.strip()
            if not line_s or line_s.startswith("="):
                continue

            if re.match(r"^(?:\d+\.\s*)?(?:الأنشطة|المسارات|المواصلات|الجولات|القطارات|حجز القطار|Transfers|Tours|Transportation|Daily Itinerary|Suggested Itinerary|Itinerary)", line_s, re.IGNORECASE):
                continue
            if any(h in line_s for h in ["الأنشطة والمسارات", "المواصلات والجولات", "المواصلات والقطارات", "بسائق خاص", "Transfers & Tours", "Tours & Transfers"]):
                continue

            is_item_line = bool(re.match(r"^(?:اليوم|Day)\s+[^\(:]+[\(:]", line_s, re.IGNORECASE))
            if not is_item_line:
                if current_items and (line_s.startswith(detail_prefixes) or ":" in line_s or len(line_s) >= 35):
                    last_item = current_items[-1]
                    clean_detail = clean_markdown(line_s).strip(" .-•*")
                    if clean_detail:
                        last_item["activities"].append(clean_detail)
                    if ("الدرجة الأولى" in clean_detail or "درجة أولى" in clean_detail or "first class" in clean_detail.lower()) and ("قطار" in last_item.get("vehicle_type", "") or "train" in last_item.get("vehicle_type", "").lower()):
                        last_item["vehicle_type"] = "Fast Train (First Class)" if is_en else "قطار سريع (درجة أولى)"
                    continue

                if (len(line_s) < 40 and 
                    not line_s.startswith(("-", "•", "*", "السيارة", "الاستقبال", "التنقلات", "الجولات", "خدمة", "مدة", "The ", "All ")) and
                    not line_s.endswith((".", "!", "؟", "?", ":")) and
                    not any(kw in line_s for kw in ["سائق", "وقود", "شامل", "طوال", "المطار", "فترة", "برنامج", "توصيل", "استقبال", "driver", "fuel", "airport", "transfer"])):
                    
                    if current_items:
                        transports_list.append({
                            "city_name": current_city,
                            "items": current_items
                        })
                        current_items = []
                    current_city = line_s
                continue

            if is_item_line:
                day_m = re.match(r"^((?:اليوم|Day)\s+[^\(:–—\-]+?)(?:\s*[\(\-–—]\s*([0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2}|[^)\:]+)\s*\)?)?\s*:\s*(.*)", line_s, re.IGNORECASE)
                if day_m:
                    day_label = day_m.group(1).strip()
                    date_val = day_m.group(2).strip() if day_m.group(2) else ""
                    rest = day_m.group(3).strip()

                    vehicle = default_vehicle
                    activities = []
                    is_train_line = any(w in rest for w in ["قطار", "Railjet", "EuroCity", "Train"])
                    if is_train_line:
                        if "الدرجة الأولى" in rest or "درجة أولى" in rest or "first class" in rest.lower():
                            vehicle = "Fast Train (First Class)" if is_en else "قطار سريع (درجة أولى)"
                        else:
                            vehicle = "Fast Tourist Train" if is_en else "قطار سياحي سريع"

                    paren_groups = _extract_top_level_parens(rest)
                    spans_to_remove = []

                    for g_start, g_end, g_inner in paren_groups:
                        is_train_paren = any(tk in g_inner.lower() for tk in ["railjet", "eurocity", "fast train", "express train"])
                        if is_train_paren:
                            spans_to_remove.append((g_start, g_end))
                            continue

                        parts = _split_top_level_dashes(g_inner)
                        if len(parts) > 1:
                            # Check if first part is vehicle (e.g., "(سياره متوسطه - شاطئ 1 - شاطئ 2)")
                            if not is_train_line and veh_kw_re.search(parts[0]) and len(parts[0]) <= 38:
                                vehicle = _normalize_vehicle_ar(parts[0])
                                activities.extend(parts[1:])
                                spans_to_remove.append((g_start, g_end))
                            # Or if last part is vehicle (e.g., "(شاطئ 1 - شاطئ 2 - سيارة خاصة)")
                            elif not is_train_line and veh_kw_re.search(parts[-1]) and len(parts[-1]) <= 38:
                                vehicle = _normalize_vehicle_ar(parts[-1])
                                activities.extend(parts[:-1])
                                spans_to_remove.append((g_start, g_end))
                            else:
                                activities.extend(parts)
                                spans_to_remove.append((g_start, g_end))
                        else:
                            # Single phrase inside parentheses without '-'
                            if not is_train_line and veh_kw_re.search(g_inner) and len(g_inner) <= 45:
                                vehicle = _normalize_vehicle_ar(g_inner)
                                spans_to_remove.append((g_start, g_end))
                            elif len(g_inner) > 25:
                                activities.append(clean_markdown(g_inner).strip())
                                spans_to_remove.append((g_start, g_end))

                    # Remove processed parenthesized groups from rest (from right to left)
                    title_builder = rest
                    for s_start, s_end in sorted(spans_to_remove, key=lambda x: x[0], reverse=True):
                        title_builder = title_builder[:s_start] + " " + title_builder[s_end:]
                    title_clean = re.sub(r"\s+", " ", title_builder).strip(" .:-")

                    route_details = None
                    if " -> " in title_clean or " ← " in title_clean:
                        route_details = title_clean

                    current_items.append({
                        "day_label": day_label,
                        "date": date_val,
                        "title": clean_markdown(title_clean),
                        "route_details": route_details,
                        "activities": activities,
                        "vehicle_type": vehicle
                    })

        if current_items:
            transports_list.append({
                "city_name": current_city,
                "items": current_items
            })

        data["transports"] = transports_list

    # --- 2.5 Parse Extra Services ---
    if "extra_services" in sections_text:
        srv_text = sections_text["extra_services"]
        arabic_days_map = {
            1: "اليوم الأول", 2: "اليوم الثاني", 3: "اليوم الثالث", 4: "اليوم الرابع",
            5: "اليوم الخامس", 6: "اليوم السادس", 7: "اليوم السابع", 8: "اليوم الثامن",
            9: "اليوم التاسع", 10: "اليوم العاشر", 11: "اليوم الحادي عشر", 12: "اليوم الثاني عشر",
            13: "اليوم الثالث عشر", 14: "اليوم الرابع عشر", 15: "اليوم الخامس عشر"
        }
        trip_start_date = None
        if data["flights"] and data["flights"][0].get("date"):
            trip_start_date = parse_date_obj(data["flights"][0]["date"].split(" - ")[0].strip())
        if not trip_start_date and data["hotels"] and data["hotels"][0].get("check_in"):
            trip_start_date = parse_date_obj(data["hotels"][0]["check_in"].strip())

        for line in srv_text.splitlines():
            line_s = line.strip()
            if not line_s or "خدمات" in line_s or re.search(r"\bServices\b", line_s, re.IGNORECASE) or re.match(r"^\d+\.", line_s):
                continue

            name_m = re.match(r"^([^:]+):(.*)", line_s)
            if name_m:
                s_name = clean_markdown(name_m.group(1)).strip()
                details = name_m.group(2)

                detail_parts = [p.strip() for p in details.split("|") if p.strip()]
                if detail_parts and not any(k in detail_parts[0].lower() for k in ["العدد", "التاريخ", "اليوم", "qty", "quantity", "count", "date", "day"]):
                    extra_desc = clean_markdown(detail_parts[0]).strip()
                    if extra_desc and not extra_desc.isdigit():
                        s_name = f"{s_name} ({extra_desc})"

                qty = 1
                qty_m = re.search(r"(?:العدد|Qty|Quantity|Count)\s*[:\s]*(\d+)", details, re.IGNORECASE)
                if qty_m:
                    qty = int(qty_m.group(1))

                date_s = "2026-11-24"
                date_m = re.search(r"(?:التاريخ|Date)\s*:\s*([0-9\-\/]+)", details, re.IGNORECASE)
                if date_m:
                    date_s = date_m.group(1)
                elif data["flights"] and data["flights"][0].get("date"):
                    date_s = data["flights"][0]["date"]
                elif data["hotels"] and data["hotels"][0].get("check_in"):
                    date_s = data["hotels"][0]["check_in"]

                country = re.sub(r"\s*\([^)]+\)", "", data["meta"]["destination"]).strip()
                country_m = re.search(r"\|\s*([^\s\|]+(?:\s+[^\s\|]+)?)\s*\|", details)
                if country_m and not any(k in country_m.group(1).lower() for k in ["العدد", "التاريخ", "qty", "quantity", "count", "date"]):
                    country = clean_markdown(country_m.group(1)).strip()

                day_label = "Day 1" if is_en else "اليوم الأول"
                day_m = re.search(r"\(((?:اليوم|Day)\s+[^\)]+)\)", details, re.IGNORECASE)
                if day_m:
                    day_label = day_m.group(1).strip()
                else:
                    matched_day = None
                    for t_grp in data.get("transports", []):
                        for t_it in t_grp.get("items", []):
                            if t_it.get("date") == date_s and t_it.get("day_label"):
                                matched_day = t_it["day_label"]
                                break
                    if matched_day:
                        day_label = matched_day
                    elif trip_start_date:
                        srv_d = parse_date_obj(date_s)
                        if srv_d and srv_d >= trip_start_date:
                            diff_days = (srv_d - trip_start_date).days + 1
                            day_label = f"Day {diff_days}" if is_en else arabic_days_map.get(diff_days, f"اليوم {diff_days}")

                data["extra_services"].append({
                    "day_label": day_label,
                    "date": date_s,
                    "country": country,
                    "service_name": s_name,
                    "quantity": qty
                })
            elif len(line_s) > 3 and not line_s.startswith("="):
                s_name = clean_markdown(line_s).strip("•-–* ")
                def_date = "Full Trip" if is_en else "طوال الرحلة"
                if data["flights"] and data["flights"][0].get("date"):
                    def_date = data["flights"][0]["date"]
                elif data["hotels"] and data["hotels"][0].get("check_in"):
                    def_date = data["hotels"][0]["check_in"]

                data["extra_services"].append({
                    "day_label": "Included" if is_en else "خدمة مشمولة",
                    "date": def_date,
                    "country": data["meta"]["destination"],
                    "service_name": s_name,
                    "quantity": 1
                })

    # --- 2.6 Parse Total Price ---
    total_m = re.search(
        r"(?:الإجمالي كلياً|الاجمالي كليا|السعر الإجمالي|المبلغ الإجمالي|السعر|إجمالي السعر|التكلفة الإجمالية|التكلفة|Grand Total|Total Price|Total Package Price|Total Amount|Package Price|Total Cost|Total|Price)\s*:\s*([0-9\.,]+)\s*([^\n\r]+)",
        full_text,
        re.IGNORECASE
    )
    if total_m:
        data["total_price"] = {
            "amount": clean_markdown(total_m.group(1)).strip(),
            "currency": clean_markdown(total_m.group(2)).strip()
        }
    else:
        total_text_m = re.search(
            r"(?:الإجمالي كلياً|الاجمالي كليا|السعر الإجمالي|المبلغ الإجمالي|السعر|إجمالي السعر|التكلفة الإجمالية|التكلفة|Grand Total|Total Price|Total Package Price|Total Amount|Package Price|Total Cost|Total|Price)\s*:\s*([^\n\r]+)",
            full_text,
            re.IGNORECASE
        )
        if total_text_m:
            raw_val = clean_markdown(total_text_m.group(1)).strip()
            # Support prefix currency like "SAR 16,800" or "$4,500 USD"
            prefix_curr = re.match(r"^(SAR|USD|EUR|AED|GBP|\$|€)\s*([0-9\.,]+)(?:\s*([A-Za-z]+))?$", raw_val, re.IGNORECASE)
            curr_match = re.search(r"[–\-\s]\s*(ريال\s*سعودي|ريال|SAR|USD|\$|EUR|AED|GBP|Saudi Riyals?|درهم|دينار)", raw_val, re.IGNORECASE)
            if prefix_curr:
                data["total_price"] = {
                    "amount": prefix_curr.group(2).strip(),
                    "currency": (prefix_curr.group(3) or prefix_curr.group(1)).strip()
                }
            elif curr_match:
                data["total_price"] = {
                    "amount": raw_val[:curr_match.start()].strip(),
                    "currency": curr_match.group(1).strip()
                }
            else:
                data["total_price"] = {
                    "amount": raw_val,
                    "currency": "SAR" if is_en else "ريال سعودي"
                }

    # --- 2.7 Parse Notes ---
    if "notes" in sections_text:
        notes_text = sections_text["notes"]
        for line in notes_text.splitlines():
            line_s = clean_markdown(line)
            if not line_s or line_s.startswith("=") or any(w in line_s for w in ["ملاحظات مهمة", "يتولى النظام", "يمكنك ترك", "الشروط والأحكام", "Important Notes", "Terms & Conditions", "Terms and Conditions"]):
                continue
            if re.match(r"^\d+\.\s*(?:ملاحظات|الشروط|Important Notes|Terms|Notes)", line_s, re.IGNORECASE):
                continue
            if len(line_s) > 10:
                if len(line_s) > 190 and ". " in line_s:
                    sub_notes = [sn.strip().rstrip(".") + "." for sn in re.split(r"\.\s+(?=[أ-يA-Z])", line_s) if len(sn.strip()) > 20]
                    if len(sub_notes) > 1:
                        data["notes"].extend(sub_notes)
                    else:
                        data["notes"].append(line_s)
                else:
                    data["notes"].append(line_s)

    if not data["notes"]:
        data["notes"] = generate_smart_notes(data, lang=detected_lang)

    # --- 2.7.1 Auto-detect destination from flights if generic ---
    if data["meta"]["destination"] in ["رحلة سياحية", "تايلند", "Travel Package", "Thailand"] and data["flights"]:
        dest_cities = []
        for flt in data["flights"]:
            to_ap = flt.get("to_airport", "")
            cleaned_ap = re.sub(r"[-–—,\s]*(?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+", "", to_ap, flags=re.IGNORECASE)
            cleaned_ap = re.sub(r"\([A-Z]{3}\)", "", cleaned_ap).strip(" -–—,")
            parts = [p.strip() for p in re.split(r"[-–—]", cleaned_ap) if p.strip()]
            candidate = parts[-1] if len(parts) > 1 else cleaned_ap
            candidate = re.sub(r"(?:مطار|الدولي|المحلية|المحلي|الجديد|القديم|International|Airport|Domestic)", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and candidate not in dest_cities and not any(home in candidate.lower() for home in ["جدة", "الرياض", "الدمام", "المدينة", "jeddah", "riyadh", "dammam", "medina"]):
                dest_cities.append(candidate)
        if dest_cities:
            data["meta"]["destination"] = (" & " if is_en else " و ").join(dest_cities)

    # --- 2.8 Auto-calculate Nights Duration if not provided ---
    if not data["meta"]["total_nights"]:
        if data["hotels"]:
            total_h_nights = sum(h["nights_count"] for h in data["hotels"])
            if total_h_nights > 0:
                data["meta"]["total_nights"] = total_h_nights
        elif data["flights"] and len(data["flights"]) >= 2:
            f_first_date = data["flights"][0]["date"].split("-")[0].strip()
            f_last_date = data["flights"][-1]["date"].split("-")[-1].strip()
            d1 = parse_date_obj(f_first_date)
            d2 = parse_date_obj(f_last_date)
            if d1 and d2 and d2 > d1:
                data["meta"]["total_nights"] = (d2 - d1).days

    # Clean empty lists so dynamic sections omit cleanly if empty
    if not data["hotels"]:
        data["hotels"] = None
    if not data["flights"]:
        data["flights"] = None
    if not data["transports"]:
        data["transports"] = None
    if not data["car_rentals"]:
        data["car_rentals"] = None
    if not data["extra_services"]:
        data["extra_services"] = None
    if not data["notes"]:
        data["notes"] = None

    return data
