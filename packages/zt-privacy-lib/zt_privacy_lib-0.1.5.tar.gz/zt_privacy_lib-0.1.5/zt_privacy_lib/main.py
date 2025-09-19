from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from faker import Faker
import uvicorn
from zt_privacy_lib.tools.pii_detection.detect_pii import detect_pii
from zt_privacy_lib.tools.pii_detection.schema.pii_prompt import PIIPromptLiteRequest, PIIPromptRequest
from zt_privacy_lib.tools.pii_detection.detect_pii import get_anonymized_prompt

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
    uvicorn.run("zt_privacy_lib.main:app", host="127.0.0.1", port=8000, reload=False)


# --- Additional Endpoints for Custom PII Detection Logic ---
from zt_privacy_lib.tools.pii_detection.services import detect_pii_gliner
from zt_privacy_lib.tools.pii_detection.utils.constants import GLINER_MODEL_ENTITIES
from fastapi import Body


# 1. GLiNER strict detection using the same service as zt-gliner
@app.post("/detect-sensitive-data-gliner-strict", tags=["zt-features-lib"])
async def detect_sensitive_data_gliner_strict(request: Request, body: PIIPromptLiteRequest):
    from zt_privacy_lib.tools.pii_detection.services.detect_anonymize_pii_service_strict import get_pii_from_user_prompt_strict_gliner
    
    # Use the same strict service function as zt-gliner
    result = await get_pii_from_user_prompt_strict_gliner(
        prompt=body.prompt,
        anonymize_keywords="",
        pii_entities="person,organization,phone number,address,passport number,credit card number,social security number,health insurance id number,date time,url,date of birth,bank account number,medical condition,identity card number,national id number,ip address,license plate number,postal code,serial number,insurance company,email",
        preserve_keywords=""
    )
    
    # Extract the detected PII in the expected format
    detected_pii = []
    if "detected_pii_in_prompt" in result:
        detected_pii.extend(result["detected_pii_in_prompt"])
    if "detected_custom_pii_prompt" in result:
        detected_pii.extend(result["detected_custom_pii_prompt"])
    
    # Apply top_n limit if specified
    if body.top_n is not None and body.top_n > 0:
        detected_pii = detected_pii[:body.top_n]
    
    return {"success": True, "data": detected_pii}

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
