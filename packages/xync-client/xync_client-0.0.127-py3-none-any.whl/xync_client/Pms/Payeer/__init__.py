import logging
from asyncio import run
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from math import ceil
from time import sleep

from asyncpg.pgproto.pgproto import timedelta
from payeer_api import PayeerAPI
from playwright.async_api import async_playwright, Playwright, Error
from playwright._impl._errors import TimeoutError

from xync_client.loader import TORM

from xync_client.Abc.PmAgent import PmAgentClient
from xync_client.Pms.Payeer.login import login


class Client(PmAgentClient):
    class Pages(StrEnum):
        _base = "https://payeer.com/en/"
        LOGIN = _base + "auth/"
        SEND = _base + "account/send/"

    norm: str = "payeer"
    pages: type(StrEnum) = Pages
    api: PayeerAPI

    async def start(self, pw: Playwright, headed: bool = False) -> "PmAgentClient":
        await super().start(pw, headed)
        if api_id := self.agent.auth.get("api_id"):
            self.api = PayeerAPI(self.agent.auth["email"], api_id, self.agent.auth["api_sec"])
        return self

    async def _login(self):
        await login(self.agent)
        for cookie in self.agent.state["cookies"]:
            await self.page.context.add_cookies([cookie])
        await self.page.goto(self.pages.SEND)

    async def send(self, dest: str, amount: int, cur: str) -> tuple[int, bytes, int] | int:
        self.last_active = datetime.now()
        page = self.page
        if not page.url.startswith(self.pages.SEND):
            try:
                await page.goto(self.pages.SEND)
            except (TimeoutError, Error):
                await login(self.agent)
                for cookie in self.agent.state["cookies"]:
                    await page.context.add_cookies([cookie])
                sleep(0.5)
                await page.goto("https://payeer.com/en/account/send/")
        has_amount = float(self.api.get_balance()[cur]["DOSTUPNO"])
        if float(amount) <= has_amount:
            sleep(0.1)
            await page.locator('input[name="param_ACCOUNT_NUMBER"]').fill(dest)
            await page.locator("select[name=curr_receive]").select_option(value=cur)
            sleep(0.8)
            await page.locator('input[name="sum_receive"]').fill(str(amount))
            sleep(0.1)
            # await page.locator("div.n-form--title").first.click()
            # sleep(0.1)
            await page.click(".btn.n-form--btn.n-form--btn-mod")
            sleep(0.5)
            await page.click(".btn.n-form--btn.n-form--btn-mod")
            sleep(1.1)
            if await page.locator(".input4").count():
                await page.locator(".input4").fill(self.agent.auth.get("master_key"))
                await page.click(".ok.button_green2")
            sleep(1)
            try:
                await page.locator(".note_txt").wait_for(state="visible", timeout=6000)
            except TimeoutError as _:
                logging.error("Repeat!")
                sleep(0.5)
                return await self.send(dest, amount, cur)
            if await page.locator('.note_txt:has-text("successfully completed")').count():
                transaction = await page.locator(".note_txt").all_text_contents()
                trans_num = int(transaction[0].replace("Transaction #", "").split()[0])
                await page.goto("https://payeer.com/ru/account/history/")
                await page.click(f".history-id-{trans_num} a.link")
                sleep(1)
                receipt = await page.query_selector(".ui-dialog.ui-corner-all")
                return trans_num, await receipt.screenshot(path=f"tmp/{dest}.png"), int(has_amount - amount)
            else:
                await self.bot.send("Payeer хз", self.uid, photo=await self.page.screenshot())
                return -1
        else:
            await self.bot.send(
                f"Payeer no have {amount}, only {has_amount}{cur} to {dest}",
                self.uid,
                photo=await self.page.screenshot(),
            )
            return has_amount

    def check_in(
        self, amount: Decimal | int | float, cur: str, tme: datetime = None, tid: str | int = None
    ) -> tuple[Decimal | None, int | None]:
        history = self.api.history(type="incoming", append=tid, count=3)
        if tid:
            return (t := history.get(tid)) and Decimal(t["creditedAmount"])
        t = [
            h
            for h in history.values()
            if (
                amount <= Decimal(h["creditedAmount"]) <= ceil(amount)
                and h["creditedCurrency"] == cur
                and datetime.fromisoformat(h["date"]) > tme - timedelta(minutes=1)
            )
        ]
        if not (t := t and t[0]):
            return None, None
        return (
            amount <= (am := Decimal(t["creditedAmount"])) <= ceil(amount) and t["creditedCurrency"] == cur
        ) and am, t["id"]

    async def proof(self) -> bytes: ...


async def main(uid: int):
    from x_model import init_db

    _ = await init_db(TORM, True)
    playwright: Playwright = await async_playwright().start()
    pyr = Client(uid)
    try:
        await pyr.start(playwright, False)

        dest, amount, cur = "P79619335", 2, "RUB"

        res = await pyr.send(dest, amount, cur)
        res = await pyr.send(dest, 3, cur)
        res = await pyr.send(dest, amount, cur)
        res = await pyr.send(dest, 3, cur)
        res = await pyr.send(dest, amount, cur)

        res = pyr.check_in(2, cur, datetime.now())

        if len(res) > 1 and isinstance(res[1], bytes):
            await pyr.bot.send(f"Transaction #{res[0]}", uid, photo=res[1])
        elif res[0] > 0:
            await pyr.bot.send(f"Sreen of transaction #{res[0]} failed", uid, photo=await pyr.page.screenshot())
        else:
            await pyr.bot.send(f"Sending {amount} {cur} to {dest} FAILED", uid, photo=await pyr.page.screenshot())

    except TimeoutError as te:
        await pyr.bot.send(repr(te), uid, photo=await pyr.page.screenshot())
        raise te
    # finally:
    #     await pyr.stop()


if __name__ == "__main__":
    run(main(1779829771))
