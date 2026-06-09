"""
Gemini client wrapper for text and multimodal DriveLegal requests.
"""
import base64
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import google.generativeai as genai


def _extract_user_question(user_prompt: str) -> str:
    marker = "User Question:"
    if marker not in user_prompt:
        return user_prompt.strip()
    return user_prompt.split(marker, 1)[1].strip()


class GeminiClient:
    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    async def complete(self, system: str, user: str) -> str:
        if not self.model:
            return "[STUB] Gemini API key not set. Set GEMINI_API_KEY in .env"
        prompt = f"{system}\n\n{user}"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Gemini Client] Text completion failed: {e}")
            question = _extract_user_question(user)
            return (
                "DriveLegal AI could not reach Gemini right now because the API quota was exceeded, "
                "the request timed out, or the network was unavailable.\n\n"
                f"Your question: {question}\n\n"
                "Please try again later, or ask a direct fine lookup such as helmet, seatbelt, "
                "license, overspeeding, or drunk driving so DriveLegal can answer from the local database."
            )

    async def stream(self, system: str, user: str):
        if not self.model:
            yield "[STUB] Gemini API key not set."
            return
        prompt = f"{system}\n\n{user}"
        try:
            for chunk in self.model.generate_content(prompt, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"[Gemini Client] Text stream failed: {e}")
            question = _extract_user_question(user)
            yield (
                "DriveLegal AI could not reach Gemini right now because the API quota was exceeded, "
                "the request timed out, or the network was unavailable.\n\n"
                f"Your question: {question}\n\n"
                "Please try again later, or ask a direct fine lookup so DriveLegal can answer from "
                "the local database."
            )

    async def complete_multimodal(self, prompt: str, file_bytes: bytes, mime_type: str) -> str:
        if not self.model:
            openai_answer = await self._complete_openai_multimodal(prompt, file_bytes, mime_type)
            if openai_answer:
                return openai_answer
            local_answer = self._complete_local_ocr(file_bytes, mime_type)
            if local_answer:
                return local_answer
            return (
                "> [!WARNING]\n"
                "> OCR is not configured on this DriveLegal backend.\n\n"
                "### OCR Service Setup Needed\n"
                "- Install Tesseract OCR, or add a valid `GEMINI_API_KEY`/`OPENAI_API_KEY` with available quota.\n"
                "- Restart the FastAPI backend after changing OCR configuration.\n"
                "- Upload the challan image again.\n\n"
                "No challan details were extracted."
            )

        try:
            image_part = {
                "mime_type": mime_type,
                "data": file_bytes,
            }
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except Exception as e:
            print(f"[Gemini Client] Multimodal completion failed: {e}")
            openai_answer = await self._complete_openai_multimodal(prompt, file_bytes, mime_type)
            if openai_answer:
                return (
                    "> [!NOTE]\n"
                    "> Gemini OCR was unavailable, so DriveLegal used OpenAI Vision OCR instead.\n\n"
                    f"{openai_answer}"
                )
            local_answer = self._complete_local_ocr(file_bytes, mime_type)
            if local_answer:
                return (
                    "> [!NOTE]\n"
                    "> Online AI OCR was unavailable, so DriveLegal used local Tesseract OCR instead.\n\n"
                    f"{local_answer}"
                )

            return (
                "> [!WARNING]\n"
                "> The image was uploaded, but OCR could not run because online AI providers have no available quota "
                "and local Tesseract OCR is not available.\n\n"
                "### OCR Service Unavailable\n"
                "- Install Tesseract OCR, or add a Gemini/OpenAI API key with active billing/quota in `backend/.env`.\n"
                "- Restart the FastAPI backend after updating OCR configuration.\n"
                "- Try the upload again after the quota resets or billing is enabled.\n"
                "- You can still verify challan details on the official Parivahan portal: "
                "[echallan.parivahan.gov.in](https://echallan.parivahan.gov.in).\n\n"
                "No challan details were extracted."
            )

    async def _complete_openai_multimodal(self, prompt: str, file_bytes: bytes, mime_type: str) -> str | None:
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            return None

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=openai_key)
            encoded_image = base64.b64encode(file_bytes).decode("ascii")
            model_name = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are DriveLegal AI, a careful OCR assistant for Indian traffic challans.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{encoded_image}",
                                },
                            },
                        ],
                    },
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenAI Client] Multimodal fallback failed: {e}")
            return None

    def _complete_local_ocr(self, file_bytes: bytes, mime_type: str) -> str | None:
        tesseract_cmd = shutil.which("tesseract") or self._find_tesseract_executable()
        if not tesseract_cmd:
            return None

        suffix = ".png" if mime_type == "image/png" else ".jpg"
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                input_path = Path(tmp_dir) / f"challan{suffix}"
                output_base = Path(tmp_dir) / "challan_ocr"
                input_path.write_bytes(file_bytes)

                subprocess.run(
                    [tesseract_cmd, str(input_path), str(output_base), "-l", "eng", "--psm", "6"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                ocr_text = output_base.with_suffix(".txt").read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[Local OCR] Tesseract fallback failed: {e}")
            return None

        if not ocr_text.strip():
            return None

        return self._format_challan_from_ocr_text(ocr_text)

    def _find_tesseract_executable(self) -> str | None:
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        return None

    def _format_challan_from_ocr_text(self, ocr_text: str) -> str:
        normalized_text = re.sub(r"\s+", " ", ocr_text).strip()
        lower_text = normalized_text.lower()

        violation, section = self._infer_violation_and_section(lower_text)
        fine = self._extract_first_match(
            normalized_text,
            [
                r"(?:fine|penalty|amount|fee|rs\.?|inr|₹)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9][0-9,]{1,8})",
                r"(?:rs\.?|inr|₹)\s*([0-9][0-9,]{1,8})",
            ],
            flags=re.IGNORECASE,
        )
        vehicle = self._extract_first_match(
            normalized_text.upper(),
            [r"\b([A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{3,4})\b"],
        )
        challan_no = self._extract_first_match(
            normalized_text,
            [
                r"(?:challan|notice|ticket)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-\/]{5,})",
                r"\b([A-Z]{2}\d{6,})\b",
            ],
        )
        date_time = self._extract_first_match(
            normalized_text,
            [
                r"\b(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)\b",
                r"\b(\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)\b",
            ],
        )
        state = self._infer_state(normalized_text, vehicle)
        location = self._extract_first_match(
            normalized_text,
            [
                r"(?:location|place|offence place|offense place)\s*[:\-]?\s*([A-Za-z0-9,\- ]{3,80})",
                r"(?:traffic police|police)\s*[:\-]?\s*([A-Za-z0-9,\- ]{3,80})",
            ],
        )
        status = self._extract_first_match(
            normalized_text,
            [r"(?:status|payment status)\s*[:\-]?\s*(paid|unpaid|pending|disposed|open|closed)"],
            flags=re.IGNORECASE,
        )

        fine_value = f"INR {fine}" if fine else "Not visible"
        vehicle_value = self._clean_vehicle_number(vehicle) if vehicle else "Not visible"

        return (
            "### E-Challan AI Extraction Results\n"
            f"- **Violation / Offense:** {violation}\n"
            f"- **Section Violated:** {section}\n"
            f"- **Fine Amount:** {fine_value}\n"
            f"- **Vehicle Number:** {vehicle_value}\n"
            f"- **Challan Number:** {challan_no or 'Not visible'}\n"
            f"- **Date & Time:** {date_time or 'Not visible'}\n"
            f"- **Offense Location:** {location or 'Not visible'}\n"
            f"- **State Jurisdiction:** {state or 'Not visible'}\n"
            f"- **Payment Status:** {status.title() if status else 'Not visible'}\n\n"
            "#### Action Steps\n"
            "1. Verify these OCR-extracted details on https://echallan.parivahan.gov.in before paying.\n"
            "2. Pay only through an official government or authorized payment portal.\n"
            "3. If any field says \"Not visible\", upload a clearer, well-lit image of the full challan.\n\n"
            "#### OCR Text Used\n"
            f"{ocr_text.strip()[:1200]}"
        )

    def _infer_violation_and_section(self, lower_text: str) -> tuple[str, str]:
        rules = [
            (["helmet", "headgear"], "Riding without wearing protective headgear (Helmet)", "Section 194D, Motor Vehicles Act"),
            (["seatbelt", "seat belt"], "Driving without wearing seatbelt", "Section 194B, Motor Vehicles Act"),
            (["over speed", "overspeed", "speeding"], "Overspeeding / speed limit violation", "Section 183, Motor Vehicles Act"),
            (["drunk", "alcohol", "intoxicat"], "Driving under the influence", "Section 185, Motor Vehicles Act"),
            (["licence", "license", "dl"], "Driving without a valid driving license", "Section 181, Motor Vehicles Act"),
            (["mobile", "phone"], "Use of mobile phone while driving", "Section 184, Motor Vehicles Act"),
            (["insurance"], "Driving without valid insurance", "Section 196, Motor Vehicles Act"),
            (["registration", " rc "], "Driving without valid registration certificate", "Section 192, Motor Vehicles Act"),
            (["pollution", "puc", "pucc"], "Driving without valid pollution certificate", "Central Motor Vehicles Rules"),
        ]
        for keywords, violation, section in rules:
            if any(keyword in lower_text for keyword in keywords):
                return violation, section
        return "Not visible", "Not visible"

    def _infer_state(self, text: str, vehicle: str | None) -> str | None:
        states = {
            "DL": "National Capital Territory of Delhi",
            "WB": "West Bengal",
            "MH": "Maharashtra",
            "KA": "Karnataka",
            "TN": "Tamil Nadu",
            "UP": "Uttar Pradesh",
            "HR": "Haryana",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "GJ": "Gujarat",
            "BR": "Bihar",
            "TS": "Telangana",
            "AP": "Andhra Pradesh",
            "OD": "Odisha",
            "KL": "Kerala",
        }
        text_upper = text.upper()
        for state in states.values():
            if state.upper() in text_upper:
                return state
        if vehicle:
            prefix = re.sub(r"[^A-Z0-9]", "", vehicle.upper())[:2]
            return states.get(prefix)
        return None

    def _extract_first_match(self, text: str, patterns: list[str], flags: int = 0) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags)
            if match:
                return match.group(1).strip(" :-")
        return None

    def _clean_vehicle_number(self, value: str) -> str:
        compact = re.sub(r"[^A-Z0-9]", "", value.upper())
        match = re.match(r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})(\d{3,4})$", compact)
        if not match:
            return value
        return "-".join(match.groups())
