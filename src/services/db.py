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
        self.model = get_registry().get("bedrock-text").create(**args)
        self.table_name = "rag"
        
        class TextModel(LanceModel):
            text: str = self.model.SourceField()
            vector: Vector(self.model.ndims()) = self.model.VectorField()
        
        self.textModel = TextModel
        
    def load_files(self, files):
        chunks = []
        for file in files:
            text = file.read().decode()
            chunks.append({"text": text})
        
        self.db = lancedb.connect("./tables")
        self.db.drop_table(self.table_name)
        db_tables= self.db.table_names()
        if self.table_name not in db_tables:
            print(f"Creating table {self.table_name}...")
            self.tbl = self.db.create_table(self.table_name, schema=self.textModel, mode="overwrite")
            self.tbl.add(chunks)
        else:
            print(f"Table {self.table_name} already exists, using existing table...")
            self.tbl = self.db.open_table(self.table_name)
        
    def get_best(self, n, message):
        rs = self.tbl.search(message).limit(n)
        rs.to_pydantic(self.textModel)
        df = rs.to_pandas()
        
        res = []
        
        for i in range(min(n, len(df))):
            res.append(df.iloc[i]["text"])
        
        return res
        
        