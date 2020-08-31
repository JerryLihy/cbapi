import cbapi

def test_cbapi():
    # normal search for people
    search_test_1 = cbapi.get_information(info_type = 'people', name = 'jobs')
    print('search_test_1, first 5 rows: ', search_test_1.head(5))
    print()
    
    # normal search for organizations
    search_test_2 = cbapi.get_information(info_type = 'organizations', name = 'jobs', page = 1)
    print('search_test_2, first 5 rows: ', search_test_2.head(5))
    print()
    
    # given page too large
    search_test_3 = cbapi.get_information(info_type = 'organizations', name = 'jobs', page = 200)
    print('search_test_3, first 5 rows: ', search_test_3.head(5))
    print()
    
    # no results found for the given info
    search_test_4 = cbapi.get_information(info_type = 'organizations', name = 'fdsafdsfasdfasdfsdf')
    print('search_test_4, first 5 rows: ', search_test_4.head(5))
    print()
    
    # invalid search type
    search_test_5 = cbapi.get_information(info_type = 'dadfsdydy', name = 'jobs')
    print('search_test_5, first 5 rows: ', search_test_5.head(5))
    print()

if __name__ == "__main__":
    test_cbapi()




