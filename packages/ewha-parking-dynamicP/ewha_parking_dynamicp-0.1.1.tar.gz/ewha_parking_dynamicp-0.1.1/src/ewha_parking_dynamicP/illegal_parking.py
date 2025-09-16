import warnings
from typing import Dict, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


class IllegalParking:
    """
    Identify illegal parking points using geopandas.sjoin on GIS layers.

    Assumptions
    -----------
    - All layers & points use CRS = EPSG:4326 (WGS84).
    - Input has a 'Geometry' column containing shapely Points or 'POINT(lon lat)' strings.

    Output columns:
      ['CCTV_ID', 'time', 'Geometry', 'Leaving_time', 'Traj_ID', 'Duration', 'ufid']

    Parameters
    ----------
    illegal_parking_df : gpd.GeoDataFrame
        A GeoDataFrame containing the illegal parking area geometries.
    """

    def __init__(self, illegal_parking_df: gpd.GeoDataFrame) -> None:
        self.gdf_layers = self._process_layers(illegal_parking_df)

    # ------------------------- helpers ------------------------- #
    def _process_layers(self, illegal_parking_df: gpd.GeoDataFrame) -> Dict[str, gpd.GeoDataFrame]:
        """Process the input DataFrame and separate layers by type."""
        if not isinstance(illegal_parking_df, gpd.GeoDataFrame):
            raise TypeError("illegal_parking_df must be a GeoDataFrame.")

        # CRS 확인 및 변환
        if illegal_parking_df.crs is None:
            warnings.warn("Input GeoDataFrame has no CRS; assuming EPSG:4326.")
            illegal_parking_df.set_crs(epsg=4326, inplace=True)
        elif illegal_parking_df.crs.to_epsg() != 4326:
            illegal_parking_df = illegal_parking_df.to_crs(epsg=4326)

        # 'type_id' 열을 사용하여 레이어를 분리
        layers: Dict[str, gpd.GeoDataFrame] = {}
        layer_mapping_1min_ids = [0, 1, 2, 3, 5, 6]
        layer_mapping_5min_ids = [7, 8, 10, 11]

        if 'type_id' not in illegal_parking_df.columns:
            raise KeyError("The input illegal_parking_df must have a 'type_id' column to differentiate area types.")

        layers['1min_areas'] = illegal_parking_df[illegal_parking_df['type_id'].isin(layer_mapping_1min_ids)]
        layers['5min_areas'] = illegal_parking_df[illegal_parking_df['type_id'].isin(layer_mapping_5min_ids)]
        layers['custom_area'] = illegal_parking_df[illegal_parking_df['type_id'] == 11]

        return layers

    @staticmethod
    def _parse_point(value):
        """Parse 'POINT(lon lat)' to Point; passthrough if already Point."""
        if isinstance(value, Point):
            return value
        if isinstance(value, str) and value.startswith("POINT("):
            try:
                lon, lat = value.replace("POINT(", "").replace(")", "").split()
                return Point(float(lon), float(lat))
            except Exception:
                return None
        return None

    @staticmethod
    def _flag_within(points: gpd.GeoDataFrame, polys: gpd.GeoDataFrame) -> pd.Series:
        """
        Return boolean Series aligned to points.index, True if point is within any polygon.
        Uses geopandas.sjoin(predicate='within') and reduces multiple hits via any().
        """
        if polys.empty:
            return pd.Series(False, index=points.index)

        left = points[["Geometry"]].reset_index()
        joined = gpd.sjoin(left, polys[["geometry"]], how="left", predicate="within")
        flags = joined.groupby("index")["index_right"].apply(lambda s: s.notna().any())
        return flags.reindex(points.index, fill_value=False)

    # --------------------------- API --------------------------- #
    def analyze(self, frequent_parking_result: pd.DataFrame) -> pd.DataFrame:
        """Apply rule-based illegal parking detection using spatial joins."""
        if frequent_parking_result is None or frequent_parking_result.empty or "Geometry" not in frequent_parking_result.columns:
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        gdf = frequent_parking_result.copy()

        if gdf["Geometry"].dtype == object:
            gdf["Geometry"] = gdf["Geometry"].apply(self._parse_point)
        
        gdf.dropna(subset=["Geometry"], inplace=True)
        if gdf.empty:
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])
        
        gdf = gpd.GeoDataFrame(gdf, geometry="Geometry", crs="EPSG:4326")

        if "Duration" not in gdf.columns:
            warnings.warn("Duration column not found. Illegal parking analysis will be skipped.")
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        if not pd.api.types.is_timedelta64_dtype(gdf["Duration"]):
            try:
                gdf["Duration"] = pd.to_timedelta(gdf["Duration"])
            except Exception:
                warnings.warn("Could not convert 'Duration' to Timedelta.")
                return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])
        
        gdf["duration_minutes"] = gdf["Duration"].dt.total_seconds() / 60.0

        # 공간 조인 기반 플래그
        in_1min_area = self._flag_within(gdf, self.gdf_layers["1min_areas"])
        in_5min_area = self._flag_within(gdf, self.gdf_layers["5min_areas"])
        in_custom_area = self._flag_within(gdf, self.gdf_layers["custom_area"])

        dur = gdf["duration_minutes"].fillna(0)

        # 불법 주차 규칙 적용
        # 1분 조건: 1분 구역 내에 있고, custom_area에는 없는 경우
        illegal_1min = (dur >= 1) & in_1min_area & (~in_custom_area)
        # 5분 조건: 5분 구역 내에 있거나, 1분 구역 내에 있으면서 custom_area에도 있는 경우
        illegal_5min = (dur >= 5) & (in_5min_area | (in_1min_area & in_custom_area))

        mask = illegal_1min | illegal_5min
        if not mask.any():
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        sel = gdf.loc[mask].drop_duplicates()
        
        output_cols = ["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"]
        
        final_df = pd.DataFrame(sel[output_cols])

        return final_df

    def call(self, frequent_parking_result: pd.DataFrame) -> pd.DataFrame:
        """Alias for analyze()."""
        return self.analyze(frequent_parking_result)