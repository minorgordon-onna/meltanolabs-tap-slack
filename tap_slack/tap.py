"""Slack tap class."""

from typing import List, Optional

from singer_sdk import Tap, Stream
from singer_sdk import typing as th
from singer_sdk.helpers._compat import final

from tap_slack.streams import (
    ChannelsStream,
    ChannelMembersStream,
    MessagesStream,
    ThreadsStream,
    UsersStream,
)

STREAM_TYPES = [
    UsersStream,
    ChannelsStream,
    ChannelMembersStream,
    MessagesStream,
    ThreadsStream,
]


class TapSlack(Tap):
    """Slack tap class."""

    name = "tap-slack"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the Slack API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        # th.Property(
        #     "thread_lookback_days",
        #     th.IntegerType,
        #     default=1,
        #     description="The number of days to look in the past for new thread replies to existing messages",
        # ),
        th.Property(
            "channel_types",
            th.ArrayType(th.StringType),
            default=["public_channel"],
            description="The types of conversations the tap will attempt to extract data from. Must be one of 'public_channel', 'mpim', 'private_channel', or 'im'. Note that the Slack app must have the appropriate privileges and be a member of the conversations to sync messages.",
        ),
        th.Property(
            "auto_join_channels",
            th.BooleanType,
            default=False,
            description="Whether the bot user should attempt to join channels that it has not yet joined. The bot user must be a member of the channel to retrieve messages.",
        ),
        th.Property(
            "selected_channels",
            th.ArrayType(th.StringType),
            description="A list of channel IDs that should be retrieved. If not defined then all are selected.",
        ),
        th.Property(
            "excluded_channels",
            th.ArrayType(th.StringType),
            description="A list of channel IDs that should not be retrieved. Excluding overrides a selected setting, so if a channel is included in both selected and excluded, it will be excluded.",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

    def load_streams(self) -> List[Stream]:
        # Hack: the parent class sorts streams by type and name
        # We want users to always be first.
        sorted_streams = Tap.load_streams(self)
        other_streams: List[Stream] = []
        users_stream: Optional[UsersStream] = None
        for stream in sorted_streams:
            if isinstance(stream, UsersStream):
                users_stream = stream
            else:
                other_streams.append(stream)
        assert users_stream is not None
        return [users_stream] + other_streams

    @property
    def expectations(self):
        return [
            "tap__cli",
            "tap__discovery",
            "tap__stream_connections",
        ]


if __name__ == "__main__":
    TapSlack.cli()
