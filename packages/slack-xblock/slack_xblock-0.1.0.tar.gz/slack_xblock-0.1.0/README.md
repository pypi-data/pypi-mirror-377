# Slack XBlock for Open edX

An XBlock that integrates Slack channels directly into Open edX courses, enabling seamless communication between course content and discussions.

## Features

- 🚀 Easy integration with existing Slack workspaces
- 🎯 Auto-generated channel names based on course context
- 🎨 Responsive, modern UI design
- ⚙️ Studio-configurable settings
- 📊 Optional analytics and tracking
- 🔧 Flexible channel management

## Installation

### Development

```bash
git clone git@github.com:3N61N33R/slack-xblock.git
cd slack-xblock
pip install -e .
```

### Production

```bash
pip install slack-xblock
```

## Configuration

This XBlock requires configuration at both the environment level and within Open edX.

Environment Variables

First, you need to set up the following environment variables in your Open edX instance. You can add these to a .env file or your platform's configuration management system.

Here's an example:

```.env.example

Slack API Credentials

Your bot's xoxb token
SLACK_BOT_TOKEN=

Your app's signing secret
SLACK_SIGNING_SECRET=

Auto-channel creation settings
Set to 'True' to automatically create channels, 'False' to disable
AUTO_CREATE_CHANNELS=True

Prefix for auto-created channel names (e.g., 'course-')
CHANNEL_PREFIX=course-

Suffix for auto-created channel names (e.g., '-discussion')
CHANNEL_SUFFIX=-discussion

Default workspace settings
The main URL of your Slack workspace (e.g., "https://your-team.slack.com")
DEFAULT_WORKSPACE_URL="your-workspace-url"

The invite link for your workspace
WORKSPACE_INVITE_URL="workspace-invite"

```

- SLACK_BOT_TOKEN: Your Slack app's Bot User OAuth Token (starts with xoxb-).

- SLACK_SIGNING_SECRET: The signing secret from your Slack app's "Basic Information" page.

- AUTO_CREATE_CHANNELS: A boolean (True/False) to enable or disable automatic channel creation.

- CHANNEL_PREFIX & CHANNEL_SUFFIX: The prefix and suffix for automatically generated channel names. For example, course- and -discussion would create a channel like course-cs101-discussion.

- DEFAULT_WORKSPACE_URL: The base URL for your Slack workspace.

- WORKSPACE_INVITE_URL: The public invite link for users to join the workspace.

## Open edX Settings

1. Add to Open edX settings:

```python
INSTALLED_APPS += ['slack_xblock']
FEATURES['ENABLE_SLACK_XBLOCK'] = True
```

2. Configure in Studio:

- Add Slack component to course units
- Set workspace URL and channel settings
- Customize display options

## Usage

For detailed usage instructions, see the [Installation Guide](docs/installation.md).

## License

---
