import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Slot, SlotCreate, SlotUpdate, SlotFilters } from '../models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SlotService {
  private readonly baseUrl = `${environment.apiUrl}/slots`;

  constructor(private http: HttpClient) {}

  /**
   * Get all slots with optional filters
   */
  getSlots(filters?: SlotFilters): Observable<Slot[]> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.skip !== undefined) {
        params = params.set('skip', filters.skip.toString());
      }
      if (filters.limit !== undefined) {
        params = params.set('limit', filters.limit.toString());
      }
      if (filters.available_only !== undefined) {
        params = params.set('available_only', filters.available_only.toString());
      }
      if (filters.start_date) {
        params = params.set('start_date', filters.start_date);
      }
      if (filters.end_date) {
        params = params.set('end_date', filters.end_date);
      }
    }

    return this.http.get<Slot[]>(this.baseUrl, { params })
      .pipe(catchError(this.handleError));
  }

  /**
   * Get available slots only
   */
  getAvailableSlots(filters?: Omit<SlotFilters, 'available_only'>): Observable<Slot[]> {
    return this.getSlots({ ...filters, available_only: true });
  }

  /**
   * Get slot by ID
   */
  getSlot(id: string): Observable<Slot> {
    return this.http.get<Slot>(`${this.baseUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Create new slot (Admin only)
   */
  createSlot(slotData: SlotCreate): Observable<Slot> {
    return this.http.post<Slot>(this.baseUrl, slotData)
      .pipe(catchError(this.handleError));
  }

  /**
   * Update slot (Admin only)
   */
  updateSlot(id: string, slotData: SlotUpdate): Observable<Slot> {
    return this.http.put<Slot>(`${this.baseUrl}/${id}`, slotData)
      .pipe(catchError(this.handleError));
  }

  /**
   * Delete slot (Admin only)
   */
  deleteSlot(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get slots for today
   */
  getTodaySlots(): Observable<Slot[]> {
    const today = new Date();
    const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);

    return this.getSlots({
      start_date: startOfDay.toISOString(),
      end_date: endOfDay.toISOString(),
      available_only: true
    });
  }

  /**
   * Get upcoming slots (next 7 days)
   */
  getUpcomingSlots(): Observable<Slot[]> {
    const now = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(now.getDate() + 7);

    return this.getSlots({
      start_date: now.toISOString(),
      end_date: nextWeek.toISOString(),
      available_only: true,
      limit: 50
    });
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else {
      if (error.status === 404) {
        errorMessage = 'Slot not found';
      } else if (error.status === 403) {
        errorMessage = 'Not authorized to perform this action';
      } else if (error.status === 400) {
        errorMessage = error.error?.detail || 'Invalid request';
      } else if (error.status === 500) {
        errorMessage = 'Server error. Please try again later';
      } else {
        errorMessage = error.error?.detail || `Error Code: ${error.status}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
