# Service Scheduler - Development Guide

## Architecture Overview

This service scheduling application consists of three main components:

### 1. **Backend (FastAPI + Python)**
- **Location**: `backend/`
- **Port**: 8000
- **Features**:
  - JWT-based authentication
  - Role-based access control (Admin/User)
  - RESTful API for slots and bookings
  - SQLAlchemy ORM with PostgreSQL
  - Async/await patterns for performance

### 2. **Frontend (Angular + Material)**
- **Location**: `frontend/`
- **Port**: 4200
- **Features**:
  - Modern Angular 17+ with standalone components
  - Angular Material UI components
  - Reactive forms and HTTP client
  - Authentication guards and interceptors
  - Role-based routing

### 3. **Database & GraphQL (PostgreSQL + Hasura)**
- **PostgreSQL Port**: 5432
- **Hasura Port**: 8080
- **Features**:
  - Database schema with proper relationships
  - Real-time GraphQL subscriptions via Hasura
  - Role-based permissions
  - Database triggers for business logic

## User Roles & Permissions

### Admin Users
- ✅ Create, edit, delete time slots
- ✅ View all bookings
- ✅ Cancel any booking
- ✅ Manage user roles
- ✅ Access admin dashboard

### Regular Users
- ✅ View available time slots
- ✅ Book/claim available slots
- ✅ View their own bookings
- ✅ Cancel their own bookings
- ❌ Cannot access admin features

## API Endpoints

### Authentication
```
POST /api/v1/auth/register - Register new user
POST /api/v1/auth/login    - Login user
POST /api/v1/auth/token    - OAuth2 compatible login
```

### Slots (Time Slots Management)
```
GET    /api/v1/slots       - List all slots (with filters)
POST   /api/v1/slots       - Create slot (Admin only)
GET    /api/v1/slots/{id}  - Get specific slot
PUT    /api/v1/slots/{id}  - Update slot (Admin only)
DELETE /api/v1/slots/{id}  - Delete slot (Admin only)
```

### Bookings
```
POST   /api/v1/bookings       - Create booking (claim slot)
GET    /api/v1/bookings/my    - Get user's bookings
GET    /api/v1/bookings       - Get all bookings (Admin only)
GET    /api/v1/bookings/{id}  - Get specific booking
DELETE /api/v1/bookings/{id}  - Cancel booking
```

## Database Schema

### Tables

1. **users**
   - Primary key: `id` (UUID)
   - Unique: `email`
   - Fields: `first_name`, `last_name`, `role`, `is_active`
   - Passwords: Hashed with bcrypt

2. **slots**
   - Primary key: `id` (UUID)
   - Foreign key: `created_by` → `users.id`
   - Fields: `title`, `description`, `start_time`, `end_time`
   - Availability: `is_available`, `max_participants`, `current_participants`

3. **bookings**
   - Primary key: `id` (UUID)
   - Foreign keys: `slot_id` → `slots.id`, `user_id` → `users.id`
   - Constraint: Unique combination of `slot_id` + `user_id`
   - Fields: `status`, `notes`, `booked_at`, `cancelled_at`

### Database Triggers
- **Auto-update participant counts**: When bookings are created/deleted
- **Slot availability management**: Automatically marks slots as unavailable when full
- **Timestamp management**: Auto-updates `updated_at` fields

## Quick Start

### 1. Start Database Services
```bash
cd service-scheduler
docker-compose up -d postgres redis hasura
```

### 2. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
ng serve
```

### 4. Access Applications
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Hasura Console**: http://localhost:8080

## Default Test Users

The system comes with pre-configured test users:

### Admin User
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Capabilities**: Full system access

### Regular Users
- **Email**: `user1@example.com` / **Password**: `admin123`
- **Email**: `user2@example.com` / **Password**: `admin123`
- **Capabilities**: Limited to user functions

## Development Workflow

### Adding New Features

1. **Backend Changes**:
   - Update models in `backend/app/models/`
   - Create/update API endpoints in `backend/app/api/`
   - Add new schemas in `backend/app/schemas/`
   - Run database migrations if needed

2. **Frontend Changes**:
   - Update models in `frontend/src/app/core/models/`
   - Update services in `frontend/src/app/core/services/`
   - Create/update components in `frontend/src/app/features/`
   - Add new routes if needed

3. **Database Changes**:
   - Update `hasura/init.sql` for schema changes
   - Update Hasura metadata for permissions
   - Apply migrations via Hasura console

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test

# E2E tests
cd frontend
npm run e2e
```

## Security Features

### Authentication
- JWT tokens with configurable expiration
- Secure password hashing with bcrypt
- Token refresh mechanism
- Automatic logout on token expiration

### Authorization
- Role-based access control
- API endpoint protection with decorators
- Frontend route guards
- Hasura row-level security

### Data Protection
- SQL injection prevention via parameterized queries
- CORS configuration
- Request validation with Pydantic
- Environment variable configuration

## Performance Optimizations

### Backend
- Async/await for database operations
- Connection pooling
- Query optimization with proper indexing
- Caching with Redis (optional)

### Frontend
- Lazy loading of feature modules
- OnPush change detection strategy
- HTTP interceptors for efficient API calls
- Reactive programming with RxJS

### Database
- Proper indexing on frequently queried columns
- Database triggers for business logic
- Connection pooling
- Query optimization

## Production Deployment

The application is designed for Azure deployment:

### Recommended Azure Services
- **Frontend**: Azure Static Web Apps
- **Backend**: Azure Container Apps
- **Database**: Azure Database for PostgreSQL
- **Container Registry**: Azure Container Registry
- **Monitoring**: Azure Application Insights

### Environment Variables

**Backend (.env)**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
HASURA_GRAPHQL_ENDPOINT=https://your-hasura.com/v1/graphql
HASURA_ADMIN_SECRET=your-secret
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend (environment.prod.ts)**:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api.com/api/v1',
  hasuraUrl: 'https://your-hasura.com/v1/graphql'
};
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if PostgreSQL is running: `docker-compose ps`
   - Verify connection string in `.env`
   - Ensure database exists and is accessible

2. **Authentication Errors**
   - Check JWT secret consistency between backend and Hasura
   - Verify token expiration settings
   - Clear browser localStorage if needed

3. **Permission Denied**
   - Verify user roles in database
   - Check Hasura permissions configuration
   - Ensure proper JWT claims

4. **CORS Issues**
   - Update `CORS_ORIGINS` in backend configuration
   - Check frontend API URL configuration
   - Verify proxy settings for development

### Logs and Debugging

```bash
# Backend logs
cd backend
uvicorn main:app --reload --log-level debug

# Database logs
docker-compose logs postgres

# Hasura logs
docker-compose logs hasura
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at `/docs`
- Check Hasura console for GraphQL schema
- Create an issue in the repository
