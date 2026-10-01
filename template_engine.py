"""
Dynamic HTML/CSS Template Engine for Attar Travel Quotations & Packages.
Signature Design:
- Deep Navy & Sky Blue gradients (#01579b, #0284c7, #0b4f71, #083344)
- Vibrant Orange accents (#ea580c, #f97316)
- Fonts: Cairo & Tajawal
- Natural page flow: Continuous, densely filled pages without unwanted blank breaks.
"""

import os
import sys
import html
import re
from typing import Union, Dict, Any, List
from models import TravelPackage

# Load company branding logo (base64)
LOGO_URI = ""
def _load_logo():
    global LOGO_URI
    candidates = [
        "logo_base64.txt",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_base64.txt"),
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "logo_base64.txt") if sys.argv else "",
    ]
    if hasattr(sys, "_MEIPASS"):
        candidates.append(os.path.join(sys._MEIPASS, "logo_base64.txt"))
    for path in candidates:
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as _f:
                    LOGO_URI = _f.read().strip()
                    if LOGO_URI:
                        return
            except Exception:
                pass

_load_logo()

# Fallback logo URL
if not LOGO_URI:
    LOGO_URI = "https://lh3.googleusercontent.com/aida-public/AB6AXuBARVtyLSwbhLObLqKoGkPi23u6G0ou9_hBVrkgo5YNwiFTzI2TYABM90ZvQ1nsQXGhJABE_wVLcLauuqLwlnCCxAtoYKMGB16TnM75eIkFb4xVIdy0uqsntGczhb0jsbaZKf94qS8lDf-cJHtgfcc2gkgQut7PVv_hZ1t3vZMna6264eQrJgkBlIx8htrIIOUH4ZYnC4OqiclYQq2y8ANFLqNF8q9_GFcLR6xYN8P60ZXAtolwLuFFBOh7-Sw2IIYTfw"


def get_smart_notes_for_package(pkg: TravelPackage) -> List[str]:
    notes = []
    has_flights = bool(pkg.flights and len(pkg.flights) > 0)
    has_cars = bool(pkg.car_rentals and len(pkg.car_rentals) > 0)
    has_hotels = bool(pkg.hotels and len(pkg.hotels) > 0)
    has_transports = bool(pkg.transports and len(pkg.transports) > 0)

    # 1. Flight terms
    if has_flights:
        notes.append("تذاكر الطيران (الداخلي والدولي) غير قابلة للاسترجاع أو تغيير الأسماء بعد الإصدار، وتخضع التعديلات لرسوم وغرامات شركة الطيران المعنية.")
        notes.append("الوزن المسموح به هو الموضح في جدول الرحلات، وأي أوزان أو حقائب إضافية يسددها المسافر مباشرة لشركة الطيران بالمطار.")
        notes.append("يلزم التواجد في المطار قبل موعد الرحلات الداخلية بساعتين وقبل الدولية بـ 3 ساعات، مع التأكد من سريان الجواز (6 أشهر على الأقل) والتأشيرات المطلوبة.")

    # 2. Car Rental terms
    if has_cars:
        notes.append("استئجار السيارة يتطلب إلزامياً إبراز أصل رخصة القيادة المحلية سارية المفعول + رخصة القيادة الدولية المعتمدة (International Driving Permit) وأصل جواز السفر وبطاقة ائتمانية (Credit Card باسم السائق حصراً) لحجز مبلغ التأمين المسترد.")
        notes.append("الحد الأدنى لعمر السائق 21 سنة. التأمين شامل ويُشترط لتفعيله عند وقوع أي حادث (لا قدر الله) إحضار تقرير شرطة رسمي فوري وضبط الحادث.")
        notes.append("تُسلّم السيارة بمستوى وقود محدد وتُعاد بنفس المستوى، وأي مخالفات مرورية أو رسوم بوابات تقع على عاتق المستأجر بالكامل.")

    # 3. Hotel terms
    if has_hotels:
        notes.append("تسجيل الدخول المعتاد للفنادق يبدأ الساعة 14:00 (2:00 ظهراً) وتسجيل المغادرة حتى الساعة 12:00 ظهراً، والدخول المبكر أو الخروج المتأخر يخضع لتوفر الغرف ورسوم الفندق.")
        notes.append("الغرف القياسية مخصصة لـ (2 بالغين)، وطلب سرير إضافي للأطفال أو البالغين يخضع لسياسة الفندق وبرسوم إضافية.")
        notes.append("قد تشترط بعض الفنادق بطاقة ائتمانية أو مبلغ تأمين نقدي مسترد عند تسجيل الدخول لضمان الخدمات الإضافية الخاصة بالنزيل.")
        notes.append("ضريبة المدينة أو ضريبة السياحة البلدية (City Tax / Tourist Tax) في بعض الوجهات تسدد مباشرة من قبل النزيل للفندق عند تسجيل الدخول أو المغادرة بحسب القوانين المحلية.")
        notes.append("الإلغاء أو التعديل الفندقي يخضع لسياسة وشروط الفندق في مواسم الحجز.")

    # 4. Transports / Tours terms
    if has_transports:
        if has_cars:
            notes.append("الأنشطة والمعالم المذكورة هي مسارات مقترحة تم تصميمها لتناسب تنقلاتكم بحرية بالسيارة المستأجرة، ولا يشمل العرض تذاكر دخول المعالم.")
        else:
            notes.append("مدة الجولة السياحية اليومية 8 ساعات كحد أقصى مع سائق خاص داخل نطاق المدينة، وتشمل الوقود والسيارة دون تذاكر المزارات السياحية (الجولات والأنشطة اختيارية ومتاحة للتعديل أو التغيير ضمن نطاق المدينة حسب رغبتكم).")
            notes.append("تم تحديد حجم السيارة بناءً على عدد الأشخاص الموضح بالعرض؛ وأي زيادة في عدد الركاب أو الأمتعة تتطلب ترقية السيارة مع تحمل فارق التكلفة.")

    # 5. General & Pricing confirmation
    notes.append("الأسعار المعروضة مبدئية وخاضعة للإتاحة حتى سداد الدفعة وتأكيد إصدار الحجوزات الفعلي.")

    return notes


def render_html(data: Union[TravelPackage, Dict[str, Any]]) -> str:
    """Generates the full HTML string for a TravelPackage instance or dictionary."""
    if isinstance(data, dict):
        pkg = TravelPackage(**data)
    else:
        pkg = data

    meta = pkg.meta

    # 1. HOTELS SECTION
    hotels_html = ""
    if pkg.hotels and len(pkg.hotels) > 0:
        hotel_cards = []
        for idx, h in enumerate(pkg.hotels):
            # Format day range nicely
            day_parts = [p.strip() for p in re.split(r'<br\s*/?>|»|-', h.day_range) if p.strip()]
            if len(day_parts) >= 2:
                day_progression = f"""
                <div class="text-[#0369a1] font-extrabold text-xs">{html.escape(day_parts[0])}</div>
                <div class="border-t border-sky-200 my-0.5"></div>
                <div class="text-[#0369a1] font-extrabold text-xs">{html.escape(day_parts[1])}</div>
                """
            else:
                day_progression = f"""<div class="text-[#0369a1] font-extrabold text-xs">{html.escape(h.day_range)}</div>"""

            card = f"""
            <div class="border-2 border-sky-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden avoid-break" data-purpose="hotel-card-{idx+1}">
              <!-- Top Row: Badges -->
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <span class="bg-[#ea580c] text-white text-xs md:text-sm font-bold px-4 py-1 rounded-full shadow-sm">
                    {html.escape(h.city_order)}
                  </span>
                  <div class="bg-[#0284c7] text-white text-xs md:text-sm font-bold px-3 py-1 rounded-full flex items-center gap-2 shadow-sm">
                    <span>{html.escape(h.city_name)}</span>
                    <span class="bg-sky-900/40 text-white text-[11px] px-2 py-0.5 rounded-full border border-sky-300/40 font-num">{h.nights_count} ليالي</span>
                  </div>
                </div>
                <div class="border-2 border-sky-400 rounded-xl px-4 py-1 text-center bg-sky-50/50 min-w-[120px]">
                  {day_progression}
                </div>
              </div>

              <!-- Check-in / Check-out Orange Bar (Compact) -->
              <div class="bg-gradient-to-r from-[#ea580c] to-[#f97316] text-white rounded-lg sm:rounded-xl px-3 py-1 sm:py-1.5 font-bold text-[11px] sm:text-xs flex items-center justify-center gap-2 sm:gap-3 shadow-sm text-center font-num whitespace-nowrap">
                <span>📅 تاريخ الدخول: {html.escape(h.check_in)}</span>
                <span class="text-amber-200 tracking-widest font-black">&gt;&gt;&gt;</span>
                <span>🏁 تاريخ الخروج: {html.escape(h.check_out)}</span>
              </div>

              <!-- Hotel Name Dark Navy Bar -->
              <div class="bg-[#083344] text-white rounded-xl px-4 py-2 flex items-center justify-between gap-2 shadow-sm">
                <h3 class="font-black text-sm md:text-base tracking-wide flex-1">
                  {html.escape(h.hotel_name)}
                </h3>
              </div>

              <!-- Room Information Strip (Light Blue) -->
              <div class="bg-[#0284c7] text-white rounded-xl px-4 py-2 text-xs md:text-sm font-bold grid grid-cols-3 text-center items-center shadow-inner">
                <div class="border-l border-sky-300/40">{html.escape(h.meal_plan)}</div>
                <div class="border-l border-sky-300/40">{html.escape(h.room_type)}</div>
                <div>عدد: {h.rooms_count}</div>
              </div>
            </div>
            """
            hotel_cards.append(card)

        hotels_html = f"""
        <!-- SECTION 1: HOTELS BOOKING -->
        <section class="space-y-3.5" data-purpose="hotels-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#0369a1] via-[#0284c7] to-[#0ea5e9] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md shadow-sky-500/20 flex items-center gap-2 border-2 border-sky-300">
              <span>🏨</span>
              <span class="tracking-wide">حجز الفنادق</span>
            </div>
          </div>
          <div class="space-y-3.5">
            {"".join(hotel_cards)}
          </div>
        </section>
        """

    # 2. FLIGHTS SECTION (Timeline Flight Cards Stack Design)
    flights_html = ""
    if pkg.flights and len(pkg.flights) > 0:
        all_domestic = all("داخلي" in str(getattr(f, "flight_type", "") or "") for f in pkg.flights)
        has_intl = any("دولي" in str(getattr(f, "flight_type", "") or "") for f in pkg.flights)
        has_dom = any("داخلي" in str(getattr(f, "flight_type", "") or "") for f in pkg.flights)

        if all_domestic:
            flight_title = "حجز الطيران الداخلي"
        elif has_intl and has_dom:
            flight_title = "حجز الطيران (الدولي والداخلي)"
        else:
            flight_title = "حجز الطيران (الدولي والداخلي)" if len(pkg.flights) > 2 else "حجز الطيران"

        AIRPORT_CODES = {
            "جدة": "JED",
            "الرياض": "RUH",
            "الدمام": "DMM",
            "المدينة": "MED",
            "أبها": "AHB",
            "تبوك": "TUU",
            "الدوحة": "DOH",
            "باريس": "CDG",
            "فيينا": "VIE",
            "النمسا": "VIE",
            "لندن": "LHR",
            "اسطنبول": "IST",
            "إسطنبول": "IST",
            "طرابزون": "TZX",
            "أنطاليا": "AYT",
            "دبي": "DXB",
            "أبوظبي": "AUH",
            "الشارقة": "SHJ",
            "الكويت": "KWI",
            "البحرين": "BAH",
            "مسقط": "MCT",
            "صلالة": "SLL",
            "القاهرة": "CAI",
            "عمان": "AMM",
            "بانكوك": "BKK",
            "بوكيت": "HKT",
            "كوالالمبور": "KUL",
            "روما": "FCO",
            "ميلانو": "MXP",
            "ميونخ": "MUC",
            "فرانكفورت": "FRA",
            "برشلونة": "BCN",
            "مدريد": "MAD",
            "جنيف": "GVA",
            "زيورخ": "ZRH",
            "أمستردام": "AMS",
            "تبليسي": "TBS",
            "باتومي": "BUS",
            "باكو": "GYD",
            "طشقند": "TAS",
        }

        AIRLINE_ENGLISH = {
            "الخطوط الجوية القطرية": "Qatar Airways",
            "الخطوط القطرية": "Qatar Airways",
            "الخطوط الجوية النمساوية": "Austrian Airlines",
            "الخطوط النمساوية": "Austrian Airlines",
            "الخطوط الجوية السعودية": "Saudia",
            "الخطوط السعودية": "Saudia",
            "طيران ناس": "flynas",
            "طيران أديل": "flyadeal",
            "طيران الإمارات": "Emirates",
            "الخطوط الجوية التركية": "Turkish Airlines",
            "الخطوط التركية": "Turkish Airlines",
            "الاتحاد للطيران": "Etihad Airways",
            "طيران الخليج": "Gulf Air",
            "الخطوط الجوية الكويتية": "Kuwait Airways",
            "الطيران العماني": "Oman Air",
            "مصر للطيران": "EgyptAir",
            "الخطوط الجوية البريطانية": "British Airways",
            "الخطوط الجوية الفرنسية": "Air France",
            "لوفتهانزا": "Lufthansa",
            "فلاي دبي": "flydubai",
            "العربية للطيران": "Air Arabia",
        }

        # (local_offset_mins, actual_flight_mins, arabic_duration_str)
        ROUTE_ESTIMATES = {
            ("CDG", "VIE"): (125, 125, "ساعتان و 5 دقائق"),
            ("VIE", "CDG"): (125, 125, "ساعتان و 5 دقائق"),
            ("DOH", "CDG"): (330, 390, "6 ساعات و 30 دقيقة"),
            ("DOH", "VIE"): (275, 345, "5 ساعات و 45 دقيقة"),
            ("DOH", "JED"): (150, 150, "ساعتان و 30 دقيقة"),
            ("JED", "DOH"): (140, 140, "ساعتان و 20 دقيقة"),
            ("VIE", "DOH"): (445, 325, "5 ساعات و 25 دقيقة"),
            ("CDG", "DOH"): (450, 390, "6 ساعات و 30 دقيقة"),
            ("JED", "LHR"): (270, 390, "6 ساعات و 30 دقيقة"),
            ("LHR", "JED"): (480, 360, "6 ساعات"),
            ("JED", "IST"): (225, 225, "3 ساعات و 45 دقيقة"),
            ("IST", "JED"): (225, 225, "3 ساعات و 45 دقيقة"),
            ("RUH", "LHR"): (300, 410, "6 ساعات و 50 دقيقة"),
            ("JED", "CAI"): (75, 135, "ساعتان و 15 دقيقة"),
            ("JED", "DXB"): (225, 165, "ساعتان و 45 دقيقة"),
        }

        def _get_iata_code(ap_name: str) -> str:
            if not ap_name:
                return ""
            m = re.search(r"\b([A-Z]{3})\b", ap_name)
            if m:
                return m.group(1)
            for city, code in AIRPORT_CODES.items():
                if city in ap_name:
                    return code
            return ""

        def _get_short_city(ap_name: str) -> str:
            if not ap_name:
                return ""
            # Remove terminal info like "- مبنى 3" or "- صالة 1" or "Terminal A"
            cleaned = re.sub(r"[-–—,\s]*(?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+", "", ap_name, flags=re.IGNORECASE)
            cleaned = re.sub(r"\([A-Z]{3}\)", "", cleaned).strip(" -–—,")
            parts = [p.strip() for p in re.split(r"[-–—]", cleaned) if p.strip()]
            if len(parts) > 1:
                return parts[-1]
            c = re.sub(r"(?:مطار|الدولي|المحلية|المحلي)", "", cleaned).strip()
            return c if c else cleaned

        def _get_airport_only(ap_name: str) -> str:
            if not ap_name:
                return ""
            term_m = re.search(r"((?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+)", ap_name, flags=re.IGNORECASE)
            term_str = f" ({term_m.group(1).strip()})" if term_m else ""
            cleaned = re.sub(r"[-–—,\s]*(?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+", "", ap_name, flags=re.IGNORECASE)
            cleaned = re.sub(r"\([A-Z]{3}\)", "", cleaned).strip(" -–—,")
            parts = [p.strip() for p in re.split(r"[-–—]", cleaned) if p.strip()]
            base_ap = parts[0] if parts else cleaned
            if term_str and term_m.group(1).strip() not in base_ap:
                return f"{base_ap}{term_str}"
            return base_ap

        def _format_airline(airline_name: str) -> str:
            if not airline_name:
                return "الطيران المعتمد"
            a = airline_name.strip()
            if "(" not in a:
                for ar_name, en_name in AIRLINE_ENGLISH.items():
                    if ar_name in a:
                        return f"{a} ({en_name})"
            return a

        def _get_airline_en(airline_name: str) -> str:
            if not airline_name:
                return ""
            for ar_name, en_name in AIRLINE_ENGLISH.items():
                if ar_name in airline_name:
                    return en_name
            m = re.search(r"\(([^)]+)\)", airline_name)
            return m.group(1) if m else airline_name

        def _parse_mins(t_str: str):
            if not t_str:
                return None
            m = re.search(r"(\d{1,2}):(\d{2})", t_str)
            if not m:
                return None
            hh, mm = int(m.group(1)), int(m.group(2))
            is_pm = any(w in t_str for w in ["مساء", "عصر", "ظهر", "ليل", "م"]) and not any(w in t_str for w in ["صباح", "فجر"])
            is_am = any(w in t_str for w in ["صباح", "فجر", "ص"])
            if is_pm and hh < 12:
                hh += 12
            elif is_am and hh == 12:
                hh = 0
            return hh * 60 + mm

        def _mins_to_ar(total_mins: int) -> str:
            total_mins = total_mins % (24 * 60)
            hh24 = total_mins // 60
            mm = total_mins % 60
            hh12 = hh24 % 12
            if hh12 == 0:
                hh12 = 12
            if 0 <= hh24 < 5:
                suf = "فجراً"
            elif 5 <= hh24 < 12:
                suf = "صباحاً"
            elif 12 <= hh24 < 15:
                suf = "ظهراً"
            elif 15 <= hh24 < 18:
                suf = "عصراً"
            else:
                suf = "مساءً"
            return f"{hh12:02d}:{mm:02d} {suf}"

        def _split_time_parts(t_str: str):
            if not t_str:
                return ("--:--", "", "")
            raw = t_str.strip()
            note_str = ""
            paren_m = re.search(r"\(([^)]+)\)", raw)
            if paren_m:
                note_str = paren_m.group(1).strip()
                raw = (raw[:paren_m.start()] + raw[paren_m.end():]).strip()
            m = re.search(r"(\d{1,2}:\d{2})\s*(.*)", raw)
            if m:
                t_num = m.group(1)
                if len(t_num.split(":")[0]) == 1:
                    t_num = "0" + t_num
                rest = m.group(2).strip()
                return (t_num, rest, note_str)
            return (raw, "", note_str)

        def _parse_dur_mins(dur_str: str) -> int:
            if not dur_str:
                return 0
            total = 0
            h_m = re.search(r"(\d+)\s*ساع", dur_str)
            if h_m:
                total += int(h_m.group(1)) * 60
            elif "ساعتين" in dur_str or "ساعتان" in dur_str:
                total += 120
            elif "ساعة" in dur_str:
                total += 60
            m_m = re.search(r"(\d+)\s*دقيق", dur_str)
            if m_m:
                total += int(m_m.group(1))
            return total

        def _format_duration_ar(mins: int) -> str:
            if mins <= 0:
                return ""
            h = mins // 60
            m = mins % 60
            h_part = ""
            if h == 1:
                h_part = "ساعة واحدة"
            elif h == 2:
                h_part = "ساعتان"
            elif 3 <= h <= 10:
                h_part = f"{h} ساعات"
            elif h > 10:
                h_part = f"{h} ساعة"
            m_part = f"{m} دقيقة" if m > 0 else ""
            if h_part and m_part:
                return f"{h_part} و {m_part}"
            return h_part or m_part

        flight_cards = []
        for idx, f in enumerate(pkg.flights, 1):
            ftype = getattr(f, "flight_type", None) or ""
            flabel = getattr(f, "flight_label", None) or ""
            segments = getattr(f, "segments", None) or []
            is_transit = bool(
                getattr(f, "transit_duration", None)
                or getattr(f, "transit_airport", None)
                or len(segments) > 1
            )

            combined_type_str = f"{ftype} {flabel}"
            is_return = "عودة" in combined_type_str or (idx == len(pkg.flights) and len(pkg.flights) >= 2 and "داخلي" not in combined_type_str and idx > 1)
            is_domestic_or_euro = "داخلي" in combined_type_str or "أوروبي" in combined_type_str or (not is_return and idx > 1 and len(pkg.flights) > 2)

            origin_code = _get_iata_code(f.from_airport)
            dest_code = _get_iata_code(f.to_airport)
            origin_city = _get_short_city(f.from_airport)
            dest_city = _get_short_city(f.to_airport)
            origin_ap_clean = _get_airport_only(f.from_airport)
            dest_ap_clean = _get_airport_only(f.to_airport)

            airline_full = _format_airline(f.airline)
            airline_short = re.sub(r"\s*\([^)]+\)", "", f.airline or "الطيران المعتمد").strip() or (f.airline or "الطيران المعتمد")
            airline_en = _get_airline_en(f.airline or "")

            # Passengers summary
            pax_parts = []
            if f.passengers.adults:
                pax_parts.append(f"{f.passengers.adults} بالغين")
            if f.passengers.children:
                pax_parts.append(f"{f.passengers.children} أطفال")
            if f.passengers.infants:
                pax_parts.append(f"{f.passengers.infants} رضيع")
            pax_summary = " ، ".join(pax_parts) if pax_parts else "2 بالغين"

            # Baggage formatting (separate checked vs cabin baggage cleanly without duplication)
            raw_luggage = (f.luggage or "25 كجم").strip()
            raw_luggage = re.sub(r"(?:لكل\s*مسافر|للمسافر)\s*$", "", raw_luggage).strip(" /+-،")
            cabin_weight = "7 كجم"
            plus_split = re.split(r"\+|،|و(?=\s*\d+\s*(?:كجم|كيلو)\s*(?:كابينة|يد))", raw_luggage)
            if len(plus_split) >= 2 and any(k in plus_split[-1] for k in ["كابينة", "يد", "7", "8", "10"]):
                main_weight = plus_split[0].strip()
                cw_raw = plus_split[-1].strip()
                cw_m = re.search(r"(\d+\s*(?:كجم|كيلو))", cw_raw)
                if cw_m:
                    cabin_weight = cw_m.group(1).strip()
                else:
                    cabin_weight = re.sub(r"(?:كابينة|حقيبة\s*يد|يد|لكل\s*مسافر)", "", cw_raw).strip() or "7 كجم"
            elif raw_luggage == "1":
                main_weight = "1 قطعة (23 كجم)"
            elif re.match(r"^\d+$", raw_luggage):
                main_weight = f"{raw_luggage} قطعة (23 كجم)"
            else:
                main_weight = raw_luggage

            # Resolve timings & segments
            dep_note = ""
            arr_note = ""
            if is_transit:
                seg1 = segments[0] if len(segments) >= 1 else None
                seg2 = segments[1] if len(segments) >= 2 else None

                seg1_dep = (seg1.departure_time if seg1 and seg1.departure_time else f.departure_time) or ""
                if seg2:
                    seg1_arr = (seg1.arrival_time if seg1 and seg1.arrival_time else "") or ""
                    seg2_dep = (seg2.departure_time if seg2 and seg2.departure_time else "") or ""
                    final_arr = (seg2.arrival_time if seg2 and seg2.arrival_time else f.arrival_time) or ""
                else:
                    seg1_arr = ""
                    seg2_dep = ""
                    final_arr = f.arrival_time or (seg1.arrival_time if seg1 else "") or ""

                transit_ap = (
                    getattr(f, "transit_airport", None)
                    or (seg1.to_airport if seg1 and seg2 else None)
                    or (seg2.from_airport if seg2 else None)
                    or "مطار الترانزيت"
                )
                transit_code = _get_iata_code(transit_ap)
                transit_city = _get_short_city(transit_ap)
                transit_ap_clean = _get_airport_only(transit_ap)
                transit_dur = (
                    getattr(f, "transit_duration", None)
                    or (seg1.transit_duration if seg1 else None)
                    or (seg2.transit_duration if seg2 else None)
                    or "ترانزيت"
                )

                # Estimate seg1_arr if missing
                if not seg1_arr and seg1_dep and origin_code and transit_code:
                    est1 = ROUTE_ESTIMATES.get((origin_code, transit_code))
                    dep1_m = _parse_mins(seg1_dep)
                    if est1 and dep1_m is not None:
                        seg1_arr = _mins_to_ar(dep1_m + est1[0])

                # Estimate final_arr if missing
                if not final_arr and seg2_dep and transit_code and dest_code:
                    est2 = ROUTE_ESTIMATES.get((transit_code, dest_code))
                    dep2_m = _parse_mins(seg2_dep)
                    if est2 and dep2_m is not None:
                        final_arr = _mins_to_ar(dep2_m + est2[0])

                # Calculate total journey duration if possible
                est1 = ROUTE_ESTIMATES.get((origin_code, transit_code))
                est2 = ROUTE_ESTIMATES.get((transit_code, dest_code))
                t_mins = _parse_dur_mins(transit_dur)
                if est1 and est2 and t_mins > 0:
                    total_dur_str = _format_duration_ar(est1[1] + t_mins + est2[1])
                else:
                    total_dur_str = f"ترانزيت ({transit_dur})"

                dep_num, dep_period, dep_note = _split_time_parts(seg1_dep)
                arr_num, arr_period, arr_note = _split_time_parts(final_arr) if final_arr else ("--:--", "حسب الجدول", "")
            else:
                dep_raw = f.departure_time or ""
                arr_raw = getattr(f, "arrival_time", None) or ""
                est_direct = ROUTE_ESTIMATES.get((origin_code, dest_code))
                if not arr_raw and dep_raw and est_direct:
                    dep_m = _parse_mins(dep_raw)
                    if dep_m is not None:
                        arr_raw = _mins_to_ar(dep_m + est_direct[0])
                total_dur_str = est_direct[2] if est_direct else "رحلة مباشرة"
                dep_num, dep_period, dep_note = _split_time_parts(dep_raw)
                arr_num, arr_period, arr_note = _split_time_parts(arr_raw) if arr_raw else ("--:--", "توقيت محلي", "")

            # Detect cabin class if mentioned in flight_type (e.g. درجة رجال الأعمال / الدرجة الأولى)
            cabin_badge_suffix = ""
            if "رجال الأعمال" in combined_type_str or "بزنس" in combined_type_str or "Business" in combined_type_str:
                cabin_badge_suffix = " - درجة رجال الأعمال"
            elif "الدرجة الأولى" in combined_type_str or "درجة أولى" in combined_type_str or "First Class" in combined_type_str:
                cabin_badge_suffix = " - الدرجة الأولى"

            # Choose theme colors & badges based on flight category (No Open-Jaw or Multi-City jargon)
            if is_return:
                # Theme 3: Indigo / Return Leg
                card_border = "border-indigo-200"
                header_bg = "bg-gradient-to-r from-indigo-700 via-indigo-800 to-[#0E446E]"
                header_sub_text = "text-indigo-200"
                header_icon = '<path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                header_badge_title = ("رحلة العودة (ترانزيت)" if is_transit else "رحلة العودة (مباشرة)") + cabin_badge_suffix
                sidebar_bg = "bg-indigo-50/40 border-indigo-200"
                sidebar_title_cls = "text-indigo-950 border-indigo-200"
                sidebar_box_border = "border-indigo-200/70"
                sidebar_icon_cls = "text-indigo-800"
                sidebar_bag_cls = "text-indigo-900"
                sidebar_footer_border = "border-indigo-200/60"
                sidebar_footer_text = "text-indigo-900"
                dest_time_cls = "text-indigo-900"
                dest_period_cls = "text-indigo-700"
                dest_pill_cls = "text-indigo-800 bg-indigo-100/70"
                dest_code_cls = "text-indigo-950"
            elif is_domestic_or_euro:
                # Theme 2: Emerald / Domestic or Intermediate Flight
                card_border = "border-emerald-300"
                header_bg = "bg-gradient-to-r from-emerald-600 via-emerald-600 to-teal-700"
                header_sub_text = "text-emerald-100"
                header_icon = '<path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                if "أوروبي" in combined_type_str and "داخلي" not in combined_type_str:
                    base_dom_title = "رحلة طيران أوروبي (ترانزيت)" if is_transit else "رحلة طيران أوروبي (مباشرة)"
                else:
                    base_dom_title = "رحلة داخلية (ترانزيت)" if is_transit else "رحلة داخلية (مباشرة)"
                header_badge_title = base_dom_title + cabin_badge_suffix
                sidebar_bg = "bg-emerald-50/50 border-emerald-200"
                sidebar_title_cls = "text-emerald-950 border-emerald-200"
                sidebar_box_border = "border-emerald-200/70"
                sidebar_icon_cls = "text-emerald-800"
                sidebar_bag_cls = "text-emerald-800"
                sidebar_footer_border = "border-emerald-200/60"
                sidebar_footer_text = "text-emerald-900"
                dest_time_cls = "text-emerald-700"
                dest_period_cls = "text-emerald-800"
                dest_pill_cls = "text-emerald-800 bg-emerald-100/70"
                dest_code_cls = "text-emerald-900"
            else:
                # Theme 1: Orange / International Outbound Flight
                card_border = "border-[#F9A272]"
                header_bg = "bg-gradient-to-r from-orange-500 via-[#EB5E18] to-orange-600"
                header_sub_text = "text-orange-100"
                header_icon = '<path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                header_badge_title = ("رحلة ترانزيت دولية" if is_transit else "رحلة دولية مباشرة") + cabin_badge_suffix
                sidebar_bg = "bg-[#FFF6F0]/60 border-orange-200"
                sidebar_title_cls = "text-orange-950 border-orange-200/80"
                sidebar_box_border = "border-orange-200/70"
                sidebar_icon_cls = "text-[#0E446E]"
                sidebar_bag_cls = "text-[#EB5E18]"
                sidebar_footer_border = "border-orange-200/60"
                sidebar_footer_text = "text-[#0E446E]"
                dest_time_cls = "text-emerald-700"
                dest_period_cls = "text-emerald-800"
                dest_pill_cls = "text-emerald-800 bg-emerald-100/70"
                dest_code_cls = "text-emerald-900"

            # Middle Track & Bottom Callout Box
            if is_transit:
                tran_code_label = f" ({transit_code})" if transit_code else ""
                transit_ap_display = transit_ap if (not transit_code or transit_code in transit_ap) else f"{transit_ap}{tran_code_label}"
                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-slate-600 mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>⏱ المدة الإجمالية:</span>
                    <span class="text-[#0E446E]">{html.escape(total_dur_str)}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-slate-300 min-w-[8px]"></div>
                    <div class="badge bg-white px-2.5 py-0.5 rounded-full border border-amber-300 shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-amber-800 inline-flex items-center justify-center gap-1 flex-wrap leading-tight">
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                        <span>ترانزيت بـ {html.escape(transit_city)}{html.escape(tran_code_label)}</span>
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-slate-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 text-[#EB5E18] transform rotate-180 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">توقف في {html.escape(transit_ap_clean)}{html.escape(tran_code_label)}</span>
                </div>
                """

                bottom_callout_html = f"""
                <!-- Transit Highlight Callout Box -->
                <div class="info-box bg-amber-50/90 border border-amber-200/90 rounded-xl p-3 space-y-2 text-xs">
                  <div class="flex items-start gap-2">
                    <span class="p-1.5 bg-amber-200 text-amber-900 rounded-lg shrink-0 mt-0.5">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                    </span>
                    <div class="min-w-0 flex-1">
                      <span class="font-bold text-amber-950 text-xs block leading-snug">محطة التوقف والترانزيت: {html.escape(transit_ap_display)}</span>
                      <span class="text-amber-800 text-[11px] font-num block mt-0.5 leading-snug">وصول {html.escape(transit_city)}: <strong>{html.escape(seg1_arr or '—')}</strong> &nbsp;|&nbsp; إقلاع {html.escape(transit_city)}: <strong>{html.escape(seg2_dep or '—')}</strong></span>
                    </div>
                  </div>
                  <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-amber-200/70">
                    <span class="badge font-bold text-amber-900 bg-amber-100 px-2.5 py-1 rounded-md border border-amber-300 font-num text-[11px]">
                      ⏱ انتظار: {html.escape(transit_dur)}
                    </span>
                    <span class="badge inline-flex items-center gap-1 font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200 text-[11px]">
                      <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                      <span>الأمتعة مشحونة مباشرة للوجهة النهائية</span>
                    </span>
                  </div>
                </div>
                """
            elif is_return:
                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-indigo-900 mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>⏱ المدة: {html.escape(total_dur_str)}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-indigo-300 min-w-[8px]"></div>
                    <div class="badge bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-indigo-900 leading-tight">
                        طيران مباشر بدون توقف
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-indigo-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 text-indigo-600 transform rotate-180 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">وصول مباشر إلى {html.escape(dest_ap_clean)}</span>
                </div>
                """
                bottom_callout_html = f"""
                <div class="info-box bg-indigo-50/70 border border-indigo-200/80 rounded-xl p-3 flex flex-wrap items-center justify-between text-xs text-indigo-950 gap-2">
                  <div class="flex items-start gap-2 min-w-0 flex-1">
                    <span class="p-1 bg-indigo-200/80 rounded text-indigo-800 font-bold shrink-0">ℹ️</span>
                    <span class="leading-snug"><strong>التوقيتات:</strong> جميع أوقات الإقلاع والوصول موضحة بالتوقيت المحلي لكل دولة ومطار بدقة.</span>
                  </div>
                  <div class="flex items-center gap-2 font-semibold text-indigo-900">
                    <span>{html.escape(airline_short)}</span>
                  </div>
                </div>
                """
            else:
                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-emerald-800 mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>⏱ المدة: {html.escape(total_dur_str)}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-emerald-300 min-w-[8px]"></div>
                    <div class="badge bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-emerald-800 leading-tight">
                        طيران مباشر بدون توقف
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-emerald-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 text-emerald-600 transform rotate-180 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">رحلة سريعة ومباشرة بين المدينتين</span>
                </div>
                """
                bottom_callout_html = f"""
                <div class="info-box bg-emerald-50 border border-emerald-200 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 text-xs text-emerald-900">
                  <div class="flex items-start gap-2 min-w-0 flex-1">
                    <span class="text-emerald-600 font-bold shrink-0">✓</span>
                    <span class="leading-snug"><strong>رحلة مباشرة بالكامل:</strong> بدون أي محطات توقف أو تغيير للطائرة، وصول سريع ومباشر.</span>
                  </div>
                  <span class="font-semibold text-slate-600">{html.escape(airline_en)}</span>
                </div>
                """

            dep_note_html = f'<div class="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 mt-0.5 inline-block">{html.escape(dep_note)}</div>' if dep_note else ""
            arr_note_html = f'<div class="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 mt-0.5 inline-block">{html.escape(arr_note)}</div>' if arr_note else ""

            card_html = f"""
            <div class="flight-card card bg-white rounded-2xl border-2 {card_border} shadow-sm overflow-hidden transition-all hover:shadow-md avoid-break">
              <!-- Card Header Strip -->
              <div class="{header_bg} px-4 py-2.5 text-white flex flex-wrap items-center justify-between gap-2">
                <div class="flex flex-wrap items-center gap-2 min-w-0">
                  <span class="badge inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/20 backdrop-blur-sm text-xs font-bold border border-white/30 text-white">
                    <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {header_icon}
                    </svg>
                    <span>{header_badge_title}</span>
                  </span>
                  <span class="text-xs font-semibold {header_sub_text} font-num">الرحلة رقم {idx}</span>
                </div>
                <div class="flex flex-wrap items-center gap-3 text-xs min-w-0">
                  <div class="flex items-center gap-1">
                    <span class="{header_sub_text}">التاريخ:</span>
                    <span class="badge font-bold text-white bg-white/20 px-2 py-0.5 rounded-md font-num">{html.escape(f.date)}</span>
                  </div>
                  <div class="flex items-center gap-1 sm:border-r sm:border-white/25 sm:pr-3 min-w-0">
                    <span class="{header_sub_text}">الناقل الجوي:</span>
                    <span class="font-bold text-white">{html.escape(airline_full)}</span>
                  </div>
                </div>
              </div>

              <!-- Card Body Grid -->
              <div class="card-body p-4 grid grid-cols-1 sm:grid-cols-12 gap-4 items-stretch">
                <!-- Visual Timeline Column -->
                <div class="sm:col-span-8 min-w-0 flex flex-col justify-between space-y-3">
                  <!-- Timeline Main Path -->
                  <div class="info-box bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
                    <div class="flex-container flex flex-col sm:flex-row items-center justify-between gap-3 relative">
                      <!-- Origin Station -->
                      <div class="flex-1 min-w-0 text-center sm:text-right w-full sm:w-auto">
                        <span class="text-[11px] font-semibold text-slate-500 block mb-0.5">مغادرة من</span>
                        <div class="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight font-num">{html.escape(dep_num)} <span class="text-xs font-semibold text-slate-600 font-sans">{html.escape(dep_period)}</span></div>
                        {dep_note_html}
                        <div class="font-bold text-slate-900 text-xs mt-1 leading-snug">{html.escape(origin_ap_clean)}</div>
                        <div class="badge inline-flex flex-wrap items-center gap-1 mt-1 text-[11px] font-bold text-[#0E446E] bg-sky-100/70 px-2 py-0.5 rounded max-w-full">
                          <span>{html.escape(origin_city)}</span>
                          <span class="text-[10px] font-mono font-bold text-sky-800">{html.escape(origin_code)}</span>
                        </div>
                      </div>

                      <!-- Journey Flow Line & Duration -->
                      {middle_track_html}

                      <!-- Destination Station -->
                      <div class="flex-1 min-w-0 text-center sm:text-left w-full sm:w-auto">
                        <span class="text-[11px] font-semibold text-slate-500 block mb-0.5">{'وصول نهائي إلى' if is_transit else 'وصول مباشر إلى'}</span>
                        <div class="text-xl md:text-2xl font-extrabold {dest_time_cls} tracking-tight font-num">{html.escape(arr_num)} <span class="text-xs font-semibold {dest_period_cls} font-sans">{html.escape(arr_period)}</span></div>
                        {arr_note_html}
                        <div class="font-bold text-slate-900 text-xs mt-1 leading-snug">{html.escape(dest_ap_clean)}</div>
                        <div class="badge inline-flex flex-wrap items-center gap-1 mt-1 text-[11px] font-bold {dest_pill_cls} px-2 py-0.5 rounded max-w-full">
                          <span>{html.escape(dest_city)}</span>
                          <span class="text-[10px] font-mono font-bold {dest_code_cls}">{html.escape(dest_code)}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Bottom Callout Box -->
                  {bottom_callout_html}
                </div>

                <!-- Meta Sidebar Details (Luggage & Passengers) -->
                <div class="sm:col-span-4 min-w-0 {sidebar_bg} border rounded-xl p-3.5 flex flex-col justify-between gap-3">
                  <div>
                    <h4 class="text-xs font-bold {sidebar_title_cls} uppercase tracking-wider mb-2.5 pb-1 border-b">بيانات التذكرة والركاب</h4>
                    <div class="space-y-2.5">
                      <!-- Passengers -->
                      <div class="info-box flex flex-wrap items-center justify-between gap-1.5 text-xs bg-white/90 p-2.5 rounded-lg border {sidebar_box_border}">
                        <span class="text-slate-600 font-medium flex items-center gap-1.5">
                          <svg class="w-4 h-4 shrink-0 {sidebar_icon_cls}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                          <span>المسافرين:</span>
                        </span>
                        <span class="badge font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded font-num">{html.escape(pax_summary)}</span>
                      </div>
                      <!-- Baggage -->
                      <div class="info-box bg-white/90 p-2.5 rounded-lg border {sidebar_box_border} space-y-1.5 text-xs">
                        <div class="flex flex-wrap items-center justify-between gap-1">
                          <span class="text-slate-600 font-medium flex items-center gap-1.5">
                            <svg class="w-4 h-4 shrink-0 {sidebar_bag_cls}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                            <span>أمتعة الشحن:</span>
                          </span>
                          <span class="font-extrabold {sidebar_bag_cls} text-xs md:text-sm font-num">{html.escape(main_weight)} <span class="text-[10px] font-normal text-slate-500">/ للمسافر</span></span>
                        </div>
                        <div class="flex flex-wrap items-center justify-between gap-1 text-[11px] pt-1 border-t border-slate-100 text-slate-500 font-num">
                          <span>حقيبة اليد (الكابينة):</span>
                          <span class="font-bold text-slate-800">{html.escape(cabin_weight)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- Airline Footer Badge -->
                  <div class="text-[11px] text-slate-600 pt-2 border-t {sidebar_footer_border} flex flex-wrap items-center justify-between gap-1">
                    <span class="text-slate-500">طيران الرحلة:</span>
                    <span class="font-semibold {sidebar_footer_text}">{html.escape(airline_short)}</span>
                  </div>
                </div>
              </div>
            </div>
            """
            flight_cards.append(card_html)

        flights_html = f"""
        <!-- SECTION: FLIGHT BOOKING (Timeline Cards Stack) -->
        <section class="space-y-4 pt-2" data-purpose="flight-section">
          <!-- Header: Top Navy Pill Badge -->
          <header class="flex justify-center section-pill-badge" data-purpose="section-header">
            <div class="inline-flex items-center gap-2.5 px-8 py-2.5 bg-[#0E446E] hover:bg-[#0A3150] text-white rounded-full shadow-md transition-colors duration-200">
              <svg class="w-5 h-5 -scale-x-100 transform" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
              </svg>
              <h2 class="text-base md:text-lg font-bold tracking-normal select-none">
                {flight_title}
              </h2>
            </div>
          </header>
          <!-- Flight Cards Stack -->
          <div class="space-y-4" data-purpose="flight-cards-stack">
            {"".join(flight_cards)}
          </div>
        </section>
        """

    # 3. TRANSPORTS, TRAINS & TOURS SECTION
    transports_html = ""
    if pkg.transports and len(pkg.transports) > 0:
        has_car_rental = bool(pkg.car_rentals and len(pkg.car_rentals) > 0)
        all_items_flat = [it for g in pkg.transports for it in g.items]
        has_trains = any(
            any(w in (it.title or "") or w in (it.vehicle_type or "") for w in ["قطار", "Railjet", "EuroCity", "Train"])
            for it in all_items_flat
        )
        all_trains = bool(all_items_flat) and all(
            any(w in (it.title or "") or w in (it.vehicle_type or "") for w in ["قطار", "Railjet", "EuroCity", "Train"])
            for it in all_items_flat
        )

        if all_trains:
            section_title = "حجز القطارات والتنقلات السياحية"
            section_icon = "🚆"
        elif has_trains:
            section_title = "المواصلات والقطارات السياحية"
            section_icon = "🚆"
        elif has_car_rental:
            section_title = "الأنشطة والمسارات السياحية المقترحة"
            section_icon = "🗺️"
        else:
            section_title = "المواصلات والجولات السياحية"
            section_icon = "🚗"

        city_blocks = []
        for grp in pkg.transports:
            grp_is_train = any(
                any(w in (it.title or "") or w in (it.vehicle_type or "") for w in ["قطار", "Railjet", "EuroCity", "Train"])
                for it in grp.items
            )
            item_rows = []
            for item in grp.items:
                item_is_train = any(w in (item.title or "") or w in (item.vehicle_type or "") for w in ["قطار", "Railjet", "EuroCity", "Train"])
                activities_html = ""
                if item.activities:
                    # Check if activities are structured key:value lines (like وقت المغادرة:, وقت الوصول:, نوع التذكرة:)
                    has_kv_details = any(":" in a for a in item.activities)
                    if has_kv_details or item_is_train:
                        detail_lines = []
                        for a in item.activities:
                            if ":" in a:
                                k, v = a.split(":", 1)
                                icon = "🕒" if "وقت" in k or "مغادرة" in k or "وصول" in k else ("🎫" if "تذكرة" in k or "درجة" in k else "▪️")
                                detail_lines.append(
                                    f'<div class="text-xs text-slate-700 mt-1 flex items-start gap-1.5 bg-slate-50 border border-slate-200/80 rounded-lg px-2.5 py-1">'
                                    f'<span>{icon}</span>'
                                    f'<span><strong class="text-[#083344]">{html.escape(k.strip())}:</strong> {html.escape(v.strip())}</span>'
                                    f'</div>'
                                )
                            else:
                                detail_lines.append(f'<div class="text-xs text-slate-600 mt-1">• {html.escape(a)}</div>')
                        activities_html = f'<div class="mt-1.5 space-y-1">{"".join(detail_lines)}</div>'
                    else:
                        acts = " | ".join([f"{html.escape(a)}" for a in item.activities])
                        activities_html = f'<div class="text-[11px] text-slate-500 font-normal mt-0.5">{acts}</div>'

                route_html = (
                    f'<div class="text-[11px] text-slate-500 font-normal mt-0.5">{html.escape(item.route_details)}</div>'
                    if item.route_details
                    else ""
                )

                if item_is_train:
                    veh_label = f"🚆 {html.escape(item.vehicle_type)}"
                elif has_car_rental:
                    veh_label = "بالسيارة المستأجرة"
                else:
                    veh_label = html.escape(item.vehicle_type)

                row = f"""
                <tr class="hover:bg-sky-50/40 transition avoid-break">
                  <!-- Flight / Transport Date -->
                  <td class="p-3 font-num text-slate-800 font-bold whitespace-nowrap align-top">{html.escape(item.date)}</td>
                  <!-- Day Label -->
                  <td class="p-3 font-bold text-slate-800 whitespace-nowrap align-top">{html.escape(item.day_label)}</td>
                  <!-- Vehicle Type Badge -->
                  <td class="p-3 text-center whitespace-nowrap align-top">
                    <span class="inline-block border border-sky-300 bg-sky-50 text-[#0284c7] font-bold px-3 py-1 rounded-full text-xs shadow-sm">{veh_label}</span>
                  </td>
                  <!-- Description & Route -->
                  <td class="p-3 text-right align-top">
                    <div class="font-bold text-slate-900 text-xs md:text-sm">{html.escape(item.title)}</div>
                    {route_html}
                    {activities_html}
                  </td>
                </tr>
                """
                item_rows.append(row)

            if grp_is_train:
                city_badge_text = "تذاكر قطار ومقاعد مؤكدة"
                city_title_text = f"🚆 مسار القطار السريع: {html.escape(grp.city_name)}"
                scope_note = """
                  <div class="text-[11px] text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                    <span>🚆</span>
                    <span>تشمل تذاكر القطار السريع مع حجز المقاعد والأمتعة المحددة بين المحطات المركزية.</span>
                  </div>
                """
                veh_col_title = "وسيلة التنقل"
            elif has_car_rental:
                city_badge_text = "قيادة ذاتية (مسار مقترح)"
                city_title_text = f"📍 مسار وجولات مقترحة: {html.escape(grp.city_name)}"
                scope_note = """
                  <div class="text-[11px] text-teal-900 bg-teal-50 border border-teal-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                    <span>💡</span>
                    <span>برنامج وجولات مقترحة يمكنكم زيارتها بالسيارة المستأجرة بأريحية تامة حسب رغبتكم.</span>
                  </div>
                """
                veh_col_title = "وسيلة التنقل"
            else:
                city_badge_text = "سيارة خاصة مع سائق"
                city_title_text = f"📍 جولات ومواصلات: {html.escape(grp.city_name)}"
                scope_note = """
                  <div class="text-[11px] text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                    <span>ℹ️</span>
                    <span>تشمل الجولات والتنقلات بسائق خاص داخل المدينة، والمسارات اختيارية وقابلة للتعديل حسب رغبتكم.</span>
                  </div>
                """
                veh_col_title = "نوع السيارة"

            block = f"""
            <div class="border-2 border-sky-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden avoid-break">
              <!-- City Header Navy Bar -->
              <div class="bg-[#083344] text-white px-4 py-2 rounded-xl font-bold text-xs md:text-sm flex items-center justify-between shadow-sm">
                <span>{city_title_text}</span>
                <span class="bg-[#0284c7] text-white px-3 py-1 rounded-full text-xs font-bold shadow-sm">{city_badge_text}</span>
              </div>
              {scope_note}
              <!-- Table -->
              <div class="overflow-x-auto border border-sky-200 rounded-xl shadow-sm">
                <table class="w-full text-center border-collapse text-xs md:text-sm">
                  <thead>
                    <tr class="bg-gradient-to-r from-[#0284c7] to-[#0369a1] text-white font-bold divide-x divide-white/20">
                      <th class="py-2.5 px-3 whitespace-nowrap" style="width: 15%;">التاريخ</th>
                      <th class="py-2.5 px-3 whitespace-nowrap" style="width: 15%;">اليوم</th>
                      <th class="py-2.5 px-3 whitespace-nowrap" style="width: 22%;">{veh_col_title}</th>
                      <th class="py-2.5 px-4 text-right" style="width: 48%;">الوصف والمسار</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-200 text-slate-700 font-semibold bg-white">
                    {"".join(item_rows)}
                  </tbody>
                </table>
              </div>
            </div>
            """
            city_blocks.append(block)

        transports_html = f"""
        <!-- SECTION: TRANSPORTS & TOURS -->
        <section class="space-y-4 pt-2" data-purpose="transports-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-[#0b4f71] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-sky-200">
              <span>{section_icon}</span>
              <span class="tracking-wide">{section_title}</span>
            </div>
          </div>
          <div class="space-y-4">
            {"".join(city_blocks)}
          </div>
        </section>
        """

    # 4. CAR RENTALS SECTION
    car_rentals_html = ""
    if pkg.car_rentals and len(pkg.car_rentals) > 0:
        car_cards = []
        for c in pkg.car_rentals:
            days_pill = f'<span class="bg-sky-900/40 text-white text-[11px] px-2 py-0.5 rounded-full border border-sky-300/40 font-num">{c.days_count} أيام</span>' if c.days_count else ''
            card = f"""
            <div class="border-2 border-teal-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden avoid-break">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <span class="bg-teal-600 text-white text-xs md:text-sm font-bold px-4 py-1 rounded-full shadow-sm">
                    استئجار سيارة
                  </span>
                  <div class="bg-[#0284c7] text-white text-xs md:text-sm font-bold px-3 py-1 rounded-full flex items-center gap-2 shadow-sm">
                    <span>{html.escape(c.car_model)}</span>
                    {days_pill}
                  </div>
                </div>
                <span class="bg-slate-100 text-slate-700 text-xs font-bold px-3 py-1 rounded-full border border-slate-300">
                  {html.escape(c.driver_type)}
                </span>
              </div>
              <div class="bg-[#083344] text-white rounded-xl px-4 py-2 text-xs md:text-sm font-bold grid grid-cols-3 text-center items-center shadow-inner">
                <div class="border-l border-sky-300/40">🛡️ {html.escape(c.insurance)}</div>
                <div class="border-l border-sky-300/40">⚙️ {html.escape(c.transmission)}</div>
                <div>🛣️ {html.escape(c.mileage)}</div>
              </div>
              <div class="bg-gradient-to-r from-teal-600 to-[#0284c7] text-white rounded-xl px-4 py-2 font-bold text-xs md:text-sm flex flex-wrap items-center justify-between gap-2 shadow text-center font-num">
                <span>📍 الاستلام: {html.escape(c.pickup_location)} ({html.escape(c.pickup_date)})</span>
                <span class="hidden sm:inline">&gt;&gt;&gt;</span>
                <span>🏁 التسليم: {html.escape(c.dropoff_location)} ({html.escape(c.dropoff_date)})</span>
              </div>
            </div>
            """
            car_cards.append(card)

        car_rentals_html = f"""
        <!-- SECTION 4: CAR RENTALS -->
        <section class="space-y-3 pt-1" data-purpose="car-rentals-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#0f766e] via-[#0d9488] to-[#14b8a6] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-teal-300">
              <span>🚘</span>
              <span class="tracking-wide">استئجار السيارات الخاصة</span>
            </div>
          </div>
          <div class="space-y-3">
            {"".join(car_cards)}
          </div>
        </section>
        """

    # 5. EXTRA SERVICES SECTION
    extra_services_html = ""
    if pkg.extra_services and len(pkg.extra_services) > 0:
        svc_rows = []
        for s in pkg.extra_services:
            row = f"""
            <tr class="hover:bg-sky-50/40 transition avoid-break">
              <td class="p-2.5 font-bold text-slate-900 font-num">{s.quantity}</td>
              <td class="p-2.5 font-bold text-slate-900 text-right">{html.escape(s.service_name)}</td>
              <td class="p-2.5 text-slate-700">{html.escape(s.country)}</td>
              <td class="p-2.5 text-slate-700 font-num">{html.escape(s.date)}</td>
              <td class="p-2.5 font-bold text-[#0b4f71]">{html.escape(s.day_label)}</td>
            </tr>
            """
            svc_rows.append(row)

        extra_services_html = f"""
        <!-- SECTION 5: EXTRA SERVICES -->
        <section class="space-y-3 pt-1" data-purpose="extra-services-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#9d174d] via-[#db2777] to-[#f43f5e] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-pink-300">
              <span>🎁</span>
              <span class="tracking-wide">الخدمات والهدايا المشمولة</span>
            </div>
          </div>
          <div class="overflow-x-auto border border-pink-200 rounded-xl shadow-sm avoid-break">
            <table class="w-full text-center border-collapse text-xs md:text-sm">
              <thead>
                <tr class="bg-gradient-to-r from-pink-600 to-purple-600 text-white font-bold divide-x divide-white/20">
                  <th class="py-2 px-2" style="width: 15%;">العدد</th>
                  <th class="py-2 px-3 text-right" style="width: 45%;">اسم الخدمة</th>
                  <th class="py-2 px-2" style="width: 15%;">الدولة</th>
                  <th class="py-2 px-2" style="width: 15%;">التاريخ</th>
                  <th class="py-2 px-2" style="width: 10%;">اليوم</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 text-slate-700 font-semibold bg-white">
                {"".join(svc_rows)}
              </tbody>
            </table>
          </div>
        </section>
        """

    # 6. TOTAL PRICE & TERMS
    total_price_display = ""
    if pkg.total_price and pkg.total_price.amount:
        total_price_display = f"""
        <div class="bg-gradient-to-br from-[#083344] via-[#0b4f71] to-[#01579b] text-white rounded-2xl p-4 md:p-5 shadow-md flex items-center justify-between gap-4 border-2 border-sky-200 avoid-break">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-amber-400 text-slate-900 flex items-center justify-center font-black text-2xl shadow shrink-0">
              💰
            </div>
            <div>
              <div class="text-xs md:text-sm text-sky-200 font-bold">الإجمالي الكلي النهائي للعرض السياحي:</div>
              <div class="text-[11px] md:text-xs text-sky-300">شامل كافة الضرائب، الرسوم السياحية، والمصروفات المذكورة</div>
            </div>
          </div>
          <div class="text-left bg-white/10 px-5 py-2 rounded-xl border border-white/20 shadow-inner shrink-0 whitespace-nowrap">
            <span class="text-2xl md:text-3xl font-black text-amber-400 font-num tracking-tight">{html.escape(pkg.total_price.amount)}</span>
            <span class="text-xs text-white font-bold mr-1">{html.escape(pkg.total_price.currency)}</span>
          </div>
        </div>
        """

    # Terms & Notes banner
    effective_notes = pkg.notes if (pkg.notes and len(pkg.notes) > 0) else get_smart_notes_for_package(pkg)
    notes_items = "".join([
        f'<li class="flex items-start gap-2"><span class="text-[#0E446E] font-bold text-base leading-none">•</span><span>{html.escape(n)}</span></li>'
        for n in effective_notes
    ])
    notes_list_html = f"""
    <section class="bg-[#EFF6FA] border border-[#C7E2F3] rounded-2xl p-5 md:p-6 text-slate-800 space-y-3.5 shadow-sm avoid-break" data-purpose="terms-and-conditions">
      <div class="flex items-center gap-2 text-slate-900 font-bold text-base md:text-lg border-b border-[#C7E2F3] pb-2.5">
        <span class="text-xl">📌</span>
        <h2>الشروط والملاحظات المهمة:</h2>
      </div>
      <ul class="space-y-2.5 text-xs md:text-sm leading-relaxed text-slate-700">
        {notes_items}
      </ul>
    </section>
    """

    # Master HTML Document
    full_html = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>عرض سعر سياحي - {html.escape(meta.company_name)} ({html.escape(meta.destination)})</title>

<!-- Google Fonts: Cairo & Tajawal -->
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Tajawal:wght@400;500;700;800;900&display=swap" rel="stylesheet">

<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script data-purpose="tailwind-config">
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              navy: '#0E446E',
              darkNavy: '#0A3150',
              orange: '#EB5E18',
              orangeLight: '#FFF6F0',
              orangeBorder: '#F9A272',
              blueBg: '#EFF6FA',
              blueBorder: '#C7E2F3',
            }},
            attar: {{
              cyan: '#38bdf8',
              teal: '#0284c7',
              navy: '#0b4f71',
              darkNavy: '#083344',
              orange: '#f97316',
              deepOrange: '#ea580c',
              softBg: '#f8fafc',
              cardBorder: '#38bdf8',
            }}
          }},
          fontFamily: {{
            sans: ['Cairo', 'sans-serif'],
            cairo: ['Cairo', 'sans-serif'],
            tajawal: ['Tajawal', 'sans-serif'],
          }}
        }}
      }}
    }}
</script>

<style data-purpose="custom-styling">
    body {{
      font-family: 'Cairo', 'Tajawal', sans-serif;
      -webkit-font-smoothing: antialiased;
      background-color: #5d6d7e;
      direction: rtl;
    }}

    .font-num {{
      font-feature-settings: "tnum";
      font-variant-numeric: tabular-nums;
    }}

    /* 1. منع النص من الخروج خارج الحاوية وتطبيقه على التفاف الكلمات */
    .card, .info-box, .badge, div {{
      word-wrap: break-word;
      overflow-wrap: break-word;
      white-space: normal;
    }}

    /* 2. ضبط الكروت والحاويات الداخلية لمنع الخروج الأفقي */
    .flight-card, .card-body {{
      max-width: 100%;
      box-sizing: border-box;
      overflow: hidden;
    }}

    /* 3. ضبط الـ Flexbox / Grid إذا كانت الكروت تستخدم Flex */
    .flex-container > div,
    .card-body > div {{
      min-width: 0;
      flex-shrink: 1;
    }}

    /* 4. معالجة النصوص الطويلة أو أسماء الطيران */
    .text-truncated {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    /* Print settings for dense, continuous page filling */
    @page {{
      size: A4 portrait;
      margin: 6mm 4mm;
    }}

    @media print {{
      body {{
        background-color: #ffffff !important;
        padding: 0 !important;
        margin: 0 !important;
      }}
      .no-print {{
        display: none !important;
      }}
      .document-shadow {{
        box-shadow: none !important;
        border: none !important;
      }}
      .page-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        border: none !important;
        border-radius: 0 !important;
      }}
      /* Sections must flow naturally into empty space */
      section, main {{
        break-inside: auto !important;
        page-break-inside: auto !important;
      }}
      /* Keep section pill headers with their content */
      .section-pill-badge {{
        break-after: avoid !important;
        page-break-after: avoid !important;
      }}
      /* Only avoid breaking inside cards/rows */
      .avoid-break, tr, [data-purpose^="hotel-card"], footer {{
        break-inside: avoid !important;
        page-break-inside: avoid !important;
      }}
    }}

    .avoid-break {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .section-pill-badge {{
      break-after: avoid;
      page-break-after: avoid;
    }}
</style>
</head>
<body class="min-h-screen py-4 md:py-8 px-2 sm:px-4 flex flex-col items-center justify-start text-slate-800">

<!-- Top level document container matching exact document proportions -->
<div class="page-container w-full max-w-[850px] bg-white rounded-xl shadow-2xl overflow-hidden relative document-shadow border border-slate-200" data-purpose="quotation-sheet">

  <!-- BEGIN: HeaderSection -->
  <header class="relative bg-gradient-to-br from-[#01579b] via-[#0284c7] to-[#0369a1] text-white overflow-hidden shadow-md avoid-break">
    <div class="absolute inset-0 opacity-15 pointer-events-none">
      <svg class="w-full h-full object-cover" preserveAspectRatio="none" viewBox="0 0 850 260" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M-50 180 C 150 120, 350 240, 550 140 C 700 70, 800 190, 950 110 L 950 0 L -50 0 Z" fill="#ffffff" opacity="0.2"></path>
        <path d="M-20 220 C 200 160, 400 270, 650 170 C 780 110, 880 230, 980 160 L 980 0 L -20 0 Z" fill="#38bdf8" opacity="0.25"></path>
      </svg>
    </div>

    <div class="relative z-10 px-6 md:px-10 pt-5 pb-5 space-y-4">
      <!-- Top Row: Company Name + Official Badge -->
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-sky-300/30 pb-3">
        <div class="flex items-center gap-2">
          <h1 class="text-lg md:text-xl font-black text-white font-tajawal drop-shadow-sm">
            {html.escape(meta.company_name)} | {html.escape(meta.company_name_en)}
          </h1>
        </div>
        <div class="flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 px-3.5 py-1 rounded-full shadow-sm text-xs font-bold text-sky-100">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>عرض سعر سياحي رسمي معتمد</span>
        </div>
      </div>

      <!-- Logo Full Width Banner -->
      <div class="w-full bg-white rounded-xl p-3 shadow-md border border-sky-100 flex items-center justify-center overflow-hidden">
        <img alt="{html.escape(meta.company_name)} - {html.escape(meta.company_name_en)}" class="w-full max-h-20 md:max-h-24 object-contain" src="{LOGO_URI}">
      </div>

      <!-- Bottom Row: All 4 Badges Compact and Fitting Perfectly Without Scroll -->
      <div class="pt-2 w-full flex items-center justify-between gap-1 sm:gap-1.5 text-[10px] sm:text-[11px] text-sky-100">
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap">
          <span>🛡️</span>
          <span>الحالة: {html.escape(getattr(meta, 'booking_status', None) or 'حجز مبدئي غير مؤكد')}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>📄</span>
          <span>عرض سعر رقم: {html.escape(meta.quotation_no)}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>🔢</span>
          <span>رقم الحجز: {html.escape(meta.booking_no)}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>📅</span>
          <span>تاريخ الإصدار: {html.escape(getattr(meta, 'issue_date', None) or '21 سبتمبر 2026')}</span>
        </span>
      </div>
    </div>

    <div class="h-2 bg-gradient-to-r from-amber-400 via-[#f97316] to-[#0284c7]"></div>
  </header>
  <!-- END: HeaderSection -->

  <!-- BEGIN: MainContent -->
  <main class="p-4 md:p-6 space-y-4 bg-white">
    {flights_html}
    {car_rentals_html}
    {hotels_html}
    {transports_html}
    {extra_services_html}
    {total_price_display}
    {notes_list_html}
  </main>
  <!-- END: MainContent -->

  <!-- BEGIN: DocumentFooter -->
  <footer class="relative bg-gradient-to-r from-[#014168] via-[#025682] to-[#082a3d] text-white overflow-hidden avoid-break" data-purpose="document-footer">
    <div class="h-1.5 bg-gradient-to-r from-[#ea580c] via-amber-400 to-[#38bdf8]"></div>
    <div class="px-6 py-4 md:px-8 md:py-4.5 space-y-0 relative z-10">
      <!-- Row 1: Brand & Service Badges -->
      <div class="grid grid-cols-3 items-center py-3 text-xs">
        <div class="flex items-center justify-start gap-2 font-bold text-white text-sm">
          <span class="w-6 h-6 rounded-full bg-white/10 border border-amber-400/40 flex items-center justify-center text-xs">📍</span>
          <span>{html.escape(meta.company_name)}</span>
        </div>
        <div class="flex items-center justify-center">
          <div class="bg-white/10 border border-sky-300/30 px-3.5 py-1 rounded-full text-xs font-semibold text-sky-100 flex items-center gap-1.5 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>خدمة العملاء 24/7</span>
          </div>
        </div>
        <div class="flex items-center justify-end gap-1.5 text-xs font-bold text-sky-100">
          <span class="text-amber-400 text-sm">⭐</span>
          <span>وكالة سفر وسياحة معتمدة</span>
        </div>
      </div>

      <!-- Row 2: Contact Hyperlinks -->
      <div class="grid grid-cols-3 items-center py-3.5 border-y border-sky-400/20">
        <div class="flex items-center justify-start">
          <a href="https://wa.me/966555434406" target="_blank" class="flex items-center gap-2 text-xs md:text-sm font-bold text-white hover:text-sky-200 transition font-num">
            <span class="w-7 h-7 rounded-full bg-red-950/40 border border-red-500/40 text-red-400 flex items-center justify-center text-xs shadow-sm">📞</span>
            <span dir="ltr">+966 55 543 4406</span>
          </a>
        </div>
        <div class="flex items-center justify-center">
          <a href="https://attartravel.com" target="_blank" class="flex items-center gap-2 text-xs md:text-sm font-bold text-white hover:text-sky-200 transition tracking-wide">
            <span class="w-7 h-7 rounded-full bg-sky-950/40 border border-sky-400/50 text-sky-300 flex items-center justify-center text-xs shadow-sm">🌐</span>
            <span>ATTARTRAVEL.COM</span>
          </a>
        </div>
        <div class="flex items-center justify-end">
          <a href="mailto:holidays@attartravel.com" class="flex items-center gap-2 text-xs md:text-sm font-bold text-white hover:text-sky-200 transition tracking-wide">
            <span class="w-7 h-7 rounded-full bg-amber-950/40 border border-amber-400/50 text-amber-300 flex items-center justify-center text-xs shadow-sm">✉️</span>
            <span>HOLIDAYS@ATTARTRAVEL.COM</span>
          </a>
        </div>
      </div>

      <!-- Row 3: Rights, License & Verification -->
      <div class="grid grid-cols-3 items-center py-3 text-xs text-sky-200">
        <div class="flex items-center justify-start">
          <span>صُنِع خصيصاً لرحلتكم</span>
        </div>
        <div class="flex items-center justify-center">
          <div class="bg-sky-900/50 border border-sky-300/30 px-3.5 py-0.5 rounded-full text-sky-100 font-semibold font-num text-[11px]">ترخيص سياحي رقم: 73107681</div>
        </div>
        <div class="flex items-center justify-end gap-1.5 text-emerald-400 font-bold">
          <span class="text-xs">✓</span>
          <span>نسخة رسمية صادرة آلياً وموثقة</span>
        </div>
      </div>
    </div>
  </footer>
  <!-- END: DocumentFooter -->

</div>
<!-- END: MainSheetContainer -->

<!-- BEGIN: InteractiveActionButtons -->
<div class="no-print mt-6 mb-8 flex flex-wrap items-center justify-center gap-3" data-purpose="actions-toolbar">
  <button class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" onclick="if(window.parent && typeof window.parent.exportPdf === 'function'){{ window.parent.exportPdf('continuous'); }} else {{ window.printContinuous(); }}">
    <span>⬇️</span>
    <span>تصدير PDF (متصل بدون حدود A4)</span>
  </button>
  <button class="bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" onclick="if(window.parent && typeof window.parent.exportPdf === 'function'){{ window.parent.exportPdf('a4'); }} else {{ window.printA4(); }}">
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
    </svg>
    <span>تصدير PDF (صفحات A4)</span>
  </button>
  <a class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" href="https://wa.me/966555434406" target="_blank">
    <span>💬</span>
    <span>مشاركة عبر واتساب</span>
  </a>
</div>
<!-- END: InteractiveActionButtons -->

<script>
  window.setPrintMode = function(mode) {{
    let styleEl = document.getElementById('dynamic-print-mode-style');
    if (!styleEl) {{
      styleEl = document.createElement('style');
      styleEl.id = 'dynamic-print-mode-style';
      document.head.appendChild(styleEl);
    }}
    if (mode === 'a4') {{
      styleEl.textContent = `
        @page {{
          size: A4 portrait;
          margin: 6mm 4mm;
        }}
      `;
    }} else {{
      const container = document.querySelector('.page-container');
      const h = container ? Math.ceil(container.getBoundingClientRect().height) + 2 : 2000;
      styleEl.textContent = `
        @page {{
          size: 850px ${{h}}px;
          margin: 0mm;
        }}
        @media print {{
          html, body {{
            width: 850px !important;
            height: ${{h}}px !important;
            max-height: ${{h}}px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
          }}
          .page-container {{
            width: 850px !important;
            max-width: 850px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
          }}
        }}
      `;
    }}
  }};

  window.printContinuous = function() {{
    window.setPrintMode('continuous');
    window.print();
  }};

  window.printA4 = function() {{
    window.setPrintMode('a4');
    window.print();
  }};
</script>

</body>
</html>
"""
    return full_html
