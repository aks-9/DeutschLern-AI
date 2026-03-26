from fastapi import APIRouter

router = APIRouter(prefix="/exercises", tags=["exercises"])


# Routes implemented in Week 2
# GET  /exercises/{topic_id}
# POST /exercises/check
# GET  /exercises/translate
# POST /exercises/translate/check
