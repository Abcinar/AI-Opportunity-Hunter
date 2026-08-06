"""
AI Opportunity Hunter - LLM Rationale Generator
Groq (Llama 3) ile Türkçe/İngilizce gerekçe üretir.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_rationale(
    title: str,
    source: str,
    points: int = 0,
    comments: int = 0,
    score_breakdown: Optional[dict] = None,
    language: str = "tr"
) -> str:
    """
    Fırsat için kısa gerekçe üretir.
    language: "tr" veya "en"
    """

    lang_instruction = (
        "Türkçe, net ve profesyonel bir dille yaz. 2-3 cümle olsun."
        if language == "tr"
        else "Write in clear, professional English. 2-3 sentences."
    )

    breakdown_text = ""
    if score_breakdown:
        breakdown_text = f"""
Skor detayları:
- Momentum: {score_breakdown.get('momentum', '-')}
- Pain Clarity: {score_breakdown.get('pain_clarity', '-')}
- Competition Gap: {score_breakdown.get('competition_gap', '-')}
- Solo Feasibility: {score_breakdown.get('solo_feasibility', '-')}
- Monetization: {score_breakdown.get('monetization_clarity', '-')}
"""

    prompt = f"""
Sen bir startup fırsat analistiisin. Aşağıdaki sinyale bakarak solo founder için kısa bir gerekçe yaz.

Başlık: {title}
Kaynak: {source}
Puan/Skor: {points}
Yorum: {comments}
{breakdown_text}

Kurallar:
- {lang_instruction}
- Neden fırsat olabileceğini söyle
- Solo founder için yapılabilirlikten bahset
- Abartma, gerçekçi ol
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen deneyimli bir startup analistiisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=180,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Gerekçe üretilemedi: {e}"


if __name__ == "__main__":
    # Test
    text = generate_rationale(
        title="AI tool that automatically replies to customer support emails for small e-commerce stores",
        source="hacker_news",
        points=280,
        comments=65,
        language="tr"
    )
    print(text)
