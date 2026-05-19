from __future__ import annotations

import pandas as pd

from models.schemas import OptionsChainSnapshot


class OptionsFeatureBuilder:
    """Builds options-chain pressure and anomaly features."""

    def build(self, frame: pd.DataFrame, snapshots: list[OptionsChainSnapshot]) -> pd.DataFrame:
        if frame.empty:
            return frame
        if not snapshots:
            for column in (
                "pcr",
                "pcr_trend",
                "call_oi_change",
                "put_oi_change",
                "iv",
                "iv_trend",
                "iv_spike",
                "max_pain_distance",
                "unusual_oi_activity",
                "options_volume_imbalance",
            ):
                frame[column] = 0.0
            return frame
        options = pd.DataFrame([snapshot.model_dump() for snapshot in snapshots])
        options["timestamp"] = pd.to_datetime(options["timestamp"], utc=True)
        options["date"] = options["timestamp"].dt.floor("D")
        frame = frame.copy()
        frame["date"] = pd.to_datetime(frame["timestamp"], utc=True).dt.floor("D")
        latest_by_day = options.sort_values("timestamp").groupby("date").tail(1).set_index("date")
        joined = frame.merge(latest_by_day.drop(columns=["symbol", "timestamp"]), how="left", left_on="date", right_index=True)
        for column in ("pcr", "call_oi_change", "put_oi_change", "iv", "options_volume_call", "options_volume_put"):
            joined[column] = joined[column].ffill().fillna(0.0)
        joined["pcr_trend"] = joined["pcr"].diff(3).fillna(0.0)
        joined["iv_trend"] = joined["iv"].diff(3).fillna(0.0)
        joined["iv_spike"] = (joined["iv"] > joined["iv"].rolling(20, min_periods=3).mean() + 2 * joined["iv"].rolling(20, min_periods=3).std(ddof=0)).astype(int)
        joined["max_pain"] = joined["max_pain"].ffill()
        joined["max_pain_distance"] = (joined["close"] - joined["max_pain"]) / joined["close"].replace(0, pd.NA)
        oi_total = joined["call_oi_change"].abs() + joined["put_oi_change"].abs()
        joined["unusual_oi_activity"] = oi_total / oi_total.rolling(20, min_periods=3).mean().replace(0, pd.NA)
        volume_total = joined["options_volume_call"] + joined["options_volume_put"]
        joined["options_volume_imbalance"] = (joined["options_volume_put"] - joined["options_volume_call"]) / volume_total.replace(0, pd.NA)
        return joined.drop(columns=["date"])
