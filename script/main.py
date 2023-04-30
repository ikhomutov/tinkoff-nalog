from dotenv import load_dotenv

from script.fetcher import APIFetcher
from script.filler import Filler

load_dotenv()


def main():
    fetcher = APIFetcher()
    filler = Filler()
    input(
        "Залогиньтесь в личном кабинете налоговой, "
        "перейдите на страницу заполнения декларации и"
        "нажмите Enter"
    )
    reports = fetcher.fetch_dividends()
    for report in reports:
        filler.fill(report)

    input(
        "Отправьте декларацию, после чего нажмите Enter. "
        "Браузер закроется автоматически"
    )
