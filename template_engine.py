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
from typing import Union, Dict, Any, List, Optional
from models import TravelPackage, get_today_arabic_date, get_today_english_date

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


_AR_TO_EN_COMMON = {
    "المدينة الأولى": "First City",
    "المدينة الثانية": "Second City",
    "المدينة الثالثة": "Third City",
    "المدينة الرابعة": "Fourth City",
    "المدينة الخامسة": "Fifth City",
    "المدينة السادسة": "Sixth City",
    "المدينة السابعة": "Seventh City",
    "المدينة الثامنة": "Eighth City",
    "المنتجع الفاخر": "Luxury Resort",
    "اليوم الأول": "Day 1",
    "اليوم الاول": "Day 1",
    "اليوم الثاني": "Day 2",
    "اليوم الثالث": "Day 3",
    "اليوم الرابع": "Day 4",
    "اليوم الخامس": "Day 5",
    "اليوم السادس": "Day 6",
    "اليوم السابع": "Day 7",
    "اليوم الثامن": "Day 8",
    "اليوم التاسع": "Day 9",
    "اليوم العاشر": "Day 10",
    "اليوم الحادي عشر": "Day 11",
    "اليوم الثاني عشر": "Day 12",
    "اليوم الثالث عشر": "Day 13",
    "اليوم الرابع عشر": "Day 14",
    "اليوم الخامس عشر": "Day 15",
    "شامل الإفطار": "Breakfast Included",
    "شامل الافطار": "Breakfast Included",
    "شامل الإفطار والعشاء": "Half Board (Breakfast & Dinner)",
    "إقامة كاملة": "Full Board",
    "بدون وجبات": "Room Only",
    "غرفة قياسية": "Standard Room",
    "سوبيريور": "Superior Room",
    "ديلوكس": "Deluxe Room",
    "حجز مبدئي غير مؤكد": "Preliminary Unconfirmed Booking",
    "حجز مؤكد": "Confirmed Booking",
    "ريال سعودي": "SAR",
    "ريال": "SAR",
    "درهم إماراتي": "AED",
    "دولار أمريكي": "USD",
    "سيارة صغيرة": "Private Sedan",
    "سيارة خاصة": "Private Car",
    "مرسيدس فيتو VIP": "Mercedes Vito VIP",
    "فان سياحي": "Tourist Van",
    "حافلة سياحية": "Tourist Coach",
    "قطار سياحي سريع": "Fast Tourist Train",
    "قطار سريع (درجة أولى)": "Fast Train (First Class)",
    "أوتوماتيك": "Automatic",
    "كيلومترات مفتوحة": "Unlimited Mileage",
    "كيلومترات مفتوحة غير محدودة": "Unlimited Mileage",
    "بدون سائق (قيادة ذاتية)": "Self-Drive (No Driver)",
    "شامل كلي (Full Coverage)": "Full Coverage",
    "خدمة مشمولة": "Included",
    "طوال الرحلة": "Full Trip",
}


def _tr_val(val: Optional[str], is_en: bool) -> str:
    if not val:
        return ""
    s = str(val).strip()
    if is_en:
        if s in _AR_TO_EN_COMMON:
            return _AR_TO_EN_COMMON[s]
        for ar_k, en_v in _AR_TO_EN_COMMON.items():
            if ar_k in s and len(ar_k) > 4:
                s = s.replace(ar_k, en_v)
        # Replace Arabic time periods if rendering in English
        s = re.sub(r"(?:صباحاً|صباحا|فجراً|فجرا)", "AM", s)
        s = re.sub(r"(?:ظهراً|ظهرا|عصراً|عصرا|مساءً|مساءا|ليلاً|ليلا)", "PM", s)
        s = re.sub(r"المدة:\s*(\d+)\s*(?:ليالي|ليلة)", r"Duration: \1 Nights", s)
    return s


def get_smart_notes_for_package(pkg: TravelPackage, lang: str = "ar") -> List[str]:
    notes = []
    has_flights = bool(pkg.flights and len(pkg.flights) > 0)
    has_cars = bool(pkg.car_rentals and len(pkg.car_rentals) > 0)
    has_hotels = bool(pkg.hotels and len(pkg.hotels) > 0)
    has_transports = bool(pkg.transports and len(pkg.transports) > 0)

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


def render_html(data: Union[TravelPackage, Dict[str, Any]], lang: Optional[str] = None) -> str:
    """Generates the full HTML string for a TravelPackage instance or dictionary in Arabic ('ar') or English ('en')."""
    explicit_lang = lang
    if isinstance(data, dict):
        if not explicit_lang and "_lang" in data:
            explicit_lang = str(data.get("_lang") or "")
        pkg = TravelPackage(**data)
    else:
        pkg = data

    meta = pkg.meta
    effective_lang = (explicit_lang or getattr(meta, "lang", None) or "ar").strip().lower()
    is_en = (effective_lang == "en")
    col_sep_cls = "border-r" if is_en else "border-l"

    # 1. HOTELS SECTION
    hotels_html = ""
    if pkg.hotels and len(pkg.hotels) > 0:
        hotel_cards = []
        for idx, h in enumerate(pkg.hotels):
            day_parts = [_tr_val(p.strip(), is_en) for p in re.split(r'<br\s*/?>|»|-', h.day_range) if p.strip()]
            if len(day_parts) >= 2:
                day_progression = f"""
                <div class="text-[#0369a1] font-extrabold text-xs">{html.escape(day_parts[0])}</div>
                <div class="border-t border-sky-200 my-0.5"></div>
                <div class="text-[#0369a1] font-extrabold text-xs">{html.escape(day_parts[1])}</div>
                """
            else:
                day_progression = f"""<div class="text-[#0369a1] font-extrabold text-xs">{html.escape(_tr_val(h.day_range, is_en))}</div>"""

            city_order_disp = _tr_val(h.city_order, is_en)
            city_name_disp = _tr_val(h.city_name, is_en)
            meal_disp = _tr_val(h.meal_plan, is_en)
            room_disp = _tr_val(h.room_type, is_en)
            nights_label = f"{h.nights_count} {'Night' if h.nights_count == 1 else 'Nights'}" if is_en else f"{h.nights_count} ليالي"
            checkin_label = f"📅 Check-in: {html.escape(h.check_in)}" if is_en else f"📅 تاريخ الدخول: {html.escape(h.check_in)}"
            checkout_label = f"🏁 Check-out: {html.escape(h.check_out)}" if is_en else f"🏁 تاريخ الخروج: {html.escape(h.check_out)}"
            rooms_count_label = f"Rooms: {h.rooms_count}" if is_en else f"عدد: {h.rooms_count}"

            card = f"""
            <div class="border-2 border-sky-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden avoid-break" data-purpose="hotel-card-{idx+1}">
              <!-- Top Row: Badges -->
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <span class="bg-[#ea580c] text-white text-xs md:text-sm font-bold px-4 py-1 rounded-full shadow-sm">
                    {html.escape(city_order_disp)}
                  </span>
                  <div class="bg-[#0284c7] text-white text-xs md:text-sm font-bold px-3 py-1 rounded-full flex items-center gap-2 shadow-sm">
                    <span>{html.escape(city_name_disp)}</span>
                    <span class="bg-sky-900/40 text-white text-[11px] px-2 py-0.5 rounded-full border border-sky-300/40 font-num">{nights_label}</span>
                  </div>
                </div>
                <div class="border-2 border-sky-400 rounded-xl px-4 py-1 text-center bg-sky-50/50 min-w-[120px]">
                  {day_progression}
                </div>
              </div>

              <!-- Check-in / Check-out Orange Bar (Compact) -->
              <div class="bg-gradient-to-r from-[#ea580c] to-[#f97316] text-white rounded-lg sm:rounded-xl px-3 py-1 sm:py-1.5 font-bold text-[11px] sm:text-xs flex items-center justify-center gap-2 sm:gap-3 shadow-sm text-center font-num whitespace-nowrap">
                <span>{checkin_label}</span>
                <span class="text-amber-200 tracking-widest font-black">&gt;&gt;&gt;</span>
                <span>{checkout_label}</span>
              </div>

              <!-- Hotel Name Dark Navy Bar -->
              <div class="bg-[#083344] text-white rounded-xl px-4 py-2 flex items-center justify-between gap-2 shadow-sm">
                <h3 class="font-black text-sm md:text-base tracking-wide flex-1">
                  {html.escape(h.hotel_name)}
                </h3>
              </div>

              <!-- Room Information Strip (Light Blue) -->
              <div class="bg-[#0284c7] text-white rounded-xl px-4 py-2 text-xs md:text-sm font-bold grid grid-cols-3 text-center items-center shadow-inner">
                <div class="{col_sep_cls} border-sky-300/40">{html.escape(meal_disp)}</div>
                <div class="{col_sep_cls} border-sky-300/40">{html.escape(room_disp)}</div>
                <div>{rooms_count_label}</div>
              </div>
            </div>
            """
            hotel_cards.append(card)

        hotels_sec_title = "Hotel Accommodation" if is_en else "حجز الفنادق"
        hotels_html = f"""
        <!-- SECTION 1: HOTELS BOOKING -->
        <section class="space-y-3.5" data-purpose="hotels-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#0369a1] via-[#0284c7] to-[#0ea5e9] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md shadow-sky-500/20 flex items-center gap-2 border-2 border-sky-300">
              <span>🏨</span>
              <span class="tracking-wide">{hotels_sec_title}</span>
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
        all_domestic = all(any(k in str(getattr(f, "flight_type", "") or "").lower() for k in ["داخلي", "domestic", "internal"]) for f in pkg.flights)
        has_intl = any(any(k in str(getattr(f, "flight_type", "") or "").lower() for k in ["دولي", "international"]) for f in pkg.flights)
        has_dom = any(any(k in str(getattr(f, "flight_type", "") or "").lower() for k in ["داخلي", "domestic", "internal"]) for f in pkg.flights)

        if is_en:
            if all_domestic:
                flight_title = "Domestic Flight Booking"
            elif has_intl and has_dom:
                flight_title = "Flight Booking (International & Domestic)"
            else:
                flight_title = "Flight Booking (International & Domestic)" if len(pkg.flights) > 2 else "Flight Booking"
        else:
            if all_domestic:
                flight_title = "حجز الطيران الداخلي"
            elif has_intl and has_dom:
                flight_title = "حجز الطيران (الدولي والداخلي)"
            else:
                flight_title = "حجز الطيران (الدولي والداخلي)" if len(pkg.flights) > 2 else "حجز الطيران"

        AIRPORT_CODES = {
            "جدة": "JED", "jeddah": "JED",
            "الرياض": "RUH", "riyadh": "RUH",
            "الدمام": "DMM", "dammam": "DMM",
            "المدينة": "MED", "medina": "MED", "madinah": "MED",
            "أبها": "AHB", "abha": "AHB",
            "تبوك": "TUU", "tabuk": "TUU",
            "الدوحة": "DOH", "doha": "DOH",
            "باريس": "CDG", "paris": "CDG",
            "فيينا": "VIE", "vienna": "VIE",
            "النمسا": "VIE", "austria": "VIE",
            "لندن": "LHR", "london": "LHR", "heathrow": "LHR",
            "اسطنبول": "IST", "إسطنبول": "IST", "istanbul": "IST",
            "طرابزون": "TZX", "trabzon": "TZX",
            "أنطاليا": "AYT", "antalya": "AYT",
            "دبي": "DXB", "dubai": "DXB",
            "أبوظبي": "AUH", "abu dhabi": "AUH",
            "الشارقة": "SHJ", "sharjah": "SHJ",
            "الكويت": "KWI", "kuwait": "KWI",
            "البحرين": "BAH", "bahrain": "BAH",
            "مسقط": "MCT", "muscat": "MCT",
            "صلالة": "SLL", "salalah": "SLL",
            "القاهرة": "CAI", "cairo": "CAI",
            "عمان": "AMM", "amman": "AMM",
            "بانكوك": "BKK", "bangkok": "BKK", "suvarnabhumi": "BKK",
            "بوكيت": "HKT", "فوكيت": "HKT", "phuket": "HKT",
            "كرابي": "KBV", "krabi": "KBV",
            "كوالالمبور": "KUL", "kuala lumpur": "KUL",
            "روما": "FCO", "rome": "FCO",
            "ميلانو": "MXP", "milan": "MXP",
            "ميونخ": "MUC", "munich": "MUC",
            "فرانكفورت": "FRA", "frankfurt": "FRA",
            "برشلونة": "BCN", "barcelona": "BCN",
            "مدريد": "MAD", "madrid": "MAD",
            "جنيف": "GVA", "geneva": "GVA",
            "زيورخ": "ZRH", "zurich": "ZRH",
            "أمستردام": "AMS", "amsterdam": "AMS",
            "تبليسي": "TBS", "tbilisi": "TBS",
            "باتومي": "BUS", "batumi": "BUS",
            "باكو": "GYD", "baku": "GYD",
            "طشقند": "TAS", "tashkent": "TAS",
            "المالديف": "MLE", "maldives": "MLE", "male": "MLE",
            "جاكرتا": "CGK", "jakarta": "CGK",
            "بالي": "DPS", "bali": "DPS",
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
            "إير أشيا": "AirAsia",
            "اير اشيا": "AirAsia",
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
            ("JED", "BKK"): (750, 510, "8 ساعات و 30 دقيقة"),
            ("BKK", "HKT"): (85, 85, "ساعة و 25 دقيقة"),
            ("HKT", "JED"): (330, 570, "9 ساعات و 30 دقيقة"),
            ("JED", "TBS"): (275, 215, "3 ساعات و 35 دقيقة"),
            ("TBS", "JED"): (155, 215, "3 ساعات و 35 دقيقة"),
        }

        def _get_iata_code(ap_name: str) -> str:
            if not ap_name:
                return ""
            m = re.search(r"\b([A-Z]{3})\b", ap_name)
            if m:
                return m.group(1)
            ap_lower = ap_name.lower()
            for city, code in AIRPORT_CODES.items():
                if city in ap_lower:
                    return code
            return ""

        def _get_short_city(ap_name: str) -> str:
            if not ap_name:
                return ""
            cleaned = re.sub(r"[-–—,\s]*(?:مبنى|صالة|تيرمينال|Terminal)\s*[A-Za-z0-9أ-ي]+", "", ap_name, flags=re.IGNORECASE)
            cleaned = re.sub(r"\([A-Z]{3}\)", "", cleaned).strip(" -–—,")
            parts = [p.strip() for p in re.split(r"[-–—]", cleaned) if p.strip()]
            if len(parts) > 1:
                return parts[-1]
            c = re.sub(r"(?:مطار|الدولي|المحلية|المحلي|International|Airport|Domestic)", "", cleaned, flags=re.IGNORECASE).strip()
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
                return "Approved Airline" if is_en else "الطيران المعتمد"
            a = airline_name.strip()
            if is_en:
                for ar_name, en_name in AIRLINE_ENGLISH.items():
                    if ar_name in a:
                        return en_name
                return a
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
            t_low = t_str.lower()
            is_pm = (any(w in t_str for w in ["مساء", "عصر", "ظهر", "ليل", "م"]) and not any(w in t_str for w in ["صباح", "فجر"])) or bool(re.search(r"\bpm\b", t_low))
            is_am = any(w in t_str for w in ["صباح", "فجر", "ص"]) or bool(re.search(r"\bam\b", t_low))
            if is_pm and hh < 12:
                hh += 12
            elif is_am and hh == 12:
                hh = 0
            return hh * 60 + mm

        def _mins_to_time(total_mins: int) -> str:
            total_mins = total_mins % (24 * 60)
            hh24 = total_mins // 60
            mm = total_mins % 60
            hh12 = hh24 % 12
            if hh12 == 0:
                hh12 = 12
            if is_en:
                suf = "AM" if hh24 < 12 else "PM"
                return f"{hh12:02d}:{mm:02d} {suf}"
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
            raw = _tr_val(t_str.strip(), is_en)
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
            h_m = re.search(r"(\d+)\s*(?:ساع|hours?|hrs?|h\b)", dur_str, re.IGNORECASE)
            if h_m:
                total += int(h_m.group(1)) * 60
            elif "ساعتين" in dur_str or "ساعتان" in dur_str:
                total += 120
            elif "ساعة" in dur_str:
                total += 60
            m_m = re.search(r"(\d+)\s*(?:دقيق|minutes?|mins?|m\b)", dur_str, re.IGNORECASE)
            if m_m:
                total += int(m_m.group(1))
            return total

        def _format_duration_str(mins: int) -> str:
            if mins <= 0:
                return ""
            h = mins // 60
            m = mins % 60
            if is_en:
                parts = []
                if h > 0:
                    parts.append(f"{h} hr" if h == 1 else f"{h} hrs")
                if m > 0:
                    parts.append(f"{m} min" if m == 1 else f"{m} mins")
                return " ".join(parts)
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
            combined_low = combined_type_str.lower()
            is_return = any(k in combined_low for k in ["عودة", "return", "inbound"]) or (idx == len(pkg.flights) and len(pkg.flights) >= 2 and not any(k in combined_low for k in ["داخلي", "domestic", "internal"]) and idx > 1)
            is_domestic_or_euro = any(k in combined_low for k in ["داخلي", "أوروبي", "domestic", "internal", "european"]) or (not is_return and idx > 1 and len(pkg.flights) > 2)

            origin_code = _get_iata_code(f.from_airport)
            dest_code = _get_iata_code(f.to_airport)
            origin_city = _get_short_city(f.from_airport)
            dest_city = _get_short_city(f.to_airport)
            origin_ap_clean = _get_airport_only(f.from_airport)
            dest_ap_clean = _get_airport_only(f.to_airport)

            airline_full = _format_airline(f.airline)
            default_al = "Approved Airline" if is_en else "الطيران المعتمد"
            if is_en:
                airline_short = _get_airline_en(f.airline or "") or default_al
            else:
                airline_short = re.sub(r"\s*\([^)]+\)", "", f.airline or default_al).strip() or (f.airline or default_al)

            # Passengers summary
            pax_parts = []
            if is_en:
                if f.passengers.adults:
                    pax_parts.append(f"{f.passengers.adults} {'Adult' if f.passengers.adults == 1 else 'Adults'}")
                if f.passengers.children:
                    pax_parts.append(f"{f.passengers.children} {'Child' if f.passengers.children == 1 else 'Children'}")
                if f.passengers.infants:
                    pax_parts.append(f"{f.passengers.infants} {'Infant' if f.passengers.infants == 1 else 'Infants'}")
                pax_summary = ", ".join(pax_parts) if pax_parts else "2 Adults"
            else:
                if f.passengers.adults:
                    pax_parts.append(f"{f.passengers.adults} بالغين")
                if f.passengers.children:
                    pax_parts.append(f"{f.passengers.children} أطفال")
                if f.passengers.infants:
                    pax_parts.append(f"{f.passengers.infants} رضيع")
                pax_summary = " ، ".join(pax_parts) if pax_parts else "2 بالغين"

            # Baggage formatting
            raw_luggage = (f.luggage or ("25 kg" if is_en else "25 كجم")).strip()
            raw_luggage = re.sub(r"(?:لكل\s*مسافر|للمسافر|per\s*passenger|/passenger)\s*$", "", raw_luggage, flags=re.IGNORECASE).strip(" /+-،,")
            cabin_weight = "7 kg" if is_en else "7 كجم"
            plus_split = re.split(r"\+|،|,|(?:\bو|\band\b)(?=\s*\d+\s*(?:كجم|كيلو|kg)\s*(?:كابينة|يد|cabin|hand))", raw_luggage, flags=re.IGNORECASE)
            if len(plus_split) >= 2 and any(k in plus_split[-1].lower() for k in ["كابينة", "يد", "cabin", "hand", "7", "8", "10"]):
                main_weight = plus_split[0].strip()
                cw_raw = plus_split[-1].strip()
                cw_m = re.search(r"(\d+\s*(?:كجم|كيلو|kg))", cw_raw, re.IGNORECASE)
                if cw_m:
                    cabin_weight = cw_m.group(1).strip()
                else:
                    cabin_weight = re.sub(r"(?:كابينة|حقيبة\s*يد|يد|لكل\s*مسافر|cabin|hand\s*luggage|hand)", "", cw_raw, flags=re.IGNORECASE).strip() or ("7 kg" if is_en else "7 كجم")
            elif raw_luggage == "1":
                main_weight = "1 Piece (23 kg)" if is_en else "1 قطعة (23 كجم)"
            elif re.match(r"^\d+$", raw_luggage):
                main_weight = f"{raw_luggage} Pieces (23 kg)" if is_en else f"{raw_luggage} قطعة (23 كجم)"
            else:
                main_weight = raw_luggage

            if is_en:
                main_weight = re.sub(r"(?:كجم|كيلو)", "kg", main_weight)
                main_weight = main_weight.replace("قطعتين", "2 Pieces").replace("قطعة", "Piece")
                cabin_weight = re.sub(r"(?:كجم|كيلو)", "kg", cabin_weight)

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
                    or ("Transit Airport" if is_en else "مطار الترانزيت")
                )
                transit_code = _get_iata_code(transit_ap)
                transit_city = _get_short_city(transit_ap)
                transit_ap_clean = _get_airport_only(transit_ap)
                transit_dur = (
                    getattr(f, "transit_duration", None)
                    or (seg1.transit_duration if seg1 else None)
                    or (seg2.transit_duration if seg2 else None)
                    or ("Transit" if is_en else "ترانزيت")
                )

                if not seg1_arr and seg1_dep and origin_code and transit_code:
                    est1 = ROUTE_ESTIMATES.get((origin_code, transit_code))
                    dep1_m = _parse_mins(seg1_dep)
                    if est1 and dep1_m is not None:
                        seg1_arr = _mins_to_time(dep1_m + est1[0])

                if not final_arr and seg2_dep and transit_code and dest_code:
                    est2 = ROUTE_ESTIMATES.get((transit_code, dest_code))
                    dep2_m = _parse_mins(seg2_dep)
                    if est2 and dep2_m is not None:
                        final_arr = _mins_to_time(dep2_m + est2[0])

                est1 = ROUTE_ESTIMATES.get((origin_code, transit_code))
                est2 = ROUTE_ESTIMATES.get((transit_code, dest_code))
                t_mins = _parse_dur_mins(transit_dur)
                if est1 and est2 and t_mins > 0:
                    total_dur_str = _format_duration_str(est1[1] + t_mins + est2[1])
                else:
                    total_dur_str = f"Transit ({transit_dur})" if is_en else f"ترانزيت ({transit_dur})"

                dep_num, dep_period, dep_note = _split_time_parts(seg1_dep)
                arr_num, arr_period, arr_note = _split_time_parts(final_arr) if final_arr else ("--:--", "Scheduled" if is_en else "حسب الجدول", "")
            else:
                dep_raw = f.departure_time or ""
                arr_raw = getattr(f, "arrival_time", None) or ""
                est_direct = ROUTE_ESTIMATES.get((origin_code, dest_code))
                if not arr_raw and dep_raw and est_direct:
                    dep_m = _parse_mins(dep_raw)
                    if dep_m is not None:
                        arr_raw = _mins_to_time(dep_m + est_direct[0])
                if est_direct:
                    total_dur_str = _format_duration_str(est_direct[1]) if is_en else est_direct[2]
                else:
                    total_dur_str = "Direct Flight" if is_en else "رحلة مباشرة"
                dep_num, dep_period, dep_note = _split_time_parts(dep_raw)
                arr_num, arr_period, arr_note = _split_time_parts(arr_raw) if arr_raw else ("--:--", "Local Time" if is_en else "توقيت محلي", "")

            # Detect cabin class if mentioned in flight_type
            cabin_badge_suffix = ""
            if "رجال الأعمال" in combined_type_str or "بزنس" in combined_type_str or "business" in combined_low:
                cabin_badge_suffix = " - Business Class" if is_en else " - درجة رجال الأعمال"
            elif "الدرجة الأولى" in combined_type_str or "درجة أولى" in combined_type_str or "first class" in combined_low:
                cabin_badge_suffix = " - First Class" if is_en else " - الدرجة الأولى"

            if is_domestic_or_euro:
                card_border = "border-emerald-300"
                header_bg = "bg-gradient-to-r from-[#059669] via-emerald-600 to-[#0F766E]"
                header_sub_text = "text-emerald-100"
                header_icon = '<path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                if is_en:
                    if "أوروبي" in combined_type_str or "european" in combined_low:
                        base_dom_title = "European Flight (Transit)" if is_transit else "European Flight (Direct)"
                    else:
                        base_dom_title = "Domestic Flight (Transit)" if is_transit else "Domestic Flight (Direct)"
                else:
                    if "أوروبي" in combined_type_str and "داخلي" not in combined_type_str:
                        base_dom_title = "رحلة طيران أوروبي (ترانزيت)" if is_transit else "رحلة طيران أوروبي (مباشرة)"
                    else:
                        base_dom_title = "رحلة داخلية (ترانزيت)" if is_transit else "رحلة داخلية (مباشرة)"
                header_badge_title = base_dom_title + cabin_badge_suffix
                sidebar_bg = "bg-emerald-50/50 border-emerald-200"
                sidebar_title_cls = "text-emerald-950 border-emerald-200"
                sidebar_box_border = "border-emerald-200/70"
                sidebar_icon_cls = "text-emerald-700"
                sidebar_bag_cls = "text-emerald-800"
                sidebar_footer_border = "border-emerald-200/60"
                sidebar_footer_text = "text-emerald-900"
                dest_time_cls = "text-emerald-700"
                dest_period_cls = "text-emerald-800"
                dest_pill_cls = "text-emerald-800 bg-emerald-100/70"
                dest_code_cls = "text-emerald-900"
            else:
                card_border = "border-sky-300"
                header_bg = "bg-gradient-to-r from-[#0E446E] via-[#01579b] to-[#0284c7]"
                header_sub_text = "text-sky-100"
                if is_return:
                    header_icon = '<path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                    if is_en:
                        base_intl_title = "Return Flight - International (Transit)" if is_transit else "Return Flight - International (Direct)"
                    else:
                        base_intl_title = "رحلة العودة - طيران دولي (ترانزيت)" if is_transit else "رحلة العودة - طيران دولي (مباشر)"
                else:
                    header_icon = '<path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>'
                    if is_en:
                        base_intl_title = "Outbound Flight - International (Transit)" if is_transit else "Outbound Flight - International (Direct)"
                    else:
                        base_intl_title = "رحلة الذهاب - طيران دولي (ترانزيت)" if is_transit else "رحلة الذهاب - طيران دولي (مباشر)"
                header_badge_title = base_intl_title + cabin_badge_suffix
                sidebar_bg = "bg-sky-50/50 border-sky-200"
                sidebar_title_cls = "text-[#0E446E] border-sky-200"
                sidebar_box_border = "border-sky-200/80"
                sidebar_icon_cls = "text-[#0284c7]"
                sidebar_bag_cls = "text-[#0E446E]"
                sidebar_footer_border = "border-sky-200/70"
                sidebar_footer_text = "text-[#0E446E]"
                dest_time_cls = "text-[#01579b]"
                dest_period_cls = "text-[#0284c7]"
                dest_pill_cls = "text-[#01579b] bg-sky-100/80"
                dest_code_cls = "text-[#0E446E]"

            plane_rot_cls = "rotate-90" if is_en else "rotate-180"

            # Middle Track & Bottom Callout Box
            if is_transit:
                tran_code_label = f" ({transit_code})" if transit_code else ""
                transit_ap_display = transit_ap if (not transit_code or transit_code in transit_ap) else f"{transit_ap}{tran_code_label}"
                plane_icon_cls = "text-emerald-600" if is_domestic_or_euro else "text-[#0284c7]"
                dur_lbl = "⏱ Total Duration:" if is_en else "⏱ المدة الإجمالية:"
                tran_badge_txt = f"Transit in {html.escape(transit_city)}{html.escape(tran_code_label)}" if is_en else f"ترانزيت بـ {html.escape(transit_city)}{html.escape(tran_code_label)}"
                stop_sub_txt = f"Stopover at {html.escape(transit_ap_clean)}{html.escape(tran_code_label)}" if is_en else f"توقف في {html.escape(transit_ap_clean)}{html.escape(tran_code_label)}"

                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-slate-600 mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>{dur_lbl}</span>
                    <span class="text-[#0E446E]">{html.escape(total_dur_str)}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-slate-300 min-w-[8px]"></div>
                    <div class="badge bg-white px-2.5 py-0.5 rounded-full border border-amber-300 shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-amber-800 inline-flex items-center justify-center gap-1 flex-wrap leading-tight">
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                        <span>{tran_badge_txt}</span>
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-slate-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 {plane_icon_cls} transform {plane_rot_cls} shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">{stop_sub_txt}</span>
                </div>
                """

                if is_en:
                    bottom_callout_html = f"""
                    <div class="info-box bg-amber-50/90 border border-amber-200/90 rounded-xl p-3 space-y-2 text-xs">
                      <div class="flex items-start gap-2">
                        <span class="p-1.5 bg-amber-200 text-amber-900 rounded-lg shrink-0 mt-0.5">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                        </span>
                        <div class="min-w-0 flex-1">
                          <span class="font-bold text-amber-950 text-xs block leading-snug">Transit & Stopover Station: {html.escape(transit_ap_display)}</span>
                          <span class="text-amber-800 text-[11px] font-num block mt-0.5 leading-snug">Arrive {html.escape(transit_city)}: <strong>{html.escape(_tr_val(seg1_arr, True) or '—')}</strong> &nbsp;|&nbsp; Depart {html.escape(transit_city)}: <strong>{html.escape(_tr_val(seg2_dep, True) or '—')}</strong></span>
                        </div>
                      </div>
                      <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-amber-200/70">
                        <span class="badge font-bold text-amber-900 bg-amber-100 px-2.5 py-1 rounded-md border border-amber-300 font-num text-[11px]">
                          ⏱ Layover: {html.escape(transit_dur)}
                        </span>
                        <span class="badge inline-flex items-center gap-1 font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200 text-[11px]">
                          <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                          <span>Baggage checked through to final destination</span>
                        </span>
                      </div>
                    </div>
                    """
                else:
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
            elif is_domestic_or_euro:
                dur_lbl = f"⏱ Duration: {html.escape(total_dur_str)}" if is_en else f"⏱ المدة: {html.escape(total_dur_str)}"
                nonstop_lbl = "Non-stop Direct Flight" if is_en else "طيران مباشر بدون توقف"
                sub_lbl = "Fast direct connection between cities" if is_en else "رحلة سريعة ومباشرة بين المدينتين"
                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-emerald-800 mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>{dur_lbl}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-emerald-300 min-w-[8px]"></div>
                    <div class="badge bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-emerald-800 leading-tight">
                        {nonstop_lbl}
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-emerald-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 text-emerald-600 transform {plane_rot_cls} shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">{sub_lbl}</span>
                </div>
                """
                callout_txt = "<strong>Direct Domestic Flight:</strong> Non-stop service with no aircraft change for a smooth, fast arrival." if is_en else "<strong>رحلة داخلية مباشرة:</strong> بدون أي محطات توقف أو تغيير للطائرة، وصول سريع ومباشر."
                bottom_callout_html = f"""
                <div class="info-box bg-emerald-50 border border-emerald-200 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 text-xs text-emerald-900">
                  <div class="flex items-start gap-2 min-w-0 flex-1">
                    <span class="text-emerald-600 font-bold shrink-0">✓</span>
                    <span class="leading-snug">{callout_txt}</span>
                  </div>
                  <span class="font-semibold text-emerald-800">{html.escape(airline_short)}</span>
                </div>
                """
            else:
                dur_lbl = f"⏱ Duration: {html.escape(total_dur_str)}" if is_en else f"⏱ المدة: {html.escape(total_dur_str)}"
                nonstop_lbl = "Direct International Flight" if is_en else "طيران دولي مباشر بدون توقف"
                sub_lbl = f"Direct arrival at {html.escape(dest_ap_clean)}" if is_en else f"وصول مباشر إلى {html.escape(dest_ap_clean)}"
                middle_track_html = f"""
                <div class="flex-[1.35] min-w-0 w-full flex flex-col items-center px-1 py-1 text-center">
                  <div class="text-[11px] font-bold text-[#0E446E] mb-2 flex flex-wrap items-center justify-center gap-1 font-num">
                    <span>{dur_lbl}</span>
                  </div>
                  <div class="w-full flex items-center gap-1 my-1">
                    <div class="h-0.5 flex-1 bg-sky-300 min-w-[8px]"></div>
                    <div class="badge bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full shadow-sm max-w-full">
                      <span class="text-[10px] font-bold text-[#0E446E] leading-tight">
                        {nonstop_lbl}
                      </span>
                    </div>
                    <div class="h-0.5 flex-1 bg-sky-300 min-w-[8px]"></div>
                    <svg class="w-4 h-4 text-[#0284c7] transform {plane_rot_cls} shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path>
                    </svg>
                  </div>
                  <span class="text-[10px] text-slate-500 mt-1.5 leading-snug">{sub_lbl}</span>
                </div>
                """
                callout_txt = "<strong>Direct International Flight:</strong> Non-stop service with no layovers or aircraft change. All times shown are local." if is_en else "<strong>رحلة دولية مباشرة بالكامل:</strong> بدون أي محطات توقف أو تغيير للطائرة، وجميع الأوقات بالتوقيت المحلي."
                bottom_callout_html = f"""
                <div class="info-box bg-sky-50/70 border border-sky-200/80 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 text-xs text-[#0E446E]">
                  <div class="flex items-start gap-2 min-w-0 flex-1">
                    <span class="text-[#0284c7] font-bold shrink-0">✓</span>
                    <span class="leading-snug">{callout_txt}</span>
                  </div>
                  <span class="font-semibold text-[#01579b]">{html.escape(airline_short)}</span>
                </div>
                """

            dep_note_html = f'<div class="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 mt-0.5 inline-block">{html.escape(dep_note)}</div>' if dep_note else ""
            arr_note_html = f'<div class="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 mt-0.5 inline-block">{html.escape(arr_note)}</div>' if arr_note else ""

            flight_no_lbl = f"Flight #{idx}" if is_en else f"الرحلة رقم {idx}"
            date_lbl = "Date:" if is_en else "التاريخ:"
            carrier_lbl = "Airline:" if is_en else "الناقل الجوي:"
            carrier_border_cls = "sm:border-l sm:border-white/25 sm:pl-3" if is_en else "sm:border-r sm:border-white/25 sm:pr-3"
            origin_align_cls = "sm:text-left" if is_en else "sm:text-right"
            dest_align_cls = "sm:text-right" if is_en else "sm:text-left"
            dep_from_lbl = "Departure From" if is_en else "مغادرة من"
            arr_to_lbl = ("Final Arrival To" if is_transit else "Direct Arrival To") if is_en else ("وصول نهائي إلى" if is_transit else "وصول مباشر إلى")
            sidebar_hdr_lbl = "Ticket & Passenger Info" if is_en else "بيانات التذكرة والركاب"
            pax_lbl = "Passengers:" if is_en else "المسافرين:"
            checked_bag_lbl = "Checked Baggage:" if is_en else "أمتعة الشحن:"
            per_pax_lbl = "/ pax" if is_en else "/ للمسافر"
            cabin_bag_lbl = "Cabin Baggage:" if is_en else "حقيبة اليد (الكابينة):"
            op_airline_lbl = "Operating Airline:" if is_en else "طيران الرحلة:"

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
                  <span class="text-xs font-semibold {header_sub_text} font-num">{flight_no_lbl}</span>
                </div>
                <div class="flex flex-wrap items-center gap-3 text-xs min-w-0">
                  <div class="flex items-center gap-1">
                    <span class="{header_sub_text}">{date_lbl}</span>
                    <span class="badge font-bold text-white bg-white/20 px-2 py-0.5 rounded-md font-num">{html.escape(f.date)}</span>
                  </div>
                  <div class="flex items-center gap-1 {carrier_border_cls} min-w-0">
                    <span class="{header_sub_text}">{carrier_lbl}</span>
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
                      <div class="flex-1 min-w-0 text-center {origin_align_cls} w-full sm:w-auto">
                        <span class="text-[11px] font-semibold text-slate-500 block mb-0.5">{dep_from_lbl}</span>
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
                      <div class="flex-1 min-w-0 text-center {dest_align_cls} w-full sm:w-auto">
                        <span class="text-[11px] font-semibold text-slate-500 block mb-0.5">{arr_to_lbl}</span>
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
                    <h4 class="text-xs font-bold {sidebar_title_cls} uppercase tracking-wider mb-2.5 pb-1 border-b">{sidebar_hdr_lbl}</h4>
                    <div class="space-y-2.5">
                      <!-- Passengers -->
                      <div class="info-box flex flex-wrap items-center justify-between gap-1.5 text-xs bg-white/90 p-2.5 rounded-lg border {sidebar_box_border}">
                        <span class="text-slate-600 font-medium flex items-center gap-1.5">
                          <svg class="w-4 h-4 shrink-0 {sidebar_icon_cls}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                          <span>{pax_lbl}</span>
                        </span>
                        <span class="badge font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded font-num">{html.escape(pax_summary)}</span>
                      </div>
                      <!-- Baggage -->
                      <div class="info-box bg-white/90 p-2.5 rounded-lg border {sidebar_box_border} space-y-1.5 text-xs">
                        <div class="flex flex-wrap items-center justify-between gap-1">
                          <span class="text-slate-600 font-medium flex items-center gap-1.5">
                            <svg class="w-4 h-4 shrink-0 {sidebar_bag_cls}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                            <span>{checked_bag_lbl}</span>
                          </span>
                          <span class="font-extrabold {sidebar_bag_cls} text-xs md:text-sm font-num">{html.escape(main_weight)} <span class="text-[10px] font-normal text-slate-500">{per_pax_lbl}</span></span>
                        </div>
                        <div class="flex flex-wrap items-center justify-between gap-1 text-[11px] pt-1 border-t border-slate-100 text-slate-500 font-num">
                          <span>{cabin_bag_lbl}</span>
                          <span class="font-bold text-slate-800">{html.escape(cabin_weight)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- Airline Footer Badge -->
                  <div class="text-[11px] text-slate-600 pt-2 border-t {sidebar_footer_border} flex flex-wrap items-center justify-between gap-1">
                    <span class="text-slate-500">{op_airline_lbl}</span>
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
              <svg class="w-5 h-5 {'' if is_en else '-scale-x-100'} transform" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
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

        if is_en:
            if all_trains:
                section_title = "Train Tickets & Tourist Transfers"
                section_icon = "🚆"
            elif has_trains:
                section_title = "Transfers & Tourist Trains"
                section_icon = "🚆"
            elif has_car_rental:
                section_title = "Suggested Daily Itinerary & Tours"
                section_icon = "🗺️"
            else:
                section_title = "Private Transfers & Sightseeing Tours"
                section_icon = "🚗"
        else:
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

        desc_align_cls = "text-left" if is_en else "text-right"
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
                    has_kv_details = any(":" in a for a in item.activities)
                    if has_kv_details or item_is_train:
                        detail_lines = []
                        for a in item.activities:
                            if ":" in a:
                                k, v = a.split(":", 1)
                                k_low = k.lower()
                                icon = "🕒" if any(x in k_low for x in ["وقت", "مغادرة", "وصول", "time", "depart", "arriv"]) else ("🎫" if any(x in k_low for x in ["تذكرة", "درجة", "ticket", "class"]) else "▪️")
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

                veh_disp = _tr_val(item.vehicle_type, is_en)
                if item_is_train:
                    veh_label = f"🚆 {html.escape(veh_disp)}"
                elif has_car_rental:
                    veh_label = "Rental Car (Self-Drive)" if is_en else "بالسيارة المستأجرة"
                else:
                    veh_label = html.escape(veh_disp)

                day_lbl_disp = _tr_val(item.day_label, is_en)

                row = f"""
                <tr class="hover:bg-sky-50/40 transition avoid-break">
                  <!-- Flight / Transport Date -->
                  <td class="p-2.5 font-num text-slate-800 font-bold whitespace-nowrap align-top">{html.escape(item.date)}</td>
                  <!-- Day Label -->
                  <td class="p-2.5 font-bold text-slate-800 whitespace-nowrap align-top">{html.escape(day_lbl_disp)}</td>
                  <!-- Vehicle Type Badge -->
                  <td class="p-2.5 text-center align-top">
                    <span class="inline-block border border-sky-300 bg-sky-50 text-[#0284c7] font-bold px-2.5 py-1 rounded-full text-xs shadow-sm leading-snug max-w-[145px]">{veh_label}</span>
                  </td>
                  <!-- Description & Route -->
                  <td class="p-3 {desc_align_cls} align-top">
                    <div class="font-bold text-slate-900 text-xs md:text-sm leading-relaxed">{html.escape(item.title)}</div>
                    {route_html}
                    {activities_html}
                  </td>
                </tr>
                """
                item_rows.append(row)

            if is_en:
                if grp_is_train:
                    city_badge_text = "Confirmed Train Tickets & Seats"
                    city_title_text = f"🚆 Express Train Route: {html.escape(grp.city_name)}"
                    scope_note = """
                      <div class="text-[11px] text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                        <span>🚆</span>
                        <span>Includes express train tickets with confirmed seat reservations and specified luggage between central stations.</span>
                      </div>
                    """
                    veh_col_title = "Transport Mode"
                elif has_car_rental:
                    city_badge_text = "Self-Drive (Suggested Route)"
                    city_title_text = f"📍 Suggested Itinerary & Tours: {html.escape(grp.city_name)}"
                    scope_note = """
                      <div class="text-[11px] text-teal-900 bg-teal-50 border border-teal-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                        <span>💡</span>
                        <span>Suggested daily itinerary and attractions you can comfortably explore at your own pace with your rental car.</span>
                      </div>
                    """
                    veh_col_title = "Transport Mode"
                else:
                    city_badge_text = "Private Car with Driver"
                    city_title_text = f"📍 Tours & Transfers: {html.escape(grp.city_name)}"
                    scope_note = """
                      <div class="text-[11px] text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                        <span>ℹ️</span>
                        <span>Includes private transfers and tours with a dedicated driver within the city; routes are flexible according to your preference.</span>
                      </div>
                    """
                    veh_col_title = "Vehicle Type"
                th_date, th_day, th_desc = "Date", "Day", "Itinerary & Route Description"
            else:
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
                th_date, th_day, th_desc = "التاريخ", "اليوم", "الوصف والمسار"

            city_avoid_cls = "avoid-break" if len(grp.items) <= 4 else ""
            block = f"""
            <div class="border-2 border-sky-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden {city_avoid_cls}">
              <!-- City Header Navy Bar -->
              <div class="bg-[#083344] text-white px-4 py-2 rounded-xl font-bold text-xs md:text-sm flex items-center justify-between shadow-sm">
                <span>{city_title_text}</span>
                <span class="bg-[#0284c7] text-white px-3 py-1 rounded-full text-xs font-bold shadow-sm">{city_badge_text}</span>
              </div>
              {scope_note}
              <!-- Table -->
              <div class="overflow-x-auto border border-sky-200 rounded-xl shadow-sm">
                <table class="w-full text-center border-collapse text-xs md:text-sm" style="table-layout: fixed;">
                  <thead>
                    <tr class="bg-gradient-to-r from-[#0284c7] to-[#0369a1] text-white font-bold divide-x divide-white/20">
                      <th class="py-2.5 px-2 whitespace-nowrap" style="width: 13%;">{th_date}</th>
                      <th class="py-2.5 px-2 whitespace-nowrap" style="width: 13%;">{th_day}</th>
                      <th class="py-2.5 px-2 whitespace-nowrap" style="width: 18%;">{veh_col_title}</th>
                      <th class="py-2.5 px-4 {desc_align_cls}" style="width: 56%;">{th_desc}</th>
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
            days_txt = f"{c.days_count} {'Day' if c.days_count == 1 else 'Days'}" if is_en else f"{c.days_count} أيام"
            days_pill = f'<span class="bg-sky-900/40 text-white text-[11px] px-2 py-0.5 rounded-full border border-sky-300/40 font-num">{days_txt}</span>' if c.days_count else ''
            car_badge_lbl = "Car Rental" if is_en else "استئجار سيارة"
            driver_disp = _tr_val(c.driver_type, is_en)
            ins_disp = _tr_val(c.insurance, is_en)
            trans_disp = _tr_val(c.transmission, is_en)
            mile_disp = _tr_val(c.mileage, is_en)
            pickup_lbl = f"📍 Pick-up: {html.escape(c.pickup_location)} ({html.escape(c.pickup_date)})" if is_en else f"📍 الاستلام: {html.escape(c.pickup_location)} ({html.escape(c.pickup_date)})"
            dropoff_lbl = f"🏁 Drop-off: {html.escape(c.dropoff_location)} ({html.escape(c.dropoff_date)})" if is_en else f"🏁 التسليم: {html.escape(c.dropoff_location)} ({html.escape(c.dropoff_date)})"

            card = f"""
            <div class="border-2 border-teal-300 rounded-2xl p-3 md:p-3.5 bg-white shadow-sm space-y-2.5 relative overflow-hidden avoid-break">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <span class="bg-teal-600 text-white text-xs md:text-sm font-bold px-4 py-1 rounded-full shadow-sm">
                    {car_badge_lbl}
                  </span>
                  <div class="bg-[#0284c7] text-white text-xs md:text-sm font-bold px-3 py-1 rounded-full flex items-center gap-2 shadow-sm">
                    <span>{html.escape(c.car_model)}</span>
                    {days_pill}
                  </div>
                </div>
                <span class="bg-slate-100 text-slate-700 text-xs font-bold px-3 py-1 rounded-full border border-slate-300">
                  {html.escape(driver_disp)}
                </span>
              </div>
              <div class="bg-[#083344] text-white rounded-xl px-4 py-2 text-xs md:text-sm font-bold grid grid-cols-3 text-center items-center shadow-inner">
                <div class="{col_sep_cls} border-sky-300/40">🛡️ {html.escape(ins_disp)}</div>
                <div class="{col_sep_cls} border-sky-300/40">⚙️ {html.escape(trans_disp)}</div>
                <div>🛣️ {html.escape(mile_disp)}</div>
              </div>
              <div class="bg-gradient-to-r from-teal-600 to-[#0284c7] text-white rounded-xl px-4 py-2 font-bold text-xs md:text-sm flex flex-wrap items-center justify-between gap-2 shadow text-center font-num">
                <span>{pickup_lbl}</span>
                <span class="hidden sm:inline">&gt;&gt;&gt;</span>
                <span>{dropoff_lbl}</span>
              </div>
            </div>
            """
            car_cards.append(card)

        car_sec_title = "Private Car Rental" if is_en else "استئجار السيارات الخاصة"
        car_rentals_html = f"""
        <!-- SECTION 4: CAR RENTALS -->
        <section class="space-y-3 pt-1" data-purpose="car-rentals-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#0f766e] via-[#0d9488] to-[#14b8a6] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-teal-300">
              <span>🚘</span>
              <span class="tracking-wide">{car_sec_title}</span>
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
        svc_align_cls = "text-left" if is_en else "text-right"
        svc_rows = []
        for s in pkg.extra_services:
            row = f"""
            <tr class="hover:bg-sky-50/40 transition avoid-break">
              <td class="p-2.5 font-bold text-slate-900 font-num">{s.quantity}</td>
              <td class="p-2.5 font-bold text-slate-900 {svc_align_cls}">{html.escape(s.service_name)}</td>
              <td class="p-2.5 text-slate-700">{html.escape(s.country)}</td>
              <td class="p-2.5 text-slate-700 font-num">{html.escape(_tr_val(s.date, is_en))}</td>
              <td class="p-2.5 font-bold text-[#0b4f71]">{html.escape(_tr_val(s.day_label, is_en))}</td>
            </tr>
            """
            svc_rows.append(row)

        extra_sec_title = "Included Services & Complimentary Gifts" if is_en else "الخدمات والهدايا المشمولة"
        th_qty = "Qty" if is_en else "العدد"
        th_srv = "Service Name" if is_en else "اسم الخدمة"
        th_cnt = "Country" if is_en else "الدولة"
        th_dt = "Date" if is_en else "التاريخ"
        th_dy = "Day" if is_en else "اليوم"

        extra_services_html = f"""
        <!-- SECTION 5: EXTRA SERVICES -->
        <section class="space-y-3 pt-1" data-purpose="extra-services-section">
          <div class="flex justify-center section-pill-badge">
            <div class="bg-gradient-to-r from-[#9d174d] via-[#db2777] to-[#f43f5e] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-pink-300">
              <span>🎁</span>
              <span class="tracking-wide">{extra_sec_title}</span>
            </div>
          </div>
          <div class="overflow-x-auto border border-pink-200 rounded-xl shadow-sm avoid-break">
            <table class="w-full text-center border-collapse text-xs md:text-sm">
              <thead>
                <tr class="bg-gradient-to-r from-pink-600 to-purple-600 text-white font-bold divide-x divide-white/20">
                  <th class="py-2 px-2" style="width: 15%;">{th_qty}</th>
                  <th class="py-2 px-3 {svc_align_cls}" style="width: 45%;">{th_srv}</th>
                  <th class="py-2 px-2" style="width: 15%;">{th_cnt}</th>
                  <th class="py-2 px-2" style="width: 15%;">{th_dt}</th>
                  <th class="py-2 px-2" style="width: 10%;">{th_dy}</th>
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
        tot_lbl = "Grand Total Package Price:" if is_en else "الإجمالي الكلي النهائي للعرض السياحي:"
        tot_sub = "Inclusive of all mentioned accommodations, transfers, taxes, and service charges" if is_en else "شامل كافة الضرائب، الرسوم السياحية، والمصروفات المذكورة"
        curr_disp = _tr_val(pkg.total_price.currency, is_en)
        curr_margin = "ml-1" if is_en else "mr-1"
        total_price_display = f"""
        <div class="bg-gradient-to-br from-[#083344] via-[#0b4f71] to-[#01579b] text-white rounded-2xl p-4 md:p-5 shadow-md flex items-center justify-between gap-4 border-2 border-sky-200 avoid-break">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-amber-400 text-slate-900 flex items-center justify-center font-black text-2xl shadow shrink-0">
              💰
            </div>
            <div>
              <div class="text-xs md:text-sm text-sky-200 font-bold">{tot_lbl}</div>
              <div class="text-[11px] md:text-xs text-sky-300">{tot_sub}</div>
            </div>
          </div>
          <div class="text-left bg-white/10 px-5 py-2 rounded-xl border border-white/20 shadow-inner shrink-0 whitespace-nowrap">
            <span class="text-2xl md:text-3xl font-black text-amber-400 font-num tracking-tight">{html.escape(pkg.total_price.amount)}</span>
            <span class="text-xs text-white font-bold {curr_margin}">{html.escape(curr_disp)}</span>
          </div>
        </div>
        """

    # Terms & Notes banner
    if pkg.notes and len(pkg.notes) > 0:
        # If rendering in English and all notes are purely Arabic boilerplate, generate English smart notes
        all_notes_arabic = is_en and all(len(re.findall(r"[\u0600-\u06FF]", n)) > len(re.findall(r"[A-Za-z]", n)) for n in pkg.notes)
        effective_notes = get_smart_notes_for_package(pkg, lang="en") if all_notes_arabic else pkg.notes
    else:
        effective_notes = get_smart_notes_for_package(pkg, lang=effective_lang)

    notes_items = "".join([
        f'<li class="flex items-start gap-2"><span class="text-[#0E446E] font-bold text-base leading-none">•</span><span>{html.escape(n)}</span></li>'
        for n in effective_notes
    ])
    notes_hdr = "Important Notes & Booking Terms:" if is_en else "الشروط والملاحظات المهمة:"
    notes_list_html = f"""
    <section class="bg-[#EFF6FA] border border-[#C7E2F3] rounded-2xl p-5 md:p-6 text-slate-800 space-y-3.5 shadow-sm avoid-break" data-purpose="terms-and-conditions">
      <div class="flex items-center gap-2 text-slate-900 font-bold text-base md:text-lg border-b border-[#C7E2F3] pb-2.5">
        <span class="text-xl">📌</span>
        <h2>{notes_hdr}</h2>
      </div>
      <ul class="space-y-2.5 text-xs md:text-sm leading-relaxed text-slate-700">
        {notes_items}
      </ul>
    </section>
    """

    html_dir = "ltr" if is_en else "rtl"
    html_lang = "en" if is_en else "ar"
    doc_title = f"Travel Quotation - {html.escape(meta.company_name_en)} ({html.escape(meta.destination)})" if is_en else f"عرض سعر سياحي - {html.escape(meta.company_name)} ({html.escape(meta.destination)})"
    top_official_badge = "Official Certified Travel Quotation" if is_en else "عرض سعر سياحي رسمي معتمد"
    status_disp = _tr_val(getattr(meta, 'booking_status', None) or ('Preliminary Unconfirmed Booking' if is_en else 'حجز مبدئي غير مؤكد'), is_en)
    status_badge_lbl = f"Status: {html.escape(status_disp)}" if is_en else f"الحالة: {html.escape(status_disp)}"
    quote_badge_lbl = f"Quotation No: {html.escape(meta.quotation_no)}" if is_en else f"عرض سعر رقم: {html.escape(meta.quotation_no)}"
    booking_badge_lbl = f"Booking No: {html.escape(meta.booking_no)}" if is_en else f"رقم الحجز: {html.escape(meta.booking_no)}"
    raw_issue = getattr(meta, 'issue_date', None)
    if not raw_issue or raw_issue == '21 سبتمبر 2026':
        issue_disp = get_today_english_date() if is_en else get_today_arabic_date()
    else:
        issue_disp = raw_issue
    issue_badge_lbl = f"Issue Date: {html.escape(issue_disp)}" if is_en else f"تاريخ الإصدار: {html.escape(issue_disp)}"

    footer_brand = html.escape(meta.company_name_en if is_en else meta.company_name)
    footer_support = "24/7 Customer Support" if is_en else "خدمة العملاء 24/7"
    footer_agency = "Certified Travel & Tourism Agency" if is_en else "وكالة سفر وسياحة معتمدة"
    footer_crafted = "Crafted Exclusively for Your Journey" if is_en else "صُنِع خصيصاً لرحلتكم"
    footer_license = "Tourism License No: 73107681" if is_en else "ترخيص سياحي رقم: 73107681"
    footer_verified = "Official Automated & Verified Document" if is_en else "نسخة رسمية صادرة آلياً وموثقة"

    btn_pdf_cont = "Export PDF (Continuous Seamless)" if is_en else "تصدير PDF (متصل بدون حدود A4)"
    btn_pdf_a4 = "Export PDF (A4 Pages)" if is_en else "تصدير PDF (صفحات A4)"
    btn_whatsapp = "Share via WhatsApp" if is_en else "مشاركة عبر واتساب"

    header_title_display = f"{html.escape(meta.company_name_en)} | {html.escape(meta.company_name)}" if is_en else f"{html.escape(meta.company_name)} | {html.escape(meta.company_name_en)}"

    # Master HTML Document
    full_html = f"""<!DOCTYPE html>
<html dir="{html_dir}" lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>{doc_title}</title>

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
      direction: {html_dir};
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
            {header_title_display}
          </h1>
        </div>
        <div class="flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 px-3.5 py-1 rounded-full shadow-sm text-xs font-bold text-sky-100">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>{top_official_badge}</span>
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
          <span>{status_badge_lbl}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>📄</span>
          <span>{quote_badge_lbl}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>🔢</span>
          <span>{booking_badge_lbl}</span>
        </span>
        <span class="bg-sky-900/40 border border-sky-300/40 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full flex items-center gap-1 shadow-sm font-semibold text-white whitespace-nowrap font-num">
          <span>📅</span>
          <span>{issue_badge_lbl}</span>
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
          <span>{footer_brand}</span>
        </div>
        <div class="flex items-center justify-center">
          <div class="bg-white/10 border border-sky-300/30 px-3.5 py-1 rounded-full text-xs font-semibold text-sky-100 flex items-center gap-1.5 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>{footer_support}</span>
          </div>
        </div>
        <div class="flex items-center justify-end gap-1.5 text-xs font-bold text-sky-100">
          <span class="text-amber-400 text-sm">⭐</span>
          <span>{footer_agency}</span>
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
          <span>{footer_crafted}</span>
        </div>
        <div class="flex items-center justify-center">
          <div class="bg-sky-900/50 border border-sky-300/30 px-3.5 py-0.5 rounded-full text-sky-100 font-semibold font-num text-[11px]">{footer_license}</div>
        </div>
        <div class="flex items-center justify-end gap-1.5 text-emerald-400 font-bold">
          <span class="text-xs">✓</span>
          <span>{footer_verified}</span>
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
    <span>{btn_pdf_cont}</span>
  </button>
  <button class="bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" onclick="if(window.parent && typeof window.parent.exportPdf === 'function'){{ window.parent.exportPdf('a4'); }} else {{ window.printA4(); }}">
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
    </svg>
    <span>{btn_pdf_a4}</span>
  </button>
  <a class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" href="https://wa.me/966555434406" target="_blank">
    <span>💬</span>
    <span>{btn_whatsapp}</span>
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
