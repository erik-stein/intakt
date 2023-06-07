import base64
import json
import os
import time

import fortnox_data
import requests


class Fortnox:
    BASE_URL = "https://api.fortnox.se/3"
    REDIRECT_URI = "http://localhost:6060/auth"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

        self.try_read_token_from_file()

    def generate_vouchers(self) -> list:
        with open("response.json") as f:
            zettle_data = json.load(f)

        vouchers = []

        for utskott in zettle_data.keys():
            account_totals = {}

            for date, sold_items in zettle_data[utskott].items():
                account_totals[date] = {}

                for _itemName, item in sold_items.items():
                    if item["account"] in account_totals[date]:
                        account_totals[date][item["account"]] += (
                            item["quantity"] * item["unit_price"]
                        )
                    else:
                        account_totals[date][item["account"]] = (
                            item["quantity"] * item["unit_price"]
                        )

                voucher = {
                    "Voucher": {
                        "Description": fortnox_data.DATA[utskott][fortnox_data.DESC],
                        "TransactionDate": date,
                        "VoucherSeries": fortnox_data.VOUCHER_SERIES,
                        # "Year": year,
                        "VoucherRows": [
                            {
                                "Account": account,
                                "Credit": amount / 100,
                                "CostCenter": self.get_cost_center(
                                    utskott, account, date
                                ),
                            }
                            for account, amount in account_totals[date].items()
                        ],
                    }
                }
                voucher["Voucher"]["VoucherRows"].append(
                    {
                        "Account": fortnox_data.ACCOUT_ZETTLE,
                        "Debit": sum(account_totals[date].values()) / 100,
                    }
                )
                vouchers.append(voucher)

        print(json.dumps(vouchers[0]))
        return vouchers

    def get_cost_center(self, utskott: str, account: int, date: str) -> str:
        try:
            return fortnox_data.DATA[utskott][fortnox_data.COST_CENTERS][account]
        except KeyError:
            # TODO add timestamp to prompt
            return input(f"Cost center for {utskott} on {date}: ")

    def try_read_token_from_file(self) -> None:
        saved_token_file_path = (
            os.path.dirname(os.path.realpath(__file__))
            + "/../main/credentials/last_used_fortnox_token.json"
        )

        try:
            with open(saved_token_file_path) as saved_token_file:
                saved_token_obj = json.load(saved_token_file)

            self.access_token = saved_token_obj["access_token"]
            self.refresh_token = saved_token_obj["refresh_token"]
            self.expires_at = saved_token_obj["expires_at"]

        except FileNotFoundError:
            pass

    def save_token(self) -> None:
        saved_token_file_path = (
            os.path.dirname(os.path.realpath(__file__))
            + "/../main/credentials/last_used_fortnox_token.json"
        )

        with open(saved_token_file_path, "w") as saved_token_file:
            json.dump(
                {
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires_at": self.expires_at,
                },
                saved_token_file,
            )

    def get_access_token(self) -> None:
        if self.refresh_token:
            res = requests.post(
                "https://apps.fortnox.se/oauth-v1/token",
                data=f"grant_type=refresh_token&refresh_token={self.refresh_token}",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()}",
                },
            )

            if res.ok:
                res_json = res.json()
                self.access_token = res_json["access_token"]
                self.refresh_token = res_json["refresh_token"]
                self.expires_at = res_json["expires_in"] + time.time()
                self.save_token()
                return

        if self.auth_code is None:
            raise Exception("No auth code")

        res = requests.post(
            "https://apps.fortnox.se/oauth-v1/token",
            data=f"grant_type=authorization_code&code={self.auth_code}&redirect_uri={self.REDIRECT_URI}",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()}",
            },
        )
        if res.ok:
            res_json = res.json()
            self.access_token = res_json["access_token"]
            self.refresh_token = res_json["refresh_token"]
            self.expires_at = res_json["expires_in"] + time.time()
            self.save_token()
        else:
            raise Exception(f"Error: {res.status_code} {res.reason}")

    def get(self, url: str) -> dict:
        if self.access_token is None or time.time() >= self.expires_at:
            self.get_access_token()

        res = requests.get(
            self.BASE_URL + url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )
        if res.ok:
            return res.json()

        raise Exception(f"Error: {res.status_code} {res.reason}")

    def post(self, url: str, data: dict) -> dict:
        if self.access_token is None or time.time() >= self.expires_at:
            self.get_access_token()

        res = requests.post(
            self.BASE_URL + url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json=data,
        )
        return res.json()

    def post_many(self, url: str, data: list) -> list:
        if self.access_token is None or time.time() >= self.expires_at:
            self.get_access_token()

        res_list = []

        for d in data:
            res = requests.post(
                self.BASE_URL + url,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json=d,
            )
            if not res.ok:
                # TODO: Handle error
                raise Exception(f"Error: {res.status_code} {res.reason}")

            res_list.append(res.json())

            # Fortnox API rate limit is 300 requests per minute (5 requests per second)
            time.sleep(1 / 5)

        return res_list
