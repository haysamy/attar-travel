"""
Data Models and Schema for Travel Package / Quotation Generator
Supports flexible, optional sections (Hotels, Flights, Transports, Extra Services, etc.)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class FlightPassengerInfo(BaseModel):
    adults: int = 2
    children: int = 0
    infants: int = 0

    def to_display_string(self) -> str:
        return f"البالغين: {self.adults}<br>الاطفال: {self.children}<br>رضيع: {self.infants}"


class FlightItem(BaseModel):
    date: str = Field(..., description="تاريخ الرحلة مثلاً 2026-11-25")
    from_airport: str = Field(..., description="مطار الإقلاع")
    to_airport: str = Field(..., description="مطار الوصول")
    airline: Optional[str] = Field(None, description="اسم شركة الطيران مثلاً اير اشيا")
    passengers: FlightPassengerInfo = Field(default_factory=FlightPassengerInfo)
    luggage: str = Field("20 كيلو", description="الوزن / الأمتعة")
    departure_time: Optional[str] = Field("10:30 صباحاً", description="وقت الإقلاع")
    flight_type: Optional[str] = Field(None, description="نوع الرحلة: طيران دولي أو طيران داخلي")


class HotelItem(BaseModel):
    day_range: str = Field(..., description="نطاق الأيام مثل: اليوم الاول - اليوم الثاني")
    city_order: str = Field(..., description="ترتيب المدينة مثل: المدينة الأولى")
    city_name: str = Field(..., description="اسم المدينة مثل: بانكوك")
    nights_count: int = Field(..., description="عدد الليالي")
    hotel_name: str = Field(..., description="اسم الفندق أو المنتجع")
    details_url: Optional[str] = Field("#", description="رابط تفاصيل الفندق")
    room_type: str = Field(..., description="نوع الغرفة مثل: ديلوكس مطلة على البحر")
    rooms_count: int = Field(1, description="عدد الغرف")
    meal_plan: str = Field("شامل الإفطار", description="نوع الوجبة")
    check_in: str = Field(..., description="تاريخ الدخول YYYY-MM-DD")
    check_out: str = Field(..., description="تاريخ الخروج YYYY-MM-DD")


class TransportItem(BaseModel):
    day_label: str = Field(..., description="اليوم مثل: اليوم الأول")
    date: str = Field(..., description="التاريخ YYYY-MM-DD")
    title: str = Field(..., description="عنوان التحرك أو النشاط")
    route_details: Optional[str] = Field(None, description="مسار التوصيل من وإلى")
    activities: Optional[List[str]] = Field(default_factory=list, description="قائمة المعالم والأنشطة السياحية")
    vehicle_type: str = Field("سيارة صغيرة", description="نوع السيارة")


class CityTransportGroup(BaseModel):
    city_name: str = Field(..., description="اسم المدينة لمجموعة الجولات مثل: بانكوك")
    items: List[TransportItem] = Field(default_factory=list)


class ExtraServiceItem(BaseModel):
    day_label: str = Field("اليوم الاول", description="اليوم")
    date: str = Field(..., description="التاريخ")
    country: str = Field(..., description="الدولة")
    service_name: str = Field(..., description="اسم الخدمة")
    quantity: int = Field(1, description="العدد")


class CarRentalItem(BaseModel):
    car_model: str = Field(..., description="نوع وموديل السيارة مثلاً تويوتا برادو 2025")
    pickup_location: str = Field(..., description="مكان وتاريخ الاستلام")
    dropoff_location: str = Field(..., description="مكان وتاريخ التسليم")
    pickup_date: str = Field(..., description="تاريخ الاستلام")
    dropoff_date: str = Field(..., description="تاريخ التسليم")
    days_count: Optional[int] = Field(None, description="عدد أيام الإيجار")
    insurance: str = Field("شامل كلي (Full Coverage)", description="نوع التأمين")
    transmission: str = Field("أوتوماتيك", description="ناقل الحركة")
    mileage: str = Field("كيلومترات مفتوحة", description="الكيلومترات")
    driver_type: str = Field("بدون سائق (قيادة ذاتية)", description="مع سائق أو قيادة ذاتية")


class QuotationMeta(BaseModel):
    company_name: str = Field("عطار للسياحة", description="اسم الشركة")
    company_name_en: str = Field("Attar Travel", description="اسم الشركة بالإنجليزية")
    tagline: str = Field("عطار ترافل", description="الشعار الترويجي")
    booking_no: str = Field("TAJ2411724881", description="رقم الحجز")
    quotation_no: str = Field("QTAJ2411724881", description="رقم عرض السعر")
    destination: str = Field("تايلند", description="الوجهة السياحية")
    total_nights: Optional[int] = Field(14, description="إجمالي عدد الليالي")
    issue_date: Optional[str] = Field("21 سبتمبر 2026", description="تاريخ الإصدار")
    booking_status: Optional[str] = Field("حجز مبدئي غير مؤكد", description="حالة الحجز")


class PriceTotal(BaseModel):
    amount: str = Field("12,875.32", description="المبلغ الإجمالي")
    currency: str = Field("ريال سعودي", description="العملة")


class TravelPackage(BaseModel):
    meta: QuotationMeta = Field(default_factory=QuotationMeta)
    hotels: Optional[List[HotelItem]] = Field(default_factory=list, description="قائمة الفنادق (اختياري)")
    flights: Optional[List[FlightItem]] = Field(default_factory=list, description="قائمة الرحلات الجوية (اختياري)")
    transports: Optional[List[CityTransportGroup]] = Field(default_factory=list, description="جولات ومواصلات حسب المدينة (اختياري)")
    car_rentals: Optional[List[CarRentalItem]] = Field(default_factory=list, description="استئجار سيارات (اختياري)")
    extra_services: Optional[List[ExtraServiceItem]] = Field(default_factory=list, description="خدمات إضافية (اختياري)")
    total_price: Optional[PriceTotal] = Field(None, description="السعر الإجمالي (اختياري)")
    notes: Optional[List[str]] = Field(default_factory=list, description="قائمة الشروط والملاحظات المهمة")
