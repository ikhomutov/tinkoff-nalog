from dotenv import load_dotenv

from script.fetcher import APIFetcher
from script.filler import Filler

load_dotenv()


def main():
    fetcher = APIFetcher()
    reports = fetcher.fetch_dividends()
    filler = Filler()
    input(
        "Залогиньтесь в личном кабинете налоговой, "
        "перейдите на страницу заполнения декларации и"
        "нажмите Enter"
    )
    try:
        for report in reports:
            filler.fill(report)
    except Exception as e:
        print(e)
        import ipdb; ipdb.set_trace()

    input(
        "Отправьте декларацию, после чего нажмите Enter. "
        "Браузер закроется автоматически"
    )
