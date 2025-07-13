export interface Booking {
  id: string;
  slot_id: string;
  user_id: string;
  status: BookingStatus;
  notes?: string;
  booked_at: string;
  cancelled_at?: string;
  is_active: boolean;
  slot?: any; // Slot object
  user?: any; // User object
}

export interface BookingCreate {
  slot_id: string;
  notes?: string;
}

export interface BookingUpdate {
  notes?: string;
  status?: BookingStatus;
}

export enum BookingStatus {
  ACTIVE = 'active',
  CANCELLED = 'cancelled'
}

export interface BookingFilters {
  skip?: number;
  limit?: number;
}
