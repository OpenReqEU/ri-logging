# class for creating SQL for mysql tables
class RiLoggingMySqlQueryCreator:
    sizes: dict = {
        "string": "255",
        "integer": "11",
        "float": ["12", "4"]
    }
    datatypes: dict = {
        "string": "VARCHAR",
        "integer": "INT",
        "float": "DECIMAL"
    }

    @staticmethod
    def table_exists(table_name: str):
        sql = "SHOW TABLES LIKE '" + table_name + "';"
        return sql

    @staticmethod
    def create_table(table_name: str, target_name, timestamp_name, fields: list) -> str:
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + " ("
        sql += "id INT(" + RiLoggingMySqlQueryCreator.sizes.get("integer") + ") NOT NULL AUTO_INCREMENT,"
        sql += target_name + " VARCHAR(" + RiLoggingMySqlQueryCreator.sizes.get("string") + ") NOT NULL,"
        sql += timestamp_name + " DATETIME NOT NULL,"
        for field in fields:
            field_datatype = "string"
            if field.get("datatype") is not None:
                field_datatype = field.get("datatype")
            sql += field.get("name") + " " + str(RiLoggingMySqlQueryCreator.datatypes.get(field_datatype))
            if RiLoggingMySqlQueryCreator.sizes.get(field_datatype, "") != "":
                datatype = RiLoggingMySqlQueryCreator.sizes.get(field_datatype, "")
                if type(datatype) is list:
                    datatype = ",".join(datatype)
                sql += "(" + datatype + ")"
            sql += " NOT NULL,"
        sql += "PRIMARY KEY (id)"
        sql += ") ENGINE=MyISAM DEFAULT CHARSET=utf8 DEFAULT COLLATE utf8_general_ci;"

        return sql

    @staticmethod
    def create_insert_query(table_name: str, field_name_target: str, field_name_timestamp: str, fields: list, values: dict) -> str:
        query = "INSERT INTO " + table_name + "("
        query_fields = [field_name_target, field_name_timestamp]
        query_values = ["\"" + values.get(field_name_target) + "\"", "\"" + values.get(field_name_timestamp) + "\""]

        for field in fields:
            query_fields.append(field.get("name"))
        query += ", ".join(query_fields) + ") VALUES "

        for field in fields:
            value = values.get(field.get("name"))
            datatype = "string"
            if field.get("datatype") is not None:
                datatype = field.get("datatype")
            query_values.append(RiLoggingMySqlQueryCreator.format_value(value=value, datatype=datatype))

        query += "(" + ", ".join(query_values) + ");"

        return query

    @staticmethod
    def format_value(value, datatype: str):
        if datatype == "integer":
            if type(value) is str and value == "" or value is None:
                value = 0
            else:
                value = int(value)
        if datatype == "float":
            if type(value) is str and value == "":
                value = 0.0
            else:
                datatype_limits = RiLoggingMySqlQueryCreator.sizes.get(datatype)
                value = round(float(value), int(datatype_limits[1]))
        if datatype == "string":
            if type(value) is not str:
                value = ""
            if len(value) >= int(RiLoggingMySqlQueryCreator.sizes.get(datatype)):
                value = value[:int(RiLoggingMySqlQueryCreator.sizes.get(datatype))]
            value = "\"" + value + "\""

        return str(value)
