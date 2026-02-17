from celery import shared_task
from ETL.Extractor import Extractor
from ETL.Transformer import Transformer
from ETL.Loader import Loader

@shared_task
def extract_task(json_file_path):
    extractor = Extractor(json_file_path)
    raw_data = extractor.extract()
    return raw_data

@shared_task
def transform_task(raw_data):
    transformer = Transformer(raw_data)
    df = transformer.transform()
    stats = transformer.get_statistics()
    return {"df": df.to_dict(), "stats": stats}

@shared_task
def load_task(transformed):
    loader = Loader(transformed["df"])
    result = loader.load()
    return {"status": "success", "details": result}

@shared_task
def notify_task(load_result):
    return {"pipeline": "completed", "details": load_result}
