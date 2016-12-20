from api_imports import *

@endpoints.api(name='stats',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class StatsApi(remote.Service):
    @endpoints.method(AccountMessage, AccountStatsMessage,
            path='accountStatsOnDemand',
            http_method='POST', name='accountStatsOnDemand')
    def accountStatsOnDemand(self, request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountKey = Key(Account, int(request.accountId))

        # Get all the distinct years.
        years = Bill.query(projection=['year'], distinct=True, ancestor = accountKey).fetch()
        year_counts = {}
        for year in years:
            year_counts[year.year] = Bill.query(Bill.year == year.year, ancestor = accountKey).count()

        asm = AccountStatsMessage()
        asm.bill_count = sum(year_counts.values())
        for year in years:
            ysm = YearStatsMessage()
            ysm.year = year.year
            ysm.bill_count = year_counts[year.year]

            # Get distinct months
            months = Bill.query(Bill.year == year.year, projection=['month'], distinct=True, ancestor = accountKey).fetch()
            for month in months:
                msm = MonthStatsMessage()
                msm.month = month.month
                msm.bill_count = Bill.query(Bill.year == year.year, Bill.month == month.month, ancestor = accountKey).count()
                ysm.month_stats.append(msm)

            asm.year_stats.append(ysm)

        return asm
