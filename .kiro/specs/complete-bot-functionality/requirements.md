# Requirements Document

## Introduction

This document specifies the complete functional requirements for the Hududiy Agent Bot, a professional Telegram bot for group and channel automation. The bot provides weather updates, prayer times, news aggregation, job listings, AI assistance, content moderation, mandatory subscription enforcement, and invite threshold management for Uzbekistan-based Telegram communities.

## Glossary

- **Bot**: The Hududiy Agent Telegram bot system
- **User**: A Telegram user interacting with the Bot
- **Group**: A Telegram group or channel where the Bot is installed
- **Admin**: A Telegram group administrator with Bot configuration permissions
- **Super_Admin**: A Bot owner with global configuration permissions
- **Region**: A geographic area in Uzbekistan (viloyat and tuman combination)
- **Weather_Module**: The subsystem providing weather forecasts and updates
- **Prayer_Module**: The subsystem providing Islamic prayer times
- **News_Module**: The subsystem aggregating and posting news from RSS feeds
- **Jobs_Module**: The subsystem aggregating and posting job listings
- **AI_Module**: The subsystem providing Gemini AI-powered assistance
- **Moderation_Module**: The subsystem filtering banned words and applying penalties
- **Subscription_Module**: The subsystem enforcing mandatory channel subscriptions
- **Invite_Module**: The subsystem tracking user invites and enforcing thresholds
- **Scheduler**: The APScheduler-based task execution system
- **Database**: The PostgreSQL database storing all Bot data
- **Cache**: The Redis cache for performance optimization
- **API_Key**: Authentication credential for external services (Gemini, OpenWeatherMap)
- **Penalty**: A moderation action (delete, warn, mute, ban)
- **Warning**: A recorded violation count for a User in a Group
- **Threshold**: The minimum number of valid invites required before posting
- **Valid_Invite**: An invite of a real User (not a bot, not duplicate)

- **Duplicate_Post**: Content with identical hash already sent to the same Group
- **RSS_Feed**: A news or job source providing XML-formatted updates
- **Content_Hash**: A SHA-256 hash uniquely identifying post content
- **Rate_Limit**: Maximum number of requests allowed per time period
- **Schedule**: A configured time for automatic content posting
- **Migration**: A database schema change managed by Alembic

## Requirements

### Requirement 1: Weather Module - Data Retrieval

**User Story:** As a Group Admin, I want the Bot to fetch accurate weather data for my Region, so that Group members receive relevant local forecasts.

#### Acceptance Criteria

1. WHEN an Admin configures a Region for a Group, THE Weather_Module SHALL store the Region association in the Database
2. WHEN the Weather_Module fetches weather data, THE Weather_Module SHALL use the OpenWeatherMap API with the configured API_Key
3. WHEN the Weather_Module receives weather data, THE Weather_Module SHALL include temperature, conditions, humidity, and wind speed
4. IF the OpenWeatherMap API returns an error, THEN THE Weather_Module SHALL log the error and retry after 5 minutes
5. WHEN weather data is fetched, THE Weather_Module SHALL cache the data in Redis for 30 minutes
6. WHEN cached weather data exists and is less than 30 minutes old, THE Weather_Module SHALL return cached data without API call

### Requirement 2: Weather Module - AI Recommendations

**User Story:** As a Group member, I want to receive AI-powered weather recommendations, so that I can plan my activities appropriately.

#### Acceptance Criteria

1. WHEN the Weather_Module posts weather data, THE Weather_Module SHALL request recommendations from the AI_Module
2. WHEN the AI_Module generates weather recommendations, THE AI_Module SHALL use the Gemini API with current weather conditions as input
3. WHEN the AI_Module receives recommendations, THE Weather_Module SHALL include them in the weather post
4. IF the Gemini API returns an error, THEN THE Weather_Module SHALL post weather data without recommendations
5. WHEN AI recommendations are generated, THE Bot SHALL log the request and response in the ai_logs table


### Requirement 3: Weather Module - Scheduled Posting

**User Story:** As a Group Admin, I want to schedule automatic weather posts, so that members receive updates at consistent times.

#### Acceptance Criteria

1. WHEN an Admin creates a weather Schedule, THE Bot SHALL store the schedule_time in the weather_schedules table
2. WHEN the Scheduler executes at a scheduled_time, THE Scheduler SHALL trigger the Weather_Module for all Groups with matching Schedules
3. WHEN the Weather_Module posts to a Group, THE Bot SHALL send a formatted message with weather data and AI recommendations
4. WHEN a weather post is sent, THE Bot SHALL record the post in the sent_posts table with post_type "weather"
5. WHEN an Admin disables a Schedule, THE Scheduler SHALL not execute that Schedule until re-enabled
6. WHEN multiple Schedules exist for one Group, THE Weather_Module SHALL execute each Schedule independently

### Requirement 4: Prayer Times Module - Data Retrieval

**User Story:** As a Group Admin, I want the Bot to fetch accurate prayer times for my Region, so that Group members know when to pray.

#### Acceptance Criteria

1. WHEN an Admin configures a Region for a Group, THE Prayer_Module SHALL use the Region's latitude and longitude
2. WHEN the Prayer_Module fetches prayer times, THE Prayer_Module SHALL use the Aladhan API with the Region coordinates
3. WHEN the Prayer_Module receives prayer times, THE Prayer_Module SHALL include Fajr, Dhuhr, Asr, Maghrib, and Isha times
4. IF the Aladhan API returns an error, THEN THE Prayer_Module SHALL log the error and retry after 10 minutes
5. WHEN prayer times are fetched, THE Prayer_Module SHALL cache the data in Redis for 24 hours
6. WHEN cached prayer times exist for the current date, THE Prayer_Module SHALL return cached data without API call

### Requirement 5: Prayer Times Module - Scheduled Posting

**User Story:** As a Group Admin, I want to schedule automatic prayer time posts, so that members receive daily reminders.

#### Acceptance Criteria

1. WHEN an Admin creates a prayer Schedule, THE Bot SHALL store the schedule_time in the prayer_schedules table
2. WHEN the Scheduler executes at a scheduled_time, THE Scheduler SHALL trigger the Prayer_Module for all Groups with matching Schedules
3. WHEN the Prayer_Module posts to a Group, THE Bot SHALL send a formatted message with all five prayer times
4. WHEN a prayer post is sent, THE Bot SHALL record the post in the sent_posts table with post_type "prayer"
5. WHEN an Admin disables a Schedule, THE Scheduler SHALL not execute that Schedule until re-enabled


### Requirement 6: News Module - RSS Feed Aggregation

**User Story:** As a Group Admin, I want the Bot to aggregate news from RSS feeds, so that members stay informed about relevant topics.

#### Acceptance Criteria

1. WHEN a Super_Admin adds a news source, THE Bot SHALL store the RSS_Feed URL in the news_sources table
2. WHEN the News_Module fetches news, THE News_Module SHALL parse all active RSS_Feeds from the news_sources table
3. WHEN the News_Module parses an RSS_Feed, THE News_Module SHALL extract title, description, link, and publication date
4. IF an RSS_Feed returns an error, THEN THE News_Module SHALL log the error and continue with remaining feeds
5. WHEN the News_Module processes a news item, THE News_Module SHALL compute a Content_Hash from title and link
6. WHEN a Content_Hash matches an existing entry in sent_posts for the same Group, THE News_Module SHALL skip that item as a Duplicate_Post

### Requirement 7: News Module - Topic Filtering

**User Story:** As a Group Admin, I want to filter news by topics, so that members only see relevant content.

#### Acceptance Criteria

1. WHEN an Admin configures news topics for a Group, THE Bot SHALL store the topics in the group_settings.news_topics array
2. WHEN the News_Module posts to a Group, THE News_Module SHALL only include news items matching the configured topics
3. WHEN no topics are configured for a Group, THE News_Module SHALL post all news items regardless of topic
4. THE Bot SHALL support the following topics: local, sports, tech, economy, government, emergency
5. WHEN a news source has a topic assignment, THE News_Module SHALL use that topic for filtering

### Requirement 8: News Module - AI Summarization

**User Story:** As a Group member, I want to receive AI-generated news summaries, so that I can quickly understand key points.

#### Acceptance Criteria

1. WHEN the News_Module posts a news item, THE News_Module SHALL request a summary from the AI_Module
2. WHEN the AI_Module generates a summary, THE AI_Module SHALL use the Gemini API with the news title and description as input
3. WHEN the AI_Module receives a summary, THE News_Module SHALL include it in the news post
4. IF the Gemini API returns an error, THEN THE News_Module SHALL post the original news description without summary
5. WHEN AI summaries are generated, THE Bot SHALL log the request and response in the ai_logs table


### Requirement 9: Jobs Module - Job Listing Aggregation

**User Story:** As a Group Admin, I want the Bot to aggregate job listings from multiple sources, so that members can find employment opportunities.

#### Acceptance Criteria

1. WHEN a Super_Admin adds a job source, THE Bot SHALL store the source URL in the job_sources table
2. WHEN the Jobs_Module fetches jobs, THE Jobs_Module SHALL parse all active sources from the job_sources table
3. WHEN the Jobs_Module parses a job source, THE Jobs_Module SHALL extract title, company, location, salary, and link
4. IF a job source returns an error, THEN THE Jobs_Module SHALL log the error and continue with remaining sources
5. WHEN the Jobs_Module processes a job listing, THE Jobs_Module SHALL compute a Content_Hash from title and link
6. WHEN a Content_Hash matches an existing entry in sent_posts for the same Group, THE Jobs_Module SHALL skip that listing as a Duplicate_Post
7. THE Bot SHALL support job sources from OLX, hh.uz, and ishbor.uz

### Requirement 10: Jobs Module - Region-Based Filtering

**User Story:** As a Group Admin, I want to filter job listings by Region, so that members see locally relevant opportunities.

#### Acceptance Criteria

1. WHEN a Group has a configured Region, THE Jobs_Module SHALL only post job listings matching that Region
2. WHEN the Jobs_Module filters by Region, THE Jobs_Module SHALL match the job location against the Region's viloyat and tuman
3. WHEN no Region is configured for a Group, THE Jobs_Module SHALL post all job listings regardless of location
4. WHEN a job listing has no location data, THE Jobs_Module SHALL skip that listing

### Requirement 11: AI Module - User Question Answering

**User Story:** As a Group member, I want to ask the AI assistant questions, so that I can get helpful information.

#### Acceptance Criteria

1. WHEN a User sends a message starting with "/ai", THE Bot SHALL extract the question text after the command
2. WHEN the AI_Module receives a question, THE AI_Module SHALL send the question to the Gemini API
3. WHEN the Gemini API returns a response, THE Bot SHALL send the response to the User
4. IF the Gemini API returns an error, THEN THE Bot SHALL send an error message to the User
5. WHEN an AI request is processed, THE Bot SHALL log the request and response in the ai_logs table with user_id and group_id


### Requirement 12: AI Module - Rate Limiting

**User Story:** As a Super_Admin, I want to limit AI requests per User, so that API costs remain controlled.

#### Acceptance Criteria

1. WHEN a User sends an AI request, THE Bot SHALL check the Cache for the User's request count in the current hour
2. WHEN the User's request count is less than 10, THE Bot SHALL process the request and increment the count
3. WHEN the User's request count reaches 10, THE Bot SHALL reject further requests until the next hour
4. WHEN a request is rejected due to Rate_Limit, THE Bot SHALL send a message informing the User of the limit
5. WHEN a new hour begins, THE Bot SHALL reset the request count for all Users

### Requirement 13: Moderation Module - Banned Word Detection

**User Story:** As a Group Admin, I want to filter banned words from messages, so that the Group maintains appropriate content.

#### Acceptance Criteria

1. WHEN an Admin adds a banned word, THE Bot SHALL store the word in the banned_words table for that Group
2. WHEN a User sends a message in a Group, THE Moderation_Module SHALL check the message text against all active banned words for that Group
3. WHEN a message contains a banned word, THE Moderation_Module SHALL apply the configured Penalty
4. WHEN checking for banned words, THE Moderation_Module SHALL perform case-insensitive matching
5. WHEN an Admin removes a banned word, THE Moderation_Module SHALL no longer check for that word

### Requirement 14: Moderation Module - Penalty Application

**User Story:** As a Group Admin, I want to configure penalties for banned word violations, so that I can enforce Group rules appropriately.

#### Acceptance Criteria

1. WHEN an Admin configures a Penalty type, THE Bot SHALL store the ban_penalty in the group_settings table
2. WHEN the Penalty is "delete", THE Bot SHALL delete the violating message
3. WHEN the Penalty is "warn", THE Bot SHALL delete the message and record a Warning in the warnings table
4. WHEN the Penalty is "mute", THE Bot SHALL delete the message and restrict the User from sending messages for 24 hours
5. WHEN the Penalty is "ban", THE Bot SHALL delete the message and remove the User from the Group
6. THE Bot SHALL support the following Penalty types: delete, warn, mute, ban


### Requirement 15: Moderation Module - Auto-Mute After Warnings

**User Story:** As a Group Admin, I want Users to be automatically muted after 3 warnings, so that repeat offenders are restricted.

#### Acceptance Criteria

1. WHEN a User receives a Warning, THE Bot SHALL count all Warnings for that User in that Group
2. WHEN the Warning count reaches 3, THE Bot SHALL automatically mute the User for 24 hours
3. WHEN a User is auto-muted, THE Bot SHALL send a notification message to the Group
4. WHEN a User is auto-muted, THE Bot SHALL log the action in the admin_logs table
5. WHEN an Admin manually clears Warnings, THE auto-mute count SHALL reset to zero

### Requirement 16: Subscription Module - Channel Subscription Enforcement

**User Story:** As a Group Admin, I want to require channel subscriptions before Users can post, so that I can grow my channels.

#### Acceptance Criteria

1. WHEN an Admin adds a required channel, THE Bot SHALL store the channel_id in the required_channels table
2. WHEN a User sends a message in a Group with subscription enforcement enabled, THE Subscription_Module SHALL check if the User is subscribed to all required channels
3. WHEN the User is not subscribed to all required channels, THE Bot SHALL delete the message and send a subscription prompt with channel links
4. WHEN the User is subscribed to all required channels, THE Bot SHALL allow the message
5. WHEN the Subscription_Module checks subscription status, THE Bot SHALL cache the result in Redis for 5 minutes
6. WHEN cached subscription status exists and is less than 5 minutes old, THE Subscription_Module SHALL use cached data without API call

### Requirement 17: Subscription Module - Global and Group-Level Channels

**User Story:** As a Super_Admin, I want to configure global required channels that apply to all Groups, so that I can promote important channels universally.

#### Acceptance Criteria

1. WHEN a Super_Admin adds a global required channel, THE Bot SHALL store the channel with is_global set to true
2. WHEN the Subscription_Module checks subscriptions, THE Subscription_Module SHALL include both global channels and Group-specific channels
3. WHEN an Admin views required channels, THE Bot SHALL display global channels separately from Group-specific channels
4. WHEN a Super_Admin removes a global channel, THE Subscription_Module SHALL no longer enforce that channel for any Group


### Requirement 18: Invite Module - Invite Tracking

**User Story:** As a Group Admin, I want to track User invites, so that I can enforce invite requirements before posting.

#### Acceptance Criteria

1. WHEN a new User joins a Group, THE Bot SHALL check if the User was invited by another User
2. WHEN the Bot detects an invite, THE Bot SHALL record the inviter_id, invited_id, and group_id in the invite_tracking table
3. WHEN the invited User is a bot, THE Bot SHALL mark the invite as invalid (is_valid = false)
4. WHEN the invited User was already invited by the same inviter in the same Group, THE Bot SHALL mark the new invite as invalid
5. WHEN an Admin queries invite counts, THE Bot SHALL count only Valid_Invites (is_valid = true)

### Requirement 19: Invite Module - Threshold Enforcement

**User Story:** As a Group Admin, I want to require Users to invite members before posting, so that the Group grows organically.

#### Acceptance Criteria

1. WHEN an Admin configures an invite Threshold, THE Bot SHALL store the invite_threshold in the group_settings table
2. WHEN a User sends a message in a Group with invite enforcement enabled, THE Invite_Module SHALL count the User's Valid_Invites
3. WHEN the Valid_Invite count is less than the Threshold, THE Bot SHALL delete the message and send a prompt explaining the requirement
4. WHEN the Valid_Invite count meets or exceeds the Threshold, THE Bot SHALL allow the message
5. WHEN an Admin sets the Threshold, THE Bot SHALL validate that the value is between 1 and 100
6. IF the Threshold value is outside the valid range, THEN THE Bot SHALL reject the configuration and send an error message

### Requirement 20: Database - Schema Management

**User Story:** As a developer, I want database schema changes to be managed automatically, so that deployments are reliable.

#### Acceptance Criteria

1. WHEN the Bot starts, THE Bot SHALL run Alembic migrations to upgrade the Database to the latest schema
2. WHEN a Migration is applied, THE Bot SHALL log the migration version and status
3. IF a Migration fails, THEN THE Bot SHALL log the error and exit with a non-zero status code
4. WHEN the Database schema is current, THE Bot SHALL skip migration execution and continue startup
5. THE Bot SHALL support all 21 tables defined in the models: users, groups, group_settings, regions, weather_schedules, prayer_schedules, news_sources, job_sources, sent_posts, required_channels, user_subscriptions, invite_tracking, banned_words, warnings, ai_logs, admin_logs, global_settings, scheduled_posts


### Requirement 21: Database - Connection Management

**User Story:** As a developer, I want database connections to be managed efficiently, so that the Bot remains stable under load.

#### Acceptance Criteria

1. WHEN the Bot starts, THE Bot SHALL verify Database connectivity before accepting requests
2. IF the Database connection fails at startup, THEN THE Bot SHALL log the error and exit with a non-zero status code
3. WHEN the Bot shuts down, THE Bot SHALL close all Database connections gracefully
4. WHEN a Database query fails, THE Bot SHALL log the error and retry up to 3 times with exponential backoff
5. IF all retry attempts fail, THEN THE Bot SHALL return an error to the User

### Requirement 22: Cache - Redis Integration

**User Story:** As a developer, I want to use Redis for caching, so that the Bot responds quickly and reduces API calls.

#### Acceptance Criteria

1. WHEN the Bot starts, THE Bot SHALL verify Cache connectivity
2. IF the Cache connection fails at startup, THEN THE Bot SHALL log a warning and continue without caching
3. WHEN the Bot caches data, THE Bot SHALL set an appropriate TTL (time-to-live) based on data type
4. WHEN the Bot retrieves cached data, THE Bot SHALL check if the data has expired
5. WHEN cached data has expired, THE Bot SHALL fetch fresh data and update the Cache
6. WHEN the Bot shuts down, THE Bot SHALL close all Cache connections gracefully

### Requirement 23: Configuration - Environment Variables

**User Story:** As a developer, I want to configure the Bot via environment variables, so that deployments are flexible and secure.

#### Acceptance Criteria

1. WHEN the Bot starts, THE Bot SHALL load configuration from environment variables
2. THE Bot SHALL require the following variables: BOT_TOKEN, SUPER_ADMIN_IDS, DATABASE_URL, REDIS_URL
3. THE Bot SHALL support the following optional variables: GEMINI_API_KEY, WEATHER_API_KEY, TIMEZONE, LOG_LEVEL
4. IF a required variable is missing, THEN THE Bot SHALL log an error and exit with a non-zero status code
5. WHEN an optional variable is missing, THE Bot SHALL use a default value and log a warning


### Requirement 24: Configuration - API Key Management

**User Story:** As a Super_Admin, I want to configure API keys at runtime, so that I can update credentials without redeploying.

#### Acceptance Criteria

1. WHEN a Super_Admin sends the "/setgemini" command with an API_Key, THE Bot SHALL store the key in the global_settings table
2. WHEN a Super_Admin sends the "/setweather" command with an API_Key, THE Bot SHALL store the key in the global_settings table
3. WHEN the AI_Module needs a Gemini API_Key, THE AI_Module SHALL first check global_settings, then fall back to environment variables
4. WHEN the Weather_Module needs an OpenWeatherMap API_Key, THE Weather_Module SHALL first check global_settings, then fall back to environment variables
5. WHEN an API_Key is updated, THE Bot SHALL use the new key for all subsequent requests

### Requirement 25: Logging - Structured Logging

**User Story:** As a developer, I want structured logs, so that I can debug issues and monitor Bot health.

#### Acceptance Criteria

1. WHEN the Bot logs a message, THE Bot SHALL include timestamp, log level, module name, and message text
2. THE Bot SHALL support the following log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
3. WHEN the LOG_LEVEL environment variable is set, THE Bot SHALL only log messages at that level or higher
4. WHEN an error occurs, THE Bot SHALL log the full stack trace at ERROR level
5. WHEN the Bot starts or stops, THE Bot SHALL log lifecycle events at INFO level

### Requirement 26: Logging - Admin Action Logging

**User Story:** As a Super_Admin, I want to audit Admin actions, so that I can track configuration changes and moderation decisions.

#### Acceptance Criteria

1. WHEN an Admin changes Group settings, THE Bot SHALL record the action in the admin_logs table
2. WHEN an Admin adds or removes a banned word, THE Bot SHALL record the action in the admin_logs table
3. WHEN an Admin adds or removes a required channel, THE Bot SHALL record the action in the admin_logs table
4. WHEN the Bot logs an Admin action, THE Bot SHALL include admin_id, group_id, action type, details, and timestamp
5. WHEN a Super_Admin views logs, THE Bot SHALL display logs filtered by level (info, warning, error)


### Requirement 27: Error Handling - Graceful Degradation

**User Story:** As a User, I want the Bot to continue functioning when external services fail, so that I can still use available features.

#### Acceptance Criteria

1. IF the Gemini API is unavailable, THEN THE Bot SHALL post weather and news without AI enhancements
2. IF the OpenWeatherMap API is unavailable, THEN THE Bot SHALL skip weather posts and log the error
3. IF the Aladhan API is unavailable, THEN THE Bot SHALL skip prayer posts and log the error
4. IF an RSS_Feed is unavailable, THEN THE Bot SHALL continue processing remaining feeds
5. IF the Cache is unavailable, THEN THE Bot SHALL fetch data directly from APIs without caching

### Requirement 28: Error Handling - User-Facing Error Messages

**User Story:** As a User, I want clear error messages when something goes wrong, so that I understand what happened.

#### Acceptance Criteria

1. WHEN an API request fails, THE Bot SHALL send a user-friendly error message without exposing technical details
2. WHEN a User command has invalid parameters, THE Bot SHALL send a message explaining the correct usage
3. WHEN a User lacks permissions for a command, THE Bot SHALL send a message explaining the permission requirement
4. WHEN the Bot encounters an unexpected error, THE Bot SHALL send a generic error message and log the full error details
5. WHEN the Bot sends an error message, THE Bot SHALL include relevant context (e.g., command name, feature name)

### Requirement 29: Deployment - Docker Container

**User Story:** As a developer, I want to deploy the Bot using Docker, so that the environment is consistent and reproducible.

#### Acceptance Criteria

1. WHEN the Bot is built, THE Dockerfile SHALL create a container with Python 3.11 or higher
2. WHEN the container starts, THE Bot SHALL install all dependencies from requirements.txt
3. WHEN the container runs, THE Bot SHALL execute the main.py entry point
4. WHEN the container stops, THE Bot SHALL shut down gracefully and close all connections
5. THE Docker image SHALL include the Bot code, Alembic migrations, and configuration files


### Requirement 30: Deployment - Docker Compose Orchestration

**User Story:** As a developer, I want to deploy all services using Docker Compose, so that the Bot, Database, and Cache run together.

#### Acceptance Criteria

1. WHEN docker-compose is started, THE system SHALL start three services: bot, postgres, redis
2. WHEN the postgres service starts, THE Database SHALL be initialized with the configured credentials
3. WHEN the redis service starts, THE Cache SHALL be available on port 6379
4. WHEN the bot service starts, THE Bot SHALL wait for postgres and redis to be ready before connecting
5. WHEN docker-compose is stopped, THE system SHALL stop all services gracefully and preserve Database data

### Requirement 31: Scheduler - Task Execution

**User Story:** As a developer, I want scheduled tasks to run reliably, so that automated posts are delivered on time.

#### Acceptance Criteria

1. WHEN the Scheduler starts, THE Scheduler SHALL load all active Schedules from the Database
2. WHEN a Schedule's time is reached, THE Scheduler SHALL execute the corresponding task (weather, prayer, news, jobs)
3. WHEN a task execution fails, THE Scheduler SHALL log the error and continue with the next scheduled task
4. WHEN a task execution succeeds, THE Scheduler SHALL log the success and update the last_run timestamp
5. WHEN the Scheduler is stopped, THE Scheduler SHALL complete any running tasks before shutting down

### Requirement 32: Scheduler - Separate Process

**User Story:** As a developer, I want the Scheduler to run as a separate process, so that scheduled tasks don't block Bot message handling.

#### Acceptance Criteria

1. WHEN the system is deployed, THE Scheduler SHALL run in a separate container or process from the Bot
2. WHEN the Scheduler executes a task, THE Scheduler SHALL use the same Database and Cache connections as the Bot
3. WHEN the Scheduler posts a message, THE Scheduler SHALL use the Bot's Telegram API token
4. WHEN the Bot is restarted, THE Scheduler SHALL continue running without interruption
5. WHEN the Scheduler is restarted, THE Bot SHALL continue handling messages without interruption


### Requirement 33: Security - Input Validation

**User Story:** As a developer, I want all User inputs to be validated, so that the Bot is protected from malicious data.

#### Acceptance Criteria

1. WHEN a User sends a command with parameters, THE Bot SHALL validate parameter types and ranges before processing
2. WHEN a User provides a URL, THE Bot SHALL validate that the URL is well-formed and uses HTTPS
3. WHEN a User provides a numeric value, THE Bot SHALL validate that the value is within acceptable bounds
4. IF validation fails, THEN THE Bot SHALL reject the input and send an error message to the User
5. WHEN the Bot stores User input in the Database, THE Bot SHALL sanitize the input to prevent SQL injection

### Requirement 34: Security - Permission Checks

**User Story:** As a Group Admin, I want only authorized Users to access Admin commands, so that Group settings remain secure.

#### Acceptance Criteria

1. WHEN a User sends an Admin command, THE Bot SHALL verify that the User is a Group administrator
2. WHEN a User sends a Super_Admin command, THE Bot SHALL verify that the User's telegram_id is in SUPER_ADMIN_IDS
3. IF a User lacks the required permissions, THEN THE Bot SHALL reject the command and send a permission error message
4. WHEN the Bot checks permissions, THE Bot SHALL use the Telegram API to verify current administrator status
5. WHEN the Bot caches permission status, THE Bot SHALL cache for no more than 5 minutes

### Requirement 35: Performance - Message Rate Limiting

**User Story:** As a developer, I want to rate-limit User messages, so that the Bot is protected from spam and abuse.

#### Acceptance Criteria

1. WHEN a User sends a message, THE Bot SHALL check the Cache for the User's message count in the current minute
2. WHEN the User's message count exceeds 5 messages per minute, THE Bot SHALL ignore further messages until the next minute
3. WHEN a message is rate-limited, THE Bot SHALL not send an error message to avoid further spam
4. WHEN a new minute begins, THE Bot SHALL reset the message count for all Users
5. WHEN rate-limiting is applied, THE Bot SHALL log the event for monitoring


### Requirement 36: Performance - Database Query Optimization

**User Story:** As a developer, I want database queries to be optimized, so that the Bot responds quickly under load.

#### Acceptance Criteria

1. WHEN the Bot queries the Database, THE Bot SHALL use indexes on frequently queried columns (telegram_id, group_id, user_id)
2. WHEN the Bot fetches related data, THE Bot SHALL use eager loading to minimize query count
3. WHEN the Bot performs bulk operations, THE Bot SHALL use batch inserts and updates
4. WHEN the Bot queries large tables, THE Bot SHALL use pagination to limit result set size
5. WHEN the Bot executes a slow query (>100ms), THE Bot SHALL log the query and execution time for optimization

### Requirement 37: Monitoring - Health Checks

**User Story:** As a developer, I want health check endpoints, so that I can monitor Bot availability.

#### Acceptance Criteria

1. THE Bot SHALL provide a health check endpoint that returns HTTP 200 when healthy
2. WHEN the health check is called, THE Bot SHALL verify Database connectivity
3. WHEN the health check is called, THE Bot SHALL verify Cache connectivity
4. IF the Database or Cache is unavailable, THEN THE health check SHALL return HTTP 503
5. WHEN the health check succeeds, THE response SHALL include uptime and version information

### Requirement 38: User Commands - Help Command

**User Story:** As a User, I want to see available commands, so that I know how to use the Bot.

#### Acceptance Criteria

1. WHEN a User sends "/help", THE Bot SHALL send a message listing all available User commands
2. WHEN a User sends "/help" in a private chat, THE Bot SHALL include both User and Admin commands
3. WHEN a User sends "/help" in a Group, THE Bot SHALL only include User commands
4. WHEN the Bot sends help text, THE Bot SHALL format commands with descriptions
5. WHEN the Bot sends help text, THE Bot SHALL include examples for complex commands


### Requirement 39: User Commands - Manual Content Requests

**User Story:** As a User, I want to manually request weather, prayer times, news, and jobs, so that I can get information on demand.

#### Acceptance Criteria

1. WHEN a User sends "/weather", THE Bot SHALL fetch and send current weather for the Group's Region
2. WHEN a User sends "/prayer", THE Bot SHALL fetch and send today's prayer times for the Group's Region
3. WHEN a User sends "/news", THE Bot SHALL fetch and send the latest news items matching the Group's topics
4. WHEN a User sends "/jobs", THE Bot SHALL fetch and send the latest job listings for the Group's Region
5. IF a Group has no configured Region, THEN THE Bot SHALL send an error message asking the Admin to configure a Region

### Requirement 40: Admin Commands - Configuration Panel

**User Story:** As a Group Admin, I want an interactive configuration panel, so that I can easily manage Bot settings.

#### Acceptance Criteria

1. WHEN an Admin sends "/admin", THE Bot SHALL send an inline keyboard with configuration options
2. WHEN an Admin selects a module (weather, prayer, news, jobs, AI, moderation, subscription, invite), THE Bot SHALL show module-specific settings
3. WHEN an Admin enables or disables a module, THE Bot SHALL update the group_settings table
4. WHEN an Admin changes a setting, THE Bot SHALL send a confirmation message
5. WHEN an Admin views current settings, THE Bot SHALL display all configured values

### Requirement 41: Admin Commands - Region Configuration

**User Story:** As a Group Admin, I want to configure my Group's Region, so that location-based features work correctly.

#### Acceptance Criteria

1. WHEN an Admin selects Region configuration, THE Bot SHALL display a list of available Regions (viloyat and tuman)
2. WHEN an Admin selects a Region, THE Bot SHALL update the group.region_id in the Database
3. WHEN a Region is configured, THE Bot SHALL send a confirmation message with the selected Region
4. WHEN an Admin views the current Region, THE Bot SHALL display the viloyat and tuman names
5. THE Bot SHALL support all Regions in Uzbekistan (14 viloyats with their tumans)


### Requirement 42: Admin Commands - Schedule Management

**User Story:** As a Group Admin, I want to manage posting schedules, so that automated content is delivered at preferred times.

#### Acceptance Criteria

1. WHEN an Admin configures a weather Schedule, THE Bot SHALL store the schedule_time in the weather_schedules table
2. WHEN an Admin configures a prayer Schedule, THE Bot SHALL store the schedule_time in the prayer_schedules table
3. WHEN an Admin adds a Schedule, THE Bot SHALL validate that the time is in HH:MM format
4. WHEN an Admin removes a Schedule, THE Bot SHALL delete the corresponding entry from the Database
5. WHEN an Admin views Schedules, THE Bot SHALL display all configured Schedules with their times and status

### Requirement 43: Super Admin Commands - Global Configuration

**User Story:** As a Super_Admin, I want to manage global settings, so that I can control Bot behavior across all Groups.

#### Acceptance Criteria

1. WHEN a Super_Admin sends "/superadmin", THE Bot SHALL send an inline keyboard with global configuration options
2. WHEN a Super_Admin adds a global required channel, THE Bot SHALL store the channel with is_global set to true
3. WHEN a Super_Admin adds a news source, THE Bot SHALL store the RSS_Feed URL in the news_sources table
4. WHEN a Super_Admin adds a job source, THE Bot SHALL store the source URL in the job_sources table
5. WHEN a Super_Admin views global settings, THE Bot SHALL display all global channels, news sources, and job sources

### Requirement 44: Super Admin Commands - Broadcast

**User Story:** As a Super_Admin, I want to broadcast messages to all Groups, so that I can make important announcements.

#### Acceptance Criteria

1. WHEN a Super_Admin sends "/broadcast [message]", THE Bot SHALL send the message to all active Groups
2. WHEN the Bot broadcasts a message, THE Bot SHALL send to Groups sequentially to avoid rate limits
3. WHEN a broadcast message fails for a Group, THE Bot SHALL log the error and continue with remaining Groups
4. WHEN the broadcast completes, THE Bot SHALL send a summary to the Super_Admin with success and failure counts
5. WHEN the Bot sends a broadcast message, THE Bot SHALL include a footer indicating it is an official announcement


### Requirement 45: Group Events - New Member Welcome

**User Story:** As a Group Admin, I want the Bot to welcome new members, so that they feel included and understand Group rules.

#### Acceptance Criteria

1. WHEN a new User joins a Group, THE Bot SHALL send a welcome message
2. WHEN the Bot sends a welcome message, THE Bot SHALL include the User's name
3. WHEN subscription enforcement is enabled, THE welcome message SHALL include required channel links
4. WHEN invite enforcement is enabled, THE welcome message SHALL explain the invite requirement
5. WHEN the Bot sends a welcome message, THE Bot SHALL delete the message after 60 seconds to avoid clutter

### Requirement 46: Group Events - Bot Added to Group

**User Story:** As a Group Admin, I want the Bot to initialize settings when added to a Group, so that I can start using features immediately.

#### Acceptance Criteria

1. WHEN the Bot is added to a Group, THE Bot SHALL create an entry in the groups table
2. WHEN the Bot is added to a Group, THE Bot SHALL create default settings in the group_settings table
3. WHEN the Bot creates default settings, THE Bot SHALL disable all modules by default
4. WHEN the Bot is added to a Group, THE Bot SHALL send a welcome message explaining how to configure the Bot
5. WHEN the Bot is added to a Group, THE Bot SHALL log the event in the admin_logs table

### Requirement 47: Internationalization - Language Support

**User Story:** As a Group Admin, I want to configure the Bot's language, so that messages are in my preferred language.

#### Acceptance Criteria

1. WHEN an Admin configures a language, THE Bot SHALL store the language code in the group_settings table
2. WHEN the Bot sends a message to a Group, THE Bot SHALL use the configured language for that Group
3. THE Bot SHALL support the following languages: Uzbek (uz), Russian (ru), English (en)
4. WHEN no language is configured, THE Bot SHALL default to Uzbek (uz)
5. WHEN the Bot sends a message, THE Bot SHALL load translations from language files


### Requirement 48: Data Retention - Cleanup Tasks

**User Story:** As a developer, I want old data to be cleaned up automatically, so that the Database doesn't grow indefinitely.

#### Acceptance Criteria

1. WHEN the Scheduler runs daily cleanup, THE Bot SHALL delete sent_posts entries older than 30 days
2. WHEN the Scheduler runs daily cleanup, THE Bot SHALL delete ai_logs entries older than 90 days
3. WHEN the Scheduler runs daily cleanup, THE Bot SHALL delete admin_logs entries older than 180 days
4. WHEN the Scheduler runs daily cleanup, THE Bot SHALL delete user_subscriptions entries older than 7 days
5. WHEN cleanup completes, THE Bot SHALL log the number of deleted records

### Requirement 49: Reliability - Automatic Retry Logic

**User Story:** As a developer, I want failed operations to be retried automatically, so that transient errors don't cause permanent failures.

#### Acceptance Criteria

1. WHEN an API request fails with a network error, THE Bot SHALL retry up to 3 times with exponential backoff
2. WHEN a Database query fails with a connection error, THE Bot SHALL retry up to 3 times with exponential backoff
3. WHEN all retry attempts fail, THE Bot SHALL log the error and return a failure status
4. WHEN a retry succeeds, THE Bot SHALL log the success and continue normal operation
5. WHEN the Bot retries an operation, THE Bot SHALL wait 1 second, then 2 seconds, then 4 seconds between attempts

### Requirement 50: Testing - Integration Test Support

**User Story:** As a developer, I want to run integration tests, so that I can verify Bot functionality before deployment.

#### Acceptance Criteria

1. THE Bot SHALL support a test mode that uses a separate test Database
2. WHEN running in test mode, THE Bot SHALL not send messages to real Telegram chats
3. WHEN running in test mode, THE Bot SHALL mock external API calls (Gemini, OpenWeatherMap, Aladhan)
4. WHEN tests complete, THE Bot SHALL clean up all test data from the test Database
5. THE Bot SHALL provide test fixtures for common scenarios (User joins, Admin configures, message sent)

---

## Summary

This requirements document defines 50 functional requirements across 8 major modules for the Hududiy Agent Bot. All requirements follow EARS patterns and INCOSE quality rules to ensure clarity, testability, and completeness. The requirements cover core functionality, error handling, security, performance, deployment, and testing to deliver a production-ready Telegram bot for Uzbekistan-based communities.
