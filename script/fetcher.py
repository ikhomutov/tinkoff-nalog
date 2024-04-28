"""Модуль отвечает за получаение данных о дивидендах"""
import logging
import os
from datetime import datetime, UTC
from time import sleep

from tinkoff.invest import Client
from tinkoff.invest import schemas
from tinkoff.invest.utils import quotation_to_decimal

from script.dto import Report

logger = logging.getLogger(__name__)


class APIFetcher:
    def __init__(self):
        self.token = os.getenv("TINKOFF_TOKEN")
        self.account_id = os.getenv("TINKOFF_ACCOUNT_ID")
        year = int(os.getenv("YEAR"))
        self.date_from = datetime(year, 1, 1, 0, 0, tzinfo=UTC)
        self.date_to = datetime(year, 12, 31, 23, 59, tzinfo=UTC)

    def _get_div_foreign_issuer_report_kwargs(self, task_id, page=0):
        return {
            'get_div_foreign_issuer_report': schemas.GetDividendsForeignIssuerReportRequest(
                task_id=task_id,
                page=page
            )
        }

    def _generate_div_foreign_issuer_report_kwargs(self):
        return {
            'generate_div_foreign_issuer_report': schemas.GenerateDividendsForeignIssuerReportRequest(
                account_id=self.account_id,
                from_=self.date_from,
                to=self.date_to
            )
        }

    def _fetch_data_from_tinkoff(self, client, **kwargs):
        print('Fetching data with kwargs: %s' % kwargs)
        result = client.operations.get_dividends_foreign_issuer(**kwargs)
        print('Got response from tinkoff: %s' % result)
        return result

    def fetch_dividends(self):
        with Client(self.token) as client:
            reports = []
            kwargs = self._generate_div_foreign_issuer_report_kwargs()
            while True:
                result = self._fetch_data_from_tinkoff(client, **kwargs)
                if result.generate_div_foreign_issuer_report_response is None:
                    # В ответе содержится сгенерированный результат
                    # TODO: стоит добавить итерирование по страницам
                    reports.extend(result.div_foreign_issuer_report.dividends_foreign_issuer_report)
                    break
                sleep(1)
            return [
                Report(
                    payment_date=report.payment_date,
                    company=report.security_name,
                    country=report.issuer_country,
                    amount=quotation_to_decimal(report.dividend_gross),
                    tax=quotation_to_decimal(report.tax),
                    currency=report.currency,
                ) for report in reports
            ]
