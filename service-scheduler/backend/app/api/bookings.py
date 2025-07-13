from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.slot import Slot
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingResponse, BookingWithDetails
from app.auth.dependencies import get_current_active_user, get_current_admin_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking (claim a slot)."""
    try:
        # Check if slot exists and is available
        result = await db.execute(
            select(Slot).where(Slot.id == booking_data.slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        if not slot.is_available or slot.is_full:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot is not available"
            )
        
        # Check if user already has a booking for this slot
        result = await db.execute(
            select(Booking).where(
                and_(
                    Booking.slot_id == booking_data.slot_id,
                    Booking.user_id == current_user.id,
                    Booking.status == BookingStatus.ACTIVE
                )
            )
        )
        existing_booking = result.scalar_one_or_none()
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active booking for this slot"
            )
        
        # Create new booking
        new_booking = Booking(
            slot_id=booking_data.slot_id,
            user_id=current_user.id,
            notes=booking_data.notes
        )
        
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)
        
        logger.info(f"New booking created by {current_user.email}: {new_booking.id}")
        return new_booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking creation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Booking creation failed"
        )


@router.get("/my", response_model=List[BookingWithDetails])
async def get_my_bookings(
    skip: int = Query(0, ge=0, description="Number of bookings to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of bookings to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookings."""
    try:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.slot).selectinload(Slot.creator),
                selectinload(Booking.user)
            )
            .where(Booking.user_id == current_user.id)
            .order_by(Booking.booked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        bookings = result.scalars().all()
        
        return bookings
        
    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings"
        )


@router.get("/", response_model=List[BookingWithDetails])
async def get_all_bookings(
    skip: int = Query(0, ge=0, description="Number of bookings to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of bookings to return"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all bookings (Admin only)."""
    try:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.slot).selectinload(Slot.creator),
                selectinload(Booking.user)
            )
            .order_by(Booking.booked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        bookings = result.scalars().all()
        
        return bookings
        
    except Exception as e:
        logger.error(f"Error getting all bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings"
        )


@router.get("/{booking_id}", response_model=BookingWithDetails)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific booking by ID."""
    try:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.slot).selectinload(Slot.creator),
                selectinload(Booking.user)
            )
            .where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check permissions
        if current_user.role.value != "admin" and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve booking"
        )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking."""
    try:
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check permissions
        if current_user.role.value != "admin" and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        if booking.status != BookingStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled"
            )
        
        # Cancel the booking
        booking.cancel()
        await db.commit()
        
        logger.info(f"Booking cancelled by {current_user.email}: {booking.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking cancellation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Booking cancellation failed"
        )
