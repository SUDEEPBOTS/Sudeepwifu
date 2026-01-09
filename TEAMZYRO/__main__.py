from TEAMZYRO import *
import importlib
import logging
import asyncio
from TEAMZYRO.modules import ALL_MODULES


async def post_init(application):
    await ZYRO.start()


def main() -> None:

    # Load all modules (safe)
    for module_name in ALL_MODULES:
        importlib.import_module("TEAMZYRO.modules." + module_name)
        
    LOGGER("TEAMZYRO.modules").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    application.post_init = post_init

    # Prevent "Event loop is closed"
    application.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )

    LOGGER("TEAMZYRO").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎MADE BY GOJOXNETWORK☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )


if __name__ == "__main__":
    main()
