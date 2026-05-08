from __future__ import annotations

import math
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


OUTPUT_PATH = Path("synthetic_data/UC-190_Additional_PRD_Datasets_Synthetic_Data.xlsx")
SEED = 1902026
random.seed(SEED)


REGIONS = ["Abu Dhabi City", "Al Ain", "Al Dhafra"]
DISTRICTS = ["Yas Island", "Saadiyat", "Mussafah", "Khalifa City", "Al Ain Central", "Ruwais"]
SECTORS = ["Construction", "Manufacturing", "Mining", "Energy", "Hospitality", "Retail", "Government"]
RETAIL_CATEGORIES = ["Food", "Clothing", "Electronics", "Restaurants", "Travel", "Household Goods"]
PRICE_PRODUCTS = [
    ("P001", "Rice 5kg", "Food", "KG"),
    ("P002", "Chicken 1kg", "Food", "KG"),
    ("P003", "Eggs 30 pack", "Food", "PACK"),
    ("P004", "Dates 1kg", "Food", "KG"),
    ("P005", "School uniform", "Clothing", "ITEM"),
    ("P006", "Abaya", "Clothing", "ITEM"),
    ("P007", "Smartphone", "Electronics", "ITEM"),
    ("P008", "Laptop", "Electronics", "ITEM"),
    ("P009", "Hotel room night", "Hospitality", "NIGHT"),
    ("P010", "Restaurant meal", "Restaurants", "MEAL"),
    ("P011", "Petrol litre", "Transport", "LITRE"),
    ("P012", "Electricity kWh", "Utilities", "KWH"),
]


def daterange(start: date, end: date, step_days: int = 1):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=step_days)


def month_range(start_year: int, start_month: int, end_year: int, end_month: int):
    year = start_year
    month = start_month
    while (year, month) <= (end_year, end_month):
        yield year, month
        month += 1
        if month == 13:
            month = 1
            year += 1


def week_range(start: date, end: date):
    current = start - timedelta(days=start.weekday())
    while current <= end:
        yield current
        current += timedelta(days=7)


def month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def ramadan_window(year: int) -> tuple[date, date]:
    windows = {
        2024: (date(2024, 3, 11), date(2024, 4, 9)),
        2025: (date(2025, 3, 1), date(2025, 3, 29)),
        2026: (date(2026, 2, 18), date(2026, 3, 19)),
        2027: (date(2027, 2, 7), date(2027, 3, 8)),
        2028: (date(2028, 1, 27), date(2028, 2, 25)),
    }
    return windows[year]


def eid_fitr_window(year: int) -> tuple[date, date]:
    _, ramadan_end = ramadan_window(year)
    start = ramadan_end + timedelta(days=1)
    return start, start + timedelta(days=3)


def eid_adha_window(year: int) -> tuple[date, date]:
    windows = {
        2024: (date(2024, 6, 16), date(2024, 6, 19)),
        2025: (date(2025, 6, 6), date(2025, 6, 9)),
        2026: (date(2026, 5, 27), date(2026, 5, 30)),
        2027: (date(2027, 5, 16), date(2027, 5, 19)),
        2028: (date(2028, 5, 5), date(2028, 5, 8)),
    }
    return windows[year]


def white_friday(year: int) -> date:
    current = date(year, 11, 30)
    while current.weekday() != 4:
        current -= timedelta(days=1)
    return current


def is_between(day: date, window: tuple[date, date]) -> bool:
    return window[0] <= day <= window[1]


def count_days(start: date, end: date, predicate) -> int:
    return sum(1 for day in daterange(start, end) if predicate(day))


def public_holiday_name(day: date) -> str:
    if day.month == 1 and day.day == 1:
        return "New Year"
    if day.month == 12 and day.day in (2, 3):
        return "UAE National Day"
    if is_between(day, eid_fitr_window(day.year)):
        return "Eid Al Fitr"
    if is_between(day, eid_adha_window(day.year)):
        return "Eid Al Adha"
    return ""


def features(day: date) -> dict:
    return {
        "is_weekend": day.weekday() in (5, 6),
        "holiday_name": public_holiday_name(day),
        "is_ramadan": is_between(day, ramadan_window(day.year)),
        "is_eid_al_fitr": is_between(day, eid_fitr_window(day.year)),
        "is_eid_al_adha": is_between(day, eid_adha_window(day.year)),
        "is_summer_heat": day.month in (6, 7, 8, 9),
        "is_tourism_peak": day.month in (1, 2, 3, 10, 11, 12),
        "is_retail_event": abs((day - white_friday(day.year)).days) <= 3,
        "is_fiscal_q4": day.month in (10, 11, 12),
    }


def style_sheet(ws):
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for column_cells in ws.columns:
        column = column_cells[0].column
        max_length = 0
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, min(len(value), 55))
        ws.column_dimensions[get_column_letter(column)].width = max(12, min(max_length + 2, 45))
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top")


def add_sheet(wb: Workbook, name: str, rows: list[dict]):
    ws = wb.create_sheet(name)
    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row.get(header, "") for header in headers])
        style_sheet(ws)
    return ws


def rnd(value: float, digits: int = 2) -> float:
    return round(float(value), digits)


def noise(scale: float) -> float:
    return random.uniform(-scale, scale)


def seasonal_strength(day: date, driver: str) -> float:
    f = features(day)
    if driver == "Ramadan":
        return 1.0 if f["is_ramadan"] else 0.0
    if driver == "Eid":
        return 1.0 if f["is_eid_al_fitr"] or f["is_eid_al_adha"] else 0.0
    if driver == "Summer heat":
        return 1.0 if f["is_summer_heat"] else 0.0
    if driver == "Tourism":
        return 1.0 if f["is_tourism_peak"] else 0.0
    if driver == "Retail event":
        return 1.0 if f["is_retail_event"] else 0.0
    if driver == "Fiscal":
        return 1.0 if f["is_fiscal_q4"] else 0.0
    return 0.0


def readme_rows():
    return [
        {"SECTION": "Workbook", "DETAIL": "UC-190 additional PRD synthetic datasets"},
        {"SECTION": "Purpose", "DETAIL": "Synthetic data for the additional Seasonality Pattern Highlighter datasets listed by the user: Hijri calendar, working days, weather, tourism events, fiscal, mobility, price microdata, construction, IPI, retail, e-commerce events, diagnostics, outliers, and model metadata."},
        {"SECTION": "PRD analysis", "DETAIL": "The workspace does not contain a file named prd.md. This workbook is based on the uploaded UC-190 markdown, the PRD text shared in the conversation, and the additional dataset table pasted by the user."},
        {"SECTION": "Synthetic data notice", "DETAIL": "All records are fictional and designed for Bayaan UI, analytics, seasonal modelling, and alert testing only."},
        {"SECTION": "Seasonality model support", "DETAIL": "Datasets include moving-holiday regressors, calendar effects, heat cycles, event effects, fiscal spikes, intra-month behaviour, price volatility, diagnostics, and metadata for reproducibility."},
    ]


def catalog_rows():
    datasets = [
        ("HIJRI_CALENDAR", "Moving-holiday regression input", "Ramadan/Eid flags, Hijri month, pre/post Ramadan, days in month"),
        ("PUBLIC_HOLIDAY_WORKDAY", "Calendar and trading-day adjustment", "working days, weekends, holiday type, business day counts"),
        ("WEATHER_TEMPERATURE", "Extreme heat cycle modelling", "daily max/avg temperature, heatwave days, humidity, cooling degree days"),
        ("TOURISM_EVENT_CALENDAR", "Event-driven tourism seasonality", "event name, dates, location, attendance, impact score"),
        ("GOVERNMENT_FISCAL", "Fiscal year and Q4 spending effects", "monthly expenditure, capital expenditure, procurement cycles"),
        ("MOBILITY_DAILY", "Intra-month behavioural seasonality", "daily mobility index by location and movement type"),
        ("PRICE_MICRODATA", "Product-level CPI seasonal decomposition", "SKU, category, weekly price, quantity sold, retailer"),
        ("CONSTRUCTION_ACTIVITY", "Summer construction slowdown", "output index, permits, starts, completions, labour hours"),
        ("INDUSTRIAL_PRODUCTION_IPI", "Core production monitoring", "production index, sector, volume, working hours"),
        ("RETAIL_SALES_INDEX", "Official retail benchmark", "sales value, category, YoY/MoM, segment, region"),
        ("ECOMMERCE_PROMO_EVENTS", "Evolving retail seasonality", "event windows, intensity, online/offline channel"),
        ("HIGH_FREQ_PRICE", "Sub-month price fluctuation", "daily/weekly price index, volatility, short-term trend"),
        ("RESIDUAL_DIAGNOSTICS", "Quality assurance for seasonal models", "residuals, spectral tests, F-tests, seasonal strength"),
        ("OUTLIER_DETECTION", "Pre-decomposition shock treatment", "outlier type, level shift, temporary change, correction applied"),
        ("MODEL_METADATA", "Auditability and reproducibility", "model type, ARIMA order, parameters, version, calibration date"),
    ]
    return [{"SHEET_NAME": name, "WHY_NEEDED": why, "KEY_SYNTHETIC_FIELDS": fields} for name, why, fields in datasets]


def hijri_calendar_rows():
    rows = []
    for day in daterange(date(2024, 1, 1), date(2028, 12, 31)):
        f = features(day)
        ram_start, ram_end = ramadan_window(day.year)
        pre_start = ram_start - timedelta(days=14)
        post_end = eid_fitr_window(day.year)[1] + timedelta(days=14)
        hijri_month = "Ramadan" if f["is_ramadan"] else "Shawwal" if f["is_eid_al_fitr"] else "Dhul Hijjah" if f["is_eid_al_adha"] else "Synthetic Hijri Month"
        rows.append({
            "GREGORIAN_DATE": day.isoformat(),
            "GREGORIAN_YEAR": day.year,
            "HIJRI_YEAR": 1445 + (day.year - 2024),
            "HIJRI_MONTH": hijri_month,
            "HIJRI_DAY_SYNTHETIC": ((day.timetuple().tm_yday - 1) % 30) + 1,
            "RAMADAN_START": ram_start.isoformat(),
            "RAMADAN_END": ram_end.isoformat(),
            "EID_AL_FITR_START": eid_fitr_window(day.year)[0].isoformat(),
            "EID_AL_FITR_END": eid_fitr_window(day.year)[1].isoformat(),
            "EID_AL_ADHA_START": eid_adha_window(day.year)[0].isoformat(),
            "EID_AL_ADHA_END": eid_adha_window(day.year)[1].isoformat(),
            "IS_RAMADAN": f["is_ramadan"],
            "IS_PRE_RAMADAN": pre_start <= day < ram_start,
            "IS_POST_RAMADAN": eid_fitr_window(day.year)[1] < day <= post_end,
            "IS_EID": f["is_eid_al_fitr"] or f["is_eid_al_adha"],
            "RAMADAN_DAYS_IN_GREGORIAN_MONTH": count_days(date(day.year, day.month, 1), month_end(day.year, day.month), lambda d: features(d)["is_ramadan"]),
        })
    return rows


def public_holiday_workday_rows():
    rows = []
    for year, month in month_range(2024, 1, 2028, 12):
        start = date(year, month, 1)
        end = month_end(year, month)
        working = count_days(start, end, lambda d: not features(d)["is_weekend"] and not features(d)["holiday_name"])
        weekends = count_days(start, end, lambda d: features(d)["is_weekend"])
        holidays = count_days(start, end, lambda d: bool(features(d)["holiday_name"]))
        rows.append({
            "YEAR": year,
            "MONTH": month,
            "PERIOD_LABEL": f"{year}-{month:02d}",
            "WORKING_DAYS": working,
            "WEEKEND_DAYS": weekends,
            "PUBLIC_HOLIDAYS": holidays,
            "BUSINESS_DAYS": working,
            "FRIDAY_COUNT": count_days(start, end, lambda d: d.weekday() == 4),
            "SATURDAY_COUNT": count_days(start, end, lambda d: d.weekday() == 5),
            "SUNDAY_COUNT": count_days(start, end, lambda d: d.weekday() == 6),
            "MONTH_DAY_WEIGHTS": rnd(working / max(1, end.day), 4),
            "HOLIDAY_TYPES": ", ".join(sorted({features(d)["holiday_name"] for d in daterange(start, end) if features(d)["holiday_name"]})),
        })
    return rows


def weather_rows():
    rows = []
    for day in daterange(date(2025, 1, 1), date(2028, 12, 31)):
        for region in REGIONS:
            summer = features(day)["is_summer_heat"]
            region_add = 2.5 if region == "Al Ain" else -1.0 if region == "Al Dhafra" else 0
            seasonal = 9 * math.sin(2 * math.pi * (day.timetuple().tm_yday - 100) / 365)
            avg_temp = 28 + seasonal + region_add + noise(2.2)
            max_temp = avg_temp + random.uniform(5, 10)
            humidity = random.uniform(35, 78) if region != "Al Dhafra" else random.uniform(25, 55)
            cdd = max(0, avg_temp - 24)
            rows.append({
                "WEATHER_DATE": day.isoformat(),
                "REGION": region,
                "MAX_TEMPERATURE_C": rnd(max_temp),
                "AVG_TEMPERATURE_C": rnd(avg_temp),
                "HEATWAVE_DAY_GT45C": max_temp > 45,
                "HUMIDITY_PCT": rnd(humidity),
                "COOLING_DEGREE_DAYS": rnd(cdd),
                "TEMPERATURE_INDEX": rnd((avg_temp - 20) / 25 * 100),
                "SUMMER_HEAT_FLAG": summer,
            })
    return rows


def tourism_event_rows():
    rows = []
    event_templates = [
        ("Formula 1 Grand Prix", "Sports", "Yas Island", 95, 11),
        ("Cultural Season Festival", "Culture", "Saadiyat", 74, 12),
        ("International Exhibition", "Business", "ADNEC", 68, 2),
        ("Eid Travel Peak", "Holiday", "Abu Dhabi City", 82, 3),
        ("Summer Family Offer", "Tourism Promotion", "Yas Island", 50, 7),
        ("New Year Events", "Celebration", "Abu Dhabi City", 88, 12),
    ]
    event_id = 1
    for year in range(2024, 2029):
        for name, event_type, location, impact, month in event_templates:
            start = date(year, month, random.randint(3, 20))
            duration = random.randint(2, 8)
            rows.append({
                "EVENT_ID": f"EVT_{event_id:04d}",
                "EVENT_NAME": f"{name} {year}",
                "EVENT_TYPE": event_type,
                "START_DATE": start.isoformat(),
                "END_DATE": (start + timedelta(days=duration)).isoformat(),
                "LOCATION": location,
                "EXPECTED_ATTENDANCE": random.randint(8000, 120000),
                "EVENT_CATEGORY": event_type,
                "EVENT_IMPACT_SCORE": rnd(impact + noise(8), 1),
                "AFFECTED_INDICATORS": "Hotel occupancy; tourist arrivals; retail sales; transport",
            })
            event_id += 1
    return rows


def government_fiscal_rows():
    rows = []
    for year, month in month_range(2024, 1, 2028, 12):
        fiscal_q = ((month - 1) // 3) + 1
        q4_spike = 1.35 if fiscal_q == 4 else 1.0
        for sector in ["Infrastructure", "Education", "Health", "Housing", "Culture and Tourism", "Digital Government"]:
            base = random.uniform(180, 950)
            monthly = base * q4_spike * (1.15 if month == 12 else 1.0)
            capex = monthly * random.uniform(0.25, 0.58)
            rows.append({
                "YEAR": year,
                "MONTH": month,
                "FISCAL_QUARTER": f"Q{fiscal_q}",
                "SECTOR": sector,
                "MONTHLY_GOVERNMENT_EXPENDITURE_AED_MN": rnd(monthly),
                "CAPITAL_EXPENDITURE_AED_MN": rnd(capex),
                "CURRENT_EXPENDITURE_AED_MN": rnd(monthly - capex),
                "BUDGET_CYCLE_PERIOD": "Year-end closeout" if fiscal_q == 4 else "Normal execution",
                "PROCUREMENT_CYCLE": random.choice(["Tendering", "Award", "Mobilisation", "Delivery", "Closeout"]),
                "FISCAL_YEAR_INDICATOR": f"FY{year}",
                "Q4_SPENDING_SPIKE_FLAG": fiscal_q == 4,
            })
    return rows


def mobility_rows():
    rows = []
    for day in daterange(date(2026, 1, 1), date(2028, 12, 31)):
        f = features(day)
        for location in ["Retail", "Workplace", "Residential", "Transit", "Tourism Zone"]:
            base = 100
            if location == "Workplace" and (f["is_ramadan"] or f["is_weekend"]):
                base -= 18
            if location in ("Retail", "Tourism Zone") and (f["is_tourism_peak"] or f["is_eid_al_fitr"] or f["is_eid_al_adha"]):
                base += 16
            if location == "Residential" and f["is_summer_heat"]:
                base += 12
            rows.append({
                "MOBILITY_DATE": day.isoformat(),
                "LOCATION_TYPE": location,
                "REGION": random.choice(REGIONS),
                "WEEKDAY_WEEKEND": "Weekend" if f["is_weekend"] else "Weekday",
                "MOVEMENT_INDEX": rnd(base + noise(7)),
                "MOBILITY_CHANGE_PCT": rnd(base - 100 + noise(4)),
                "RAMADAN_WORKING_HOURS_FLAG": f["is_ramadan"],
                "TOURISM_FLOW_FLAG": f["is_tourism_peak"],
                "MOBILITY_HEATMAP_SCORE": rnd((base + noise(5)) / 130 * 100),
            })
    return rows


def price_microdata_rows():
    rows = []
    retailers = ["Retailer_A", "Retailer_B", "Retailer_C", "Online_Market"]
    for week in week_range(date(2026, 1, 1), date(2028, 12, 31)):
        f = features(week)
        for product_id, product_name, category, unit in PRICE_PRODUCTS:
            for retailer in retailers:
                base = random.uniform(8, 500)
                if category == "Food" and f["is_ramadan"]:
                    base *= 1.10
                if category in ("Clothing", "Electronics") and f["is_retail_event"]:
                    base *= 0.86
                quantity = random.randint(20, 900)
                rows.append({
                    "PRICE_DATE": week.isoformat(),
                    "SKU_ID": product_id,
                    "PRODUCT_NAME": product_name,
                    "ID_CATEGORY": category,
                    "UNIT": unit,
                    "DAILY_WEEKLY_PRICE": rnd(base + noise(base * 0.05)),
                    "QUANTITY_SOLD": quantity,
                    "RETAILER_ID": retailer,
                    "PRICE_CHANGE_FREQUENCY": random.choice(["Daily", "Weekly", "Monthly"]),
                    "RAMADAN_FOOD_FLAG": category == "Food" and f["is_ramadan"],
                    "PROMOTION_FLAG": f["is_retail_event"],
                })
    return rows


def construction_activity_rows():
    rows = []
    for year, month in month_range(2024, 1, 2028, 12):
        period_date = date(year, month, 1)
        f = features(period_date)
        for region in REGIONS:
            for classification in ["Residential", "Commercial", "Infrastructure", "Hospitality"]:
                heat_effect = -18 if f["is_summer_heat"] else 0
                output = 100 + (year - 2024) * 2 + heat_effect + noise(5)
                permits = int(120 + noise(25) + (15 if classification == "Residential" else 0))
                starts = int(permits * random.uniform(0.45, 0.75))
                completions = int(permits * random.uniform(0.25, 0.55))
                labour_hours = max(10000, 80000 + output * 900 + noise(12000))
                rows.append({
                    "YEAR": year,
                    "MONTH": month,
                    "REGION": region,
                    "SECTOR_CLASSIFICATION": classification,
                    "MONTHLY_CONSTRUCTION_OUTPUT_INDEX": rnd(output),
                    "PERMITS_ISSUED": permits,
                    "PROJECT_STARTS": starts,
                    "PROJECT_COMPLETIONS": completions,
                    "LABOUR_HOURS": int(labour_hours),
                    "SUMMER_HEAT_FLAG": f["is_summer_heat"],
                    "EXPECTED_Q3_DROP_FLAG": month in (7, 8, 9),
                })
    return rows


def ipi_rows():
    rows = []
    for year, month in month_range(2024, 1, 2028, 12):
        period_date = date(year, month, 1)
        f = features(period_date)
        for sector in ["Manufacturing", "Mining", "Energy", "Food Processing", "Construction Materials"]:
            working_days = count_days(period_date, month_end(year, month), lambda d: not features(d)["is_weekend"] and not features(d)["holiday_name"])
            sector_effect = -5 if sector == "Construction Materials" and f["is_summer_heat"] else 4 if sector == "Food Processing" and f["is_ramadan"] else 0
            index = 100 + (year - 2024) * 1.8 + sector_effect + noise(4)
            rows.append({
                "YEAR": year,
                "MONTH": month,
                "SECTOR_BREAKDOWN": sector,
                "MONTHLY_PRODUCTION_INDEX": rnd(index),
                "PRODUCTION_VOLUME": rnd(index * random.uniform(850, 1200)),
                "WORKING_HOURS": int(working_days * random.uniform(7500, 13000)),
                "WORKING_DAYS": working_days,
                "CALENDAR_EFFECT_FLAG": working_days < 20,
                "SEASONAL_DRIVER": "Ramadan food processing" if sector == "Food Processing" and f["is_ramadan"] else "Summer heat" if f["is_summer_heat"] else "Normal production cycle",
            })
    return rows


def retail_sales_rows():
    rows = []
    for year, month in month_range(2024, 1, 2028, 12):
        period_date = date(year, month, 1)
        f = features(period_date)
        for region in REGIONS:
            for category in RETAIL_CATEGORIES:
                seasonal = 1.0
                if category in ("Food", "Restaurants") and f["is_ramadan"]:
                    seasonal += 0.18
                if category in ("Clothing", "Electronics") and month == 11:
                    seasonal += 0.16
                if category == "Travel" and f["is_tourism_peak"]:
                    seasonal += 0.14
                sales = random.uniform(80, 650) * seasonal * (1 + (year - 2024) * 0.035)
                rows.append({
                    "YEAR": year,
                    "MONTH": month,
                    "REGION": region,
                    "CATEGORY_BREAKDOWN": category,
                    "RETAIL_SEGMENT_CLASSIFICATION": random.choice(["Mall", "High street", "Online", "Grocery chain"]),
                    "MONTHLY_RETAIL_SALES_VALUE_AED_MN": rnd(sales),
                    "MOM_GROWTH_PCT": rnd(noise(8) + (seasonal - 1) * 100),
                    "YOY_GROWTH_PCT": rnd(3.5 + noise(5) + (seasonal - 1) * 25),
                    "OFFICIAL_INDEX_VALUE": rnd(100 + (year - 2024) * 3 + (seasonal - 1) * 20 + noise(3)),
                    "SEASONAL_DRIVER": "Ramadan" if f["is_ramadan"] else "White Friday" if month == 11 else "Tourism peak" if f["is_tourism_peak"] else "Normal",
                })
    return rows


def ecommerce_event_rows():
    rows = []
    events = [
        ("White Friday", 11, 22, 8, "Online"),
        ("Singles Day", 11, 11, 2, "Online"),
        ("Year-end Sale", 12, 20, 10, "Both"),
        ("Ramadan Online Deals", 2, 18, 21, "Both"),
        ("Back to School", 8, 20, 14, "Offline"),
    ]
    event_id = 1
    for year in range(2024, 2029):
        for event_name, month, day_num, duration, channel in events:
            start = date(year, month, min(day_num, month_end(year, month).day))
            intensity = random.uniform(45, 95)
            rows.append({
                "EVENT_ID": f"PROMO_{event_id:04d}",
                "EVENT_NAME": f"{event_name} {year}",
                "START_DATE": start.isoformat(),
                "END_DATE": (start + timedelta(days=duration)).isoformat(),
                "DISCOUNT_INTENSITY_INDEX": rnd(intensity),
                "CHANNEL": channel,
                "ONLINE_OFFLINE_FLAG": channel,
                "AFFECTED_CATEGORIES": random.choice(["Electronics; Clothing", "Food; Restaurants", "Travel; Hotels", "All retail"]),
                "EVOLVING_INTENSITY_PARAMETER": rnd(intensity / 100 + (year - 2024) * 0.05, 3),
                "EXPECTED_SEASONAL_DIRECTION": "Increase sales" if event_name != "Year-end Sale" else "Shift demand from January",
            })
            event_id += 1
    return rows


def high_freq_price_rows():
    rows = []
    for day in daterange(date(2026, 1, 1), date(2028, 12, 31), 2):
        f = features(day)
        for category in ["Food", "Clothing", "Transport", "Hospitality", "Utilities"]:
            base = 100 + (day.year - 2026) * 2
            if category == "Food" and f["is_ramadan"]:
                base += 6
            if category == "Hospitality" and f["is_tourism_peak"]:
                base += 9
            if category == "Utilities" and f["is_summer_heat"]:
                base += 7
            volatility = random.uniform(0.5, 4.5)
            rows.append({
                "PRICE_DATE": day.isoformat(),
                "CATEGORY": category,
                "DAILY_WEEKLY_PRICE_INDEX": rnd(base + noise(volatility)),
                "SHORT_TERM_PRICE_FLUCTUATION": rnd(noise(volatility)),
                "CATEGORY_LEVEL_TREND": rnd(base - 100),
                "VOLATILITY_INDEX": rnd(volatility),
                "SUB_MONTH_PATTERN": "Ramadan daily fluctuation" if f["is_ramadan"] else "Weekend price cycle" if features(day)["is_weekend"] else "Normal",
            })
    return rows


def residual_diagnostics_rows():
    rows = []
    indicators = ["HOTEL_OCC_RATE", "RETAIL_SALES_INDEX", "CPI_FOOD_PRICE", "CONSTRUCTION_OUTPUT", "IPI_MANUFACTURING", "ECOMMERCE_SPEND", "MOBILITY_RETAIL"]
    for year, month in month_range(2025, 1, 2028, 12):
        for indicator in indicators:
            residual = noise(2.5)
            f_test = random.uniform(0.01, 0.35)
            spectral = random.uniform(0.01, 0.40)
            pass_flag = f_test > 0.05 and spectral > 0.05
            rows.append({
                "MODEL_RUN_ID": f"RUN_{year}{month:02d}_{indicator}",
                "INDICATOR_ID": indicator,
                "YEAR": year,
                "MONTH": month,
                "RESIDUAL_VALUE": rnd(residual),
                "SPECTRAL_TEST_P_VALUE": rnd(spectral, 4),
                "F_TEST_P_VALUE": rnd(f_test, 4),
                "SEASONAL_STRENGTH_METRIC": rnd(random.uniform(0.1, 0.95), 3),
                "DIAGNOSTIC_FLAG": "Pass" if pass_flag else "Fail",
                "RESIDUAL_SEASONALITY_DETECTED": not pass_flag,
            })
    return rows


def outlier_detection_rows():
    rows = []
    outlier_types = ["Additive outlier", "Level shift", "Temporary change"]
    indicators = ["RETAIL_SALES_INDEX", "HOTEL_OCC_RATE", "CONSTRUCTION_OUTPUT", "IPI_MANUFACTURING", "MOBILITY_WORKPLACE"]
    for idx in range(1, 121):
        indicator = random.choice(indicators)
        day = date(2025, 1, 1) + timedelta(days=random.randint(0, 1200))
        outlier_type = random.choice(outlier_types)
        severity = random.choice(["Low", "Medium", "High"])
        rows.append({
            "OUTLIER_ID": f"OUT_{idx:04d}",
            "INDICATOR_ID": indicator,
            "OUTLIER_DATE": day.isoformat(),
            "OUTLIER_TYPE": outlier_type,
            "ADDITIVE_OUTLIER_VALUE": rnd(noise(12)) if outlier_type == "Additive outlier" else "",
            "LEVEL_SHIFT_VALUE": rnd(noise(8)) if outlier_type == "Level shift" else "",
            "TEMPORARY_CHANGE_VALUE": rnd(noise(6)) if outlier_type == "Temporary change" else "",
            "TIMESTAMP": datetime.combine(day, datetime.min.time()).replace(hour=random.randint(0, 23)).isoformat(),
            "SEVERITY": severity,
            "CORRECTION_APPLIED": severity in ("Medium", "High"),
            "CORRECTION_METHOD": random.choice(["RegARIMA intervention", "Winsorisation", "Analyst reviewed", "No correction"]),
        })
    return rows


def model_metadata_rows():
    rows = []
    models = [
        ("HOTEL_OCC_RATE", "X-13ARIMA-SEATS", "(0,1,1)(0,1,1)", "tourism_peak,event_calendar,eid"),
        ("RETAIL_SALES_INDEX", "X-13ARIMA-SEATS", "(1,1,1)(0,1,1)", "ramadan,eid,white_friday,working_days"),
        ("CONSTRUCTION_OUTPUT", "STL", "NA", "summer_heat,working_days"),
        ("IPI_MANUFACTURING", "X-13ARIMA-SEATS", "(1,0,1)(1,1,0)", "working_days,public_holidays"),
        ("MOBILITY_DAILY", "TBATS", "NA", "weekday,ramadan,tourism,heat"),
        ("HIGH_FREQ_PRICE", "TBATS", "NA", "weekday,ramadan,retail_events"),
        ("GOVERNMENT_FISCAL", "STL", "NA", "fiscal_q4,budget_cycle"),
    ]
    for idx, (indicator, model_type, arima, regressors) in enumerate(models, start=1):
        rows.append({
            "MODEL_ID": f"UC190_MODEL_{idx:03d}",
            "INDICATOR_ID": indicator,
            "MODEL_TYPE": model_type,
            "PARAMETERS_ARIMA_ORDER": arima,
            "DECOMPOSITION_MODE": "Auto additive/multiplicative",
            "REGRESSION_INPUTS": regressors,
            "VERSION": "v1.0-synthetic",
            "CALIBRATION_DATE": date(2028, 12, 31).isoformat(),
            "TRANSFORMATION": random.choice(["None", "Log", "Box-Cox"]),
            "QUALITY_SCORE": rnd(random.uniform(0.72, 0.98), 3),
            "OWNER": "Research & Innovation - Analytics Research",
            "AUDIT_STATUS": "Ready for methodology review",
        })
    return rows


def prd_analysis_rows():
    return [
        {"PRD_REQUIREMENT": "Moving-holiday adjustment", "SYNTHETIC_SHEETS": "HIJRI_CALENDAR, PUBLIC_HOLIDAY_WORKDAY, MODEL_METADATA", "TESTING_VALUE": "Validate Ramadan/Eid regressors and month-splitting logic."},
        {"PRD_REQUIREMENT": "Extreme heat cycles", "SYNTHETIC_SHEETS": "WEATHER_TEMPERATURE, CONSTRUCTION_ACTIVITY, HIGH_FREQ_PRICE", "TESTING_VALUE": "Test summer heat annotation and construction/electricity effects."},
        {"PRD_REQUIREMENT": "Tourism season and events", "SYNTHETIC_SHEETS": "TOURISM_EVENT_CALENDAR, MOBILITY_DAILY, RETAIL_SALES_INDEX", "TESTING_VALUE": "Separate normal event uplift from anomalies."},
        {"PRD_REQUIREMENT": "Evolving retail seasonality", "SYNTHETIC_SHEETS": "ECOMMERCE_PROMO_EVENTS, RETAIL_SALES_INDEX, PRICE_MICRODATA", "TESTING_VALUE": "Detect White Friday and online-channel seasonality shifts."},
        {"PRD_REQUIREMENT": "Quality diagnostics", "SYNTHETIC_SHEETS": "RESIDUAL_DIAGNOSTICS, OUTLIER_DETECTION, MODEL_METADATA", "TESTING_VALUE": "Test residual seasonality alerts, outlier treatment, auditability."},
        {"PRD_REQUIREMENT": "Core economic monitoring", "SYNTHETIC_SHEETS": "INDUSTRIAL_PRODUCTION_IPI, GOVERNMENT_FISCAL, CONSTRUCTION_ACTIVITY", "TESTING_VALUE": "Support business-cycle analysis and prevent calendar-driven misinterpretation."},
    ]


def build_workbook():
    wb = Workbook()
    wb.remove(wb.active)
    add_sheet(wb, "00_README", readme_rows())
    add_sheet(wb, "01_PRD_ANALYSIS", prd_analysis_rows())
    add_sheet(wb, "02_DATASET_CATALOG", catalog_rows())
    add_sheet(wb, "HIJRI_CALENDAR", hijri_calendar_rows())
    add_sheet(wb, "PUBLIC_HOLIDAY_WORKDAY", public_holiday_workday_rows())
    add_sheet(wb, "WEATHER_TEMPERATURE", weather_rows())
    add_sheet(wb, "TOURISM_EVENT_CALENDAR", tourism_event_rows())
    add_sheet(wb, "GOVERNMENT_FISCAL", government_fiscal_rows())
    add_sheet(wb, "MOBILITY_DAILY", mobility_rows())
    add_sheet(wb, "PRICE_MICRODATA", price_microdata_rows())
    add_sheet(wb, "CONSTRUCTION_ACTIVITY", construction_activity_rows())
    add_sheet(wb, "INDUSTRIAL_PRODUCTION_IPI", ipi_rows())
    add_sheet(wb, "RETAIL_SALES_INDEX", retail_sales_rows())
    add_sheet(wb, "ECOMMERCE_PROMO_EVENTS", ecommerce_event_rows())
    add_sheet(wb, "HIGH_FREQ_PRICE", high_freq_price_rows())
    add_sheet(wb, "RESIDUAL_DIAGNOSTICS", residual_diagnostics_rows())
    add_sheet(wb, "OUTLIER_DETECTION", outlier_detection_rows())
    add_sheet(wb, "MODEL_METADATA", model_metadata_rows())
    add_sheet(wb, "DASHBOARD_SAMPLE", [
        {"METRIC": "Additional sheets created", "VALUE": 18},
        {"METRIC": "Calendar range", "VALUE": "2024-2028"},
        {"METRIC": "Seasonal drivers covered", "VALUE": "Ramadan, Eid, heat, tourism, working days, fiscal Q4, e-commerce"},
        {"METRIC": "Generated at", "VALUE": datetime.now(UTC).replace(microsecond=0).isoformat()},
    ])
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_workbook())
