# Multi-Tenant SaaS Task Manager

A Django-based multi-tenant task management system with real-time updates, background notifications, and async capabilities.

## Features

- **Multi-Tenant Architecture**: Each company has isolated task management
- **JWT Authentication**: Secure token-based authentication
- **REST API**: Full CRUD operations for tasks with DRF
- **Real-time Updates**: WebSocket connections for live task updates
- **Background Jobs**: Celery-powered email notifications with delay
- **Async Endpoints**: External API integration with local data merging
- **Advanced Queries**: Complex database operations and analytics

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Background Tasks**: Celery
- **WebSockets**: Django Channels
- **Async**: httpx for external API calls

## Project Structure

```
task_manager/
├── accounts/          # User authentication and company management
├── tasks/             # Task CRUD, WebSockets, and async views
├── notifications/     # Email notification models and Celery tasks
├── task_manager/      # Main project settings and configuration
├── requirements.txt   # Python dependencies
├── docker-compose.yml # PostgreSQL and Redis setup
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Demo_project
pip install -r requirements.txt
```

### 2. Database Setup

Start PostgreSQL and Redis using Docker:

```bash
docker-compose up -d postgres redis
```

Or install them locally and ensure they're running on default ports.

### 3. Django Setup

```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 4. Start Background Services

In separate terminals:

```bash
# Start Celery worker
celery -A task_manager worker --loglevel=info

# Start WebSocket server (if not using runserver)
daphne -p 8001 task_manager.asgi:application
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `GET /api/auth/company-users/` - Get company users

### Tasks

- `GET /api/tasks/` - List company tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/tasks/my_tasks/` - Get current user's tasks
- `GET /api/tasks/statistics/` - Get task statistics
- `GET /api/external-tasks/` - Async endpoint with external data

## WebSocket Connection

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tasks/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

## Usage Examples

### 1. Register and Create Company

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

### 3. Create Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Complete project setup",
    "description": "Set up the development environment",
    "status": "todo",
    "assigned_to": 1
  }'
```

## Advanced Database Queries

Run analytics command to see complex queries in action:

```bash
python manage.py task_analytics
```

This demonstrates:
- Tasks per user with aggregation
- Task status distribution with percentages
- Company performance metrics
- Daily creation trends
- Multi-table joins and annotations

## Background Jobs

When a task is created:
1. A Celery task is scheduled with 10-second delay
2. Email notification is logged to console
3. Notification record is saved in database

Monitor Celery logs to see email notifications being processed.

## Real-time Features

1. Connect to WebSocket endpoint
2. Create/update tasks via API
3. All users in the same company receive real-time updates
4. WebSocket messages include task data and update type

## Multi-Tenant Security

- Users only see tasks from their company
- API endpoints filter by company automatically
- WebSocket groups are company-specific
- Admin panel respects company boundaries

## Development Commands

```bash
# Run tests
python manage.py test

# Create sample data
python manage.py shell
# Then run sample data creation script

# Check task analytics
python manage.py task_analytics

# Reset database
python manage.py flush
```

## Production Considerations

1. **Environment Variables**: Use proper environment variables for secrets
2. **Database**: Configure PostgreSQL with proper connections and pooling
3. **Redis**: Set up Redis with persistence and proper memory limits
4. **Celery**: Use proper process management (supervisor/systemd)
5. **WebSockets**: Use proper ASGI server (daphne/uvicorn) with reverse proxy
6. **Security**: Enable HTTPS, configure CORS properly, use secure JWT settings

## API Documentation

The API follows REST conventions:
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- JWT tokens required for authenticated endpoints
- Responses include proper status codes
- Error messages are descriptive and consistent

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running on port 5432
2. **Redis Connection**: Ensure Redis is running on port 6379
3. **Celery Not Processing**: Check Redis connection and restart worker
4. **WebSocket Issues**: Ensure channels-redis is properly configured
5. **Migration Errors**: Delete migration files and recreate them

### Logs

- Django logs: Check console output
- Celery logs: Worker process shows task processing
- WebSocket logs: Connection/disconnection messages in console

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes following Django best practices
4. Add tests for new functionality
5. Submit pull request

## License

This project is for demonstration purposes.
