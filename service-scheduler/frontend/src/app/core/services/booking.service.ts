import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Booking, BookingCreate, BookingFilters } from '../models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private readonly baseUrl = `${environment.apiUrl}/bookings`;

  constructor(private http: HttpClient) {}

  /**
   * Create new booking (claim a slot)
   */
  createBooking(bookingData: BookingCreate): Observable<Booking> {
    return this.http.post<Booking>(this.baseUrl, bookingData)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get current user's bookings
   */
  getMyBookings(filters?: BookingFilters): Observable<Booking[]> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.skip !== undefined) {
        params = params.set('skip', filters.skip.toString());
      }
      if (filters.limit !== undefined) {
        params = params.set('limit', filters.limit.toString());
      }
    }

    return this.http.get<Booking[]>(`${this.baseUrl}/my`, { params })
      .pipe(catchError(this.handleError));
  }

  /**
   * Get all bookings (Admin only)
   */
  getAllBookings(filters?: BookingFilters): Observable<Booking[]> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.skip !== undefined) {
        params = params.set('skip', filters.skip.toString());
      }
      if (filters.limit !== undefined) {
        params = params.set('limit', filters.limit.toString());
      }
    }

    return this.http.get<Booking[]>(this.baseUrl, { params })
      .pipe(catchError(this.handleError));
  }

  /**
   * Get booking by ID
   */
  getBooking(id: string): Observable<Booking> {
    return this.http.get<Booking>(`${this.baseUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Cancel booking
   */
  cancelBooking(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get active bookings for current user
   */
  getActiveBookings(): Observable<Booking[]> {
    return this.getMyBookings({ limit: 100 });
  }

  /**
   * Check if user has booking for a specific slot
   */
  hasBookingForSlot(slotId: string): Observable<boolean> {
    return new Observable(observer => {
      this.getMyBookings().subscribe({
        next: (bookings) => {
          const hasBooking = bookings.some(booking => 
            booking.slot_id === slotId && booking.is_active
          );
          observer.next(hasBooking);
          observer.complete();
        },
        error: (error) => observer.error(error)
      });
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
        errorMessage = 'Booking not found';
      } else if (error.status === 403) {
        errorMessage = 'Not authorized to perform this action';
      } else if (error.status === 400) {
        errorMessage = error.error?.detail || 'Invalid request';
      } else if (error.status === 409) {
        errorMessage = 'You already have a booking for this slot';
      } else if (error.status === 500) {
        errorMessage = 'Server error. Please try again later';
      } else {
        errorMessage = error.error?.detail || `Error Code: ${error.status}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
