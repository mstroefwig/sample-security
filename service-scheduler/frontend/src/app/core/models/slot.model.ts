export interface Slot {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  max_participants: number;
  current_participants: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  available_spots: number;
  is_full: boolean;
  creator?: any; // User object
}

export interface SlotCreate {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  max_participants: number;
}

export interface SlotUpdate {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  max_participants?: number;
  is_available?: boolean;
}

export interface SlotFilters {
  skip?: number;
  limit?: number;
  available_only?: boolean;
  start_date?: string;
  end_date?: string;
}
