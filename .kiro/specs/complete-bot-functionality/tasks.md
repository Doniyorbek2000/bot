# Tasks

## 1. Fix SQLite Migration Compatibility

Fix Alembic migration file to use SQLite-compatible syntax instead of PostgreSQL-specific syntax. Replace all `server_default=sa.text('now()')` with `server_default=sa.text('CURRENT_TIMESTAMP')` and update `postgresql.ARRAY` type to use JSON or TEXT for SQLite compatibility.

## 2. Verify Database Models and Session Management

Ensure database models are correctly configured for SQLite and connection pooling works properly. Review models, verify session management, and test database connections.

**Depends on:** 1

## 3. Implement and Test Weather Module

Complete weather service implementation and verify it works with OpenWeatherMap API. Implement caching, test command handlers, and verify AI recommendations integration.

**Depends on:** 2

## 4. Implement and Test Prayer Times Module

Complete prayer times service implementation and verify it works with Aladhan API. Implement caching, test command handlers, and verify region-based prayer times.

**Depends on:** 2

## 5. Implement and Test News Module

Complete news aggregation service with RSS feeds and AI summarization. Implement RSS parsing, duplicate detection, topic filtering, and test scheduled aggregation.

**Depends on:** 2

## 6. Implement and Test Jobs Module

Complete job listings aggregation service with region filtering. Implement job scraping for OLX, hh.uz, ishbor.uz, duplicate detection, and test scheduled aggregation.

**Depends on:** 2

## 7. Implement and Test AI Assistant Module

Complete Gemini AI integration with rate limiting. Implement rate limiting (10 requests/hour/user), test question answering, weather recommendations, news summarization, and verify logging.

**Depends on:** 2

## 8. Implement and Test Moderation Module

Complete content moderation with banned words and penalties. Implement banned word detection (case-insensitive), penalty application (delete, warn, mute, ban), auto-mute after 3 warnings, and test real-time processing.

**Depends on:** 2

## 9. Implement and Test Subscription Enforcement Module

Complete mandatory channel subscription enforcement. Implement subscription checking with caching, global and group-level channels, test enforcement before posting, and verify subscription prompts.

**Depends on:** 2

## 10. Implement and Test Invite Tracking Module

Complete invite tracking and threshold enforcement. Implement invite tracking on new member join, invite validation (no bots, no duplicates), threshold enforcement, and test counting.

**Depends on:** 2

## 11. Implement Admin Panel and Commands

Complete admin panel with all configuration options. Implement admin handlers, keyboards, test module toggles, region configuration, schedule management, banned words, required channels, invite threshold, and verify logging.

**Depends on:** 2

## 12. Implement Scheduler Service

Complete scheduler service for automated posts. Implement scheduled weather posts, prayer posts, news aggregation (every 30 minutes), job aggregation (every hour), cleanup task (daily at 3 AM), and test scheduler runner.

**Depends on:** 3, 4, 5, 6

## 13. Deploy to AlwaysData Server

Deploy the bot to AlwaysData server and verify it runs correctly. Push code to GitHub, SSH to server, pull code, run migrations, start bot service, verify commands, and check logs.

**Depends on:** 1, 2, 11

## 14. End-to-End Testing

Comprehensive testing of all bot features. Test all user commands, admin commands, moderation, subscription enforcement, invite tracking, scheduled posts, error handling, and verify 100% functionality.

**Depends on:** 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

## 15. Performance Optimization and Monitoring

Optimize performance and set up monitoring. Verify Redis caching, test rate limiting, monitor database performance, check memory usage, verify logs, and test under load.

**Depends on:** 14
