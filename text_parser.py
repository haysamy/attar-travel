"""
Enhanced Arabic Text Parser for Travel Packages & Quotations.
Handles Markdown artifacts, multi-flight splits (ذهاب/عودة), car rentals, flexible dynamic sections, and automatic date/nights calculations.
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


ARABIC_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "ابريل": 4, "أبريل": 4,
    "مايو": 5, "يونيو": 6, "يوليو": 7, "اغسطس": 8, "أغسطس": 8,
    "سبتمبر": 9, "اكتوبر": 10, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12
}


def parse_arabic_time(t_str: str) -> Optional[int]:
    """Converts Arabic time string (e.g. '12:30 ظهراً', '3:40 عصراً') to minutes from midnight."""
    if not t_str:
        return None
    m = re.search(r"(\d{1,2})\s*:\s*(\d{2})", t_str)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    is_pm = any(w in t_str for w in ["مساء", "عصر", "ظهر", "م", "ليلا", "ليلاً"])
    is_am = any(w in t_str for w in ["صباح", "ص", "فجر", "فجراً"])
    if is_pm:
        if hour < 12:
            hour += 12
    elif is_am:
        if hour == 12:
            hour = 0
    return hour * 60 + minute


def format_arabic_time(minutes: int) -> str:
    """Formats minutes from midnight into standard Arabic time string."""
    minutes = minutes % (24 * 60)
    hour = minutes // 60
    minute = minutes % 60
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


def normalize_12h_time(t_str: Optional[str]) -> Optional[str]:
    """Converts any 24-hour time (e.g. '23:20 مساءً' or '16:20 عصراً (29-11-2026)') into strict 12-hour Arabic time."""
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
        # Preserve any trailing parenthesis note like (21-11-2026) or (اليوم التالي)
        paren_m = re.search(r"(\([^)]+\))", s)
        extra = f" {paren_m.group(1)}" if paren_m else ""
        return f"{hr12:02d}:{mn:02d} {period}{extra}"
    return s



def parse_transit_minutes(dur_str: str) -> Optional[int]:
    """Parses transit duration string (e.g. '50 دقيقة', '8 ساعات و30 دقيقة') to minutes."""
    if not dur_str:
        return None
    total = 0
    hr_m = re.search(r"(\d+)\s*(?:ساعة|ساعات|س)", dur_str)
    if hr_m:
        total += int(hr_m.group(1)) * 60
    elif "ساعتين" in dur_str:
        total += 120
    elif "ساعة" in dur_str:
        total += 60

    min_m = re.search(r"(\d+)\s*(?:دقيقة|دقائق|د)", dur_str)
    if min_m:
        total += int(min_m.group(1))
    elif "نصف ساعة" in dur_str:
        total += 30

    return total if total > 0 else None


def parse_date_obj(date_str: str) -> Optional[datetime]:
    """Tries to parse standard Arabic/English date formats, including Arabic month names."""
    if not date_str:
        return None
    cleaned = clean_markdown(date_str).strip()
    formats = [
        "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d",
        "%d-%m-%y", "%d.%m.%Y", "%Y.%m.%d"
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
    return None
def generate_smart_notes(data: Dict[str, Any]) -> List[str]:
    notes = []
    has_flights = bool(data.get("flights"))
    has_cars = bool(data.get("car_rentals"))
    has_hotels = bool(data.get("hotels"))
    has_transports = bool(data.get("transports"))

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


def parse_travel_text(text: str) -> Dict[str, Any]:
    lines = [clean_markdown(line) for line in text.splitlines() if line.strip()]
    full_text = "\n".join(lines)

    data: Dict[str, Any] = {
        "meta": {
            "company_name": "عطار للسياحة",
            "company_name_en": "Attar Travel",
            "tagline": "عطار ترافل",
            "booking_no": "TAJ" + datetime.now().strftime("%y%m%d%H"),
            "quotation_no": "QTAJ" + datetime.now().strftime("%y%m%d%H"),
            "destination": "رحلة سياحية",
            "total_nights": None,
            "booking_status": "حجز مبدئي غير مؤكد"
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
    comp_m = re.search(r"اسم الشركة\s*:\s*([^\n\r]+)", full_text)
    if comp_m:
        c_name = clean_markdown(comp_m.group(1))
        data["meta"]["company_name"] = c_name
        data["meta"]["tagline"] = c_name.replace("للسياحة", "ترافل")

    book_m = re.search(r"رقم الحجز\s*:\s*([A-Za-z0-9_-]+)", full_text)
    if book_m:
        data["meta"]["booking_no"] = book_m.group(1).strip()

    quot_m = re.search(r"رقم عرض السعر\s*:\s*([A-Za-z0-9_-]+)", full_text)
    if quot_m:
        data["meta"]["quotation_no"] = quot_m.group(1).strip()

    dest_m = re.search(r"الوجهة\s*:\s*([^\n\r\(\–\-]+)(?:[\(\–\-]\s*(\d+)\s*(?:ليلة|ليالي|ايام|أيام|يوم))?", full_text)
    if dest_m:
        data["meta"]["destination"] = clean_markdown(dest_m.group(1)).strip()
        if dest_m.group(2):
            data["meta"]["total_nights"] = int(dest_m.group(2))

    status_m = re.search(r"(?:حالة الحجز|الحالة)\s*:\s*([^\n\r]+)", full_text)
    if status_m:
        data["meta"]["booking_status"] = clean_markdown(status_m.group(1)).strip()

    # 2. Section Extraction Patterns
    section_patterns = [
        ("hotels", r"(?:حجز الفنادق|الفنادق|فنادق|Accommodation)"),
        ("flights", r"(?:حجز الطيران|الطيران الداخلي|الطيران الدولي|الطيران|Flights|رحلة الذهاب\s*:|رحلة المغادرة\s*:)") ,
        ("transports", r"(?:الأنشطة والمسارات السياحية|الأنشطة والمسارات|المسارات السياحية|المسارات المقترحة|المسارات|الأنشطة|المواصلات والجولات|المواصلات|الجولات السياحية|الجولات|Transfers & Tours)"),
        ("car_rentals", r"(?:استئجار السيارات|استئجار سيارة|تأجير سيارة|تأجير السيارات|إيجار سيارات|إيجار السيارات|Car Rental)"),
        ("extra_services", r"(?:خدمات وهدايا مشمولة|خدمات وهدايا|خدمات أخرى|خدمات مجانية|Free Services|خدمات إضافية)"),
        ("total_price", r"(?:السعر الإجمالي|الإجمالي كلياً|الاجمالي كليا|Total Price|💰\s*السعر\s*:|^السعر\s*:)"),
        ("notes", r"(?:ملاحظات مهمة جداً|ملاحظات مهمة|الشروط والأحكام|شروط الحجز|Notes)")
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
        # Split by city header or hotel header or day range header
        split_pat = r'(?m)(?=(?:^[ \t]*المدينة\s+[^\n:]+:|^[ \t]*فندق\s+\d+:|^[ \t]*[^\n\r:]{2,30}\s*\((?:\d+\s*(?:ليلة|ليالي|ايام|أيام)|ليلتين|ليلة واحدة)\)))'
        hotel_blocks = [b for b in re.split(split_pat, htl_text) if "الفندق" in b or "فندق" in b]
        if not hotel_blocks and ("الفندق" in htl_text or "فندق" in htl_text):
            hotel_blocks = re.split(r"(?=\bالفندق\s*:)", htl_text)

        arabic_ordinals = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة"]

        for h_idx, blk in enumerate(hotel_blocks):
            if "الفندق" not in blk and "فندق" not in blk:
                continue

            default_ord = arabic_ordinals[h_idx] if h_idx < len(arabic_ordinals) else f"المحطة {h_idx+1}"
            city_order = f"المدينة {default_ord}"
            city_name = data["meta"]["destination"]
            nights_count = 1

            # 1. المدينة الأولى: بانكوك (3 ليالي)
            alt_city = re.search(r"المدينة\s+([^:\(\n]+):\s*([^\(\n\r]+)(?:[\(\-–]\s*(\d+|ليلتين|ليلة واحدة)\s*(?:ليلة|ليالي)?)?", blk)
            if alt_city:
                city_order = f"المدينة {clean_markdown(alt_city.group(1)).strip()}"
                city_name = clean_markdown(alt_city.group(2)).strip()
                raw_n = alt_city.group(3)
                if raw_n == "ليلتين":
                    nights_count = 2
                elif raw_n == "ليلة واحدة":
                    nights_count = 1
                elif raw_n and raw_n.isdigit():
                    nights_count = int(raw_n)
            else:
                # 2. بانكوك (3 ليالي) or بوكيت (6 ليالي) or بانكوك (ليلتين)
                city_line_m = re.search(r"^[ \t]*([^\n\r:\(\d]{2,30}?)\s*\((?:(\d+)\s*(?:ليلة|ليالي|ايام|أيام)|(ليلتين)|(ليلة واحدة))\)", blk, re.MULTILINE)
                if city_line_m:
                    city_name = clean_markdown(city_line_m.group(1)).strip()
                    if city_line_m.group(2):
                        nights_count = int(city_line_m.group(2))
                    elif city_line_m.group(3):
                        nights_count = 2
                    elif city_line_m.group(4):
                        nights_count = 1

            day_range_m = re.search(r"(اليوم\s+[^\n\-–]+)\s*[\-–]\s*(اليوم\s+[^\n\r]+)", blk)
            day_range = f"{day_range_m.group(1).strip()}<br>{day_range_m.group(2).strip()}" if day_range_m else f"المدة: {nights_count} ليالي"

            hotel_name_m = re.search(r"الفندق\s*:\s*([^\n\r]+)", blk)
            hotel_name = clean_markdown(hotel_name_m.group(1)) if hotel_name_m else "فندق فاخر"

            room_type = "غرفة قياسية"
            rooms_count = 1
            room_m = re.search(r"نوع الغرفة\s*:\s*([^\|\n\r]+)(?:\|\s*العدد\s*:\s*(\d+))?", blk)
            if room_m:
                room_type = clean_markdown(room_m.group(1))
                if room_m.group(2):
                    try:
                        rooms_count = int(room_m.group(2))
                    except ValueError:
                        pass

            meal_plan = "شامل الإفطار"
            meal_m = re.search(r"الوجبة\s*:\s*([^\n\r]+)", blk)
            if meal_m:
                meal_plan = clean_markdown(meal_m.group(1))

            checkin_m = re.search(r"تاريخ الدخول\s*:\s*([0-9\-\/]+)", blk)
            checkout_m = re.search(r"تاريخ الخروج\s*:\s*([0-9\-\/]+)", blk)
            check_in = clean_markdown(checkin_m.group(1)) if checkin_m else "2026-11-24"
            check_out = clean_markdown(checkout_m.group(1)) if checkout_m else "2026-11-25"

            details_url = "#"
            url_m = re.search(r"(?:رابط بوكينج|رابط بوكنج|رابط الفندق|رابط التفاصيل|لينك بوكينج|لينك الفندق|رابط|الرابط|Booking)\s*:\s*(https?://[^\s\n\r\)]+)", blk, re.IGNORECASE)
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

    # --- 2.2 Parse Flights (Supports رحلة الذهاب, رحلة العودة, رحلة متابعة, رحلة داخلية, ترانزيت, etc.) ---
    if "flights" in sections_text:
        flt_text = sections_text["flights"]

        # Check for section-wide luggage note at the end (e.g. "الأمتعة: 25 كجم + 7 كجم كابينة")
        section_luggage_match = re.findall(r"(?:الأمتعة|الوزن المسموح به|الوزن المسموح|الوزن)\s*:\s*([^\n\r]+)", flt_text)
        global_luggage = clean_markdown(section_luggage_match[-1]) if section_luggage_match else "20 كيلو"

        # Split by flight boundaries including connecting/transit legs (at start of line so 'الرحلة' is never split into 'ال' + 'رحلة')
        flight_blocks = re.split(
            r"(?im)(?=^[ \t]*(?:(?:ال)?رحلة\s*(?:الذهاب|ذهاب|العودة|عودة|مغادرة|وصول|داخلية|داخلي|دولية|دولي|متابعة|تكميلية|ترانزيت|ربط|\d+|الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|الأول|الثاني)|الطيران\s*(?:الداخلي|الدولي)|Flight\s*\d+))",
            flt_text
        )

        # Fallback if no explicit split keyword was found but multiple flights exist
        if len([b for b in flight_blocks if "من:" in b or "من :" in b or "التاريخ:" in b or "تاريخ السفر:" in b]) <= 1 and (flt_text.count("التاريخ:") > 1 or flt_text.count("تاريخ السفر:") > 1):
            flight_blocks = re.split(r"(?=\b(?:التاريخ|تاريخ السفر)\s*:)", flt_text)

        raw_flights = []

        for fblk in flight_blocks:
            has_from_to = any(k in fblk for k in ["من:", "من :", "إلى:", "الى:", "💨", "✈️", "->"])
            if not has_from_to:
                continue

            label_m = re.search(r"^(?:(?:ال)?رحلة\s*[^\n\r:]+|طيران\s*[^\n\r:]+)", fblk.strip())
            label = clean_markdown(label_m.group(0)) if label_m else ""

            # Extract full date string with Arabic month names (e.g. '20 نوفمبر')
            date_m = re.search(r"(?:التاريخ|تاريخ السفر|تاريخ الرحلة)\s*:\s*([^\n\r]+)", fblk)
            date_str = clean_markdown(date_m.group(1)) if date_m else "2026-11-20"

            from_m = re.search(r"من\s*:\s*([^\n\r]+)", fblk)
            to_m = re.search(r"(?:إلى|الى)\s*:\s*([^\n\r]+)", fblk)
            from_ap = clean_markdown(from_m.group(1)) if from_m else None
            to_ap = clean_markdown(to_m.group(1)) if to_m else None

            if not from_ap or not to_ap:
                # Fallback for emoji route line like: 🚦 جدة 💨 جاكرتا 🚦
                route_emoji_m = re.search(r"(?:🚦\s*)?([\u0600-\u06FF\s]{2,25}?)\s*(?:💨|✈️|->|←|إلى)\s*([\u0600-\u06FF\s]{2,25}?)(?:\s*🚦|$)", fblk, re.MULTILINE)
                if route_emoji_m:
                    from_ap = from_ap or clean_markdown(route_emoji_m.group(1)).strip()
                    to_ap = to_ap or clean_markdown(route_emoji_m.group(2)).strip()

            from_ap = from_ap or "المطار"
            to_ap = to_ap or "المطار"

            airline_m = re.search(r"شركة الطيران\s*:\s*([^\n\r]+)", fblk)
            airline = clean_markdown(airline_m.group(1)) if airline_m else None

            adults, children, infants = 2, 0, 0
            pax_m = re.search(r"بالغين\s*:\s*(\d+)(?:.*?الأطفال\s*:\s*(\d+))?(?:.*?الرضع\s*:\s*(\d+))?", fblk)
            if pax_m:
                adults = int(pax_m.group(1)) if pax_m.group(1) else 2
                children = int(pax_m.group(2)) if pax_m.group(2) else 0
                infants = int(pax_m.group(3)) if pax_m.group(3) else 0

            luggage_m = re.search(r"(?:الأمتعة|الوزن المسموح به|الوزن المسموح|الوزن|الحقائب)\s*:\s*([^\n\r]+)", fblk)
            luggage = clean_markdown(luggage_m.group(1)) if luggage_m else global_luggage

            time_m = re.search(r"(?:وقت الإقلاع|وقت الاقلاع|إقلاع الرحلة الساعة|اقلاع الرحلة الساعة|الإقلاع|الاقلاع|الوقت|الساعة)\s*:\s*([^\n\r]+)", fblk)
            departure_time = normalize_12h_time(time_m.group(1)) if time_m else "10:30 صباحاً"

            arr_m = re.search(r"(?:وقت الوصول|وقت وصول|الوصول(?:\s+إلى\s+[^\n\r:]+)?(?:\s+الساعة)?)\s*:\s*([^\n\r]+)", fblk)
            arrival_time = normalize_12h_time(arr_m.group(1)) if arr_m else None

            tr_ap_m = re.search(r"(?:مطار الترانزيت|محطة الترانزيت|ترانزيت في|التوقف في|مطار التوقف)\s*:\s*([^\n\r]+)", fblk)
            transit_ap_single = clean_markdown(tr_ap_m.group(1)) if tr_ap_m else None

            tr_m = re.search(r"(?:مدة الترانزيت|الترانزيت|مدة التوقف|التوقف)\s*:\s*([^\n\r]+)", fblk)
            transit_dur = clean_markdown(tr_m.group(1)) if tr_m else None
            # If user wrote "الترانزيت: مطار الدوحة (ساعتين)" without separate transit_ap_m
            if transit_dur and not transit_ap_single and ("مطار" in transit_dur or "الدوحة" in transit_dur or "اسطنبول" in transit_dur or "إسطنبول" in transit_dur or "دبي" in transit_dur or "أبوظبي" in transit_dur or "القاهرة" in transit_dur or "فرانكفورت" in transit_dur):
                paren_m = re.search(r"([^\(\|\-]+?)\s*[\(\|\-]\s*([^\)\n\r]+)\)?", transit_dur)
                if paren_m:
                    transit_ap_single = paren_m.group(1).strip()
                    transit_dur = paren_m.group(2).strip()

            type_m = re.search(r"(?:نوع الرحلة|نوع الطيران|التصنيف)\s*:\s*([^\n\r]+)", fblk)
            flight_type = None
            fblk_no_airports = re.sub(r"(?:من|إلى|الى)\s*:[^\n\r]+", "", fblk)
            if type_m:
                flight_type = clean_markdown(type_m.group(1)).strip()
            elif re.search(r"(?:طيران\s*داخلي|رحلة\s*داخلية|\bداخلي\b|internal|domestic)", fblk_no_airports, re.IGNORECASE) or "داخلية" in label or "داخلي" in label:
                flight_type = "طيران داخلي"
            elif re.search(r"(?:طيران\s*دولي|رحلة\s*دولية|\bدولي\b|international)", fblk_no_airports, re.IGNORECASE) or "دولية" in label or "دولي" in label or "الذهاب" in label or "العودة" in label:
                flight_type = "طيران دولي"
            elif "الطيران الداخلي" in flt_text[:120] or "طيران داخلي" in flt_text[:120] or "internal" in flt_text[:120].lower():
                flight_type = "طيران داخلي"
            elif "الطيران الدولي" in flt_text[:120] or "طيران دولي" in flt_text[:120] or "international" in flt_text[:120].lower():
                flight_type = "طيران دولي"

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
            "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة"
        ]
        while i < len(raw_flights):
            curr = raw_flights[i]
            connecting_legs = []
            j = i + 1
            while j < len(raw_flights):
                nxt = raw_flights[j]
                nxt_label = nxt.get("label", "")
                explicit_transit = any(kw in nxt_label for kw in ["متابعة", "ترانزيت", "ربط", "تكميلية"])
                explicit_separate = any(kw in nxt_label for kw in separate_journey_keywords) and not explicit_transit

                if explicit_separate:
                    break

                # Check if dates are within 1 day and it's not a round-trip back to origin
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

                # Auto-calculate arrival at transit airport if not explicitly specified
                first_arr = first_leg.get("arrival_time")
                if not first_arr and transit_dur and connecting_legs[0].get("departure_time"):
                    t_dept = parse_arabic_time(connecting_legs[0]["departure_time"])
                    d_dur = parse_transit_minutes(transit_dur)
                    if t_dept is not None and d_dur is not None:
                        t_first_dept = parse_arabic_time(first_leg.get("departure_time", ""))
                        if t_first_dept is not None and t_dept < t_first_dept:
                            t_dept += 1440
                        arr_mins = t_dept - d_dur
                        first_arr = format_arabic_time(arr_mins)

                dates = [first_leg["date"]] + [c["date"] for c in connecting_legs if c.get("date")]
                unique_dates = []
                for d in dates:
                    if d not in unique_dates:
                        unique_dates.append(d)
                date_display = " - ".join(unique_dates)

                seg_list = [{
                    "segment_type": "إقلاع",
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
                        "segment_type": "رحلة متابعة",
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
                    "flight_type": first_leg.get("flight_type") or "طيران دولي",
                    "flight_label": first_leg.get("label") or "رحلة دولية",
                    "luggage": first_leg.get("luggage", global_luggage),
                    "passengers": first_leg.get("passengers", {"adults": 2, "children": 0, "infants": 0}),
                    "segments": seg_list
                }
                grouped_flights.append(journey_item)
                i = j
            else:
                has_single_transit = bool(curr.get("transit_airport") or curr.get("transit_duration"))
                seg_list = [{
                    "segment_type": "ترانزيت" if has_single_transit else "مباشر",
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
                    "flight_type": curr.get("flight_type") or "طيران دولي",
                    "flight_label": curr.get("label") or "رحلة طيران",
                    "luggage": curr.get("luggage", global_luggage),
                    "passengers": curr.get("passengers", {"adults": 2, "children": 0, "infants": 0}),
                    "segments": seg_list
                }
                grouped_flights.append(journey_item)
                i += 1

        data["flights"] = grouped_flights

    # --- 2.3 Parse Car Rentals (استئجار سيارة) ---
    if "car_rentals" in sections_text:
        car_text = sections_text["car_rentals"]
        car_blocks = re.split(r"(?=\b(?:سيارة\s+\d+|السيارة\s+\d+|نوع السيارة\s*:))", car_text)
        if not car_blocks or len(car_blocks) == 1:
            car_blocks = [car_text]

        for cblk in car_blocks:
            if "نوع" not in cblk and "موديل" not in cblk and "استلام" not in cblk:
                continue

            model_m = re.search(r"(?:نوع السيارة|الموديل|نوع وموديل السيارة)\s*:\s*([^\n\r]+)", cblk)
            car_model = clean_markdown(model_m.group(1)) if model_m else "سيارة حديثة عائلية"

            pickup_loc_m = re.search(r"(?:مكان الاستلام|الاستلام من|الاستلام)\s*:\s*([^\n\r]+)", cblk)
            pickup_loc = clean_markdown(pickup_loc_m.group(1)) if pickup_loc_m else "مطار الوصول الدولي"

            dropoff_loc_m = re.search(r"(?:مكان التسليم|التسليم في|التسليم)\s*:\s*([^\n\r]+)", cblk)
            dropoff_loc = clean_markdown(dropoff_loc_m.group(1)) if dropoff_loc_m else pickup_loc

            pickup_date_m = re.search(r"(?:تاريخ الاستلام|من تاريخ)\s*:\s*([0-9\-\/]+)", cblk)
            dropoff_date_m = re.search(r"(?:تاريخ التسليم|إلى تاريخ|الى تاريخ)\s*:\s*([0-9\-\/]+)", cblk)
            p_date = clean_markdown(pickup_date_m.group(1)) if pickup_date_m else "2026-08-17"
            d_date = clean_markdown(dropoff_date_m.group(1)) if dropoff_date_m else "2026-08-26"

            days_m = re.search(r"(?:عدد الأيام|المدة)\s*:\s*(\d+)", cblk)
            days_count = int(days_m.group(1)) if days_m else None

            insurance_m = re.search(r"التأمين\s*:\s*([^\n\r]+)", cblk)
            insurance = clean_markdown(insurance_m.group(1)) if insurance_m else "شامل كلي (Full Coverage)"

            trans_m = re.search(r"(?:ناقل الحركة|القير)\s*:\s*([^\n\r]+)", cblk)
            transmission = clean_markdown(trans_m.group(1)) if trans_m else "أوتوماتيك"

            mileage_m = re.search(r"(?:الكيلومترات|المسافة)\s*:\s*([^\n\r]+)", cblk)
            mileage = clean_markdown(mileage_m.group(1)) if mileage_m else "كيلومترات مفتوحة"

            driver_m = re.search(r"(?:السائق|نوع القيادة)\s*:\s*([^\n\r]+)", cblk)
            driver_type = clean_markdown(driver_m.group(1)) if driver_m else "بدون سائق (قيادة ذاتية)"

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
        default_vehicle = "قطار سياحي سريع" if is_train_section else "سيارة خاصة"
        if "مرسيدس فيتو" in tr_text:
            default_vehicle = "مرسيدس فيتو VIP"
        elif "فان" in tr_text:
            default_vehicle = "فان سياحي"
        elif "حافلة" in tr_text or "باص" in tr_text:
            default_vehicle = "حافلة سياحية"
        elif is_train_section:
            if "الدرجة الأولى" in tr_text or "درجة أولى" in tr_text:
                default_vehicle = "قطار سريع (درجة أولى)"
            else:
                default_vehicle = "قطار سياحي سريع"
        elif "سائق خاص" in tr_text or "سيارة خاصة" in tr_text:
            default_vehicle = "سيارة خاصة"

        detail_prefixes = (
            "وقت المغادرة", "وقت الإقلاع", "وقت الاقلاع", "مغادرة", "المغادرة",
            "وقت الوصول", "وصول", "الوصول",
            "نوع التذكرة", "الدرجة", "درجة الحجز", "المقاعد",
            "من محطة", "إلى محطة", "الى محطة", "المحطة",
            "رقم القطار", "شركة القطار", "نوع القطار", "القطار",
            "المسار", "التفاصيل", "ملاحظة", "يشمل", "شامل"
        )

        for line in lines_tr:
            line_s = line.strip()
            if not line_s or line_s.startswith("="):
                continue

            # Skip section headings or bullet notes like "4. المواصلات والجولات..."
            if re.match(r"^(?:\d+\.\s*)?(?:الأنشطة|المسارات|المواصلات|الجولات|القطارات|حجز القطار)", line_s):
                continue
            if any(h in line_s for h in ["الأنشطة والمسارات", "المواصلات والجولات", "المواصلات والقطارات", "بسائق خاص"]):
                continue

            is_item_line = bool(re.match(r"^اليوم\s+[^\(:]+[\(:]", line_s))
            if not is_item_line:
                # Check if this line is a sub-detail of the most recent item (e.g. وقت المغادرة, وقت الوصول, نوع التذكرة)
                if current_items and (line_s.startswith(detail_prefixes) or ":" in line_s or len(line_s) >= 35):
                    last_item = current_items[-1]
                    clean_detail = clean_markdown(line_s).strip(" .-•*")
                    if clean_detail:
                        last_item["activities"].append(clean_detail)
                    # Upgrade vehicle badge if first class is mentioned in sub-details
                    if ("الدرجة الأولى" in clean_detail or "درجة أولى" in clean_detail) and "قطار" in last_item.get("vehicle_type", ""):
                        last_item["vehicle_type"] = "قطار سريع (درجة أولى)"
                    continue

                # Otherwise, is it a city/route header? (e.g. "جنيف - فيينا" or "بانكوك")
                if (len(line_s) < 40 and 
                    not line_s.startswith(("-", "•", "*", "السيارة", "الاستقبال", "التنقلات", "الجولات", "خدمة", "مدة")) and
                    not line_s.endswith((".", "!", "؟", ":")) and
                    not any(kw in line_s for kw in ["سائق", "وقود", "شامل", "طوال", "المطار", "فترة", "برنامج", "توصيل", "استقبال"])):
                    
                    # If we already have items for previous city, save this block sequentially!
                    if current_items:
                        transports_list.append({
                            "city_name": current_city,
                            "items": current_items
                        })
                        current_items = []
                    current_city = line_s
                continue

            if is_item_line:
                day_m = re.match(r"^(اليوم\s+[^\(:]+)(?:\(([^)]+)\))?\s*:\s*(.*)", line_s)
                if day_m:
                    day_label = day_m.group(1).strip()
                    date_val = day_m.group(2).strip() if day_m.group(2) else ""
                    rest = day_m.group(3).strip()

                    vehicle = default_vehicle
                    if any(w in rest for w in ["قطار", "Railjet", "EuroCity", "Train"]):
                        if "الدرجة الأولى" in rest or "درجة أولى" in rest:
                            vehicle = "قطار سريع (درجة أولى)"
                        else:
                            vehicle = "قطار سياحي سريع"
                    else:
                        veh_m = re.search(r"\(([^)]*(?:سيارة|فان|باص|حافلة|VIP|مرسيدس|قطار)[^)]*)\)[\.\s]*$", rest)
                        if veh_m:
                            vehicle = clean_markdown(veh_m.group(1)).strip()
                            rest = rest[:veh_m.start()].strip()

                    activities = []
                    act_m = re.search(r"\(([^)]+)\)", rest)
                    # Only split parentheses as activities if it's a dash-separated Arabic list of sights, not an English train name like (Railjet / EuroCity Fast Train)
                    if act_m and "-" in act_m.group(1) and not re.search(r"[A-Za-z]{3,}", act_m.group(1)):
                        acts_str = act_m.group(1)
                        activities = [clean_markdown(a).strip() for a in acts_str.split("-") if a.strip()]
                        title_clean = (rest[:act_m.start()] + rest[act_m.end():]).strip(" .:-")
                    else:
                        title_clean = rest.strip(" .:-")

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
            if not line_s or "خدمات" in line_s or re.match(r"^\d+\.", line_s):
                continue

            name_m = re.match(r"^([^:]+):(.*)", line_s)
            if name_m:
                s_name = clean_markdown(name_m.group(1)).strip()
                details = name_m.group(2)

                # Check if the first segment before '|' is a descriptive note (not العدد and not التاريخ)
                detail_parts = [p.strip() for p in details.split("|") if p.strip()]
                if detail_parts and not any(k in detail_parts[0] for k in ["العدد", "التاريخ", "اليوم"]):
                    extra_desc = clean_markdown(detail_parts[0]).strip()
                    if extra_desc and not extra_desc.isdigit():
                        s_name = f"{s_name} ({extra_desc})"

                qty = 1
                qty_m = re.search(r"العدد\s*[:\s]*(\d+)", details)
                if qty_m:
                    qty = int(qty_m.group(1))

                date_s = "2026-11-24"
                date_m = re.search(r"التاريخ\s*:\s*([0-9\-\/]+)", details)
                if date_m:
                    date_s = date_m.group(1)
                elif data["flights"] and data["flights"][0].get("date"):
                    date_s = data["flights"][0]["date"]
                elif data["hotels"] and data["hotels"][0].get("check_in"):
                    date_s = data["hotels"][0]["check_in"]

                country = re.sub(r"\s*\([^)]+\)", "", data["meta"]["destination"]).strip()
                country_m = re.search(r"\|\s*([^\s\|]+(?:\s+[^\s\|]+)?)\s*\|", details)
                if country_m and "العدد" not in country_m.group(1) and "التاريخ" not in country_m.group(1):
                    country = clean_markdown(country_m.group(1)).strip()

                day_label = "اليوم الأول"
                day_m = re.search(r"\((اليوم\s+[^\)]+)\)", details)
                if day_m:
                    day_label = day_m.group(1).strip()
                else:
                    # Try matching date_s with transport items or calculating from trip_start_date
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
                            day_label = arabic_days_map.get(diff_days, f"اليوم {diff_days}")

                data["extra_services"].append({
                    "day_label": day_label,
                    "date": date_s,
                    "country": country,
                    "service_name": s_name,
                    "quantity": qty
                })
            elif len(line_s) > 3 and not line_s.startswith("="):
                # Plain bullet or item line without colon
                s_name = clean_markdown(line_s).strip("•-–* ")
                def_date = "طوال الرحلة"
                if data["flights"] and data["flights"][0].get("date"):
                    def_date = data["flights"][0]["date"]
                elif data["hotels"] and data["hotels"][0].get("check_in"):
                    def_date = data["hotels"][0]["check_in"]

                data["extra_services"].append({
                    "day_label": "خدمة مشمولة",
                    "date": def_date,
                    "country": data["meta"]["destination"],
                    "service_name": s_name,
                    "quantity": 1
                })

    # --- 2.6 Parse Total Price ---
    total_m = re.search(r"(?:الإجمالي كلياً|الاجمالي كليا|السعر الإجمالي|المبلغ الإجمالي|السعر|إجمالي السعر|التكلفة الإجمالية|التكلفة)\s*:\s*([0-9\.,]+)\s*([^\n\r]+)", full_text)
    if total_m:
        data["total_price"] = {
            "amount": clean_markdown(total_m.group(1)).strip(),
            "currency": clean_markdown(total_m.group(2)).strip()
        }
    else:
        total_text_m = re.search(r"(?:الإجمالي كلياً|الاجمالي كليا|السعر الإجمالي|المبلغ الإجمالي|السعر|إجمالي السعر|التكلفة الإجمالية|التكلفة)\s*:\s*([^\n\r]+)", full_text)
        if total_text_m:
            raw_val = clean_markdown(total_text_m.group(1)).strip()
            curr_match = re.search(r"[–\-]\s*(ريال\s*سعودي|ريال|SAR|USD|\$|EUR|درهم|دينار)", raw_val)
            if curr_match:
                data["total_price"] = {
                    "amount": raw_val[:curr_match.start()].strip(),
                    "currency": curr_match.group(1).strip()
                }
            else:
                data["total_price"] = {
                    "amount": raw_val,
                    "currency": "ريال سعودي"
                }

    # --- 2.7 Parse Notes ---
    if "notes" in sections_text:
        notes_text = sections_text["notes"]
        for line in notes_text.splitlines():
            line_s = clean_markdown(line)
            if not line_s or line_s.startswith("=") or any(w in line_s for w in ["ملاحظات مهمة", "يتولى النظام", "يمكنك ترك", "الشروط والأحكام"]):
                continue
            if re.match(r"^\d+\.\s*(?:ملاحظات|الشروط)", line_s):
                continue
            if len(line_s) > 10:
                data["notes"].append(line_s)

    if not data["notes"]:
        data["notes"] = generate_smart_notes(data)

    # --- 2.7.1 Auto-detect destination from flights if generic ---
    if data["meta"]["destination"] in ["رحلة سياحية", "تايلند"] and data["flights"]:
        dest_cities = []
        for flt in data["flights"]:
            to_ap = flt.get("to_airport", "")
            cleaned_ap = re.sub(r"[-–—,\s]*(?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+", "", to_ap, flags=re.IGNORECASE)
            cleaned_ap = re.sub(r"\([A-Z]{3}\)", "", cleaned_ap).strip(" -–—,")
            parts = [p.strip() for p in re.split(r"[-–—]", cleaned_ap) if p.strip()]
            candidate = parts[-1] if len(parts) > 1 else cleaned_ap
            candidate = re.sub(r"(?:مطار|الدولي|المحلية|المحلي|الجديد|القديم)", "", candidate).strip()
            # Filter out common home departure cities (e.g. Jeddah, Riyadh, etc.)
            if candidate and candidate not in dest_cities and not any(home in candidate for home in ["جدة", "الرياض", "الدمام", "المدينة"]):
                dest_cities.append(candidate)
        if dest_cities:
            data["meta"]["destination"] = " و ".join(dest_cities)

    # --- 2.8 Auto-calculate Nights Duration if not provided ---
    if not data["meta"]["total_nights"]:
        # Try calculating from hotels
        if data["hotels"]:
            total_h_nights = sum(h["nights_count"] for h in data["hotels"])
            if total_h_nights > 0:
                data["meta"]["total_nights"] = total_h_nights
        # Otherwise try from flights
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
