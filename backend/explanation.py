"""
explanation.py
---------------
Rule-based, MULTILINGUAL medical explanation generation module.

This intentionally avoids calling any external LLM API (no API keys required),
making the system fully self-contained and runnable offline. It mirrors the
"Medical Explanation Generation Module" described in the SDP report, but
implemented as a deterministic, transparent rule engine instead of a
fine-tuned LLM -- which is more reliable, free to run, and easier to defend
in a viva / demo setting.

Supported languages: "en" (English), "hi" (Hindi), "te" (Telugu).
Falls back to English if an unknown language code is passed.
"""

from typing import Optional

SUPPORTED_LANGUAGES = ("en", "hi", "te")
DEFAULT_LANGUAGE = "en"

# ---------------------------------------------------------------------------
# Base explanation text per class, per language
# ---------------------------------------------------------------------------
BASE_EXPLANATIONS = {
    "en": {
        "No_DR": (
            "No visible signs of diabetic retinopathy were detected in the retinal image. "
            "The retina appears healthy with no abnormal blood vessel changes, hemorrhages, "
            "or exudates observed."
        ),
        "Mild": (
            "Early signs of diabetic retinopathy detected. Small areas of balloon-like "
            "swelling (microaneurysms) may be present in the retinal blood vessels. "
            "This is the earliest stage of the disease."
        ),
        "Moderate": (
            "Moderate diabetic retinopathy detected. Blood vessels that nourish the retina "
            "are becoming more damaged, blocking blood flow to parts of the retina, which "
            "may start to affect vision over time."
        ),
        "Severe": (
            "Severe diabetic retinopathy detected. A larger number of blood vessels are "
            "blocked, depriving several areas of the retina of their blood supply. These "
            "areas may begin signaling the body to grow new, fragile blood vessels."
        ),
        "Proliferative_DR": (
            "Advanced (proliferative) diabetic retinopathy detected. Abnormal new blood "
            "vessels are growing on the surface of the retina, which can leak into the "
            "vitreous and cause severe vision loss or retinal detachment if untreated."
        ),
    },
    "hi": {
        "No_DR": (
            "रेटिना की छवि में डायबिटिक रेटिनोपैथी के कोई दिखने वाले लक्षण नहीं मिले। "
            "रेटिना स्वस्थ दिखाई दे रहा है, इसमें कोई असामान्य रक्त वाहिका परिवर्तन, "
            "रक्तस्राव, या स्राव नहीं देखा गया।"
        ),
        "Mild": (
            "डायबिटिक रेटिनोपैथी के शुरुआती लक्षण पाए गए हैं। रेटिना की रक्त वाहिकाओं में "
            "गुब्बारे जैसी छोटी सूजन (माइक्रोएन्यूरिज्म) हो सकती है। यह बीमारी की सबसे "
            "प्रारंभिक अवस्था है।"
        ),
        "Moderate": (
            "मध्यम डायबिटिक रेटिनोपैथी पाई गई है। रेटिना को पोषण देने वाली रक्त वाहिकाएं "
            "अधिक क्षतिग्रस्त हो रही हैं, जिससे रेटिना के कुछ हिस्सों में रक्त प्रवाह बाधित "
            "हो रहा है, जो समय के साथ दृष्टि को प्रभावित कर सकता है।"
        ),
        "Severe": (
            "गंभीर डायबिटिक रेटिनोपैथी पाई गई है। अधिक संख्या में रक्त वाहिकाएं अवरुद्ध हो "
            "गई हैं, जिससे रेटिना के कई हिस्सों को रक्त की आपूर्ति नहीं मिल पा रही। ये "
            "हिस्से नई, कमज़ोर रक्त वाहिकाओं को बढ़ाने का संकेत देना शुरू कर सकते हैं।"
        ),
        "Proliferative_DR": (
            "उन्नत (प्रोलिफेरेटिव) डायबिटिक रेटिनोपैथी पाई गई है। रेटिना की सतह पर असामान्य "
            "नई रक्त वाहिकाएं बढ़ रही हैं, जो विट्रियस में रिसाव कर सकती हैं और उपचार न "
            "होने पर गंभीर दृष्टि हानि या रेटिनल डिटैचमेंट का कारण बन सकती हैं।"
        ),
    },
    "te": {
        "No_DR": (
            "రెటినల్ చిత్రంలో డయాబెటిక్ రెటినోపతి యొక్క కనిపించే సంకేతాలు ఏవీ "
            "కనుగొనబడలేదు. రెటినా ఆరోగ్యంగా ఉంది, అసాధారణ రక్తనాళ మార్పులు, రక్తస్రావం, "
            "లేదా ఎక్సుడేట్స్ గమనించబడలేదు."
        ),
        "Mild": (
            "డయాబెటిక్ రెటినోపతి యొక్క ప్రారంభ సంకేతాలు కనుగొనబడ్డాయి. రెటినల్ రక్తనాళాలలో "
            "చిన్న బుడగ వంటి వాపు (మైక్రోఅన్యూరిజమ్స్) ఉండవచ్చు. ఇది వ్యాధి యొక్క "
            "ప్రారంభ దశ."
        ),
        "Moderate": (
            "మోడరేట్ డయాబెటిక్ రెటినోపతి కనుగొనబడింది. రెటినాకు పోషణ ఇచ్చే రక్తనాళాలు "
            "మరింత దెబ్బతింటున్నాయి, రెటినాలోని కొన్ని భాగాలకు రక్త ప్రసరణను అడ్డుకుంటున్నాయి, "
            "ఇది కాలక్రమేణా దృష్టిని ప్రభావితం చేయవచ్చు."
        ),
        "Severe": (
            "సివియర్ డయాబెటిక్ రెటినోపతి కనుగొనబడింది. ఎక్కువ సంఖ్యలో రక్తనాళాలు "
            "నిరోధించబడ్డాయి, రెటినాలోని అనేక ప్రాంతాలకు రక్త సరఫరా లేకుండా చేస్తున్నాయి. "
            "ఈ ప్రాంతాలు కొత్త, బలహీనమైన రక్తనాళాలను పెంచమని సంకేతాలు ఇవ్వడం "
            "మొదలుపెట్టవచ్చు."
        ),
        "Proliferative_DR": (
            "అడ్వాన్స్‌డ్ (ప్రోలిఫరేటివ్) డయాబెటిక్ రెటినోపతి కనుగొనబడింది. రెటినా ఉపరితలంపై "
            "అసాధారణ కొత్త రక్తనాళాలు పెరుగుతున్నాయి, ఇవి విట్రియస్‌లోకి లీక్ అయి, చికిత్స "
            "చేయకపోతే తీవ్రమైన దృష్టి నష్టం లేదా రెటినల్ డిటాచ్‌మెంట్‌కు కారణమవుతాయి."
        ),
    },
}

# ---------------------------------------------------------------------------
# Recommended action per class, per language
# ---------------------------------------------------------------------------
RECOMMENDATIONS = {
    "en": {
        "No_DR": "Continue routine annual eye examinations and maintain good blood sugar control.",
        "Mild": "Regular monitoring is recommended. Schedule a follow-up eye exam within 9-12 months.",
        "Moderate": "Schedule an ophthalmology consultation within the next few weeks for a detailed evaluation.",
        "Severe": "Prompt medical evaluation is advised. Consult an ophthalmologist within days, not weeks.",
        "Proliferative_DR": "Immediate specialist treatment is strongly recommended. Seek an ophthalmologist urgently to prevent permanent vision loss.",
    },
    "hi": {
        "No_DR": "नियमित वार्षिक नेत्र जांच जारी रखें और रक्त शर्करा को नियंत्रण में रखें।",
        "Mild": "नियमित निगरानी की सलाह दी जाती है। 9-12 महीनों के भीतर अनुवर्ती नेत्र जांच निर्धारित करें।",
        "Moderate": "विस्तृत मूल्यांकन के लिए अगले कुछ हफ्तों में नेत्र रोग विशेषज्ञ से सलाह लें।",
        "Severe": "तत्काल चिकित्सा मूल्यांकन की सलाह दी जाती है। हफ्तों नहीं, बल्कि दिनों के भीतर नेत्र रोग विशेषज्ञ से सलाह लें।",
        "Proliferative_DR": "तत्काल विशेषज्ञ उपचार की दृढ़ता से सलाह दी जाती है। स्थायी दृष्टि हानि को रोकने के लिए तुरंत नेत्र रोग विशेषज्ञ से मिलें।",
    },
    "te": {
        "No_DR": "సాధారణ వార్షిక నేత్ర పరీక్షలను కొనసాగించండి మరియు రక్తంలో చక్కెరను నియంత్రణలో ఉంచండి.",
        "Mild": "క్రమం తప్పకుండా పర్యవేక్షణ సిఫార్సు చేయబడింది. 9-12 నెలల్లో తదుపరి నేత్ర పరీక్షను షెడ్యూల్ చేయండి.",
        "Moderate": "వివరణాత్మక మూల్యాంకనం కోసం రాబోయే కొన్ని వారాల్లో నేత్ర వైద్య సంప్రదింపు షెడ్యూల్ చేయండి.",
        "Severe": "తక్షణ వైద్య మూల్యాంకనం సిఫార్సు చేయబడింది. వారాల్లో కాదు, రోజుల్లోనే నేత్ర వైద్యుడిని సంప్రదించండి.",
        "Proliferative_DR": "తక్షణ నిపుణుల చికిత్స గట్టిగా సిఫార్సు చేయబడింది. శాశ్వత దృష్టి నష్టాన్ని నివారించడానికి వెంటనే నేత్ర వైద్యుడిని సంప్రదించండి.",
    },
}

# ---------------------------------------------------------------------------
# Safety note per class, per language
# ---------------------------------------------------------------------------
SAFETY_NOTES = {
    "en": {
        "No_DR": "No immediate safety concerns identified.",
        "Mild": "Keep blood sugar, blood pressure, and cholesterol well controlled.",
        "Moderate": "Watch for blurred vision, floaters, or dark spots and report them promptly.",
        "Severe": "Seek urgent care if you notice sudden vision changes, flashes of light, or a curtain-like shadow in your vision.",
        "Proliferative_DR": "Treat any sudden vision loss, severe floaters, or eye pain as a medical emergency.",
    },
    "hi": {
        "No_DR": "कोई तत्काल सुरक्षा चिंता नहीं पाई गई।",
        "Mild": "रक्त शर्करा, रक्तचाप और कोलेस्ट्रॉल को अच्छी तरह नियंत्रित रखें।",
        "Moderate": "धुंधली दृष्टि, फ्लोटर्स या काले धब्बों पर ध्यान दें और तुरंत सूचित करें।",
        "Severe": "अचानक दृष्टि परिवर्तन, प्रकाश की चमक, या दृष्टि में पर्दे जैसी छाया दिखने पर तुरंत चिकित्सा सहायता लें।",
        "Proliferative_DR": "अचानक दृष्टि हानि, गंभीर फ्लोटर्स, या आंखों में दर्द को चिकित्सा आपातकाल के रूप में मानें।",
    },
    "te": {
        "No_DR": "తక్షణ భద్రతా సమస్యలు ఏవీ గుర్తించబడలేదు.",
        "Mild": "రక్తంలో చక్కెర, రక్తపోటు మరియు కొలెస్ట్రాల్‌ను బాగా నియంత్రణలో ఉంచండి.",
        "Moderate": "మసక దృష్టి, ఫ్లోటర్స్ లేదా నలుపు మరకల కోసం గమనించండి మరియు వెంటనే తెలియజేయండి.",
        "Severe": "ఆకస్మిక దృష్టి మార్పులు, కాంతి మెరుపులు, లేదా దృష్టిలో తెర వంటి నీడ గమనించినట్లయితే వెంటనే వైద్య సహాయం పొందండి.",
        "Proliferative_DR": "ఆకస్మిక దృష్టి నష్టం, తీవ్రమైన ఫ్లోటర్స్, లేదా కంటి నొప్పిని వైద్య అత్యవసర పరిస్థితిగా పరిగణించండి.",
    },
}

# ---------------------------------------------------------------------------
# Templated add-on notes (confidence / history / symptoms), per language
# ---------------------------------------------------------------------------
_CONFIDENCE_TEMPLATE = {
    "en": " This assessment was made with a model confidence of {confidence:.1f}%.",
    "hi": " यह आकलन {confidence:.1f}% मॉडल विश्वास के साथ किया गया है।",
    "te": " ఈ మూల్యాంకనం {confidence:.1f}% మోడల్ విశ్వాసంతో చేయబడింది.",
}

_HISTORY_TEMPLATE = {
    "en": " Given the diabetic history of {history} year(s), regular retinal screening is especially important.",
    "hi": " {history} वर्षों के डायबिटीज़ इतिहास को देखते हुए, नियमित रेटिना जांच विशेष रूप से महत्वपूर्ण है।",
    "te": " {history} సంవత్సరాల డయాబెటిక్ చరిత్రను పరిగణనలోకి తీసుకుంటే, క్రమం తప్పకుండా రెటినల్ స్క్రీనింగ్ చేయడం చాలా ముఖ్యం.",
}

_SYMPTOM_TEMPLATE = {
    "en": " The reported symptoms ('{symptoms}') should be discussed with the treating ophthalmologist, as they may correlate with retinal changes.",
    "hi": " बताए गए लक्षणों ('{symptoms}') पर उपचार करने वाले नेत्र रोग विशेषज्ञ से चर्चा करनी चाहिए, क्योंकि ये रेटिना में बदलाव से संबंधित हो सकते हैं।",
    "te": " నివేదించిన లక్షణాలు ('{symptoms}') చికిత్స చేస్తున్న నేత్ర వైద్యుడితో చర్చించాలి, ఇవి రెటినల్ మార్పులతో సంబంధం కలిగి ఉండవచ్చు.",
}

_FALLBACK_EXPLANATION = {
    "en": "Unable to generate explanation for this class.",
    "hi": "इस वर्ग के लिए स्पष्टीकरण उत्पन्न करने में असमर्थ।",
    "te": "ఈ తరగతి కోసం వివరణను రూపొందించడం సాధ్యం కాలేదు.",
}

_FALLBACK_RECOMMENDATION = {
    "en": "Consult an ophthalmologist for further evaluation.",
    "hi": "आगे के मूल्यांकन के लिए नेत्र रोग विशेषज्ञ से सलाह लें।",
    "te": "మరింత మూల్యాంకనం కోసం నేత్ర వైద్యుడిని సంప్రదించండి.",
}

_FALLBACK_SAFETY_NOTE = {
    "en": "Consult a medical professional for personalized advice.",
    "hi": "व्यक्तिगत सलाह के लिए किसी चिकित्सा विशेषज्ञ से सलाह लें।",
    "te": "వ్యక్తిగత సలహా కోసం వైద్య నిపుణుడిని సంప్రదించండి.",
}


def _normalize_language(language: Optional[str]) -> str:
    if language and language in SUPPORTED_LANGUAGES:
        return language
    return DEFAULT_LANGUAGE


def _symptom_note(symptoms: Optional[str], language: str) -> str:
    if not symptoms:
        return ""
    symptoms_clean = symptoms.strip()
    if not symptoms_clean:
        return ""
    template = _SYMPTOM_TEMPLATE.get(language, _SYMPTOM_TEMPLATE[DEFAULT_LANGUAGE])
    return template.format(symptoms=symptoms_clean)


def _history_note(diabetic_history: Optional[str], language: str) -> str:
    if not diabetic_history:
        return ""
    history_clean = diabetic_history.strip().lower()
    if history_clean in ("", "no", "none", "n/a"):
        return ""
    template = _HISTORY_TEMPLATE.get(language, _HISTORY_TEMPLATE[DEFAULT_LANGUAGE])
    return template.format(history=diabetic_history)


def generate_explanation(
    prediction: str,
    confidence: float,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    diabetic_history: Optional[str] = None,
    symptoms: Optional[str] = None,
    language: Optional[str] = "en",
) -> str:
    """
    Builds a patient-friendly, rule-based medical explanation string from the
    CNN prediction plus optional patient context, in the requested language.
    """
    lang = _normalize_language(language)

    base = BASE_EXPLANATIONS.get(lang, BASE_EXPLANATIONS[DEFAULT_LANGUAGE]).get(
        prediction, _FALLBACK_EXPLANATION[lang]
    )
    symptom_note = _symptom_note(symptoms, lang)
    history_note = _history_note(diabetic_history, lang)

    confidence_template = _CONFIDENCE_TEMPLATE.get(lang, _CONFIDENCE_TEMPLATE[DEFAULT_LANGUAGE])
    confidence_note = confidence_template.format(confidence=confidence)

    explanation = f"{base}{confidence_note}{history_note}{symptom_note}"
    return explanation


def generate_recommendation(prediction: str, language: Optional[str] = "en") -> str:
    lang = _normalize_language(language)
    return RECOMMENDATIONS.get(lang, RECOMMENDATIONS[DEFAULT_LANGUAGE]).get(
        prediction, _FALLBACK_RECOMMENDATION[lang]
    )


def generate_safety_note(prediction: str, language: Optional[str] = "en") -> str:
    lang = _normalize_language(language)
    return SAFETY_NOTES.get(lang, SAFETY_NOTES[DEFAULT_LANGUAGE]).get(
        prediction, _FALLBACK_SAFETY_NOTE[lang]
    )
