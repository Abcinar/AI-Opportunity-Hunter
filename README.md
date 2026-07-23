# AI Opportunity Hunter

Solo founder'lar ve indie hacker'lar için **günlük fırsat karar motoru**.

Her sabah 5–7 yüksek potansiyelli startup fırsatını **şeffaf Opportunity Score** ile sunar ve seçilen fırsatları **Opportunity Monitor** ile takip eder.

## Özellikler

- **Hacker News + Reddit** sinyal toplama
- **Şeffaf Opportunity Score** (0-100)
  - Momentum (25%)
  - Pain Clarity (20%)
  - Competition Gap (20%)
  - Solo Feasibility (20%)
  - Monetization Clarity (15%)
- Çoklu dil desteği (TR / EN) hazır altyapı
- JSON çıktı

## Kurulum

```bash
git clone https://github.com/KULLANICI_ADIN/AI-Opportunity-Hunter.git
cd AI-Opportunity-Hunter

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py