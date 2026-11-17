"""
정밀 부가가치세(VAT) 코어 연산 엔진
- Python Decimal 기반 무오차 연산
- 대한민국 부가가치세법 및 국세청 실무 단수처리 규정 준수
- 5대 실무 예외사항(1원 단수차이, 마이너스 환불, 봉사료 분리, 소수점 단가, 매입 불공제) 완벽 지원
"""

from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP, ROUND_DOWN
from enum import Enum
from typing import List, Dict, Any, Optional

class RoundingPolicy(str, Enum):
    TRUNCATE = "TRUNCATE"      # 원 미만 절사 (국세청 기본, 세법 제47조)
    ROUND_HALF_UP = "HALF_UP"  # 사사오입 (일반 반올림)
    CEILING = "CEILING"        # 올림

class TaxType(str, Enum):
    TAXABLE = "TAXABLE"        # 일반과세 (10%)
    ZERO = "ZERO"              # 영세율 (0%)
    EXEMPT = "EXEMPT"          # 면세 (비과세)
    SIMPLIFIED = "SIMPLIFIED"  # 간이과세 (업종별 부가가치율 적용)

def apply_rounding(val: Decimal, policy: RoundingPolicy) -> Decimal:
    """
    부호에 따른 왜곡을 방지하기 위해 절대값 기준으로 단수 처리 후 원래 부호를 복원합니다.
    (마이너스 세금계산서/환불 시 필수)
    """
    sign = -1 if val < 0 else 1
    abs_val = abs(val)
    
    if policy == RoundingPolicy.TRUNCATE:
        # 원 미만 버림 (0 단위 정수로 절사)
        rounded = abs_val.quantize(Decimal("1"), rounding=ROUND_DOWN)
    elif policy == RoundingPolicy.ROUND_HALF_UP:
        # 4사 5입 반올림
        rounded = abs_val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    elif policy == RoundingPolicy.CEILING:
        # 올림
        rounded = abs_val.quantize(Decimal("1"), rounding=ROUND_CEILING)
    else:
        rounded = abs_val.quantize(Decimal("1"), rounding=ROUND_DOWN)
        
    return rounded * sign


def calculate_single(
    amount: Decimal,
    is_gross: bool = False,
    tax_type: TaxType = TaxType.TAXABLE,
    simplified_rate: Decimal = Decimal("0.30"),
    service_charge: Decimal = Decimal("0"),
    rounding_policy: RoundingPolicy = RoundingPolicy.TRUNCATE,
    is_non_deductible: bool = False
) -> Dict[str, Any]:
    """
    단일 품목 또는 단일 거래에 대한 정밀 부가세 계산
    
    :param amount: 입력 금액 (공급가액 또는 공급대가)
    :param is_gross: True면 공급대가(합계금액) 기준 역산, False면 공급가액 기준 정방향
    :param tax_type: 과세 유형 (일반, 영세, 면세, 간이)
    :param simplified_rate: 간이과세 시 부가가치율 (기본 30%)
    :param service_charge: 봉사료 (비과세 항목으로 공급대가 역산 시 차감)
    :param rounding_policy: 단수처리 정책 (원미만 절사 / 반올림 / 올림)
    :param is_non_deductible: 매입세액 불공제 여부
    """
    amount = Decimal(str(amount))
    service_charge = Decimal(str(service_charge))
    simplified_rate = Decimal(str(simplified_rate))
    
    rate = Decimal("0.10")
    if tax_type == TaxType.ZERO or tax_type == TaxType.EXEMPT:
        rate = Decimal("0")
    elif tax_type == TaxType.SIMPLIFIED:
        # 간이과세: 부가가치율 × 10%
        rate = simplified_rate * Decimal("0.10")

    if is_gross:
        # ==========================================
        # [역방향 계산: 공급대가(합계) -> 공급가액, 세액]
        # ==========================================
        # 봉사료 제외 순수 과세 대상 공급대가 산출
        net_gross = amount - service_charge
        
        if tax_type == TaxType.EXEMPT or tax_type == TaxType.ZERO or rate == Decimal("0"):
            supply_value = net_gross
            tax_value = Decimal("0")
        elif tax_type == TaxType.SIMPLIFIED:
            # 간이과세 공급대가 역산: 공급대가 / (1 + rate)
            raw_supply = net_gross / (Decimal("1") + rate)
            supply_value = apply_rounding(raw_supply, rounding_policy)
            tax_value = net_gross - supply_value
        else:
            # 일반과세 10% 역산: 공급대가 / 1.1
            raw_supply = net_gross / Decimal("1.1")
            supply_value = apply_rounding(raw_supply, rounding_policy)
            # 1원 오차 방지 핵심: 공급대가 - 공급가액 = 세액
            tax_value = net_gross - supply_value
            
        total_amount = supply_value + tax_value + service_charge
    else:
        # ==========================================
        # [정방향 계산: 공급가액 -> 세액, 공급대가]
        # ==========================================
        supply_value = amount
        if tax_type == TaxType.EXEMPT or tax_type == TaxType.ZERO or rate == Decimal("0"):
            tax_value = Decimal("0")
        else:
            raw_tax = supply_value * rate
            tax_value = apply_rounding(raw_tax, rounding_policy)
            
        total_amount = supply_value + tax_value + service_charge

    # 매입세액 공제 / 불공제 처리
    deductible_tax = Decimal("0") if is_non_deductible else tax_value
    non_deductible_tax = tax_value if is_non_deductible else Decimal("0")
    
    return {
        "supply_value": int(supply_value),
        "tax_value": int(tax_value),
        "service_charge": int(service_charge),
        "total_amount": int(total_amount),
        "deductible_tax": int(deductible_tax),
        "non_deductible_tax": int(non_deductible_tax),
        "is_non_deductible": is_non_deductible,
        "tax_type": tax_type.value,
        "rounding_policy": rounding_policy.value,
        "mode": "GROSS_REVERSE" if is_gross else "NET_FORWARD"
    }


def calculate_cart(
    items: List[Dict[str, Any]],
    rounding_policy: RoundingPolicy = RoundingPolicy.TRUNCATE,
    adjust_penny: bool = True
) -> Dict[str, Any]:
    """
    복수 품목(장바구니/세금계산서) 정밀 계산 및 1원 단수차이 보정
    
    :param items: [{ name, unit_price, quantity, tax_type, ... }]
    :param rounding_policy: 단수처리 정책
    :param adjust_penny: 국세청 기준 1원 단수차이 보정 적용 여부
    """
    calculated_items = []
    total_taxable_supply = Decimal("0")
    total_exempt_supply = Decimal("0")
    total_zero_supply = Decimal("0")
    sum_item_tax = Decimal("0")
    
    # 1. 개별 품목 계산
    for idx, item in enumerate(items):
        name = item.get("name", f"품목 {idx+1}")
        unit_price = Decimal(str(item.get("unit_price", 0)))
        qty = Decimal(str(item.get("quantity", 1)))
        tax_type_str = item.get("tax_type", TaxType.TAXABLE.value)
        tax_type = TaxType(tax_type_str)
        
        # 중간 공급가액: 수량 x 단가
        item_supply = apply_rounding(unit_price * qty, rounding_policy)
        
        if tax_type == TaxType.TAXABLE:
            item_tax = apply_rounding(item_supply * Decimal("0.10"), rounding_policy)
            total_taxable_supply += item_supply
            sum_item_tax += item_tax
        elif tax_type == TaxType.ZERO:
            item_tax = Decimal("0")
            total_zero_supply += item_supply
        elif tax_type == TaxType.EXEMPT:
            item_tax = Decimal("0")
            total_exempt_supply += item_supply
        else:
            item_tax = Decimal("0")
            
        calculated_items.append({
            "id": idx + 1,
            "name": name,
            "unit_price": float(unit_price),
            "quantity": float(qty),
            "tax_type": tax_type.value,
            "supply_value": int(item_supply),
            "original_tax": int(item_tax),
            "tax_value": int(item_tax),
            "total_amount": int(item_supply + item_tax),
            "adjusted_diff": 0
        })

    # 2. 국세청 표준: 전체 과세공급가액 기준 총세액 산출
    standard_total_tax = apply_rounding(total_taxable_supply * Decimal("0.10"), rounding_policy)
    
    # 3. 단수 차이 (Penny difference)
    penny_difference = int(standard_total_tax - sum_item_tax)
    
    # 4. 차액 보정 (마지막 과세 품목에 보정액 반영)
    if adjust_penny and penny_difference != 0:
        # 과세 품목 중 마지막 품목 찾기
        target_idx = None
        for i in reversed(range(len(calculated_items))):
            if calculated_items[i]["tax_type"] == TaxType.TAXABLE.value:
                target_idx = i
                break
                
        if target_idx is not None:
            calculated_items[target_idx]["tax_value"] += penny_difference
            calculated_items[target_idx]["total_amount"] += penny_difference
            calculated_items[target_idx]["adjusted_diff"] = penny_difference

    final_tax_total = standard_total_tax if adjust_penny else sum_item_tax
    final_total_supply = total_taxable_supply + total_zero_supply + total_exempt_supply
    grand_total = final_total_supply + final_tax_total

    return {
        "items": calculated_items,
        "summary": {
            "taxable_supply": int(total_taxable_supply),
            "exempt_supply": int(total_exempt_supply),
            "zero_supply": int(total_zero_supply),
            "total_supply": int(final_total_supply),
            "sum_item_tax": int(sum_item_tax),
            "standard_total_tax": int(standard_total_tax),
            "penny_difference": penny_difference,
            "adjusted": adjust_penny,
            "final_tax": int(final_tax_total),
            "grand_total": int(grand_total)
        }
    }
