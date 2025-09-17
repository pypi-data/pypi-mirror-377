class Network_Query:
    get_network_query = """
        query GetNetworks($input: NetworkFilterInput) {
            network(input: $input) {
                id
                name
            }
        }
    """
