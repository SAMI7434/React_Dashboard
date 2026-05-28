from datetime import datetime
from decimal import Decimal, InvalidOperation


DATE_FORMATS = [
    '%Y-%m-%d',
    '%m/%d/%Y',
    '%m/%d/%y',
    '%d/%m/%Y',
    '%d.%m.%Y',
    '%Y/%m/%d',
    '%Y%m%d',
    '%d-%b-%Y',
    '%b %d %Y',
]


def clean_string(value):
    if value is None:
        return ''
    return str(value).strip()


def parse_decimal(value):
    if value is None:
        return None
    cleaned = str(value).replace(',', '').strip()
    if cleaned == '':
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_date(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    if cleaned == '':
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def normalize_usage_kwh(usage_value, usage_unit):
    if usage_value is None:
        return None
    if usage_unit is None:
        return None
    unit = usage_unit.strip().lower()
    if unit in ['kwh', 'kw-h', 'kwhr', 'kilowatt-hour']:
        return usage_value
    if unit in ['mwh', 'mw-h', 'megawatt-hour']:
        return usage_value * Decimal('1000')
    if unit in ['wh', 'watt-hour']:
        return usage_value / Decimal('1000')
    return None


ENERGY_UNIT_FACTORS_TO_MWH = {
    'wh': Decimal('0.000001'),
    'watt-hour': Decimal('0.000001'),
    'kwh': Decimal('0.001'),
    'kw-h': Decimal('0.001'),
    'kwhr': Decimal('0.001'),
    'kilowatt-hour': Decimal('0.001'),
    'mwh': Decimal('1'),
    'mw-h': Decimal('1'),
    'megawatt-hour': Decimal('1'),
    'gwh': Decimal('1000'),
    'gw-h': Decimal('1000'),
    'gigawatt-hour': Decimal('1000'),
    'btu': Decimal('0.000000293071'),
}

FINANCIAL_UNIT_FACTORS_TO_THOUSAND = {
    'dollars': Decimal('0.001'),
    'usd': Decimal('0.001'),
    '$': Decimal('0.001'),
    'thousand dollars': Decimal('1'),
    'thousand usd': Decimal('1'),
    'k dollars': Decimal('1'),
    'k usd': Decimal('1'),
    'million dollars': Decimal('1000'),
    'million usd': Decimal('1000'),
}


def normalize_energy_to_mwh(value, unit):
    if value is None:
        return None, None, 'missing value'
    if unit is None or str(unit).strip() == '':
        return None, None, 'missing unit'
    cleaned_unit = str(unit).strip().lower()
    factor = ENERGY_UNIT_FACTORS_TO_MWH.get(cleaned_unit)
    if factor is None:
        return None, None, 'unknown unit'
    normalized = value * factor
    formula = f"{cleaned_unit} * {factor}"
    return normalized, 'MWh', formula


def normalize_cost_to_thousand(value, unit):
    if value is None:
        return None, None, 'missing value'
    if unit is None or str(unit).strip() == '':
        return None, None, 'missing unit'
    cleaned_unit = str(unit).strip().lower()
    factor = FINANCIAL_UNIT_FACTORS_TO_THOUSAND.get(cleaned_unit)
    if factor is None:
        return None, None, 'unknown unit'
    normalized = value * factor
    formula = f"{cleaned_unit} * {factor}"
    return normalized, 'Thousand Dollars', formula
