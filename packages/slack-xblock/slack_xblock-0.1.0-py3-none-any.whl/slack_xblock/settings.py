"""
Configuration settings for Slack XBlock
"""

from decouple import config

# Advanced Configuration Options
SLACK_XBLOCK_ADVANCED_CONFIG = {
    # Slack API integration (future enhancement)
    "SLACK_BOT_TOKEN": config("SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": config("SLACK_SIGNING_SECRET"),
    # Auto-channel creation settings
    "AUTO_CREATE_CHANNELS": config("AUTO_CREATE_CHANNELS", default=True, cast=bool),
    "CHANNEL_PREFIX": "course-",
    "CHANNEL_SUFFIX": "-discussion",
    # Default workspace settings
    "DEFAULT_WORKSPACE_URL": config("DEFAULT_WORKSPACE_URL"),
    "WORKSPACE_INVITE_URL": config("WORKSPACE_INVITE_URL"),
    # Integration features
    "ENABLE_MEMBER_COUNT": True,
    "ENABLE_ACTIVITY_PREVIEW": True,
    "ENABLE_DIRECT_MESSAGES": False,
    # Analytics and tracking
    "TRACK_CHANNEL_JOINS": True,
    "TRACK_MESSAGE_ACTIVITY": False,
}

# Course-level settings (these go in course advanced settings in Studio)
COURSE_SLACK_SETTINGS_TEMPLATE = {
    "slack_workspace_url": config("DEFAULT_WORKSPACE_URL"),
    "auto_create_channels": True,
    "channel_naming_pattern": "week-{week_number}",
    "enable_per_unit_channels": False,
    "moderator_roles": ["instructor", "staff"],
}

# Default XBlock settings
DEFAULT_XBLOCK_SETTINGS = {
    "display_name": "Course Discussion on Slack",
    "slack_workspace_url": "",
    "channel_name": "",
    "channel_description": "Course discussion channel",
    "auto_generate_channel": True,
    "show_member_count": True,
}
