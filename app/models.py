from pydantic import BaseModel, Field, validator, root_validator, ValidationError
from datetime import datetime
from typing import List, Dict, Optional, Literal
from collections import Counter

def format_datetime(value):
    try:
        dt_obj = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        dt_obj = datetime.strptime(value, "%Y-%m-%d")

    return dt_obj.strftime("%Y-%m-%d")

class TrainReady(BaseModel):
    source: Optional[Literal['PHONE', 'LIIKE','UNKNOWN', 'KUPLA']] = None
    accepted: Optional[bool] = None
    timestamp: Optional[str] = None

    @validator('timestamp')
    def change_datetime_format(cls, v):
        try:
            return format_datetime(v)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}")

    @validator('source', 'timestamp', pre=True)
    def trim_spaces(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class Causes(BaseModel):
    categoryCodeId: Optional[int] = None
    detailedCategoryCodeId: Optional[int] = None
    thirdCategoryCodeId: Optional[int] = None

class TimeTableRows(BaseModel):
    type: Literal['ARRIVAL', 'DEPARTURE']
    trainStopping: bool
    commercialStop: Optional[bool] = None
    commercialTrack: str
    cancelled: bool
    scheduledTime: str
    liveEstimateTime: Optional[str] = None  
    estimateSource: Optional[Literal["LIIKE_USER", "MIKU_USER", "LIIKE_AUTOMATIC", "UNKNOWN", "COMBOCALC"]] = None  
    unknownDelay: Optional[bool] = None
    actualTime: Optional[str] = None
    differenceInMinutes: Optional[int] = None
    stationShortCode: str
    stationUICCode: int
    countryCode: str
    causes: Optional[List[Causes]] = None
    trainReady: Optional[TrainReady] = None

    @validator('scheduledTime', "liveEstimateTime", 'actualTime')
    def change_datetime_format(cls, v):
        try:
            return format_datetime(v)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}")

    @validator('stationShortCode', 'countryCode','type', 'commercialTrack','scheduledTime','actualTime', pre=True)
    def trim_spaces(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator('stationShortCode', pre=True)
    def testes(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class Item(BaseModel):
    trainNumber: int = Field(..., frozen=True, required=True)
    trainType: str
    trainCategory: str
    commuterLineID: str
    runningCurrently: bool
    cancelled: bool
    deleted: Optional[bool] = None
    version: Optional[int] = None
    timetableType: Literal['REGULAR', 'ADHOC']
    timetableAcceptanceDate: str
    timeTableRows: Optional[List[TimeTableRows]]
    departureDate: str
    operatorUICCode: int
    operatorShortCode: str

    @validator('trainType', 'trainCategory','trainType', 'timetableAcceptanceDate', 'operatorShortCode','commuterLineID', 'timetableType',"departureDate", pre=True)
    def trim_spaces(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @classmethod
    def check_duplicates(cls, data: List[dict]):
        train_ids = [entry['trainNumber'] for entry in data]
        counter = Counter(train_ids)
        
        duplicates = [train_id for train_id, count in counter.items() if count > 1]
        return duplicates

    @classmethod
    def check_required_fields(cls, data: List[dict]):
        required_fields = ['trainNumber', 'departureDate', "deleted"]
        missing_fields = [field for field in required_fields for entry in data if field not in entry]
        
        return ', '.join(missing_fields)

    @classmethod
    def fields_issues(cls, data: List[dict]):
        the_list = []

        for entry in data:
            if entry['departureDate'] is None:
                the_list.append('departureDate')
            if entry['trainNumber'] is None:
                the_list.append('trainNumber')

            try:
                format_datetime(entry['departureDate'])
            except:
                the_list.append('trainNumber')

        return list(set(the_list))

    

class TrainDataModel(BaseModel):
    data: List[Item]
    num_records: int = 0
    columns_with_issues: List = []
    duplicated_trainid: List = []
    missing_required_fields: List = []
    

    @property
    def num_records(self):
        return len(self.data)


    @root_validator(pre=True)
    def set_num_records(cls, values):
        values['num_records'] = len(values.get('data', []))
        return values


    @root_validator(pre=True)
    def remove_duplicates(cls, values):
        items = values.get('data', [])
        #unique_trains = {frozenset(item.items()) for item in items}
        #values['data'] = [dict(train) for train in unique_trains]

        return values

    @root_validator(pre=True)
    def required_fields(cls, values):
        data = values.get('data', [])

        #values['missing_required_fields'] = Item.check_required_fields(data)

        return values
    
    @root_validator(pre=True)
    def issue(cls, values):
        data = values.get('data', [])

        values['columns_with_issues'] = Item.fields_issues(data)

        return values

    @root_validator(pre=True)
    def checking_duplicated(cls, values):
        data = values.get('data', [])

        values['duplicated_trainid'] = Item.check_duplicates(data)

        return values
