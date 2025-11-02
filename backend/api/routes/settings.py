"""
Settings API routes for managing application configuration.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import logging

from backend.database import get_db
from backend.models.setting import Setting
from backend.services.cache_service import get_cache_service
from backend.services.speech_service import SpeechService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


# Pydantic schemas
class SettingResponse(BaseModel):
    """Response model for a setting"""
    key: str
    value: str
    updated_at: str

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    """Request model for updating a setting"""
    value: str


class DefaultPromptResponse(BaseModel):
    """Response model for default prompt"""
    default_prompt: str


class VoiceInfo(BaseModel):
    """Response model for voice information"""
    voice_id: str
    name: str
    labels: Optional[dict] = None


class VoiceSettingResponse(BaseModel):
    """Response model for voice setting"""
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None


class VoiceSettingUpdate(BaseModel):
    """Request model for updating voice setting"""
    voice_id: str
    voice_name: str


@router.get("/system_prompt", response_model=SettingResponse)
def get_system_prompt(db: Session = Depends(get_db)):
    """
    Get the current system prompt.

    Returns the system prompt from database, or file fallback if not set.
    """
    try:
        # Try to get from database
        setting = db.query(Setting).filter(Setting.key == "system_prompt_en").first()

        if setting:
            return SettingResponse(
                key=setting.key,
                value=setting.value,
                updated_at=setting.updated_at.isoformat()
            )

        # Fallback to file
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        prompt_path = prompts_dir / "system_prompt_en.txt"

        if prompt_path.exists():
            file_prompt = prompt_path.read_text(encoding="utf-8")
            return SettingResponse(
                key="system_prompt_en",
                value=file_prompt,
                updated_at="N/A"
            )

        raise HTTPException(status_code=404, detail="System prompt not found")

    except Exception as e:
        logger.error(f"Error fetching system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/system_prompt", response_model=SettingResponse)
def update_system_prompt(
    update: SettingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the system prompt.

    This updates the database and clears the cache so changes apply immediately.
    """
    try:
        # Validate that value is not empty
        if not update.value or not update.value.strip():
            raise HTTPException(status_code=400, detail="System prompt cannot be empty")

        # Update or create setting
        setting = db.query(Setting).filter(Setting.key == "system_prompt_en").first()

        if setting:
            setting.value = update.value
            logger.info("Updated existing system prompt setting")
        else:
            setting = Setting(key="system_prompt_en", value=update.value)
            db.add(setting)
            logger.info("Created new system prompt setting")

        db.commit()
        db.refresh(setting)

        # Clear cache so new prompt is loaded immediately
        cache = get_cache_service()
        cache.delete("settings:system_prompt_en")
        logger.info("Cleared system prompt cache")

        return SettingResponse(
            key=setting.key,
            value=setting.value,
            updated_at=setting.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system_prompt/default", response_model=DefaultPromptResponse)
def get_default_system_prompt():
    """
    Get the default system prompt from file.

    This is useful for the "Reset to Default" functionality.
    """
    try:
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        prompt_path = prompts_dir / "system_prompt_en.txt"

        if prompt_path.exists():
            file_prompt = prompt_path.read_text(encoding="utf-8")
            return DefaultPromptResponse(default_prompt=file_prompt)

        raise HTTPException(status_code=404, detail="Default prompt file not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading default prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
def clear_settings_cache():
    """
    Clear all settings cache.

    Forces reload from database on next request.
    Useful for testing or troubleshooting.
    """
    try:
        cache = get_cache_service()
        count = cache.clear_pattern("settings:*")

        logger.info(f"Cleared {count} cache key(s)")
        return {"message": f"Cleared {count} cache key(s)", "success": True}

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice Settings Endpoints

@router.get("/voices", response_model=list[VoiceInfo])
def get_available_voices():
    """
    Get list of available ElevenLabs voices.

    Returns all voices available in your ElevenLabs account.
    Used for voice selection dropdown in UI.
    """
    try:
        speech_service = SpeechService()
        voices = speech_service.get_available_voices()

        return [
            VoiceInfo(
                voice_id=voice["voice_id"],
                name=voice["name"],
                labels=voice.get("labels")
            )
            for voice in voices
        ]

    except Exception as e:
        logger.error(f"Error fetching available voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice", response_model=VoiceSettingResponse)
def get_default_voice(db: Session = Depends(get_db)):
    """
    Get the current default voice setting.

    Returns the default voice_id and voice_name from database.
    If not set, returns None values (system will use language-based fallback).
    """
    try:
        voice_id_setting = db.query(Setting).filter(Setting.key == "default_voice_id").first()
        voice_name_setting = db.query(Setting).filter(Setting.key == "default_voice_name").first()

        return VoiceSettingResponse(
            voice_id=voice_id_setting.value if voice_id_setting else None,
            voice_name=voice_name_setting.value if voice_name_setting else None
        )

    except Exception as e:
        logger.error(f"Error fetching default voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/voice", response_model=VoiceSettingResponse)
def update_default_voice(
    update: VoiceSettingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the default voice setting.

    Sets the default voice to be used for all calls.
    This updates the database and clears the cache.
    """
    try:
        # Validate inputs
        if not update.voice_id or not update.voice_id.strip():
            raise HTTPException(status_code=400, detail="voice_id cannot be empty")
        if not update.voice_name or not update.voice_name.strip():
            raise HTTPException(status_code=400, detail="voice_name cannot be empty")

        # Update or create voice_id setting
        voice_id_setting = db.query(Setting).filter(Setting.key == "default_voice_id").first()
        if voice_id_setting:
            voice_id_setting.value = update.voice_id
            logger.info(f"Updated default_voice_id to {update.voice_id}")
        else:
            voice_id_setting = Setting(key="default_voice_id", value=update.voice_id)
            db.add(voice_id_setting)
            logger.info(f"Created default_voice_id setting: {update.voice_id}")

        # Update or create voice_name setting
        voice_name_setting = db.query(Setting).filter(Setting.key == "default_voice_name").first()
        if voice_name_setting:
            voice_name_setting.value = update.voice_name
            logger.info(f"Updated default_voice_name to {update.voice_name}")
        else:
            voice_name_setting = Setting(key="default_voice_name", value=update.voice_name)
            db.add(voice_name_setting)
            logger.info(f"Created default_voice_name setting: {update.voice_name}")

        db.commit()
        db.refresh(voice_id_setting)
        db.refresh(voice_name_setting)

        # Clear cache
        cache = get_cache_service()
        cache.delete("settings:default_voice_id")
        cache.delete("settings:default_voice_name")
        logger.info("Cleared voice settings cache")

        return VoiceSettingResponse(
            voice_id=voice_id_setting.value,
            voice_name=voice_name_setting.value
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating default voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))
