#!/bin/bash

echo "🚀 Setting up Multi-Tenant Task Manager..."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from accounts.models import User, Company
if not User.objects.filter(username='admin').exists():
    company = Company.objects.create(name='Admin Company', description='Default admin company')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', company=company)
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️ Admin user already exists')
"

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the server: source env/bin/activate && python manage.py runserver"
echo "2. Test the API: python test_api.py"
echo "3. Start Celery worker: celery -A task_manager worker --loglevel=info"
echo "4. Access admin panel: http://localhost:8000/admin/ (admin/admin123)"
echo "5. Test WebSocket: python test_websocket.py"
echo ""
echo "🔗 API Endpoints:"
echo "   - POST /api/auth/register/ - User registration"
echo "   - POST /api/auth/login/ - User login"
echo "   - GET /api/tasks/ - List tasks"
echo "   - POST /api/tasks/ - Create task"
echo "   - GET /api/external-tasks/ - Async external data"
echo "   - WebSocket: ws://localhost:8000/ws/tasks/"
