# Hududiy Agent Bot

Professional Telegram bot for group and channel automation with weather, prayer times, news, job listings, AI assistant, and moderation features.

## Features

### 🌤 Weather Module
- Automatic weather updates based on region
- OpenWeatherMap API integration
- AI-powered recommendations via Gemini
- Customizable posting schedule

### 🕌 Prayer Times Module
- Accurate prayer times via Aladhan API
- Region-based timings
- Daily automatic posting
- Redis caching for performance

### 📰 News Module
- RSS feed integration
- Topic-based filtering (local, sports, tech, economy, government, emergency)
- AI-powered summarization
- Duplicate detection

### 💼 Jobs Module
- Job listings from OLX, hh.uz, ishbor.uz
- Region-based filtering
- Automatic posting
- Duplicate prevention

### 🤖 AI Assistant
- Gemini AI integration
- Weather recommendations
- News summarization
- User Q&A support
- Rate limiting (10 requests/hour/user)

### 🛡 Moderation
- Banned words filtering
- Multiple penalty types (delete, warn, mute, ban)
- Auto-mute after 3 warnings
- Real-time message scanning

### 📢 Mandatory Subscription
- Require channel subscription before posting
- Multiple channels support
- Redis caching for performance
- Global and per-group channels

### 👥 Invite Threshold
- Require users to invite members before posting
- Configurable threshold (1-100)
- Spam prevention (no bots, no duplicates)
- Progress tracking

## Tech Stack

- **Backend**: Python 3.11+
- **Framework**: aiogram 3.x
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Scheduler**: APScheduler
- **AI**: Google Gemini API
- **Weather**: OpenWeatherMap API
- **Prayer**: Aladhan API
- **Deployment**: Docker + docker-compose

## Installation

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (from @BotFather)
- OpenWeatherMap API Key (optional)
- Gemini API Key (optional)

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd hudud-agent-bot
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your credentials:
```env
BOT_TOKEN=your_bot_token_here
SUPER_ADMIN_IDS=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_openweathermap_api_key
```

4. Start the services:
```bash
docker-compose up -d
```

5. Check logs:
```bash
docker-compose logs -f bot
docker-compose logs -f scheduler
```

6. Run database migrations (if needed):
```bash
docker-compose exec bot alembic upgrade head
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot API token | Yes |
| `SUPER_ADMIN_IDS` | Comma-separated super admin user IDs | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | No |
| `WEATHER_API_KEY` | OpenWeatherMap API key | No |
| `TIMEZONE` | Timezone (default: Asia/Tashkent) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

### Getting API Keys

**Telegram Bot Token:**
1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token

**OpenWeatherMap API:**
1. Sign up at https://openweathermap.org/api
2. Get free API key from dashboard

**Gemini API:**
1. Visit https://makersuite.google.com/app/apikey
2. Create API key

## Usage

### For Group Admins

1. Add bot to your group
2. Send `/admin` to open admin panel
3. Configure region, modules, and settings
4. Enable desired features

### For Users

- `/start` - Start bot
- `/help` - Show help
- `/weather` - Get weather
- `/prayer` - Get prayer times
- `/news` - Get news
- `/jobs` - Get job listings
- `/ai [question]` - Ask AI assistant

### For Super Admins

- `/superadmin` - Open super admin panel
- `/broadcast [message]` - Send message to all groups
- `/setgemini [key]` - Set Gemini API key
- `/setweather [key]` - Set Weather API key

## Project Structure

```
hudud-agent-bot/
├── app/
│   ├── bot/
│   │   ├── handlers/          # Message and callback handlers
│   │   ├── keyboards/         # Inline keyboards
│   │   ├── middlewares/       # Database and rate limit middlewares
│   │   └── filters/           # Admin filters
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   └── session.py         # Database session management
│   ├── scheduler/
│   │   ├── tasks.py           # Scheduled tasks
│   │   └── runner.py          # APScheduler runner
│   ├── services/              # Business logic services
│   │   ├── weather_service.py
│   │   ├── prayer_service.py
│   │   ├── news_service.py
│   │   ├── jobs_service.py
│   │   ├── gemini_service.py
│   │   ├── subscription_service.py
│   │   ├── invite_service.py
│   │   └── moderation_service.py
│   ├── utils/
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging setup
│   │   └── validators.py     # Input validation
│   └── main.py                # Bot entry point
├── alembic/                   # Database migrations
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Bot container
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Database Schema

The bot uses PostgreSQL with 21 tables:
- `users` - Telegram users
- `groups` - Telegram groups/channels
- `group_settings` - Per-group configuration
- `regions` - Geographic regions (Uzbekistan)
- `weather_schedules` - Weather posting schedules
- `prayer_schedules` - Prayer posting schedules
- `news_sources` - News RSS feeds
- `job_sources` - Job listing sources
- `sent_posts` - Posted content tracking
- `required_channels` - Mandatory subscription channels
- `user_subscriptions` - Subscription status cache
- `invite_tracking` - User invite tracking
- `banned_words` - Moderation word list
- `warnings` - User warnings
- `ai_logs` - AI request/response logs
- `admin_logs` - Admin action logs
- `global_settings` - Global configuration
- `scheduled_posts` - Scheduled advertisements

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start bot
python -m app.main

# Start scheduler (in another terminal)
python -m app.scheduler.runner
```

### Adding New Features

1. Create service in `app/services/`
2. Add database models in `app/database/models.py`
3. Create migration: `alembic revision --autogenerate -m "description"`
4. Add handlers in `app/bot/handlers/`
5. Register handlers in `app/main.py`

## Troubleshooting

### Bot not responding
- Check bot token in `.env`
- Verify bot is running: `docker-compose ps`
- Check logs: `docker-compose logs bot`

### Database connection error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Run migrations: `docker-compose exec bot alembic upgrade head`

### Scheduler not posting
- Check scheduler logs: `docker-compose logs scheduler`
- Verify schedules in database
- Ensure modules are enabled in group settings

### API errors
- Verify API keys in `.env` or via `/setgemini` and `/setweather`
- Check API rate limits
- Review error logs in super admin panel

## Security

- Never commit `.env` file
- Use strong database passwords
- Restrict super admin IDs
- Enable rate limiting
- Sanitize all user inputs
- Use HTTPS for all API calls

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Contact super admin via Telegram

## Credits

- Built with [aiogram 3.x](https://docs.aiogram.dev/)
- Weather data from [OpenWeatherMap](https://openweathermap.org/)
- Prayer times from [Aladhan API](https://aladhan.com/prayer-times-api)
- AI powered by [Google Gemini](https://ai.google.dev/)
