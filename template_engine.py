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

    # 2. FLIGHTS SECTION (Table Structure)
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
            flight_title = "حجز الطيران"

        has_any_type = any(getattr(f, "flight_type", None) for f in pkg.flights)

        flight_rows = []
        for f in pkg.flights:
            airline_sub = (
                f'<div class="text-[#0284c7] font-bold text-[11px] md:text-xs mt-0.5">{html.escape(f.airline)}</div>'
                if f.airline
                else ""
            )
            dept_time = html.escape(getattr(f, "departure_time", None) or "10:30 صباحاً")

            ftype = getattr(f, "flight_type", None) or ""
            if "دولي" in ftype:
                badge_type = '<span class="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 border border-indigo-300 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-sm whitespace-nowrap">🌐 دولي</span>'
            elif "داخلي" in ftype:
                badge_type = '<span class="inline-flex items-center gap-1 bg-sky-50 text-sky-700 border border-sky-300 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-sm whitespace-nowrap">✈️ داخلي</span>'
            else:
                badge_type = '<span class="inline-flex items-center gap-1 bg-slate-50 text-slate-700 border border-slate-300 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-sm whitespace-nowrap">✈️ رحلة</span>'

            type_td = f'<td class="p-2.5 text-center">{badge_type}</td>' if has_any_type else ""

            # Smart Luggage Display
            raw_luggage = (f.luggage or "20 كجم").strip()
            has_handbag = any(w in raw_luggage for w in ["يد", "كابينة", "cabin", "handbag", "carry"])
            has_pax = any(w in raw_luggage for w in ["لكل مسافر", "للراكب", "per person", "per passenger"])

            if has_handbag or "حسب" in raw_luggage:
                luggage_inner = f'<div class="font-bold text-slate-800">{html.escape(raw_luggage)}</div>'
            else:
                pax_line = "" if has_pax else '<div class="text-slate-400 text-[10px]">لكل مسافر</div>'
                has_shahn = "شحن" in raw_luggage
                shahn_suffix = "" if has_shahn else " شحن"
                luggage_inner = f"""
                <div class="font-bold text-slate-800">{html.escape(raw_luggage)}{shahn_suffix}</div>
                <div class="text-slate-500 text-[11px]">+ 7 كجم حقيبة يد (كابينة)</div>
                {pax_line}
                """

            row = f"""
            <tr class="hover:bg-sky-50/40 transition avoid-break">
              {type_td}
              <!-- Flight Date -->
              <td class="p-3 font-bold text-slate-800 whitespace-nowrap font-num">
                {html.escape(f.date)}
              </td>
              <!-- Departure Time -->
              <td class="p-3 font-bold text-slate-800 whitespace-nowrap">
                {dept_time}
              </td>
              <!-- From Airport & Airline -->
              <td class="p-3">
                <div class="font-bold text-slate-900">{html.escape(f.from_airport)}</div>
                {airline_sub}
              </td>
              <!-- To Airport -->
              <td class="p-3 font-bold text-sky-950">
                {html.escape(f.to_airport)}
              </td>
              <!-- Passengers -->
              <td class="p-3 leading-tight text-[11px] md:text-xs font-num">
                <div>البالغين: <span class="font-bold text-slate-900">{f.passengers.adults}</span></div>
                <div>الاطفال: <span class="font-bold text-slate-900">{f.passengers.children}</span></div>
                <div>رضيع: <span class="font-bold text-slate-900">{f.passengers.infants}</span></div>
              </td>
              <!-- Luggage -->
              <td class="p-3 leading-tight text-[11px] md:text-xs font-num">
                {luggage_inner}
              </td>
            </tr>
            """
            flight_rows.append(row)

        type_th = '<th class="py-2.5 px-2">نوع الرحلة</th>' if has_any_type else ""

        flights_html = f"""
        <!-- SECTION: FLIGHT BOOKING -->
        <section class="space-y-4 pt-2" data-purpose="flight-section">
          <!-- Flight Section Header Pill -->
          <div class="flex justify-center section-pill-badge">
            <div class="bg-[#0b4f71] text-white font-extrabold text-base md:text-lg px-8 py-2 rounded-full shadow-md flex items-center gap-2 border-2 border-sky-200">
              <span>✈</span>
              <span class="tracking-wide">{flight_title}</span>
            </div>
          </div>
          <div class="overflow-x-auto border border-amber-300 rounded-xl shadow-sm avoid-break">
            <table class="w-full text-center border-collapse text-xs md:text-sm">
              <thead>
                <tr class="bg-gradient-to-r from-[#ea580c] to-[#f97316] text-white font-extrabold divide-x divide-white/20">
                  {type_th}
                  <th class="py-2.5 px-2">التاريخ</th>
                  <th class="py-2.5 px-2">وقت الإقلاع</th>
                  <th class="py-2.5 px-2">من مطار</th>
                  <th class="py-2.5 px-2">إلى مطار</th>
                  <th class="py-2.5 px-2">المسافرين</th>
                  <th class="py-2.5 px-2">الأمتعة</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 text-slate-700 font-semibold bg-white">
                {"".join(flight_rows)}
              </tbody>
            </table>
          </div>
        </section>
        """

    # 3. TRANSPORTS & TOURS SECTION
    transports_html = ""
    if pkg.transports and len(pkg.transports) > 0:
        has_car_rental = bool(pkg.car_rentals and len(pkg.car_rentals) > 0)
        section_title = "الأنشطة والمسارات السياحية المقترحة" if has_car_rental else "المواصلات والجولات السياحية"
        section_icon = "🗺️" if has_car_rental else "🚗"

        city_blocks = []
        for grp in pkg.transports:
            item_rows = []
            for item in grp.items:
                activities_html = ""
                if item.activities:
                    acts = " | ".join([f"{html.escape(a)}" for a in item.activities])
                    activities_html = f'<div class="text-[11px] text-slate-400 font-normal mt-0.5">{acts}</div>'

                route_html = (
                    f'<div class="text-[11px] text-slate-400 font-normal mt-0.5">{html.escape(item.route_details)}</div>'
                    if item.route_details
                    else ""
                )

                veh_label = "بالسيارة المستأجرة" if has_car_rental else html.escape(item.vehicle_type)

                row = f"""
                <tr class="hover:bg-sky-50/40 transition avoid-break">
                  <!-- Flight / Transport Date -->
                  <td class="p-3 font-num text-slate-800 font-bold whitespace-nowrap">{html.escape(item.date)}</td>
                  <!-- Day Label -->
                  <td class="p-3 font-bold text-slate-800 whitespace-nowrap">{html.escape(item.day_label)}</td>
                  <!-- Vehicle Type Badge -->
                  <td class="p-3 text-center whitespace-nowrap">
                    <span class="inline-block border border-sky-300 bg-sky-50 text-[#0284c7] font-bold px-3 py-1 rounded-full text-xs shadow-sm">{veh_label}</span>
                  </td>
                  <!-- Description & Route -->
                  <td class="p-3 text-right">
                    <div class="font-bold text-slate-900 text-xs md:text-sm">{html.escape(item.title)}</div>
                    {route_html}
                    {activities_html}
                  </td>
                </tr>
                """
                item_rows.append(row)

            city_badge_text = "قيادة ذاتية (مسار مقترح)" if has_car_rental else "سيارة خاصة مع سائق"
            city_title_text = f"📍 مسار وجولات مقترحة: {html.escape(grp.city_name)}" if has_car_rental else f"📍 جولات ومواصلات: {html.escape(grp.city_name)}"

            scope_note = """
              <div class="text-[11px] text-teal-900 bg-teal-50 border border-teal-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                <span>💡</span>
                <span>برنامج وجولات مقترحة يمكنكم زيارتها بالسيارة المستأجرة بأريحية تامة حسب رغبتكم.</span>
              </div>
            """ if has_car_rental else """
              <div class="text-[11px] text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
                <span>ℹ️</span>
                <span>تشمل الجولات والتنقلات بسائق خاص داخل المدينة، والمسارات اختيارية وقابلة للتعديل حسب رغبتكم.</span>
              </div>
            """

            veh_col_title = "وسيلة التنقل" if has_car_rental else "نوع السيارة"

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
                      <th class="py-2.5 px-3 whitespace-nowrap" style="width: 20%;">{veh_col_title}</th>
                      <th class="py-2.5 px-4 text-right" style="width: 50%;">الوصف والمسار</th>
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
    notes_items = "".join([f'<li class="flex items-start gap-1.5"><span class="text-sky-600 font-black">•</span><span>{html.escape(n)}</span></li>' for n in effective_notes])
    notes_list_html = f"""
    <div class="bg-sky-50 border border-sky-200 rounded-xl p-3 md:p-4 text-xs text-sky-900 space-y-2 avoid-break">
      <div class="font-bold flex items-center gap-1.5 text-sky-950">
        <span class="text-base">📌</span>
        <span>الشروط والملاحظات المهمة:</span>
      </div>
      <ul class="space-y-1.5 pr-2">
        {notes_items}
      </ul>
    </div>
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
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Tajawal:wght@400;500;700;800;900&display=swap" rel="stylesheet">

<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script data-purpose="tailwind-config">
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
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
  <button class="bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" onclick="window.print()">
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
    </svg>
    <span>طباعة / حفظ كـ PDF</span>
  </button>
  <a class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-6 py-2.5 rounded-full shadow-lg flex items-center gap-2 transition duration-200 transform active:scale-95 text-sm" href="https://wa.me/966555434406" target="_blank">
    <span>💬</span>
    <span>مشاركة عبر واتساب</span>
  </a>
</div>
<!-- END: InteractiveActionButtons -->

</body>
</html>
"""
    return full_html
