from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User, UserRole
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotUpdate, SlotResponse, SlotWithCreator
from app.auth.dependencies import get_current_admin_user, get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/slots", tags=["slots"])


@router.post("/", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    slot_data: SlotCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new time slot (Admin only)."""
    try:
        # Validate time range
        if slot_data.end_time <= slot_data.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
        
        my_secret = "cuwekfjuwehfkihhefuyghjwhefjwegf"
        print(my_secret)

        # Check for conflicting slots
        result = await db.execute(
            select(Slot).where(
                and_(
                    Slot.created_by == current_user.id,
                    or_(
                        and_(
                            Slot.start_time <= slot_data.start_time,
                            Slot.end_time > slot_data.start_time
                        ),
                        and_(
                            Slot.start_time < slot_data.end_time,
                            Slot.end_time >= slot_data.end_time
                        ),
                        and_(
                            Slot.start_time >= slot_data.start_time,
                            Slot.end_time <= slot_data.end_time
                        )
                    )
                )
            )
        )
        conflicting_slot = result.scalar_one_or_none()
        
        if conflicting_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time slot conflicts with existing slot"
            )
        
        # Create new slot
        new_slot = Slot(
            title=slot_data.title,
            description=slot_data.description,
            start_time=slot_data.start_time,
            end_time=slot_data.end_time,
            max_participants=slot_data.max_participants,
            created_by=current_user.id
        )
        
        db.add(new_slot)
        await db.commit()
        await db.refresh(new_slot)
        
        logger.info(f"New slot created by {current_user.email}: {new_slot.id}")
        return new_slot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slot creation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slot creation failed"
        )


@router.get("/", response_model=List[SlotWithCreator])
async def get_slots(
    skip: int = Query(0, ge=0, description="Number of slots to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of slots to return"),
    available_only: bool = Query(False, description="Return only available slots"),
    start_date: Optional[datetime] = Query(None, description="Filter slots starting from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter slots ending before this date"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of slots with optional filters."""
    try:
        query = select(Slot).options(selectinload(Slot.creator))
        
        # Apply filters
        conditions = []
        
        if available_only:
            conditions.append(Slot.is_available == True)
        
        if start_date:
            conditions.append(Slot.start_time >= start_date)
            
        if end_date:
            conditions.append(Slot.end_time <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by start time
        query = query.order_by(Slot.start_time).offset(skip).limit(limit)
        
        result = await db.execute(query)
        slots = result.scalars().all()
        
        return slots
        
    except Exception as e:
        logger.error(f"Error getting slots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve slots"
        )


@router.get("/{slot_id}", response_model=SlotWithCreator)
async def get_slot(
    slot_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific slot by ID."""
    try:
        result = await db.execute(
            select(Slot)
            .options(selectinload(Slot.creator))
            .where(Slot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        return slot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slot {slot_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve slot"
        )


@router.put("/{slot_id}", response_model=SlotResponse)
async def update_slot(
    slot_id: str,
    slot_update: SlotUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a slot (Admin only)."""
    try:
        result = await db.execute(
            select(Slot).where(Slot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        # Update fields
        update_data = slot_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(slot, field, value)
        
        # Validate time range if times are being updated
        if slot.end_time <= slot.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
        
        await db.commit()
        await db.refresh(slot)
        
        logger.info(f"Slot updated by {current_user.email}: {slot.id}")
        return slot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slot update error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slot update failed"
        )


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a slot (Admin only)."""
    try:
        result = await db.execute(
            select(Slot).where(Slot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        await db.delete(slot)
        await db.commit()
        
        logger.info(f"Slot deleted by {current_user.email}: {slot.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slot deletion error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slot deletion failed"
        )
