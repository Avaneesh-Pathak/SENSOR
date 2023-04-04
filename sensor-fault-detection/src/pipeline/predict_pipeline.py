import shutil
import os,sys
import pandas as pd
from src.logger import logging

from src.exception import CustomException
import sys
from fastapi import File
from src.utils import download_model, load_object

from dataclasses import dataclass
        
        
@dataclass
class PredictionFileDetail:
    prediction_file_path:str = "predictions/predicted_file.csv"
    prediction_file_name:str =  "predicted_file.csv"


class PredictionPipeline:
    def __init__(self, file:File):

        self.file = file 
        self.prediction_file_detail = PredictionFileDetail()



    def save_input_files(self)-> str:

        """
            Method Name :   save_input_files
            Description :   This method saves the input file to the prediction artifacts directory. 
            
            Output      :   input dataframe
            On Failure  :   Write an exception log and then raise an exception
            
            Version     :   1.2
            Revisions   :   moved setup to cloud
        """

        try:
            pred_file_input_dir = "prediction_artifacts/input_file.csv"
            os.makedirs(pred_file_input_dir, exist_ok=True)

            pred_file_path = os.path.join(pred_file_input_dir, self.file.filename)
            
            with open(pred_file_path, 'wb') as f:
                shutil.copyfileobj(self.file.file, f)
            
            logging.info("Prediction input file saved")


            return pred_file_path
        except Exception as e:
            raise CustomException(e,sys)

    def predict(self, features):
            try:
                model_path = download_model(
                    bucket_name="ineuron-test-bucket-123",
                    bucket_file_name="model.pkl",
                    dest_file_name="model.pkl",
                )

                model = load_object(file_path=model_path)

                preds = model.predict(features)

                return preds

            except Exception as e:
                raise CustomException(e, sys)
        
    def get_predicted_dataframe(self, input_dataframe_path:pd.DataFrame):

        """
            Method Name :   get_predicted_dataframe
            Description :   this method returns the dataframw with a new column containing predictions

            
            Output      :   predicted dataframe
            On Failure  :   Write an exception log and then raise an exception
            
            Version     :   1.2
            Revisions   :   moved setup to cloud
        """
   
        try:

            prediction_column_name : str = "class"
            input_dataframe: pd.DataFrame = pd.read_csv(input_dataframe_path)
            predictions = self.predict(input_dataframe)
            input_dataframe[prediction_column_name] = [pred for pred in predictions]

            input_dataframe.to_csv(self.prediction_file_detail.prediction_file_path)



        except Exception as e:
            raise CustomException(e, sys) from e
        

        
    def run_pipeline(self):
        try:
            input_csv_path = self.save_input_files()
            self.get_predicted_dataframe(input_csv_path)

            return self.prediction_file_detail


        except Exception as e:
            raise CustomException(e,sys)
            
        

 
        

        