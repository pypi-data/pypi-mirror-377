import json

# Creating a JSON schema file
# Ref: https://cloud.google.com/bigquery/docs/schemas#creating_a_JSON_schema_file
# test:
# 1. https://transform.tools/json-to-big-query
# 2. https://bigquery-json-schema-generator.com/


class BigquerySchema:
    # get generic bq coloum schema
    @staticmethod
    def _get_generic_coloum_schema(col_name: str, col_type="STRING", col_mode="NULLABLE"):
        """
        generic bigquery column schema
        """
        generic_coloum_schema = {}
        generic_coloum_schema["name"] = col_name
        generic_coloum_schema["type"] = col_type
        if col_mode != "NULLABLE":
            generic_coloum_schema["mode"] = col_mode
        # generic_coloum_schema["description"] = "_" + col_name
        return generic_coloum_schema

    # generate bigquery schema
    @staticmethod
    def generate_bq_schema(data: dict):
        """
        generate bigquery schema
        """
        out_schema = []
        for i, j in data.items():
            if type(j) == str:
                out_schema.append(
                    BigquerySchema._get_generic_coloum_schema(col_name=str(i))
                )
            elif type(j) == int:
                out_schema.append(
                    BigquerySchema._get_generic_coloum_schema(col_name=str(i), col_type="INTEGER")
                )
            elif type(j) == list:
                element = j[0]
                if type(element) == str:
                    out_schema.append(
                        BigquerySchema._get_generic_coloum_schema(col_name=str(i),
                                                                    col_mode="repeated")
                    )
                elif type(element) == int:
                    out_schema.append(
                        BigquerySchema._get_generic_coloum_schema(col_name=str(i),
                                                                    col_type="INTEGER",
                                                                    col_mode="repeated")
                    )
                elif type(element) == dict:
                    dict_obj = BigquerySchema._get_generic_coloum_schema(col_name=str(i),
                                                                           col_type="record")
                    dict_obj["fields"] = BigquerySchema.generate_bq_schema(element)
                    out_schema.append(dict_obj)
            elif type(j) == dict:
                dict_obj = BigquerySchema._get_generic_coloum_schema(col_name=str(i),
                                                                       col_type="record")
                dict_obj["fields"] = BigquerySchema.generate_bq_schema(j)
                out_schema.append(dict_obj)
            else:
                pass
        return out_schema


if __name__ == "__main__":
    bs = BigquerySchema()
    with open("tests//test_data//sample_json_01.json") as json_file:
        sample_dict = json.load(json_file)
    out = bs.generate_bq_schema(data=sample_dict)
    print(f"output from generate_bq_schema:\n{out}")
