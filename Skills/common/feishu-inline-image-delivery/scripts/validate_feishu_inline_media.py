#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Validate Hermes Feishu inline image delivery on a machine with Hermes installed.

This script intentionally exercises Hermes' FeishuAdapter normal final-response
post-processing path (`_process_message_background`) with text plus MEDIA:/path.
It does not start a second Feishu websocket and does not use lark-cli to send.

Usage:
  cd ~/.hermes/hermes-agent
  ./venv/bin/python /path/to/validate_feishu_inline_media.py \
    --chat-id oc_xxx \
    --thread-id omt_xxx \
    --reply-to-message-id om_xxx \
    --user-id ou_xxx \
    --image /absolute/path/to/image.png \
    --marker test-inline-$(date +%Y%m%d%H%M%S)

After sending, read back the thread with lark-cli or Feishu API and verify:
  msg_type == post
  thread_id == the requested current thread
  content contains the marker text and [Image: img_v3_...]
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import MessageEvent
from gateway.platforms.feishu import FEISHU_DOMAIN, LARK_DOMAIN, FeishuAdapter
from gateway.session import SessionSource, build_session_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--reply-to-message-id", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--marker", required=True)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        raise SystemExit(f"image not found: {image}")

    adapter = FeishuAdapter(PlatformConfig(enabled=True, extra={}))
    # REST client only. Do not call connect(); the live gateway owns websocket/app lock.
    domain = FEISHU_DOMAIN if adapter._domain_name != "lark" else LARK_DOMAIN
    adapter._client = adapter._build_lark_client(domain)
    adapter._get_human_delay = lambda: 0.0

    async def handler(event: MessageEvent) -> str:
        return (
            f"{args.marker}\n"
            "Hermes Feishu inline image validation.\n"
            "This should appear as one Feishu post containing text plus an inline image.\n"
            f"MEDIA:{image}"
        )

    adapter.set_message_handler(handler)
    event = MessageEvent(
        text="inline image validation trigger",
        source=SessionSource(
            platform=Platform.FEISHU,
            chat_id=args.chat_id,
            user_id=args.user_id,
            thread_id=args.thread_id,
            chat_type="group",
        ),
        message_id="om_synthetic_inline_media_validation_trigger",
        reply_to_message_id=args.reply_to_message_id,
    )
    await adapter._process_message_background(event, build_session_key(event.source))
    print(json.dumps({
        "ok": True,
        "marker": args.marker,
        "chat_id": args.chat_id,
        "thread_id": args.thread_id,
        "reply_to_message_id": args.reply_to_message_id,
        "image": str(image),
        "sent_via": "Hermes FeishuAdapter._process_message_background normal text+MEDIA pipeline",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
