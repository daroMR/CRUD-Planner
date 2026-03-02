import re
import os
import uvicorn
from typing import Dict, Optional, Any
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- CONFIGURATION (SCIENTIFIC_STRICT_MODE) ---
load_dotenv(dotenv_path="../.env")

class ParseRequest(BaseModel):
    description: str = Field(..., example="## Field\nValue")

class StringifyRequest(BaseModel):
    data: Dict[str, str] = Field(..., example={"Key": "Value"})
    originalText: Optional[str] = ""

class SyncResponse(BaseModel):
    status: str = "success"
    data: Optional[Any] = None
    markdown: Optional[str] = None

app = FastAPI(
    title="STITCH_LAB_MW",
    version="2.1.0",
    description="VBA-Planner High-Fidelity Data Stitching Interface"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CORE_LOGIC (QUANTUM_ENGINE) ---
def parse_markdown_protocol(text: str) -> Dict[str, str]:
    """Extracts key-value pairs from markdown headers ## Key\nValue."""
    try:
        data = {}
        pattern = r"##\s*([^\n]+)\n([^\n#]*)"
        matches = re.finditer(pattern, text)
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key:
                data[key] = value
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parser_Fault: {str(e)}")

def stringify_markdown_protocol(data: Dict[str, str], original_text: str = "") -> str:
    """Consolidates key-value pairs back into the markdown description block."""
    try:
        # Purge existing headers to avoid registry duplicates
        clean_text = re.sub(r"##\s*[^\n]+\n[^\n#]*", "", original_text).strip()
        
        custom_fields = [f"## {k}\n{v}" for k, v in data.items() if k and v]
        fields_block = "\n\n".join(custom_fields)
        
        return f"{clean_text}\n\n{fields_block}".strip() if clean_text else fields_block.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stringify_Fault: {str(e)}")

# --- API_ENDPOINTS ---
@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def system_health():
    return {"status": "GRID_ACTIVE", "version": "2.1.0", "engine": "Scientific_FastAPI"}

@app.post("/api/v1/parse", response_model=Dict[str, str])
async def parse_data_node(payload: ParseRequest):
    return parse_markdown_protocol(payload.description)

@app.post("/api/v1/stringify", response_model=SyncResponse)
async def stringify_data_node(payload: StringifyRequest):
    md = stringify_markdown_protocol(payload.data, payload.originalText)
    return SyncResponse(markdown=md)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
