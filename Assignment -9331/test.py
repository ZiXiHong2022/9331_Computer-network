def query_process(Qname, Qtype):
    Answer_section = []
    Authority_section = set()
    Additional_section = set()
    processed_records = set()
    
    def recursive_query(Qname, Qtype):
        while True:
            if Qname in in_cache:
                rtype, rvalue = in_cache[Qname]
                record = f"{Qname},{rtype},{rvalue}"
                if record not in processed_records:
                    processed_records.add(record)
                    if Qtype == rtype:
                        Answer_section.append(record)
                        break  # Exit the loop after finding the match
                    else:
                        if rtype == 'CNAME':
                            Answer_section.append(record)
                            Qname = rvalue
                        else:
                            break
                else:
                    break  # Exit the loop if the record has been processed
            else:
                break  # Exit the loop if Qname is not in cache
    
    recursive_query(Qname, Qtype)
    
    # If no answer was found, handle NS records
    if not Answer_section:
        root_domain = '.'
        ns_key = (root_domain, 'NS')
        if ns_key in in_cache:
            for ns_record in in_cache[ns_key]:
                if (root_domain, 'NS', ns_record) not in Authority_section:
                    Authority_section.add((root_domain, 'NS', ns_record))
                a_key = (ns_record, 'A')
                if a_key in in_cache:
                    for a_record in in_cache[a_key]:
                        if (ns_record, 'A', a_record) not in Additional_section:
                            Additional_section.add((ns_record, 'A', a_record))

    response = {
        "query": Qname,
        "answer": list(Answer_section),
        "authority": list(Authority_section),
        "additional": list(Additional_section)
    }
    return response

# Initialize the required global variables
Answer_section = []
Authority_section = set()
Additional_section = set()

# Load your in_cache as before
in_cache = {
    'foo.example.com.': ('CNAME', 'bar.example.com.'),
    'bar.example.com.': ('CNAME', 'foobar.example.com.'),
    'foobar.example.com.': ('A', '192.0.2.24'),
    'foobar.example.com.': ('A', '192.0.2.23')
}

# Example usage
Qname = 'foo.example.com.'
Qtype = 'A'
response = query_process(Qname, Qtype)
print(response)
