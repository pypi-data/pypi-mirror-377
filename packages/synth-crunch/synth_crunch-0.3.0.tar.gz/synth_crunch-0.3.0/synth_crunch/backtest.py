import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas
from tqdm.auto import tqdm

from .baseline import BaselineMiner
from .data import shared_pyth_hermes
from .interface import Asset, GenerateSimulationsOutput, SynthMiner
from .test import (ONE_DAY, ResolvedTestOutput, score_simulations,
                   validate_output, validate_simulation_parameters)

logger = logging.getLogger()


@dataclass(frozen=True)
class BacktestOutput:
    start: datetime
    end: datetime
    cycle_interval: int
    asset: Asset
    time_increment: int
    time_length: int
    num_simulations: int
    validate_output: bool
    prices: pandas.Series
    scores: pandas.DataFrame

    @property
    def total_miner_score(self) -> float:
        return self.scores["miner_score"].sum()

    @property
    def total_baseline_score(self) -> float:
        return self.scores["baseline_score"].sum()


def run(
    miner: SynthMiner,
    *,
    start=datetime(2024, 2, 1),
    end: datetime | None = None,
    cycle_interval: int = 60 * 60,
    asset: Asset = "BTC",
    time_increment: int = 300,
    time_length: int = ONE_DAY,
    num_simulations: int = 300,
    validate_output: bool = True,
):
    """
    Run a backtest.

    :param miner: The SynthMiner instance to run.
    :param start: The start date for the backtest.
    :param end: The end date for the backtest. If None, it will be set to the current time.
    :param cycle_interval: The interval in seconds for each simulation cycle (default to 1h).
    :param asset: The asset to run the backtest on.
    :param time_increment: The resolution of the predictions in seconds (default is 5min, must be >=60s).
    :param time_length: The total length of the predictions in seconds (default is 1day, must be >=60s).
    :param num_simulations: The number of simulations to run (default is 300, must be >0).
    :param validate_output: Whether to validate the output of the simulations (default is True).
    :raises ValueError: If there is not enough time between `end` and the present.
    """

    validate_simulation_parameters(
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
    )

    baseline_miner = BaselineMiner()
    now = datetime.now()

    required_seconds_before_present = time_length + (time_increment * 2)
    if end is None:
        end = now - timedelta(seconds=required_seconds_before_present)
    elif end + timedelta(seconds=required_seconds_before_present) > now:
        raise ValueError("`end` must not be too close to the present time")
    if end < start:
        raise ValueError("`end` must not be before `start`")

    start = start.replace(second=0, microsecond=0, tzinfo=timezone.utc)
    end = end.replace(second=0, microsecond=0, tzinfo=timezone.utc)

    simulation_dates = _collect_dates(
        start=start,
        end=end,
        cycle=timedelta(seconds=cycle_interval)
    )

    prices = _collect_prices(
        asset=asset,
        start=start,
        end=end,
        time_length=time_length,
        time_increment=time_increment,
    )

    scores: list[tuple[datetime, float, float]] = []

    for date in tqdm(simulation_dates, desc="Running simulations", unit="date"):
        logger.info(f"running simulations - date={date.isoformat()}")

        miner_results = _generate_and_score_simulations(
            miner=miner,
            date=date,
            prices=prices,
            asset=asset,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            should_validate_output=validate_output,
        )

        baseline_results = _generate_and_score_simulations(
            miner=baseline_miner,
            date=date,
            prices=prices,
            asset=asset,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            should_validate_output=False,
        )

        score_date = date + timedelta(seconds=time_length)
        scores.append((
            score_date,
            miner_results.score,
            baseline_results.score,
        ))

    dataframe = pandas.DataFrame(
        scores,
        columns=[
            "date",
            "miner_score",
            "baseline_score"
        ],
    )

    dataframe.set_index("date", inplace=True)

    return BacktestOutput(
        start=start,
        end=end,
        cycle_interval=cycle_interval,
        asset=asset,
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
        validate_output=validate_output,
        prices=prices,
        scores=dataframe,
    )


def _collect_dates(
    *,
    start: datetime,
    end: datetime,
    cycle: timedelta,
    inclusive: bool = False,
) -> list[datetime]:
    dates = []

    current = start
    while current < end:
        dates.append(current)
        current += cycle

    if inclusive:
        dates.append(current)

    return dates


def _collect_prices(
    *,
    asset: Asset,
    start: datetime,
    end: datetime,
    time_length: int,
    time_increment: int,
) -> pandas.Series:
    prices_dates = _collect_dates(
        start=start,
        end=end + timedelta(seconds=time_length + time_increment),
        cycle=timedelta(days=6),
        inclusive=True,
    )

    all_prices: list[pandas.Series] = []

    for from_, to in zip(prices_dates[:-1], prices_dates[1:]):
        logger.debug(f"collecting prices - from={from_} to={to}")

        prices = shared_pyth_hermes.get_price_history(
            asset=asset,
            from_=from_,
            to=to,
            resolution="minute",
            timeout=120,
        )

        all_prices.append(prices)

    prices = pandas.concat(all_prices)

    # [from_, to] are inclusive
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]

    prices = prices.resample("min").ffill()
    return prices


def _generate_and_score_simulations(
    *,
    miner: SynthMiner,
    date: datetime,
    prices: pandas.Series,
    asset: Asset,
    time_increment: int,
    time_length: int,
    num_simulations: int,
    should_validate_output: bool,
):
    simulations: GenerateSimulationsOutput = miner.generate_simulations(
        asset=asset,
        current_price=prices[date],
        start_time=date.isoformat(),
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
    )

    if should_validate_output:
        validate_output(
            simulations=simulations,
            num_simulations=num_simulations,
            time_length=time_length,
            time_increment=time_increment,
        )

    result = ResolvedTestOutput(
        simulations=simulations,
        asset=asset,
        start=date,
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
        validate_output=should_validate_output,
        prices=prices,
    )

    return score_simulations(result)


def visualize(
    result: "BacktestOutput",
    *,
    figsize: tuple[int, int] = (10, 6),
    cumulative: bool = False,
):
    """
    Visualize the backtest results.

    :param result: The BacktestOutput instance containing the results.
    :param figsize: The size of the figure to plot.
    :param cumulative: If True, plot cumulative scores; otherwise, plot raw scores.
    """

    scores = result.scores

    plt.figure(figsize=figsize)

    if cumulative:
        plt.plot(scores.index, scores["miner_score"].cumsum(), label="Miner Score (cum.)")
        plt.plot(scores.index, scores["baseline_score"].cumsum(), label="Baseline Score (cum.)")
        hint = "cumulative, lower is better"
    else:
        plt.plot(scores.index, scores["miner_score"], label="Miner Score")
        plt.plot(scores.index, scores["baseline_score"], label="Baseline Score")
        hint = "lower is better"

    plt.title(f"Your Miner Score vs Baseline {result.asset} Score Over Time ({hint})")
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()
