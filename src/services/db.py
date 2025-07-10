import json
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
import pandas as pd
import os

class VectorDBHandler:
    def __init__(self):
        args = {}
        args["name"] = "amazon.titan-embed-text-v2:0"
        args["region"] = "eu-central-1"
        model = get_registry().get("bedrock-text").create(**args)
        
        class TextModel(LanceModel):
            text: str = model.SourceField()
            vector: Vector(model.ndims()) = model.VectorField()
        
        table_name = "rag"
        
        self.db = lancedb.connect("../tables")
        db_tables= self.db.table_names()
        if "table_name" not in db_tables:
            print(f"Creating table {table_name}...")
            tbl = self.db.create_table(table_name, schema=TextModel, mode="overwrite")
            tbl.add(chunks)
        else:
            print(f"Table {table_name} already exists, using existing table...")
            tbl = db.open_table(table_name)