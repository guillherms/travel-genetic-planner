import logging
import pandas as pd
from io import StringIO
from pydantic import ValidationError
from core.model.files_schema import FileSchema
from streamlit.runtime.uploaded_file_manager import UploadedFile
  
class FileUtils:
    @staticmethod
    def read_csv(uploaded_file: UploadedFile) -> pd.DataFrame:
        try:
            df = pd.read_csv(uploaded_file)
            FileUtils._validate_schema(df)
            return df
        except Exception as e:
            logging.exception("Error reading CSV file")
            raise

    @staticmethod
    def _validate_schema(df: pd.DataFrame) -> None:
        required = {"places","latitude","longitude","mon","tue","wed","thu","fri","sat","sun","estimated_duration_min","priority"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        for i, row in df.iterrows():
            try:
                FileSchema(**row.to_dict())
            except ValidationError as e:
                raise ValueError(f"Validation error in row {i}: {e}")

    @staticmethod
    def from_string(csv_string: str) -> pd.DataFrame:
        df = pd.read_csv(StringIO(csv_string))
        df.columns = df.columns.str.strip()
        return df