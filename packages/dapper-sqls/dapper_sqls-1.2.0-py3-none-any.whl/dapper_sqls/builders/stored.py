# coding: utf-8
from typing import Type
from pydantic import BaseModel

class StoredBuilder:
    @staticmethod
    def _build_where_clause(**kwargs):
        conditions = []
        parameters = []
        for field, value in kwargs.items():
            if value is not None:
                    conditions.append(f"{field} = ?")
                    parameters.append(value)
        return " AND ".join(conditions), tuple(parameters)

    @classmethod
    def update(cls, model: Type[BaseModel], where: Type[BaseModel]):
        model._reset_defaults()
        where._reset_defaults()
        update_data = {k: int(v) if isinstance(v, bool) else v for k, v in model.model_dump(mode="json", exclude_none=True).items()}
        where_data = {k: int(v) if isinstance(v, bool) else v for k, v in where.model_dump(mode="json", exclude_none=True).items()}

        for key in where_data:
            if key in update_data:
                update_data.pop(key, None)
       
        where_clause, where_params = cls._build_where_clause(**where_data)

        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        sql_query = f"UPDATE {model.TABLE_NAME} SET {set_clause} WHERE {where_clause}"

        return sql_query, tuple(update_data.values()) + where_params

    @classmethod
    def insert(cls, model : Type[BaseModel], name_column_id = 'Id'):
        model._reset_defaults()
        insert_data = {k: int(v) if isinstance(v, bool) else v for k, v in model.model_dump(mode="json", exclude_none=True).items()}
        columns = ", ".join(insert_data.keys())
        values = ", ".join(["?" for _ in insert_data.values()])
        sql_query = f"""
            INSERT INTO {model.TABLE_NAME} ({columns})
            OUTPUT INSERTED.{name_column_id} AS Id
            VALUES ({values})
            """
        return sql_query, tuple(insert_data.values())

    @classmethod
    def select(cls, model : Type[BaseModel], additional_sql : str = "" ,select_top : int= None):
        model._reset_defaults()
        top_clause = f"TOP ({select_top}) * " if select_top else "*"
        select_data = {k: int(v) if isinstance(v, bool) else v for k, v in model.model_dump(mode="json", exclude_none=True).items()}
        where_clause, parameters = cls._build_where_clause(**select_data)

        sql_query = f"SELECT {top_clause} FROM {model.TABLE_NAME}" 
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        sql_query = f'{sql_query} {additional_sql}'
        return sql_query, parameters

    @classmethod
    def delete(cls, model : Type[BaseModel]):
        model._reset_defaults()
        delete_data = {k: int(v) if isinstance(v, bool) else v for k, v in model.model_dump(mode="json", exclude_none=True).items()}
        where_clause, parameters = cls._build_where_clause(**delete_data)
        if not where_clause:
            raise ValueError("DELETE operation requires at least one condition.")
        sql_query = f"DELETE FROM {model.TABLE_NAME} WHERE {where_clause}"
        return sql_query, parameters




