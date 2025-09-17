class Message_Query:
    get_message_query = """
        query message($input: MessageFilterInput) {
            message(input: $input) {
                id
                arbId
                name
                networkName
                ecuId
                ecuName
                fileId
            }
        }
    """

class Message_Mutation:
    create_message_mutation = """
        mutation createMessage($input: CreateMessageInput!) {
            createMessage(input: $input) {
                id
                arbId
                name
                networkName
                ecuId
                ecuName
                fileId
            }
        }
    """
