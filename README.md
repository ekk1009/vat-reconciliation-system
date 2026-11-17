# 🏛️ VAT Reconciliation & Filing System
> **국세청 전자세금계산서 vs 회계장부(ERP) 교차 대사 분석 & 부가가치세 표준 신고서 자동작성 시스템**

![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)
![Frontend: Vanilla JS](https://img.shields.io/badge/Frontend-Vanilla%20HTML%2FCSS%2FJS-black.svg)
![Design: Nike Design System](https://img.shields.io/badge/Design-Nike%20Design%20System-111111.svg)
![Status: Production Ready](https://img.shields.io/badge/Status-Completed-007d48.svg)

---

## 📌 프로젝트 소개 (Overview)

대한민국 부가가치세법 및 국세청 실무 단수처리 기준을 철저히 준수하여 구축된 **정밀 세무 대사(Reconciliation) 및 부가세 신고서 자동 생성 시스템**입니다.

서버 설치나 복잡한 환경 설정 없이 **순수 프론트엔드(HTML/CSS/JS)**만으로 브라우저에서 100% 로컬 동작하여 금융/세무 데이터의 외부 유출이 전혀 없으며, [나이키 커머스 디자인 시스템(Nike Design System)](./DESIGN-nike.md)을 적용하여 직관적이고 완성도 높은 인터페이스를 제공합니다.

---

## ⚡ 핵심 기능 (Key Features)

### 1. 🔍 듀얼 엑셀 드래그 앤 드롭 대사 (Dual Drag & Drop)
- **Source 01**: 국세청 홈택스에서 다운로드한 매출/매입 세금계산서 엑셀
- **Source 02**: 사내 회계 프로그램(더존, 위하고, 세무사랑, 이카운트 등)의 분개장 전표 엑셀
- 두 엑셀 파일을 브라우저 화면으로 끌어다 놓기만 하면 즉시 자동 매핑 및 교차 대사 수행.

### 2. ⚠️ 세무 오류 및 위험 자동 감지
- **🟢 정상 일치 (Matched)**: 공급가액 및 부가세 100% 일치
- **🔴 금액/세액 불일치 (Amount Diff)**: 타이핑 오류 및 공급가액 불일치 감지
- **🟠 회계전표 누락 (Hometax Only)**: 홈택스에는 발행되었으나 장부 미반영 (세금 과다납부 위험)
- **🟣 국세청 미발행 (ERP Only)**: 장부에는 매입 처리되었으나 세금계산서 미발행 (매입세액 부인 위험)
- **🟡 매입세액 불공제 (Non-Deductible)**: 비영업용 소형승용차, 접대비 등 불공제 전표 자동 분리

### 3. 📑 부가가치세 법정 표준 신고서 자동 작성
- 대사를 통과한 적법 증빙 데이터를 국세청 법정 서식(부가가치세법 시행규칙 [별지 제21호서식])으로 자동 집계:
  - **과세표준 및 매출세액 (① 세금계산서 발급분, ⑤ 영세율, ⑦ 총매출세액)**
  - **매입세액 (⑩ 일반매입, ⑪ 고정자산, ⑯ 불공제 차감, ⑰ 공제 매입세액)**
  - **최종 납부(환급)할 세액 자동 산출**
- **엑셀 다운로드** 및 **인쇄/PDF 저장** 지원.

### 4. 🧮 정밀 부가세 연산 코어
- 부동소수점 오차 없는 연산 로직 (`Math.round`, 절대값 기반 단수처리).
- **국세청 표준 1원 단수차이 보정**: 복수 품목 합산 시 총액 기준 10%와의 단수 오차를 마지막 과세 품목에 자동 보정.
- 공급가액 $\rightarrow$ 공급대가(정방향) 및 공급대가 $\rightarrow$ 공급가액(역산) 지원.

---

## 🎨 디자인 시스템 (Nike Design System)

- **Palette**: Deep Nike Ink (`#111111`), Pure Canvas White (`#ffffff`), Soft Cloud Gray (`#f5f5f5`), Hairline (`#cacacb`).
- **Typography**: 거대한 영문 대문자 디스플레이 헤드라인 (`Bebas Neue` 64px)과 정돈된 한글 UI 텍스트 (`Pretendard` / `Inter`).
- **Geometry**: Zero Shadow 평면 구조 및 모든 인터랙티브 요소의 **Pill(타원, `rounded.full`)** 형태 통일.
- **Micro-interaction**: 클릭 시 물리적 `scale(0.96)` 탭 피드백.

---

## 🚀 빠른 시작 (Quick Start)

### 1. 로컬 파일 직접 실행 (서버 불필요)
`index.html` 파일을 더블클릭하거나 웹 브라우저로 열기만 하면 즉시 실행됩니다.

### 2. 로컬 웹 서버 실행 (선택)
```bash
python -m http.server 8055
```
웹 브라우저에서 `http://localhost:8055` 접속.

---

## 📂 파일 구조 (Repository Structure)

```
├── index.html            # 메인 애플리케이션 (나이키 디자인 시스템 적용 Standalone Web App)
├── vat_core.py           # Python Decimal 기반 정밀 연산 백엔드 코어
├── app.py                # 로컬 백엔드 서버 (선택 사항)
├── test_vat.py           # 홈택스 역산 및 단수처리 단위 테스트 스위트
├── run.bat               # Windows 원클릭 실행 배치 파일
├── DESIGN-nike.md        # 나이키 디자인 시스템 명세서
├── VAT_CALCULATOR_PLAN.md# 세무 대사 및 신고서 아키텍처 설계서
└── README.md             # 프로젝트 안내 문서
```

---

## 📄 라이선스 (License)

This project is licensed under the MIT License.
