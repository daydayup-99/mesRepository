import pymysql
import io
def export_table_structure_and_data(host, user, password, database, table_name, output_file):
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=3306
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_table_stmt = cursor.fetchone()[1]
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"{create_table_stmt};\n\n")
                cursor.execute(f"SELECT * FROM `{table_name}`")
                rows = cursor.fetchall()
                for row in rows:
                    values = ', '.join([f"'{str(value)}'" if value is not None else 'NULL' for value in row])
                    f.write(f"INSERT INTO `{table_name}` VALUES ({values});\n")
        print(f"表 {table_name} 数据成功导出到 {output_file}...")
        # with connection.cursor() as cursor:
        #     cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        #     create_table_stmt = cursor.fetchone()[1]
        #     insert_values = []
        #     cursor.execute(f"SELECT * FROM `{table_name}`")
        #     rows = cursor.fetchall()
        #     for row in rows:
        #         values = ', '.join([f"'{str(value)}'" if value is not None else 'NULL' for value in row])
        #         insert_values.append(f"({values})")
        #     insert_stmt = ""
        #     if insert_values:
        #         insert_stmt = f"INSERT INTO `{table_name}` VALUES " + ", ".join(insert_values) + ";\n"
        #     with io.open(output_file, 'w', encoding='utf-8',buffering=4096) as f:
        #         f.write(f"{create_table_stmt};\n\n")
        #         if insert_stmt:
        #             f.write(insert_stmt)
        #     print(f"表 {table_name} 数据成功导出到 {output_file}...")
    finally:
        connection.close()


if __name__ == "__main__":
    host = input("请输入 MySQL 主机地址 (例如: 10.10.8.119): ")
    user = 'root'
    password = 'YMZ123'
    database = 'avi'
    input_name = input("请输入要导出的表名时间 (例如: 20241127): ")
    table_name = [f'tab_test_{input_name}', f'tab_err_{input_name}']
    for i in table_name:
        output_file = f"{i}.sql"
        export_table_structure_and_data(host, user, password, database, i, output_file)
