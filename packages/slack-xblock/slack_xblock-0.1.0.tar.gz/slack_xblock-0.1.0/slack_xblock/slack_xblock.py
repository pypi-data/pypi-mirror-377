"""TO-DO: Write a description of what this XBlock is."""

import logging
import pkg_resources


from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String, Boolean, Integer
from xblock.utils.studio_editable import StudioEditableXBlockMixin

from django.template import Template, Context
from .settings import SLACK_XBLOCK_ADVANCED_CONFIG, DEFAULT_XBLOCK_SETTINGS
from decouple import config

log = logging.getLogger(__name__)


class SlackXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An XBlock that displays a button/link to a Slack channel.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    # Fields for configuration in Studio
    display_name = String(
        default="Slack Channel Link",
        scope=Scope.settings,
        help="The name shown in Studio for this XBlock.",
    )

    slack_workspace_url = String(
        display_name="Slack Workspace URL",
        help="Base URL of your Slack workspace (e.g., https://yourworkspace.slack.com)",
        default="",
        scope=Scope.settings,
    )

    channel_name = String(
        display_name="Channel Name",
        help="Slack channel name (without #). Leave empty to auto-generate from course info.",
        default="",
        scope=Scope.settings,
    )

    channel_description = String(
        display_name="Channel Description",
        help="Description for the Slack channel",
        default="Course discussion channel",
        scope=Scope.settings,
        multiline_editor=True,
    )

    auto_generate_channel = Boolean(
        display_name="Auto-generate Channel Name",
        help="Automatically create channel name from course information",
        default=True,
        scope=Scope.settings,
    )

    show_member_count = Boolean(
        display_name="Show Member Count",
        help="Display the number of members in the channel",
        default=True,
        scope=Scope.settings,
    )

    # Studio editable fields
    editable_fields = (
        "display_name",
        "slack_workspace_url",
        "channel_name",
        "channel_description",
        "auto_generate_channel",
        "show_member_count",
    )

    slack_channel_url = String(
        default="https://coding-campi.slack.com/archives/C08U4LP50LT",  # Default placeholder
        scope=Scope.settings,
        help="The full URL to the Slack channel (e.g., https://yourworkspace.slack.com/archives/C1234567890)",
    )

    button_text = String(
        default="Join Our Slack Channel",
        scope=Scope.settings,
        help="Text to display on the button.",
    )
    description_text = String(
        default="For real-time discussions and quick questions, join our dedicated Slack channel:",
        scope=Scope.settings,
        help="Introductory text displayed above the button.",
    )

    def resource_string(self, path):
        """Handy helper for loading resources from our package."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_channel_name(self):
        """Generate or return the channel name"""
        if not self.auto_generate_channel and self.channel_name:
            return self.channel_name.lower().replace(" ", "-")

        # Auto-generate from course context
        course_id = str(self.course_id) if hasattr(self, "course_id") else "general"
        # Clean course ID for Slack channel naming rules
        clean_name = (
            course_id.lower().replace(":", "-").replace("+", "-").replace("/", "-")
        )
        return f"course-{clean_name}"

    def get_slack_channel_url(self):
        """Generate the full Slack channel URL"""
        if not self.slack_workspace_url:
            return None

        base_url = self.slack_workspace_url.rstrip("/")
        channel = self.get_channel_name()
        return f"{base_url}/channels/{channel}"

    def get_slack_invite_url(self):
        """Generate Slack workspace invite URL"""
        if not self.slack_workspace_url:
            return None

        base_url = self.slack_workspace_url.rstrip("/")
        return f"{base_url}/join/shared_invite"

    def render_template(self, template_path, context={}):
        """Renders a Jinja2 template."""
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader(self.runtime.handler_path))
        template = env.get_template(template_path)
        return template.render(context)

    def student_view(self, context=None):  # pylint: disable=W0613
        """
        The primary view of the XBlock, shown to students when viewing courses.
        """
        context = context or {}

        # Prepare context for template
        template_context = {
            "display_name": self.display_name,
            "channel_name": self.get_channel_name(),
            "channel_url": self.get_slack_channel_url(),
            "invite_url": self.get_slack_invite_url(),
            "channel_description": self.channel_description,
            "show_member_count": self.show_member_count,
            "workspace_configured": bool(self.slack_workspace_url),
        }

        html = self.resource_string("static/html/slack_xblock.html")
        template = Template(html)
        rendered_html = template.render(Context(template_context))

        # create the fragment with rendered HTML
        frag = Fragment(rendered_html)
        frag.add_css(self.resource_string("static/css/slack_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/slack_xblock.js"))
        frag.initialize_js("SlackXBlock")  # Initialize the JavaScript for this XBlock

        return frag

    def studio_view(self, context=None):
        """
        The view of the XBlock in Open edX Studio for authors to configure.
        """
        # Use the mixin's studio view
        return super().studio_view(context)

    @XBlock.json_handler
    def submit_edits(self, data, suffix=""):
        """
        Handler for when students click to join the channel
        Could be used for analytics or future API integration
        """
        log.info(f"Student attempted to join Slack channel: {self.get_channel_name()}")

        return {"success": True}

    # Workbench scenarios for testing
    @staticmethod
    def workbench_scenarios():
        """Create scenarios for the workbench"""
        return [
            (
                "SlackXBlock",
                """<slack_xblock/>
             """,
            ),
            (
                "SlackXBlock Configured",
                """<slack_xblock 
                    display_name="CCI Discussion" 
                    slack_workspace_url="https://coding-campi.slack.com"
                    channel_name="general-discussion"
                    channel_description="Main discussion channel for Coding Camp I"
                />""",
            ),
        ]
