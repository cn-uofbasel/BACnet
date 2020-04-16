from logStore_pkg import SqLiteConnector

def main():
    connector = SqLiteConnector.SqLiteConnector
    connector.name_database(connector, 'TestDatabase')
    connector.start_database_connection(connector)
    connector.create_table(connector, 'chat')
    connector.insert_to_table(connector, 'chat', '20:45', 'Peter', 'Hallo')
    connector.insert_to_table(connector, 'chat', '20:46', 'Max', 'Hallo')
    connector.insert_to_table(connector, 'chat', '20:47', 'Gustavo', 'Hallo')

    connector.get_all_from_table(connector, 'chat')
    rows = connector.cursor.fetchall()

    for row in rows:
        print(row)

    print("\n")
    connector.search_in_table(connector, 'chat', 'Peter')

    rows = connector.cursor.fetchall()
    print(rows)

    connector.commit_changes(connector)

    connector.close_table(connector, 'chat')

    connector.close_database_connection(connector)



if __name__ == '__main__':
    main()