"""
정밀 부가가치세(VAT) 코어 연산 엔진 검증 테스트
- 홈택스 역산 테스트
- 원 미만 단수처리 테스트
- 1원 단수차이 보정 알고리즘 테스트
- 마이너스 금액(환불) 부호 보존 테스트
- 봉사료 분리 테스트
"""

from decimal import Decimal
from vat_core import calculate_single, calculate_cart, RoundingPolicy, TaxType

def test_single_forward():
    # 1. 일반과세 정방향 100,000원 -> 부가세 10,000원, 공급대가 110,000원
    res = calculate_single(Decimal("100000"), is_gross=False, rounding_policy=RoundingPolicy.TRUNCATE)
    assert res["supply_value"] == 100000
    assert res["tax_value"] == 10000
    assert res["total_amount"] == 110000
    print("✅ 정방향 기본 계산 테스트 통과")

def test_single_reverse_rounding():
    # 2. 홈택스 역산: 10,000원 공급대가
    # 10000 / 1.1 = 9090.909...
    # 원미만 절사 시: 공급가액 9,090원, 부가세 910원, 합계 10,000원 (1원 오차 없음)
    res = calculate_single(Decimal("10000"), is_gross=True, rounding_policy=RoundingPolicy.TRUNCATE)
    assert res["supply_value"] == 9090
    assert res["tax_value"] == 910
    assert res["total_amount"] == 10000
    assert res["supply_value"] + res["tax_value"] == 10000
    print("✅ 역산 단수처리 및 합계 일치 테스트 통과 (10,000원 -> 9,090원 + 910원)")

def test_negative_refund():
    # 3. 마이너스 환불 거래 (-12,345원 공급대가)
    # 절사 시 음수 방향 왜곡 없이 절대값 기준 절사 확인
    res = calculate_single(Decimal("-12345"), is_gross=True, rounding_policy=RoundingPolicy.TRUNCATE)
    assert res["supply_value"] + res["tax_value"] == -12345
    assert res["total_amount"] == -12345
    print("✅ 마이너스 환불/수정세금계산서 연산 테스트 통과")

def test_service_charge():
    # 4. 음식점 봉사료 분리: 총 결제 110,000원 중 봉사료 10,000원
    # 순수 공급대가 100,000원 -> 공급가액 90,909원, 부가세 9,091원, 봉사료 10,000원 -> 총 110,000원
    res = calculate_single(Decimal("110000"), is_gross=True, service_charge=Decimal("10000"), rounding_policy=RoundingPolicy.TRUNCATE)
    assert res["service_charge"] == 10000
    assert res["supply_value"] == 90909
    assert res["tax_value"] == 9091
    assert res["total_amount"] == 110000
    print("✅ 봉사료 분리 기재 테스트 통과")

def test_cart_penny_difference():
    # 5. 1원 단수차이 보정 테스트
    # 품목 A: 3,333원 x 10% = 333.3 -> 333원
    # 품목 B: 3,333원 x 10% = 333.3 -> 333원
    # 품목 C: 3,334원 x 10% = 333.4 -> 333원
    # 개별 합산 세액: 333 + 333 + 333 = 999원
    # 총 공급가액: 10,000원 -> 표준 총세액: 1,000원 (1원 차이 발생!)
    items = [
        {"name": "품목 A", "unit_price": 3333, "quantity": 1, "tax_type": "TAXABLE"},
        {"name": "품목 B", "unit_price": 3333, "quantity": 1, "tax_type": "TAXABLE"},
        {"name": "품목 C", "unit_price": 3334, "quantity": 1, "tax_type": "TAXABLE"}
    ]
    # 보정 미적용 시
    res_no_adj = calculate_cart(items, rounding_policy=RoundingPolicy.TRUNCATE, adjust_penny=False)
    assert res_no_adj["summary"]["sum_item_tax"] == 999
    assert res_no_adj["summary"]["standard_total_tax"] == 1000
    assert res_no_adj["summary"]["penny_difference"] == 1

    # 보정 적용 시 (국세청 표준)
    res_adj = calculate_cart(items, rounding_policy=RoundingPolicy.TRUNCATE, adjust_penny=True)
    assert res_adj["summary"]["final_tax"] == 1000
    assert res_adj["items"][-1]["adjusted_diff"] == 1
    assert res_adj["items"][-1]["tax_value"] == 334  # 마지막 품목에 1원 보정
    print("✅ 1원 단수차이 국세청 표준 보정 알고리즘 테스트 통과")

if __name__ == "__main__":
    test_single_forward()
    test_single_reverse_rounding()
    test_negative_refund()
    test_service_charge()
    test_cart_penny_difference()
    print("\n🎉 모든 정밀 부가세 코어 연산 테스트를 100% 성공적으로 통과했습니다!")
