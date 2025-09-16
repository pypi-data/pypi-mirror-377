from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from faker import Faker
import uvicorn
from ztfeatureslib.tools.pii_detection.detect_pii import detect_pii
from ztfeatureslib.tools.pii_detection.schema.pii_prompt import PIIPromptLiteRequest, PIIPromptRequest
from ztfeatureslib.tools.pii_detection.detect_pii import get_anonymized_prompt

app = FastAPI(title="ZT Features API", description="API with custom endpoints for zt-features-lib.", version="0.1.0")
fake = Faker()

@app.get("/fake-data", tags=["zt-features-lib"])
def get_fake_data():
    return {"name": fake.name(), "address": fake.address(), "email": fake.email()}

# POST endpoint for PII detection and anonymization
@app.post("/detect-sensitive-data", tags=["zt-features-lib"])
async def detect_sensitive_data(request: Request, body: PIIPromptRequest):
    response = await detect_pii(prompt=body.prompt)
    return response

# POST endpoint for PII detection and anonymization
@app.post("/detect-sensitive-data-lite", tags=["zt-features-lib"])
async def detect_sensitive_data_lite(request: Request, body: PIIPromptLiteRequest):
    response = await detect_pii(prompt=body.prompt, top_n=body.top_n)
    return response

# POST endpoint for PII detection and anonymization
@app.post("/detect-and-anonymize", tags=["zt-features-lib"])
async def detect_and_anonymize_pii(request: Request, body: PIIPromptRequest):
    response = await get_anonymized_prompt(prompt=body.prompt)
    return response

# Custom OpenAPI to group endpoints under a tag
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({"message": "ZT Features API is running."})

def run():
    uvicorn.run("ztfeatureslib.main:app", host="127.0.0.1", port=8000, reload=False)


# --- Additional Endpoints for Custom PII Detection Logic ---
from ztfeatureslib.tools.pii_detection.services import detect_pii_gliner
from ztfeatureslib.tools.pii_detection.utils.constants import GLINER_MODEL_ENTITIES
from fastapi import Body


# 1. GLiNER-only with threshold 0.5 and no 'person' entity in gliner. However it includes Presidio results as well with 'person' entity.
@app.post("/detect-sensitive-data-gliner-strict", tags=["zt-features-lib"])
async def detect_sensitive_data_gliner_strict(request: Request, body: PIIPromptLiteRequest):
    entities = ','.join([e for e in GLINER_MODEL_ENTITIES])
    result = detect_pii_gliner.extract_pii_elements_gliner_only(
        text=body.prompt,
        pii_entities=entities,
        preserve_keywords="",
        top_n=body.top_n,
        threshold=0.5,
        exclude_entities=["person"],
        include_presidio=True
    )

    # Sensitive entity types to keep (based on GLINER_MODEL_ENTITIES)
    sensitive_types = set([
        "email", "email address", "gmail", "person", "phone number", "passport number", "credit card number",
        "social security number", "health insurance id number", "itin", "US passport_number", "date of birth",
        "mobile phone number", "bank account number", "cpf", "driver's license number", "tax identification number",
        "medical condition", "identity card number", "national id number", "ip address", "iban",
        "credit card expiration date", "username", "health insurance number", "registration number", "student id number",
        "insurance number", "cvv", "reservation number", "digital signature", "license plate number", "cnpj",
        "serial number", "vehicle registration number", "credit card brand", "fax number", "visa number",
        "insurance company", "identity document number", "transaction number", "national health insurance number",
        "cvc", "birth certificate number", "passport expiration date", "social_security_number", "medical license",
        "medication", "date time", "date", "time", "Crypto Currency number", "url", "blood type", "train ticket number"
    ])

    # Only keep results where the entity type is in sensitive_types or is a known sensitive label
    import re
    def is_plausible_address(text):
        # Match addresses with street number, street name, and city/country
        address_patterns = [
            r"\d+\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Square|Sq|Place|Pl|Terrace|Ter|Way|Park|Pkwy|Circle|Cir)",
            r"\d+\s+\w+\s+\w+", # e.g., 221B Baker Street
            r"\d+\s+\w+", # e.g., 1600 Pennsylvania
        ]
        for pat in address_patterns:
            if re.search(pat, text, re.IGNORECASE):
                return True
        # Also allow if contains a comma and at least 2 words (e.g., "London, UK")
        if "," in text and len(text.split()) > 2:
            return True
        return False


    import re
    def is_plausible_org(text):
        # Common organization suffixes and keywords
        org_keywords = [
            "inc", "ltd", "llc", "company", "corporation", "corp", "bank", "institute", "foundation", "group", "partners", "associates", "systems", "solutions", "industries", "plc", "gmbh", "s.a.", "s.r.l.", "co.", "limited", "trust", "board", "enterprise", "holdings", "ventures", "labs", "centre", "consortium", "ngo", "nonprofit"
        ]
        # Exclude generic government/location terms and common non-orgs
        generic_orgs = [
            "national parliament", "supreme court", "union buildings", "parliament", "court", "government", "city", "state", "province", "district", "department", "ministry", "office", "building", "center", "committee", "council", "school", "hospital", "clinic", "academy", "university", "college", "agency", "authority", "club", "society", "league", "alliance", "press", "media", "network", "studio", "federation", "union", "association", "chamber"
        ]
        # Remove any keyword from org_keywords that is also in generic_orgs
        org_keywords = [k for k in org_keywords if k not in generic_orgs]
        text_lower = text.lower().strip()
        # Exclude country names, continents, regions, and common non-org phrases
        country_names = [
            "south africa", "united states", "usa", "canada", "india", "china", "russia", "brazil", "germany", "france", "italy", "spain", "uk", "united kingdom", "australia", "japan", "mexico", "argentina", "egypt", "nigeria", "kenya", "sweden", "norway", "denmark", "finland", "switzerland", "netherlands", "belgium", "poland", "turkey", "saudi arabia", "uae", "israel", "iran", "pakistan", "bangladesh", "indonesia", "thailand", "vietnam", "philippines", "malaysia", "singapore", "south korea", "north korea", "new zealand", "ireland", "scotland", "wales", "portugal", "greece", "hungary", "czech republic", "slovakia", "austria", "romania", "bulgaria", "croatia", "serbia", "slovenia", "estonia", "latvia", "lithuania", "ukraine", "belarus", "moldova", "georgia", "armenia", "azerbaijan", "kazakhstan", "uzbekistan", "turkmenistan", "kyrgyzstan", "tajikistan", "mongolia", "afghanistan", "iraq", "syria", "lebanon", "jordan", "kuwait", "qatar", "oman", "yemen", "bahrain", "morocco", "algeria", "tunisia", "libya", "sudan", "ethiopia", "somalia", "tanzania", "uganda", "zambia", "zimbabwe", "botswana", "namibia", "angola", "mozambique", "madagascar", "cameroon", "ghana", "senegal", "mali", "burkina faso", "niger", "chad", "benin", "ivory coast", "guinea", "sierra leone", "liberia", "gabon", "congo", "democratic republic of the congo", "central african republic", "equatorial guinea", "cape verde", "mauritius", "seychelles", "comoros", "djibouti", "eritrea", "south sudan", "lesotho", "eswatini", "palestine", "vatican", "monaco", "liechtenstein", "andorra", "san marino", "luxembourg", "iceland", "greenland", "fiji", "papua new guinea", "solomon islands", "vanuatu", "samoa", "tonga", "kiribati", "tuvalu", "nauru", "palau", "micronesia", "marshall islands", "bahamas", "barbados", "antigua", "dominica", "grenada", "saint kitts", "saint lucia", "saint vincent", "trinidad", "jamaica", "haiti", "cuba", "dominican republic", "puerto rico", "guatemala", "honduras", "el salvador", "nicaragua", "costa rica", "panama", "colombia", "venezuela", "ecuador", "peru", "chile", "bolivia", "paraguay", "uruguay"
        ]
        continents = ["africa", "asia", "europe", "north america", "south america", "antarctica", "australia", "oceania"]
        regions = ["middle east", "far east", "eastern europe", "western europe", "northern europe", "southern europe", "central america", "latin america", "caribbean", "scandinavia", "balkans", "maghreb", "sub-saharan africa", "southeast asia", "pacific islands"]
        non_org_phrases = ["world", "earth", "globe", "continent", "region", "zone", "area", "territory", "district", "province", "state", "city", "village", "town", "municipality", "county", "suburb", "neighborhood", "metropolis", "capital", "country", "nation", "republic", "kingdom", "empire", "federation", "union", "community", "society", "club", "league", "association", "chamber", "council", "committee", "board", "office", "department", "ministry", "agency", "authority", "press", "media", "network", "studio", "school", "hospital", "clinic", "academy", "university", "college", "building", "center", "centre"]
        for word in country_names + continents + regions + non_org_phrases:
            if text_lower == word:
                return False
        # Include if ends with a business domain extension
        business_domains = [".ai", ".com", ".org", ".net", ".io", ".co", ".tech", ".biz", ".info", ".app", ".cloud", ".dev", ".inc", ".solutions", ".systems", ".agency", ".company", ".consulting", ".digital", ".finance", ".group", ".holdings", ".industries", ".international", ".media", ".network", ".partners", ".software", ".studio", ".ventures"]
        for ext in business_domains:
            if text_lower.endswith(ext):
                return True
        # Exclude generic orgs (exact or partial match)
        for g in generic_orgs:
            if g in text_lower or text_lower == g:
                return False
        # Include if matches org keywords (suffix or word in name)
        for k in org_keywords:
            if re.search(rf"\b{k}\b", text_lower):
                return True
        # Include if matches common company formats (e.g., 'X & Y Ltd', 'ABC Inc.', 'XYZ LLC')
        if re.search(r"[A-Z][A-Za-z0-9&\-\. ]+ (Inc|Ltd|LLC|PLC|GmbH|S\.A\.|S\.R\.L\.|Co\.|Corporation|Company|Corp|Bank|Trust|Holdings|Ventures|Labs|Foundation|Group|Partners|Associates|Systems|Solutions|Industries|Consortium|NGO|Nonprofit)$", text):
            return True
        # Include if contains at least two capitalized words (likely a proper name)
        if len([w for w in text.split() if w and w[0].isupper()]) >= 2:
            # Exclude if all words are capitalized (likely an acronym or not a real org)
            if not all(w.isupper() for w in text.split()):
                return True
        # Allow plausible single-word organizations (not in exclusion lists, not generic)
        if len(text.split()) == 1 and len(text) > 2:
            # Exclude if word is in exclusion lists or generic terms
            if text_lower not in country_names and text_lower not in continents and text_lower not in regions and text_lower not in non_org_phrases:
                # Exclude if word is all lowercase (likely not a proper noun)
                if not text.islower():
                    return True
        # Exclude if text is very short or generic
        if len(text.split()) < 2 or len(text) < 5:
            return False
        # Exclude if text contains only generic terms or locations
        if re.search(r"\b(city|state|province|district|building|center|committee|council|school|hospital|clinic|academy|university|college|agency|authority|club|society|league|alliance|press|media|network|studio|federation|union|association|chamber)\b", text_lower):
            return False
        return False

    def is_sensitive_entity(entity):
        # entity: [text, <LABEL>]
        label = entity[1].strip("<>").replace("_", " ").lower()
        if label == "location":
            return is_plausible_address(entity[0])
        if label == "org":
            return is_plausible_org(entity[0])
        return label in sensitive_types

    filtered_result = [ent for ent in result if is_sensitive_entity(ent)]
    return {"success": True, "data": filtered_result}

# 2. Only Presidio
@app.post("/detect-sensitive-data-presidio", tags=["zt-features-lib"])
async def detect_sensitive_data_presidio(request: Request, body: PIIPromptRequest):
    analyzer = detect_pii_gliner.get_presidio_analyzer()
    # Use all entities
    entities = GLINER_MODEL_ENTITIES
    results = detect_pii_gliner.get_presidio_result(body.prompt, presidio_entities=entities)
    return {"success": True, "data": results}

# 3. Only GLiNER (default threshold, includes 'person')
@app.post("/detect-sensitive-data-gliner", tags=["zt-features-lib"])
async def detect_sensitive_data_gliner(request: Request, body: PIIPromptRequest):
    entities = GLINER_MODEL_ENTITIES
    result = detect_pii_gliner.get_gliner_mode_result(
        text=body.prompt,
        pii_entities=entities,
        top_n=None
    )
    return {"success": True, "data": result}
